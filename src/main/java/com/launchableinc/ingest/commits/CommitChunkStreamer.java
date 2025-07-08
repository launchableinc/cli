package com.launchableinc.ingest.commits;

import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonGenerator;
import org.apache.http.entity.ContentProducer;
import org.eclipse.jgit.revwalk.RevCommit;

import java.io.IOException;
import java.io.OutputStream;
import java.util.List;
import java.util.function.Consumer;

/**
 * {@link Consumer} that groups commits into chunks and write them as JSON, using streams supplied
 * by the factory.
 */
final class CommitChunkStreamer extends ChunkStreamer<JSCommit> {
  CommitChunkStreamer(IOConsumer<ContentProducer> sender, int chunkSize) {
    super(sender, chunkSize);
  }

  @Override
  protected void writeTo(List<JSCommit> spool, OutputStream os) throws IOException {
    JsonGenerator w = new JsonFactory().createGenerator(os).useDefaultPrettyPrinter();
    w.setCodec(CommitGraphCollector.objectMapper);
    w.writeStartObject();
    w.writeArrayFieldStart("commits");

    for (JSCommit commit : spool) {
      w.writeObject(commit);
    }

    w.writeEndArray();
    w.writeEndObject();
    w.close();
  }
}
