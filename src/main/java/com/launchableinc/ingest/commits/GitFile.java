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
  final String repoName;
  final String path;
  final ObjectId blob;
  private final ObjectReader objectReader;

  public GitFile(String repoName, String path, ObjectId blob, ObjectReader objectReader) {
    this.repoName = repoName;
    this.path = path;
    this.blob = blob;
    this.objectReader = objectReader;
  }

  @Override
  public String path() {
    return path;
  }

  @Override
  public ObjectId blob() {
    return blob;
  }

  public long size() throws IOException {
    return objectReader.open(blob, OBJ_BLOB).getSize();
  }

  @Override
  public void writeTo(OutputStream os) throws IOException {
    objectReader.open(blob, OBJ_BLOB).copyTo(os);
  }

  /**
   * Returns true if this file is likely a text file, false if it's binary.
   * Simple heuristic: check if the file starts with binary data.
   */
  public boolean isText() throws IOException {
    try {
      byte[] data = objectReader.open(blob, OBJ_BLOB).getBytes();
      if (data.length == 0) return true; // Empty files are considered text
      
      // Check first 1024 bytes for null bytes which indicate binary content
      int checkLength = Math.min(data.length, 1024);
      for (int i = 0; i < checkLength; i++) {
        if (data[i] == 0) {
          return false; // Found null byte, likely binary
        }
      }
      return true; // No null bytes found, likely text
    } catch (IOException e) {
      // If we can't read the file, assume it's not text
      return false;
    }
  }
}
