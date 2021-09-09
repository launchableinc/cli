import os
import shutil


def get_java_command():
    if shutil.which("java"):
        return "java"

    if os.access(os.path.expandvars("$JAVA_HOME/bin/java"), os.X_OK):
        return os.path.expandvars("$JAVA_HOME/bin/java")

    return None
