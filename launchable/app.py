# Object representing the most global state possible, which represents a single invocation of CLI
# Currently it's used to keep global configurations.
#
# From command implementations, this is available from Click 'context.obj'
class Application(object):
    def __init__(self, dry_run: bool = False, skip_cert_verification: bool = False):
        # Dry run mode. This command is used by customers to inspect data we'd send to our server,
        # but without actually doing so.
        self.dry_run = dry_run
        # Skip SSL certificate validation
        self.skip_cert_verification = skip_cert_verification
