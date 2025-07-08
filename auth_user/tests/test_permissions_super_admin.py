"""
Test cases for loading permissions as a super admin in the IMS backend.
"""

from utils.functions import get_uuid
from test_utils.base_super_admin import TestCaseBase


class PermissionTestCase(TestCaseBase):
    """
    Test case for loading permissions as a super admin in the authentication user module.
    """

    def setUp(self):
        from tenant.tests.test_tenant_conf import TenantConfigurationTestCase

        self.tenant_conf = TenantConfigurationTestCase().setUp()
        self.path = "/api/admin/permission"

        return super().setUp()

    def test_load_permissions(self, tenant_config=None):
        """Test that permissions are loaded successfully for a given tenant configuration."""

        if not tenant_config:
            tenant_config = self.tenant_conf.test_create_tenant_configuration()

        response = self.client.post(
            self.path,
            data={"tenant_id": tenant_config["tenant"]["tenant_id"]},
        )

        response_data = response.json()

        self.created_successfully_201(response_data)

        return tenant_config

    def test_load_permission_with_wrong_tenant(self):
        """Test that loading permissions with an invalid tenant_id returns the correct error response."""

        response = self.client.post(
            self.path,
            data={"tenant_id": get_uuid()},
        )

        response_data = response.json()

        self.bad_request_404(response_data)
        self.assertEqual(len(response_data["errors"]), 1)
        self.assertEqual(response_data["errors"][0]["field"], "tenant_id")
        self.assertEqual(response_data["errors"][0]["code"], "NO_DATA_FOUND")
        self.assertEqual(response_data["errors"][0]["message"], "No Data Found.")
        return True

    def test_get_list_permissions_list(self):
        """
        Test that the permissions list endpoint returns a valid list of permissions for a given tenant.
        """

        tenant_config = self.test_load_permissions()

        response = self.client.get(
            self.path,
            data={"tenant_id": tenant_config["tenant"]["tenant_id"]},
        )

        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertIsInstance(response_data["data"], list)
        self.assertGreater(len(response_data["data"]), 0)

        permission = response_data["data"][0]
        self.assertIn("name", permission)
        self.assertIn("module", permission)
        self.assertIn("action", permission)
        self.assertIn("permission_id", permission)

        return {"permissions": response_data["data"], "tenant_config": tenant_config}

    def test_get_list_permissions_list_for_wrong_tenant(self):
        """Test that requesting permissions list with an invalid tenant_id returns the correct error response."""

        response = self.client.get(
            self.path,
            data={"tenant_id": get_uuid()},
        )

        response_data = response.json()
        self.bad_request_404(response_data)
        self.assertEqual(len(response_data["errors"]), 1)
        self.assertEqual(response_data["errors"][0]["field"], "tenant_id")
        self.assertEqual(response_data["errors"][0]["code"], "NO_DATA_FOUND")
        self.assertEqual(response_data["errors"][0]["message"], "No Data Found.")

        return True

    def test_get_list_permissions_list_for_no_tenant(self):
        """Test that requesting permissions list with an no tenant_id returns the correct error response."""

        response = self.client.get(
            self.path,
            data={},
        )

        response_data = response.json()
        self.bad_request_404(response_data)
        self.assertEqual(len(response_data["errors"]), 1)
        self.assertEqual(response_data["errors"][0]["field"], "tenant_id")
        self.assertEqual(response_data["errors"][0]["code"], "NULL")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field may not be null."
        )

        return True
