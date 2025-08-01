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
  long size() throws IOException;
  void writeTo(OutputStream os) throws IOException;
}
