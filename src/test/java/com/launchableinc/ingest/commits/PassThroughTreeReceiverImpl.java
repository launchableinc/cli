package com.launchableinc.ingest.commits;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

public class PassThroughTreeReceiverImpl implements TreeReceiver {
    private final List<VirtualFile> files = new ArrayList<>();
    @Override
    public Collection<VirtualFile> response() {
        List<VirtualFile> r = new ArrayList<>(files);
        files.clear();
        return r;
    }

    @Override
    public void accept(VirtualFile f) {
        files.add(f);
    }
}
