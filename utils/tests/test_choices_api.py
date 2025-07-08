import builtins

from django.test import TestCase

from test_utils.test_client import APITestClient
from test_utils.comm_assert import CommonTestCaseAssertsBase


class TestChoiceAPI(CommonTestCaseAssertsBase):

    def test_disable_print(self):
        """
        Test that the choices API returns the expected constant choices.
        """
        client = APITestClient()

        response = client.get("/api/choices")

        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertIn("role_types", response_data["data"])
        self.assertEqual(
            response_data["data"]["role_types"],
            [
                {"value": "SUPER_ADMIN", "label": "Super Admin"},
                {"value": "COMPANY_ADMIN", "label": "Company Admin"},
                {"value": "MANAGER", "label": "Manager"},
                {"value": "OPERATOR", "label": "Operator"},
            ],
        )

        self.assertIn("method_types", response_data["data"])
        self.assertEqual(
            response_data["data"]["method_types"],
            [
                {"value": "GET", "label": "GET"},
                {"value": "POST", "label": "POST"},
                {"value": "PUT", "label": "PUT"},
                {"value": "PATCH", "label": "PATCH"},
                {"value": "DELETE", "label": "DELETE"},
            ],
        )

        self.assertIn("severity_types", response_data["data"])
        self.assertEqual(
            response_data["data"]["severity_types"],
            [
                {"value": "LOW", "label": "Low"},
                {"value": "MEDIUM", "label": "Medium"},
                {"value": "HIGH", "label": "High"},
                {"value": "CRITICAL", "label": "Critical"},
                {"value": "INFO", "label": "Info"},
                {"value": "WARNING", "label": "Warning"},
                {"value": "ERROR", "label": "Error"},
            ],
        )

        self.assertIn("stock_types", response_data["data"])
        self.assertEqual(
            response_data["data"]["stock_types"],
            [
                {"value": "IN", "label": "In"},
                {"value": "OUT", "label": "Out"},
            ],
        )

        self.assertIn("notification_types", response_data["data"])
        self.assertEqual(
            response_data["data"]["notification_types"],
            [
                {"value": "STOCK_IN", "label": "Stock In"},
                {"value": "STOCK_OUT", "label": "Stock Out"},
                {"value": "STOCK_NOT_AVAILABLE", "label": "Stock Not Available"},
            ],
        )

        self.assertIn("authentication_types", response_data["data"])
        self.assertEqual(
            response_data["data"]["authentication_types"],
            [
                {"value": "TOKEN", "label": "Token"},
                {"value": "JWT_TOKEN", "label": "JWT Token"},
            ],
        )

        self.assertIn("database_strategy_types", response_data["data"])
        self.assertEqual(
            response_data["data"]["database_strategy_types"],
            [
                {"value": "SHARED", "label": "Shared DB"},
                {"value": "SEPARATE", "label": "Separate DB"},
            ],
        )

        self.assertIn("database_server_types", response_data["data"])
        self.assertEqual(
            response_data["data"]["database_server_types"],
            [
                {"value": "SQLITE", "label": "Sqlite3"},
                {"value": "POSTGRES", "label": "Postgres"},
            ],
        )

        return True
