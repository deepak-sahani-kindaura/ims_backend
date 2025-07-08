import os

from django.test import TestCase

from utils import settings
from utils.logger import log_msg, logging


class TestLogger(TestCase):

    def setUp(self):
        """Set up the test case."""
        self.log_file_dir = settings.read("BASE_DIR") / "logs/ims_test.log"

        return super().setUp()

    def test_log_all_type_message(self):
        """Test case to log messages of all types."""

        log_msg(logging.DEBUG, "This is a debug message", ref_data={"key": "value"})
        log_msg(logging.ERROR, "This is a error message")
        log_msg(logging.INFO, "This is a info message")
        log_msg(logging.WARNING, "This is a warning message")

        with open(self.log_file_dir, "r") as f:
            logs = f.read()

            self.assertIn("DEBUG [🛠️] [FUNC:- test_log_all_type_message]", logs)
            self.assertIn("This is a debug message", logs)
            self.assertIn("[REF_DATA:- key:value]", logs)

            self.assertIn("ERROR [🐞] [FUNC:- test_log_all_type_message]", logs)
            self.assertIn("This is a error message", logs)

            self.assertIn("INFO [📝] [FUNC:- test_log_all_type_message]", logs)
            self.assertIn("This is a info message", logs)

            self.assertIn("WARNING [⚠️] [FUNC:- test_log_all_type_message]", logs)
            self.assertIn("This is a warning message", logs)

        os.remove(self.log_file_dir)

        return True
