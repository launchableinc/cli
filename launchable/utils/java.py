import os
import shutil
import subprocess
import sys


def get_java_command():
    if shutil.which("java"):
        return "java"

    if os.access(os.path.expandvars("$JAVA_HOME/bin/java"), os.X_OK):
        return os.path.expandvars("$JAVA_HOME/bin/java")

    return None


def cygpath(p):
    # When running in Cygwin ported Python (as opposed to Windows native Python), the paths we deal with are in
    # the cygwin format. But when we invoke Windows native Java (and there's no Cygwin ported Java), those parameters
    # need to be in the Windows path format.
    #
    # In Cygwin aware world, it is always the responsibility of the Cygwin process calling Windows native process to
    # do this conversion, so here we are.
    #
    # Cygwin ported Python is not to be confused with Windows native Python running in Windows with cygwin.
    # So tests like CYGWIN env var, "uname" are incorrect.
    if sys.platform == 'cygwin':
        p = subprocess.check_output(['cygpath', '-w', p]).decode().strip()
    return p
