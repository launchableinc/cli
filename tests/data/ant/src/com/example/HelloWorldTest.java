package com.example;

import org.junit.Test;

import static org.junit.Assert.fail;

public class HelloWorldTest {

    @Test
    public void testNothing() {
    }

    @Test
    public void testWillAlwaysFail() {
        fail("An error message");
    }

}
