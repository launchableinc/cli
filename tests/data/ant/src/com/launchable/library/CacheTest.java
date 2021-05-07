package com.launchable.library;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class CacheTest {
  @Test
  public void testCache() {
    Cache<String> cache = new Cache<>();
    String key = "key";
    String val = "123";
    cache.set(key, val);
    assertEquals(val, cache.get(key));
  }  
}
