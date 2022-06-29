package com.launchableinc.ingest.commits;

import static com.google.common.collect.ImmutableList.toImmutableList;

import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.io.CharStreams;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.Closeable;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.UncheckedIOException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.function.Supplier;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;
import org.apache.http.Header;
import org.apache.http.HttpResponse;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.EntityTemplate;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.eclipse.jgit.diff.DiffAlgorithm.SupportedAlgorithm;
import org.eclipse.jgit.diff.DiffEntry;
import org.eclipse.jgit.errors.InvalidObjectIdException;
import org.eclipse.jgit.errors.MissingObjectException;
import org.eclipse.jgit.lib.ConfigConstants;
import org.eclipse.jgit.lib.ObjectId;
import org.eclipse.jgit.lib.ObjectReader;
import org.eclipse.jgit.lib.PersonIdent;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.revwalk.RevCommit;
import org.eclipse.jgit.revwalk.RevSort;
import org.eclipse.jgit.revwalk.RevWalk;
import org.eclipse.jgit.revwalk.filter.CommitTimeRevFilter;
import org.eclipse.jgit.submodule.SubmoduleWalk;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Compares what commits the local repository and the remote repository have, then send delta over.
 */
public class CommitGraphCollector {
  private static final Logger logger = LoggerFactory.getLogger(CommitGraphCollector.class);
  private static final ObjectMapper objectMapper = new ObjectMapper();

  /**
   * Root repository to start processing.
   *
   * <p>Sub modules form a tree structure rooted at this repository.
   */
  private final Repository root;

  private int commitsSent;

  private int maxDays;

  private boolean audit;

  private boolean dryRun;

  private String dryRunPrefix() {
    if (!dryRun) {
      return "";
    }
    return "(DRY RUN) ";
  }

  private boolean outputAuditLog() {
    return audit || dryRun;
  }

  public CommitGraphCollector(Repository git) {
    this.root = git;
  }

  /** How many commits did we transfer? */
  public int getCommitsSent() {
    return commitsSent;
  }

  private String dumpHeaderAsJson(Header[] headers) throws JsonProcessingException {
    ObjectNode header = objectMapper.createObjectNode();
    for (Header h : headers) {
      header.put(h.getName(), h.getValue());
    }
    return objectMapper.writeValueAsString(header);
  }

  /** Transfers the commits to the remote endpoint. */
  public void transfer(URL service, Authenticator authenticator) throws IOException {
    URL url;
    try (CloseableHttpClient client =
        HttpClientBuilder.create()
            .useSystemProperties()
            .setDefaultHeaders(authenticator.getAuthenticationHeaders())
            .build()) {
      url = new URL(service, "latest");
      if (outputAuditLog()) {
        System.err.printf(
            "AUDIT:launchable:%ssend request method:get path: %s%n", dryRunPrefix(), url);
      }
      ImmutableList<ObjectId> advertised =
          getAdvertisedRefs(handleError(url, client.execute(new HttpGet(url.toExternalForm()))));

      // every time a new stream is needed, supply ByteArrayOutputStream, and when the data is all
      // written, turn around and ship that over
      transfer(
          advertised,
          () -> {
            try {
              return new GZIPOutputStream(
                  new ByteArrayOutputStream() {
                    @Override
                    public void close() throws IOException {
                      URL url = new URL(service, "collect");
                      HttpPost request = new HttpPost(url.toExternalForm());
                      request.setHeader("Content-Type", "application/json");
                      request.setHeader("Content-Encoding", "gzip");
                      request.setEntity(new EntityTemplate(this::writeTo));

                      if (outputAuditLog()) {
                        InputStreamReader gzip =
                            new InputStreamReader(
                                new GZIPInputStream(new ByteArrayInputStream(toByteArray())),
                                StandardCharsets.UTF_8);
                        String json = CharStreams.toString(gzip);
                        System.err.printf(
                            "AUDIT:launchable:%ssend request method:post path:%s headers:%s"
                                + " args:%s%n",
                            dryRunPrefix(), url, dumpHeaderAsJson(request.getAllHeaders()), json);
                      }
                      if (dryRun) {
                        return;
                      }
                      handleError(url, client.execute(request));
                    }
                  });
            } catch (IOException e) {
              throw new UncheckedIOException(e);
            }
          },
          256);
    }
  }

  private ImmutableList<ObjectId> getAdvertisedRefs(HttpResponse response) throws IOException {
    JsonParser parser = new JsonFactory().createParser(response.getEntity().getContent());
    String[] ids = objectMapper.readValue(parser, String[].class);
    return Arrays.stream(ids)
        .map(
            s -> {
              try {
                return ObjectId.fromString(s);
              } catch (InvalidObjectIdException e) {
                // if the server sends us a bogus data, don't penalize users, silently drop that
                return null;
              }
            })
        .filter(Objects::nonNull)
        .collect(toImmutableList());
  }

  /**
   * Writes delta between local commits to the advertised to JSON stream.
   *
   * @param streams Commits are written to streams provided by this {@link Supplier}, in the given
   *     chunk size.
   */
  public void transfer(
      Collection<ObjectId> advertised, Supplier<OutputStream> streams, int chunkSize)
      throws IOException {
    try (ChunkStreamer cs = new ChunkStreamer(streams, chunkSize)) {
      new ByRepository(root).transfer(advertised, cs);
    }
  }

  /**
   * {@link Consumer} that groups commits into chunks and write them as JSON, using streams supplied
   * by the factory.
   */
  private static final class ChunkStreamer implements Consumer<JSCommit>, Closeable {

    private final Supplier<OutputStream> streams;
    private JsonGenerator w;
    /** Count # of items we wrote to this stream. */
    private int count;

    private final int chunkSize;

    ChunkStreamer(Supplier<OutputStream> streams, int chunkSize) {
      this.streams = streams;
      this.chunkSize = chunkSize;
    }

    @Override
    public void accept(JSCommit commit) {
      try {
        if (w == null) {
          open();
        }
        w.writeObject(commit);
        if (++count >= chunkSize) {
          close();
        }
      } catch (IOException e) {
        throw new UncheckedIOException(e);
      }
    }

    public void open() throws IOException {
      w = new JsonFactory().createGenerator(streams.get()).useDefaultPrettyPrinter();
      w.setCodec(objectMapper);
      w.writeStartObject();
      w.writeArrayFieldStart("commits");
    }

    @Override
    public void close() throws IOException {
      if (w == null) {
        return; // already closed
      }
      w.writeEndArray();
      w.writeEndObject();
      w.close();
      w = null;
      count = 0;
    }
  }

  /** Pass through {@link CloseableHttpResponse} but checks and throws an error. */
  private CloseableHttpResponse handleError(URL url, CloseableHttpResponse response)
      throws IOException {
    int code = response.getStatusLine().getStatusCode();
    if (code >= 400) {
      throw new IOException(
          String.format(
              "Failed to retrieve from %s: %s%n%s",
              url,
              response.getStatusLine(),
              CharStreams.toString(
                  new InputStreamReader(
                      response.getEntity().getContent(), StandardCharsets.UTF_8))));
    }
    return response;
  }

  public void setMaxDays(int days) {
    this.maxDays = days;
  }

  public void setAudit(boolean audit) {
    this.audit = audit;
  }

  public void setDryRun(boolean dryRun) {
    this.dryRun = dryRun;
  }

  /** Process commits per repository. */
  final class ByRepository implements AutoCloseable {

    private final Repository git;

    private final ObjectReader objectReader;

    ByRepository(Repository git) {
      this.git = git;
      this.objectReader = git.newObjectReader();
    }

    /**
     * Writes delta between local commits to the advertised to JSON stream.
     *
     * @param receiver Receives commits that should be sent, one by one.
     */
    public void transfer(Collection<ObjectId> advertised, Consumer<JSCommit> receiver)
        throws IOException {
      try (RevWalk walk = new RevWalk(git)) {
        // walk reverse topological order, so that older commits get added to the server earlier.
        // This way, the connectivity of the commit graph will be always maintained
        walk.sort(RevSort.TOPO);
        walk.sort(RevSort.REVERSE, true);
        // also combine this with commit time based ordering, so that we can stop walking when we
        // find old enough commits AFAICT, this is no-op in JGit and it always sorts things in
        // commit time order, but it is in the contract, so I'm assuming we shouldn't rely on the
        // implementation optimization that's currently enabling this all the time
        walk.sort(RevSort.COMMIT_TIME_DESC, true);

        // don't walk commits too far back.
        // for our purpose of computing CUT, these are unlikely to contribute meaningfully
        // and it drastically cuts down the initial commit consumption of a new large repository.
        walk.setRevFilter(
            CommitTimeRevFilter.after(
                System.currentTimeMillis() - TimeUnit.DAYS.toMillis(maxDays)));

        ObjectId headId = git.resolve("HEAD");
        walk.markStart(walk.parseCommit(headId));

        for (ObjectId id : advertised) {
          try {
            RevCommit c = walk.parseCommit(id);
            walk.markUninteresting(c);
          } catch (MissingObjectException e) {
            // it's possible that the server advertises a commit we don't have.
            //
            // TODO: how does git-push handles the case when the client doesn't recognize commits?
            // Unless it tries to negotiate further what commits they have in common,
            // git-upload-pack can end up creating a big pack with lots of redundant objects
            //
            // think about a case when a client is pushing a new branch against
            // the master branch that moved on the server.
          }
        }

        // walk the commits, transform them, and send them to the receiver
        for (RevCommit c : walk) {
          JSCommit d = transform(c);
          receiver.accept(d);
          commitsSent++;
        }
      }

      /*
         Git submodule support
         =====================

         In a fully general version of the problem, every commit we are walking might point to
         different sub-module at different commit, so we should be walking over all of those.
         That will require us to resolve sub-modules, since there's no guarantee that those submodules
         are cloned and available.

         Here, we solve a weaker version of this, that works well enough for `launchable build record`
         and obtain commits needed to determine the subject.

         That is, find submodules that are available in the working tree (thus `!isBare()`), and
         collect all the commits from those repositories.
      */
      if (!git.isBare()) {
        try (SubmoduleWalk swalk = SubmoduleWalk.forIndex(git)) {
          while (swalk.next()) {
            try (Repository subRepo = swalk.getRepository()) {
              if (subRepo != null) {
                try (ByRepository br = new ByRepository(subRepo)) {
                  br.transfer(advertised, receiver);
                }
              }
            }
          }
        }
      }
    }

    private JSCommit transform(RevCommit r) throws IOException {
      JSCommit c = new JSCommit();
      c.setCommitHash(r.name());

      PersonIdent author = r.getAuthorIdent();
      c.setAuthorEmailAddress(JSCommit.hashEmail(author.getEmailAddress()));
      c.setAuthorWhen(author.getWhen().getTime());
      c.setAuthorTimezoneOffset(author.getTimeZoneOffset());

      PersonIdent committer = r.getCommitterIdent();
      c.setCommitterEmailAddress(JSCommit.hashEmail(committer.getEmailAddress()));
      c.setCommitterWhen(committer.getWhen().getTime());
      c.setCommitterTimezoneOffset(committer.getTimeZoneOffset());

      // Change the on-memory config for the diff algorithm.
      // CGit supports patience diff while JGit doesn't. Since the FileBasedRepository reads the
      // user's .gitconfig, if a user sets this
      // algorithm, JGit causes a failure. Changing this on-memory avoids this.
      git.getConfig()
          .setEnum(
              ConfigConstants.CONFIG_DIFF_SECTION,
              null,
              ConfigConstants.CONFIG_KEY_ALGORITHM,
              SupportedAlgorithm.HISTOGRAM);

      for (RevCommit p : r.getParents()) {
        CountingDiffFormatter diff = new CountingDiffFormatter(git);
        List<DiffEntry> files = diff.scan(p.getTree(), r.getTree());
        List<JSFileChange> changes = new ArrayList<>();
        for (DiffEntry de : files) {
          try {
            changes.add(diff.process(de));
          } catch (UncheckedIOException e) {
            logger.warn("Failed to process a change to a file", e);
          }
        }
        c.getParentHashes().put(p.name(), changes);
      }
      return c;
    }

    @Override
    public void close() {
      objectReader.close();
    }
  }
}
