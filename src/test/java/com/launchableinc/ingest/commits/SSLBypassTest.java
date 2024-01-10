package com.launchableinc.ingest.commits;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;

@RunWith(JUnit4.class)
public class SSLBypassTest {
    @Test
    public void foo() {
        SSLBypass.install();
    }
}
