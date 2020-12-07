import os
import subprocess


def get_java_command():
    res = subprocess.run(["which", "java"], stdout=subprocess.DEVNULL)
    if res.returncode == 0:
        return "java"

    if os.access(os.path.expandvars("$JAVA_HOME/bin/java"), os.X_OK):
        return "$JAVA_HOME/bin/java"

    return None
