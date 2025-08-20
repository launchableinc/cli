package com.launchableinc.ingest.commits;

import org.eclipse.jgit.lib.ObjectId;

import java.io.IOException;
import java.io.OutputStream;

public interface VirtualFile {
  String path();

  /**
   * Blob ID of the file content.
   */
  ObjectId blob();

  long size() throws IOException;
  void writeTo(OutputStream os) throws IOException;
}
