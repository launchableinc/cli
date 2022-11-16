package com.launchableinc.ingest.commits;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.base.Strings;
import com.google.common.collect.ImmutableList;
import java.io.IOException;
import java.io.UncheckedIOException;
import org.apache.http.Header;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.message.BasicHeader;
import org.kohsuke.args4j.CmdLineException;

public class GitHubIdTokenAuthenticator implements Authenticator {
  private static final ObjectMapper objectMapper = new ObjectMapper();
  private final String idToken;

  public GitHubIdTokenAuthenticator() throws CmdLineException {
    String reqUrl = System.getenv("ACTIONS_ID_TOKEN_REQUEST_URL");
    String rtToken = System.getenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN");
    if (Strings.isNullOrEmpty(reqUrl) || Strings.isNullOrEmpty(rtToken)) {
      throw new CmdLineException(
          "GitHub Actions OIDC tokens cannot be retrieved.Confirm that you have added necessary"
              + " permissions following "
              + "https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-cloud-providers#adding-permissions-settings");
    }

    HttpGet request = new HttpGet(reqUrl);
    request.setHeader("Authorization", "Bearer " + rtToken);
    request.setHeader("Accept", "applicaiton/json; api-version=2.0");
    request.setHeader("Content-Type", "application/json");

    try (CloseableHttpClient client = HttpClientBuilder.create().useSystemProperties().build()) {
      try (CloseableHttpResponse resp = client.execute(request)) {
        if (resp.getStatusLine().getStatusCode() != 200) {
          throw new IOException(
              String.format("Failed to retrieve IdToken: %s", resp.getStatusLine()));
        }
        this.idToken =
            objectMapper.readValue(resp.getEntity().getContent(), IdTokenResponse.class).value;
      }
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    }
  }

  @Override
  public ImmutableList<Header> getAuthenticationHeaders() {
    return ImmutableList.of(new BasicHeader("Authorization", "Bearer " + idToken));
  }

  @JsonIgnoreProperties(ignoreUnknown = true)
  public static class IdTokenResponse {
    public String value;
  }
}
