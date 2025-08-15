package com.launchableinc.ingest.commits;

import org.apache.commons.compress.archivers.tar.TarArchiveEntry;
import org.apache.commons.compress.archivers.tar.TarArchiveOutputStream;
import org.apache.http.entity.ContentProducer;

import java.io.IOException;
import java.io.OutputStream;
import java.util.List;

import static org.apache.commons.compress.archivers.tar.TarArchiveOutputStream.*;

/**
 * Receives {@link GitFile}, buffers them, and writes them out in a gzipped tar file.
 */
final class FileChunkStreamer extends ChunkStreamer<VirtualFile> {
  FileChunkStreamer(IOConsumer<ContentProducer> sender, int chunkSize) {
    super(sender, chunkSize);
  }

  @Override
  protected void writeTo(List<VirtualFile> files, OutputStream os) throws IOException {
    try (TarArchiveOutputStream tar = new TarArchiveOutputStream(os, "UTF-8")) {
      tar.setLongFileMode(LONGFILE_POSIX);

      for (VirtualFile f : files) {
        TarArchiveEntry e = new TarArchiveEntry(f.path());
        e.setSize(f.size());
        e.setGroupName(f.blob().name()); // HACK - reuse the group name field to store the blob ID
        tar.putArchiveEntry(e);
        f.writeTo(tar);
        tar.closeArchiveEntry();
      }
    }
  }
}
