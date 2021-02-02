package com.launchableinc.rocket_car_maven;

import static org.junit.Assert.*;

import org.junit.Test;

public class App2Test {
  @Test
  public void testAppHasGreeting() {
    App testApp = new App();
    String message = "Hello rocket-car-maven";
    assertEquals(message, testApp.getGreeting());
  }

  @Test
  public void testAppHasGreeting2() {
    App testApp = new App();
    assertNotNull("Hello rocket-car-maven", testApp.getGreeting());
  }
}
