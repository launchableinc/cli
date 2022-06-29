package com.launchableinc.ingest.commits;

import com.google.common.hash.HashFunction;
import com.google.common.hash.Hashing;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class JSCommit {
  /** Hash function for scrubbing email addresses. */
  private static final HashFunction EMAIL_HASHER = Hashing.sha256();

  private String commitHash;

  /** Email address of the author */
  private String authorEmailAddress;

  /** Timestamp of the commit in Unix time, measured in ms. */
  private long authorWhen;

  /** Time zone offset in minutes. For example, JST is +9:00 so this field is 540. */
  private int authorTimezoneOffset;

  /** Email address of the committer */
  private String committerEmailAddress;

  /** Timestamp of the commit in Unix time, measured in ms. */
  private long committerWhen;

  /** Time zone offset in minutes. For example, JST is +9:00 so this field is 540. */
  private int committerTimezoneOffset;

  private Map<String, List<JSFileChange>> parentHashes = new HashMap<>();

  public String getCommitHash() {
    return commitHash;
  }

  public void setCommitHash(String commitHash) {
    this.commitHash = commitHash;
  }

  public String getAuthorEmailAddress() {
    return authorEmailAddress;
  }

  public void setAuthorEmailAddress(String authorEmailAddress) {
    this.authorEmailAddress = authorEmailAddress;
  }

  public long getAuthorWhen() {
    return authorWhen;
  }

  public void setAuthorWhen(long authorWhen) {
    this.authorWhen = authorWhen;
  }

  public int getAuthorTimezoneOffset() {
    return authorTimezoneOffset;
  }

  public void setAuthorTimezoneOffset(int authorTimezoneOffset) {
    this.authorTimezoneOffset = authorTimezoneOffset;
  }

  public String getCommitterEmailAddress() {
    return committerEmailAddress;
  }

  public void setCommitterEmailAddress(String committerEmailAddress) {
    this.committerEmailAddress = committerEmailAddress;
  }

  public long getCommitterWhen() {
    return committerWhen;
  }

  public void setCommitterWhen(long committerWhen) {
    this.committerWhen = committerWhen;
  }

  public int getCommitterTimezoneOffset() {
    return committerTimezoneOffset;
  }

  public void setCommitterTimezoneOffset(int committerTimezoneOffset) {
    this.committerTimezoneOffset = committerTimezoneOffset;
  }

  public Map<String, List<JSFileChange>> getParentHashes() {
    return parentHashes;
  }

  public static String hashEmail(String email) {
    return EMAIL_HASHER.newHasher().putString(email, StandardCharsets.UTF_8).hash().toString();
  }
}
