package com.launchableinc.ingest.commits;

import org.apache.commons.compress.archivers.tar.TarArchiveEntry;
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream;
import org.apache.commons.io.IOUtils;
import org.apache.commons.io.output.NullOutputStream;
import org.apache.http.entity.ContentProducer;
import org.eclipse.jgit.lib.ObjectId;
import org.junit.Test;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.List;

import static com.google.common.truth.Truth.*;
import static org.junit.Assert.fail;

public class FileChunkStreamerTest {
  @Test
  public void no_op_if_no_content() throws Exception {
    try (FileChunkStreamer fs = new FileChunkStreamer(content -> fail(), 2)) {
      // no write
    }
  }

  @Test
  public void basics() throws Exception {
    int[] count = new int[1];
    try (FileChunkStreamer fs = new FileChunkStreamer(content -> {
      switch(count[0]++) {
      case 0:
        assertThat(readEntries(content)).containsExactly("foo.txt", "bar.txt").inOrder();
        break;
      case 1:
        assertThat(readEntries(content)).containsExactly("zot.txt").inOrder();
        break;
      default:
        fail();
      }
    }, 2)) {
      fs.accept(new VirtualFileImpl("foo.txt"));
      fs.accept(new VirtualFileImpl("bar.txt"));
      fs.accept(new VirtualFileImpl("zot.txt"));
    }
    assertThat(count[0]).isEqualTo(2);
  }

  private List<String> readEntries(ContentProducer content) throws IOException {
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    content.writeTo(baos);

    try (TarArchiveInputStream tar = new TarArchiveInputStream(new ByteArrayInputStream(baos.toByteArray()))) {
      List<String> entries = new java.util.ArrayList<>();
      TarArchiveEntry entry;
      while ((entry = tar.getNextTarEntry()) != null) {
        entries.add(entry.getName());
        IOUtils.copy(tar, NullOutputStream.INSTANCE);
      }
      return entries;
    }
  }

  private static class VirtualFileImpl implements VirtualFile {
    private final String path;

    VirtualFileImpl(String path) {
      this.path = path;
    }

    @Override
    public String repo() {
      return "test";
    }

    @Override
    public String path() {
      return path;
    }

    @Override
    public ObjectId blob() {
      return ObjectId.zeroId();
    }

    @Override
    public long size() {
      return path.getBytes().length;
    }

    @Override
    public void writeTo(OutputStream os) throws IOException {
      os.write(path.getBytes());
    }
  }
}
