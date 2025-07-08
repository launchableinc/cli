package com.launchableinc.ingest.commits;

import java.io.IOException;
import java.io.OutputStream;

public interface VirtualFile {
  String path();
  long size() throws IOException;
  void writeTo(OutputStream os) throws IOException;
}
