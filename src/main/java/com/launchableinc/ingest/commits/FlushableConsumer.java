package com.launchableinc.ingest.commits;

import java.io.IOException;
import java.util.function.Consumer;

/**
 * Consumers that spool items it accepts and process them in bulk.
 */
public interface FlushableConsumer<T> extends Consumer<T> {
    /**
     * Process all items that have been accepted so far.
     */
    void flush() throws IOException;
}
