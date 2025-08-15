package com.launchableinc.ingest.commits;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableList;
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream;
import org.apache.commons.io.IOUtils;
import org.apache.commons.io.output.NullOutputStream;
import org.apache.http.entity.ContentProducer;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.lib.ObjectId;
import org.eclipse.jgit.lib.PersonIdent;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.revwalk.RevCommit;
import org.eclipse.jgit.submodule.SubmoduleWalk;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.Collection;
import java.util.List;

import static com.google.common.truth.Truth.*;

@RunWith(JUnit4.class)
public class CommitGraphCollectorTest {

  @Rule public TemporaryFolder tmp = new TemporaryFolder();

  private File ws;
  private File subrepoDir;
  private File mainrepoDir;

  @Before
  public void setUp() throws IOException {
    ws = tmp.newFolder();
    subrepoDir = tmp.newFolder();
    mainrepoDir = tmp.newFolder();
  }

  @Test
  public void subtreeWalk() throws Exception {
    setupRepos();

    try (Git mainrepo = Git.open(mainrepoDir)) {
      // collect commits
      CommitGraphCollector cgc = collectCommit(mainrepo.getRepository(), ImmutableList.of());
      assertThat(cgc.getCommitsSent()).isEqualTo(2);

      addCommitInSubRepo(mainrepo);

      // collect commit again and make sure we find that new commit
      cgc = collectCommit(mainrepo.getRepository(), ImmutableList.of());
      assertThat(cgc.getCommitsSent()).isEqualTo(3);

      // if we consider HEAD of the main repo to be collected, we should just find commits in the
      // sub-repo, of which there are two
      cgc =
          collectCommit(
              mainrepo.getRepository(), ImmutableList.of(mainrepo.getRepository().resolve("HEAD")));
      assertThat(cgc.getCommitsSent()).isEqualTo(2);
    }
  }

  /** Deal gracefully with bare repo */
  @Test
  public void bareRepo() throws Exception {
    setupRepos();
    File barerepoDir = tmp.newFolder();
    Git.cloneRepository()
        .setBare(true)
        .setURI(mainrepoDir.toURI().toString())
        .setDirectory(barerepoDir)
        .call();

    // this should ignore submodules and just collect what we can, which is one commit in the
    // main.git
    try (Repository r = Git.open(barerepoDir).getRepository()) {
      CommitGraphCollector cgc = collectCommit(r, ImmutableList.of());
      assertThat(cgc.getCommitsSent()).isEqualTo(1);
      assertThat(cgc.getFilesSent()).isEqualTo(1);
    }
  }

  /** Tests the chunking behavior. */
  @Test
  public void chunking() throws Exception {
    int[] councCommitChunks = new int[1];
    int[] countFilesChunks = new int[1];

    // Create 3 commits
    setupRepos();
    try (Git mainrepo = Git.open(mainrepoDir)) {
      addCommitInSubRepo(mainrepo);
      CommitGraphCollector cgc = new CommitGraphCollector("test", mainrepo.getRepository());
      cgc.setMaxDays(30);
      cgc.collectFiles(true);
      cgc.transfer(
          ImmutableList.of(),
          (ContentProducer commits) -> {
            councCommitChunks[0]++;
            assertValidJson(commits);
          },
          new PassThroughTreeReceiverImpl(),
          (ContentProducer files) -> {
            countFilesChunks[0]++;
            assertValidTar(files);
          },
          2);
    }
    assertThat(councCommitChunks[0]).isEqualTo(2);
    assertThat(countFilesChunks[0]).isEqualTo(1); // a and sub/x, 2 files, 1 chunk
  }

  private void assertValidTar(ContentProducer content) throws IOException {
    try (TarArchiveInputStream tar = new TarArchiveInputStream(read(content))) {
      while (tar.getNextEntry() != null) {
        IOUtils.copy(tar, NullOutputStream.INSTANCE);
      }
    }
  }

  private void assertValidJson(ContentProducer content) throws IOException {
    new ObjectMapper().readTree(read(content));
  }

  private InputStream read(ContentProducer content) throws IOException {
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    content.writeTo(baos);
    return new ByteArrayInputStream(baos.toByteArray());
  }

  @Test
  public void scrubPii() throws Exception {
    PersonIdent committer = setupRepos();
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    try (Git mainrepo = Git.open(mainrepoDir)) {
      addCommitInSubRepo(mainrepo);
      CommitGraphCollector cgc = new CommitGraphCollector("test", mainrepo.getRepository());
      cgc.setMaxDays(30);
      cgc.transfer(ImmutableList.of(), c -> c.writeTo(baos), new PassThroughTreeReceiverImpl(), f -> {}, Integer.MAX_VALUE);
    }
    String requestBody = baos.toString(StandardCharsets.UTF_8);
    assertThat(requestBody).doesNotContain(committer.getEmailAddress());
    assertThat(requestBody).doesNotContain(committer.getName());
  }

  private CommitGraphCollector collectCommit(Repository r, List<ObjectId> advertised)
      throws IOException {
    CommitGraphCollector cgc = new CommitGraphCollector("test", r);
    cgc.setMaxDays(30);
    cgc.collectFiles(true);
    cgc.transfer(advertised, c -> {}, new PassThroughTreeReceiverImpl(),f -> {}, 3);
    return cgc;
  }

  /**
   * Initialize a repository with a submodule.
   *
   * @return the committer identifier.
   */
  private PersonIdent setupRepos() throws Exception {
    PersonIdent ident;
    try (Git subrepo = Git.init().setDirectory(subrepoDir).call()) {
      Files.writeString(subrepoDir.toPath().resolve("a"), "");
      RevCommit c = subrepo.commit().setAll(true).setMessage("sub").call();
      ident = c.getCommitterIdent();
    }
    try (Git mainrepo = Git.init().setDirectory(mainrepoDir).call()) {
      mainrepo.submoduleAdd().setPath("sub").setURI(subrepoDir.toURI().toString()).call();
      mainrepo.commit().setAll(true).setMessage("created a submodule").call();
    }
    return ident;
  }

  private void addCommitInSubRepo(Git mainrepo) throws Exception {
    try (Git submodrepo =
        Git.wrap(SubmoduleWalk.getSubmoduleRepository(mainrepo.getRepository(), "sub"))) {
      Files.writeString(mainrepoDir.toPath().resolve("sub").resolve("x"), "");
      submodrepo.commit().setAll(true).setMessage("added x").call();
    }
  }
}
