package com.launchable.library;

import java.util.HashMap;

public class Cache<T> {
  private HashMap<String, T> cache;

  public Cache() {
    super();
    this.cache = new HashMap<>();
  }
  public void set(String key, T value) {
    this.cache.put(key, value);
  }
  public T get(String key) {
    return this.cache.get(key);
  }
}
