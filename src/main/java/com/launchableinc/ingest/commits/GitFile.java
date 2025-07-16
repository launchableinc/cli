package com.launchableinc.ingest.commits;

import org.eclipse.jgit.lib.ObjectId;
import org.eclipse.jgit.lib.ObjectReader;

import java.io.IOException;
import java.io.OutputStream;

import static org.eclipse.jgit.lib.Constants.*;

/**
 * Represents a file in a Git repository, and encapsulates the read access for convenience.
 */
final class GitFile implements VirtualFile {
  final String path;
  final ObjectId blob;
  private final ObjectReader objectReader;

  public GitFile(String path, ObjectId blob, ObjectReader objectReader) {
    this.path = path;
    this.blob = blob;
    this.objectReader = objectReader;
  }

  @Override
  public String path() {
    return path;
  }

  public long size() throws IOException {
    return objectReader.open(blob, OBJ_BLOB).getSize();
  }

  @Override
  public void writeTo(OutputStream os) throws IOException {
    objectReader.open(blob, OBJ_BLOB).copyTo(os);
  }
}
