from io import StringIO
import sys
from launchable.utils.logger import Logger
import launchable.utils.logger as logger
from unittest import TestCase
from unittest.mock import patch
import logging


class LoggerTest(TestCase):
    @patch("sys.stderr", new_callable=StringIO)
    def test_logging_default(self, mock_err):
        logging.basicConfig(level=logger.LOG_LEVEL_DEFAULT)
        l = Logger()
        l.audit("audit")
        l.info("info")
        l.warning("warn")
        l.debug("debug")
        self.assertEqual(mock_err.getvalue(), "")

    @patch("sys.stderr", new_callable=StringIO)
    def test_log_level_audit(self, mock_err):
        logging.basicConfig(level=logger.LOG_LEVEL_AUDIT)
        l = Logger()
        l.audit("audit")
        l.info("info")
        l.warning("warn")
        l.debug("debug")
        self.assertEqual(mock_err.getvalue(), "AUDIT:launchable:audit\n")
