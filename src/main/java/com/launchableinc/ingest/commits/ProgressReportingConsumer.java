package com.launchableinc.ingest.commits;

import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import java.util.function.Function;

import static java.time.Instant.now;

/**
 * Given a slow {@link Consumer} that goes over a large number of items,
 * provide a progress report to show that the work is still in progress.
 */
class ProgressReportingConsumer<T> implements Consumer<T>, AutoCloseable {
    private final Consumer<T> base;
    private final List<T> pool = new ArrayList<>();
    private final Function<T,String> printer;
    private final Duration reportInterval;

    ProgressReportingConsumer(Consumer<T> base, Function<T,String> printer, Duration reportInterval) {
        this.base = base;
        this.printer = printer;
        this.reportInterval = reportInterval;
    }

    @Override
    public void accept(T t) {
        pool.add(t);
    }

    @Override
    public void close() {
        Instant nextReportTime = now().plus(reportInterval);
        int width = String.valueOf(pool.size()).length();
        int i = 0;
        for (T x : pool) {
            i++;
            if (now().isAfter(nextReportTime)) {
                System.err.printf("%s/%d: %s%n", pad(i, width), pool.size(), printer.apply(x));
                nextReportTime = now().plus(reportInterval);
            }
            base.accept(x);
        }
        pool.clear();
    }

    static String pad(int i, int width) {
        String s = String.valueOf(i);
        while (s.length() < width) {
            s = " " + s;
        }
        return s;
    }
}
