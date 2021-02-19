import logging


LOG_LEVEL_DEFAULT = 999
LOG_LEVEL_DEFAULT_STR = "DEFAULT"
LOG_LEVEL_AUDIT = 90
LOG_LEVEL_AUDIT_STR = "AUDIT"


logging.addLevelName(LOG_LEVEL_AUDIT, "AUDIT")


def get_log_level(level=str) -> int:
    level = level.lower()

    if level == "audit":
        return LOG_LEVEL_AUDIT
    elif level == "critical":
        return logging.CRITICAL
    elif level == "error":
        return logging.ERROR
    elif level == "warn" or level == "warning":
        return logging.WARNING
    elif level == "info":
        return logging.INFO
    elif level == "debug":
        return logging.DEBUG
    else:
        return LOG_LEVEL_DEFAULT


class Logger(object):
    def __init__(self, name="launchable"):
        logger = logging.getLogger(name)
        self.logger = logger

    def audit(self, msg, *args, **kargs):
        self.logger.log(LOG_LEVEL_AUDIT, msg, *args, **kargs)

    def debug(self, msg, *args, **kargs):
        self.logger.debug(msg, *args, **kargs)

    def info(self, msg, *args, **kargs):
        self.logger.info(msg, *args, **kargs)

    def warning(self, msg, *args, **kargs):
        self.logger.warning(msg, *args, **kargs)

    def error(self, msg, *args, **kargs):
        self.logger.error(msg, *args, **kargs)

    def critical(self, msg, *args, **kargs):
        self.logger.critical(msg, *args, **kargs)
