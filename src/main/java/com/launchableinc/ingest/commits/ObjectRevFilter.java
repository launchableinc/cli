package com.launchableinc.ingest.commits;

import org.eclipse.jgit.lib.ObjectId;
import org.eclipse.jgit.revwalk.RevCommit;
import org.eclipse.jgit.revwalk.RevWalk;
import org.eclipse.jgit.revwalk.filter.RevFilter;

/**
 * Selects one commit
 */
final class ObjectRevFilter extends RevFilter {
    private final ObjectId theCommit;

    ObjectRevFilter(ObjectId theCommit) {
        this.theCommit = theCommit;
    }

    @Override
    public boolean include(RevWalk walker, RevCommit cmit) {
        return cmit.equals(theCommit);
    }

    @Override
    public RevFilter clone() {
        return this;
    }
}
