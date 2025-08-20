package com.launchableinc.ingest.commits;

import org.apache.http.entity.ContentProducer;

import java.io.Closeable;
import java.io.IOException;
import java.io.OutputStream;
import java.io.UncheckedIOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Accepts T, buffers them, and writes them out as a batch.
 */
abstract class ChunkStreamer<T> implements FlushableConsumer<T>, Closeable {
  /**
   * Encapsulation of how batches are sent.
   */
  private final IOConsumer<ContentProducer> sender;
  private final int chunkSize;
  private final List<T> spool = new ArrayList<>();

  ChunkStreamer(IOConsumer<ContentProducer> sender, int chunkSize) {
    this.sender = sender;
    this.chunkSize = chunkSize;
  }

  @Override
  public void accept(T f) {
    spool.add(f);
    if (spool.size() >= chunkSize) {
      try {
        flush();
      } catch (IOException e) {
        throw new UncheckedIOException(e);
      }
    }
  }

  @Override
  public void close() throws IOException {
    flush();
  }

  @Override
  public void flush() throws IOException {
    if (spool.isEmpty()) {
      return;
    }

    try {
      sender.accept(os -> writeTo(spool,os));
    } finally {
      spool.clear();
    }
  }

  protected abstract void writeTo(List<T> spool, OutputStream os) throws IOException;
}
