package com.launchableinc.ingest.commits;

import java.io.IOException;

public interface IOConsumer<T> {
  void accept(T t) throws IOException;
}
