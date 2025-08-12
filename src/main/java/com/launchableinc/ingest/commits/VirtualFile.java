package com.launchableinc.ingest.commits;

import java.io.IOException;
import java.io.OutputStream;

public interface VirtualFile {
  /**
   * Repository identifier, unique within the workspace.
   */
  String repo();

  /**
   * Path to the file within the repository.
   */
  String path();

  /**
   * Milliseconds since epoch when this file was last modified.
   */
  long timestamp();

  long size() throws IOException;
  void writeTo(OutputStream os) throws IOException;
}
