package com.launchableinc.ingest.commits;

import java.util.Collection;
import java.util.function.Consumer;

/**
 * Used by {@link CommitGraphCollector} as the abstraction of a server endpoint that
 * receives a list of paths in a Git repository and responds with which ones it wants to see.
 */
public interface TreeReceiver extends Consumer<VirtualFile> {
    /**
     * Receives the subset of {@link VirtualFile}s sent to the server thus far, which
     * the server wants to see.
     * <p>
     * This resets the spool.
     */
    Collection<VirtualFile> response();
}
