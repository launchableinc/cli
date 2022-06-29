package com.launchableinc.ingest.commits;

import java.util.Collection;
import org.apache.http.Header;

/** Authenticator handles authentication between CommitGraphCollector and Launchable API */
public interface Authenticator {
  /**
   * Return a list of HTTP headers that are necessary for authentication
   *
   * @return A list of HTTP headers that are necessary for authentication
   */
  Collection<Header> getAuthenticationHeaders();
}
