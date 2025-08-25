import copy
import logging
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

import smart_tests.utils.logger as logger
from smart_tests.utils.logger import Logger


class LoggerTest(TestCase):
    default_root_handlers = None

    def setUp(self):
        self.default_root_handlers = copy.copy(logging.root.handlers)

        # reset logging handler for test
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    def tearDown(self):
        logging.root.handlers = copy.copy(self.default_root_handlers)

    @patch("sys.stderr", new_callable=StringIO)
    def test_logging_default(self, mock_err):
        logging.basicConfig(level=logger.LOG_LEVEL_DEFAULT)
        logger_instance = Logger()
        logger_instance.audit("audit")
        logger_instance.info("info")
        logger_instance.warning("warn")
        logger_instance.debug("debug")
        self.assertEqual(mock_err.getvalue(), "WARNING:launchable:warn\n")

    @patch("sys.stderr", new_callable=StringIO)
    def test_log_level_audit(self, mock_err):
        logging.basicConfig(level=logger.LOG_LEVEL_AUDIT)
        logger_instance = Logger()
        logger_instance.audit("audit")
        logger_instance.critical("critical")
        logger_instance.error("error")
        logger_instance.warning("warn")
        logger_instance.info("info")
        logger_instance.debug("debug")
        self.assertEqual(mock_err.getvalue(
        ), "AUDIT:launchable:audit\nCRITICAL:launchable:critical\nERROR:launchable:error\nWARNING:launchable:warn\n")
