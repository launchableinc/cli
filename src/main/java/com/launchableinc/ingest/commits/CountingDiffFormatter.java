package com.launchableinc.ingest.commits;

import com.google.common.io.ByteStreams;
import java.io.IOException;
import java.io.UncheckedIOException;
import org.eclipse.jgit.diff.DiffEntry;
import org.eclipse.jgit.diff.DiffFormatter;
import org.eclipse.jgit.diff.Edit;
import org.eclipse.jgit.diff.EditList;
import org.eclipse.jgit.diff.RawText;
import org.eclipse.jgit.lib.Repository;

/**
 * {@link DiffFormatter} that counts the number of lines edited as opposed to print out the actual
 * diff.
 */
class CountingDiffFormatter extends DiffFormatter {
  private int add;
  private int del;

  public CountingDiffFormatter(Repository git) {
    // super class expects us to provide a stream in which diff will be written
    // but we aren't actually interested in the diff form, so plug null stream.
    super(ByteStreams.nullOutputStream());
    setRepository(git);
  }

  /** Entry point to compute a file level change. */
  JSFileChange process(DiffEntry de) {
    add = 0;
    del = 0;

    // This call internally eventually reaches to format(EditList, RawTest, RawText) that counts the
    // numbers.
    try {
      format(de);
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    }

    JSFileChange fc = new JSFileChange();
    fc.setLinesAdded(add);
    fc.setLinesDeleted(add);
    fc.setPath(de.getOldPath());
    fc.setPathTo(de.getNewPath());
    fc.setStatus(de.getChangeType().toString());
    return fc;
  }

  @Override
  public void format(EditList edits, RawText a, RawText b) {
    for (Edit edit : edits) {
      del += edit.getEndA() - edit.getBeginA();
      add += edit.getEndB() - edit.getBeginB();
    }
  }
}
