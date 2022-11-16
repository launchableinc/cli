package com.launchableinc.ingest.commits;

import ch.qos.logback.classic.Level;
import com.google.common.annotations.VisibleForTesting;
import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.lib.RepositoryBuilder;
import org.eclipse.jgit.util.FS;
import org.kohsuke.args4j.Argument;
import org.kohsuke.args4j.CmdLineException;
import org.kohsuke.args4j.CmdLineParser;
import org.kohsuke.args4j.Option;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** Driver for {@link CommitGraphCollector}. */
public class CommitIngester {
  @Deprecated
  @Argument(required = true, metaVar = "COMMAND", index = 0)
  public String dummyCommandForBackwardCompatibility;

  @Argument(required = true, metaVar = "PATH", usage = "Path to Git repository", index = 1)
  public File repo;

  @Option(name = "-org", usage = "Organization ID")
  public String org;

  @Option(name = "-ws", usage = "Workspace ID")
  public String ws;

  @Option(name = "-endpoint", usage = "Endpoint to send the data to.")
  public URL url = new URL("https://api.mercury.launchableinc.com/intake/");

  @Option(name = "-dry-run", usage = "Instead of actually sending data, print what it would do.")
  public boolean dryRun;

  /**
   * @deprecated this is an old option and this is on always.
   */
  @Deprecated
  @Option(name = "-scrub-pii", usage = "Scrub emails and names", hidden = true)
  public boolean scrubPii;

  /**
   * @deprecated this is an old option and this is off always.
   */
  @Deprecated
  @Option(name = "-commit-message", usage = "Collect commit messages")
  public boolean commitMessage;

  @Option(
      name = "-max-days",
      usage = "The maximum number of days to collect commits retroactively.")
  public int maxDays = 30;

  @Option(name = "-audit", usage = "Whether to output the audit log or not")
  public boolean audit;

  private Authenticator authenticator;

  @VisibleForTesting String launchableToken = null;

  public CommitIngester() throws CmdLineException, MalformedURLException {}

  public static void main(String[] args) throws Exception {
    CommitIngester ingester = new CommitIngester();
    CmdLineParser parser = new CmdLineParser(ingester);
    try {
      parser.parseArgument(args);
      ingester.run();
    } catch (CmdLineException e) {
      // signals error meant to be gracefully handled
      System.err.println(e.getMessage());
      System.exit(2);
    }
  }

  /**
   * @deprecated Here to keep backward compatibility.
   */
  @Deprecated
  @Option(name = "-no-commit-message", usage = "Do not collect commit messages", hidden = true)
  public void setNoCommitMessage(boolean b) {
    commitMessage = !b;
  }

  /** Ensures all the configuration is properly in place. */
  private void parseConfiguration() throws CmdLineException {
    String apiToken = launchableToken;
    if (launchableToken == null) {
      apiToken = System.getenv("LAUNCHABLE_TOKEN");
    }
    if (apiToken == null || apiToken.isEmpty()) {
      if (System.getenv("GITHUB_ACTIONS") != null) {
        String o = System.getenv("LAUNCHABLE_ORGANIZATION");
        if (org == null && o == null) {
          throw new CmdLineException("LAUNCHABLE_ORGANIZATION env variable is not set");
        }

        String w = System.getenv("LAUNCHABLE_WORKSPACE");
        if (ws == null && w == null) {
          throw new CmdLineException("LAUNCHABLE_WORKSPACE env variable is not set");
        }

        if (org == null) {
          this.org = o;
        }

        if (ws == null) {
          this.ws = w;
        }

        if (System.getenv("EXPERIMENTAL_GITHUB_OIDC_TOKEN_AUTH") != null) {
          authenticator = new GitHubIdTokenAuthenticator();
        } else {
          authenticator = new GitHubActionsAuthenticator();
        }
        return;
      }

      throw new CmdLineException("LAUNCHABLE_TOKEN env variable is not set");
    }

    this.parseLaunchableToken(apiToken);
  }

  @VisibleForTesting
  void run() throws CmdLineException, MalformedURLException, IOException {
    parseConfiguration();

    URL endpoint = new URL(url, String.format("organizations/%s/workspaces/%s/commits/", org, ws));
    try (Repository db =
        new RepositoryBuilder().setFS(FS.DETECTED).findGitDir(repo).setMustExist(true).build()) {
      Git git = Git.wrap(db);
      CommitGraphCollector cgc = new CommitGraphCollector(git.getRepository());
      cgc.setMaxDays(maxDays);
      cgc.setAudit(audit);
      cgc.setDryRun(dryRun);
      cgc.transfer(endpoint, authenticator);
      int numCommits = cgc.getCommitsSent();
      String suffix = "commit";
      if (numCommits != 1) {
        suffix = "commits";
      }
      System.out.printf("Launchable recorded %d %s from repository %s%n", numCommits, suffix, repo);
    }
  }

  private void parseLaunchableToken(String token) throws CmdLineException {
    if (token.startsWith("v1:")) {
      String[] v = token.split(":");
      if (v.length != 3) {
        throw new IllegalStateException("Malformed LAUNCHABLE_TOKEN");
      }
      v = v[1].split("/");
      if (v.length != 2) {
        throw new IllegalStateException("Malformed LAUNCHABLE_TOKEN");
      }

      // for backward compatibility, allow command line options to take precedence
      if (org == null) {
        org = v[0];
      }
      if (ws == null) {
        ws = v[1];
      }
    } else {
      // "v0" token doesn't contain org/ws, so they need to be explicitly configured
      if (org == null) {
        throw new CmdLineException("Organization must be specified with the -org option");
      }
      if (ws == null) {
        throw new CmdLineException("Workspace must be specified with the -ws option");
      }
    }

    authenticator = new TokenAuthenticator(token);
  }

  static {
    // JGit uses high logging level for errors that it recovers, and those messages are confusing
    // to users. So let's shut them off
    Logger logger = LoggerFactory.getLogger("org.eclipse.jgit");
    if (logger instanceof ch.qos.logback.classic.Logger) {
      ch.qos.logback.classic.Logger logbackLogger = (ch.qos.logback.classic.Logger) logger;
      logbackLogger.setLevel(Level.OFF);
    }
  }
}
