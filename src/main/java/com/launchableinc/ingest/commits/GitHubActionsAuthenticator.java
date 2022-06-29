package com.launchableinc.ingest.commits;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import org.apache.http.Header;
import org.apache.http.message.BasicHeader;

public class GitHubActionsAuthenticator implements Authenticator {
  public Collection<Header> getAuthenticationHeaders() {
    Collection<Header> headers =
        new ArrayList<>(
            Arrays.asList(
                new BasicHeader("GitHub-Actions", System.getenv("GITHUB_ACTIONS")),
                new BasicHeader("GitHub-Run-Id", System.getenv("GITHUB_RUN_ID")),
                new BasicHeader("GitHub-Repository", System.getenv("GITHUB_REPOSITORY")),
                new BasicHeader("GitHub-Workflow", System.getenv("GITHUB_WORKFLOW")),
                new BasicHeader("GitHub-Run-Number", System.getenv("GITHUB_RUN_NUMBER")),
                new BasicHeader("GitHub-Event-Name", System.getenv("GITHUB_EVENT_NAME")),
                new BasicHeader("GitHub-Sha", System.getenv("GITHUB_SHA"))));

    String prHeadSha = System.getenv("GITHUB_PR_HEAD_SHA");
    if (prHeadSha != null && !prHeadSha.isEmpty()) {
      headers.add(new BasicHeader("GitHub-Pr-Head-Sha", prHeadSha));
    }

    return headers;
  }
}
