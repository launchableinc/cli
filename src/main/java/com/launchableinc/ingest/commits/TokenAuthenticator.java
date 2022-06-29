package com.launchableinc.ingest.commits;

import com.google.common.collect.ImmutableList;
import org.apache.http.Header;
import org.apache.http.message.BasicHeader;

public class TokenAuthenticator implements Authenticator {
  private final String token;

  public TokenAuthenticator(String token) {
    this.token = token;
  }

  @Override
  public ImmutableList<Header> getAuthenticationHeaders() {
    return ImmutableList.of(new BasicHeader("Authorization", "Bearer " + this.token));
  }
}
