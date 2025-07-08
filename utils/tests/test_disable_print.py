import builtins

from django.test import TestCase

from utils.disable_print import disable_print, original_print
from utils.exceptions.exceptions import CommonError


class TestDisablePrint(TestCase):

    def test_disable_print(self):
        """
        Test that the print function is disabled and raises a CommonError when called.
        """
        disable_print()

        try:
            print("This should not be printed")
        except CommonError as e:
            builtins.print = original_print

            self.assertEqual(
                e.message,
                (
                    "'print' function is disabled please remove the use of it instead use the [log_msg]. "
                    "Change the DISABLE_PRINT:True in the config file to False to enable the print function. "
                ),
            )
            print()
