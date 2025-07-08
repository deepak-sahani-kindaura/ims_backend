from test_utils.tenant_user_base import TestCaseBase


class PermissionTestCase(TestCaseBase):

    def setUp(self):
        self.path = "/api/permission"
        return super().setUp()

    def test_get_permissions(self):
        """
        Test that the permissions are correctly set for the user.
        """

        response = self.client.get(self.path)

        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertIsInstance(response_data["data"], list)
        self.assertGreater(len(response_data["data"]), 0)

        permission = response_data["data"][0]
        self.assertIn("name", permission)
        self.assertIn("module", permission)
        self.assertIn("action", permission)
        self.assertIn("permission_id", permission)

        return response_data["data"]
