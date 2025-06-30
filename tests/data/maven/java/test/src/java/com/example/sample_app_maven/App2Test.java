package com.example.sample_app_maven;

import static org.junit.Assert.*;

import org.junit.Test;

public class App2Test {
  @Test
  public void testAppHasGreeting() {
    App testApp = new App();
    String message = "Hello sample-app-maven";
    assertEquals(message, testApp.getGreeting());
  }

  @Test
  public void testAppHasGreeting2() {
    App testApp = new App();
    assertNotNull("Hello sample-app-maven", testApp.getGreeting());
  }
}
