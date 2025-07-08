"""Test cases for tenant configuration API endpoints in a multi-tenant setup."""

import os

from utils import settings
from utils.functions import get_uuid
from test_utils.base_super_admin import TestCaseBase


def valid_tenant_conf_data():
    """Return valid config with JWT token and SHARED DB strategy."""
    return {"authentication_type": "JWT_TOKEN", "database_strategy": "SHARED"}


def valid_tenant_conf_data_with_auth_token():
    """Return valid config using TOKEN auth type and SHARED DB."""
    return {"authentication_type": "TOKEN", "database_strategy": "SHARED"}


def valid_tenant_conf_data_with_separate_db():
    """Return valid config with JWT auth and SEPARATE DB strategy."""
    return {"authentication_type": "JWT_TOKEN", "database_strategy": "SEPARATE"}


class TenantConfigurationTestCase(TestCaseBase):
    """Test suite for creating and retrieving tenant configurations."""

    def setUp(self):
        """Set up path and tenant instance for test execution."""
        from tenant.tests.test_tenant import TenantTestCase

        self.path = "/api/tenant/{tenant_id}/configuration"
        self.path_details = "/api/tenant/{tenant_code}/details"
        self.tenant = TenantTestCase().setUp()

        return super().setUp()

    def test_create_tenant_configuration(
        self, data=valid_tenant_conf_data(), tenant=None
    ):
        """Test creation of a tenant configuration with valid data."""
        if tenant is None:
            tenant = self.tenant.test_tenant_create()

        response = self.client.post(
            self.path.format(tenant_id=tenant["tenant_id"]), data=data
        )

        response_data = response.json()

        self.created_successfully_201(response_data)

        self.assertEqual(
            response_data["data"]["database_strategy"], data["database_strategy"]
        )
        self.assertEqual(
            response_data["data"]["authentication_type"], data["authentication_type"]
        )

        return {**response_data["data"], "tenant": tenant}

    def test_create_tenant_configuration_with_auth_token(
        self, data=valid_tenant_conf_data_with_auth_token(), tenant=None
    ):
        """Test tenant config creation with TOKEN auth strategy."""
        if tenant is None:
            tenant = self.tenant.test_tenant_create()

        response = self.client.post(
            self.path.format(tenant_id=tenant["tenant_id"]), data=data
        )
        response_data = response.json()

        self.created_successfully_201(response_data)

        self.assertEqual(
            response_data["data"]["database_strategy"], data["database_strategy"]
        )
        self.assertEqual(
            response_data["data"]["authentication_type"], data["authentication_type"]
        )

        return {**response_data["data"], "tenant": tenant}

    def test_create_tenant_configuration_with_separate_db(
        self, data=valid_tenant_conf_data_with_separate_db(), tenant=None
    ):
        """Test tenant config creation using separate DB strategy."""

        if tenant is None:
            tenant = self.tenant.test_tenant_create()

        response = self.client.post(
            self.path.format(tenant_id=tenant["tenant_id"]), data=data
        )
        response_data = response.json()

        self.created_successfully_201(response_data)

        self.assertEqual(
            response_data["data"]["database_strategy"], data["database_strategy"]
        )
        self.assertEqual(
            response_data["data"]["authentication_type"], data["authentication_type"]
        )

        self.remove_extra_created_db()

        return {**response_data["data"], "tenant": tenant}

    def remove_extra_created_db(self):
        """Remove all non-default test databases created dynamically."""
        DATABASES = settings.read("DATABASES")

        del_dbs = []
        for db in DATABASES:
            if db == "default":
                continue

            del_dbs.append(db)
            database = DATABASES[db]

            os.remove(settings.read("BASE_DIR") / database["NAME"])

        for del_db in del_dbs:
            del DATABASES[del_db]

    def test_create_tenant_conf_invalid_tenant_id(self):
        """Test tenant config creation with a non-existent tenant ID."""
        data = valid_tenant_conf_data()
        non_existing_id = get_uuid()
        response = self.client.post(
            self.path.format(tenant_id=non_existing_id), data=data
        )
        response_data = response.json()
        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 1)
        self.assertEqual(response_data["errors"][0]["field"], "tenant_id")
        self.assertEqual(response_data["errors"][0]["code"], "NO_DATA_FOUND")
        self.assertEqual(response_data["errors"][0]["message"], "No Data Found.")

        return True

    @staticmethod
    def invalid_data():
        """Return completely empty payload for testing required fields."""
        return {}

    def test_create_tenant_conf_invalid_data(self):
        """Test config creation with missing required field."""
        data = self.invalid_data()
        tenant = self.tenant.test_tenant_create()
        response = self.client.post(
            self.path.format(tenant_id=tenant["tenant_id"]), data=data
        )
        response_data = response.json()
        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 1)
        self.assertEqual(response_data["errors"][0]["field"], "authentication_type")
        self.assertEqual(response_data["errors"][0]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field is required."
        )

        return True

    @staticmethod
    def tenant_conf_none_or_blank_data():
        """Return config with null and blank values for validation."""
        return {"authentication_type": None, "database_strategy": ""}

    def test_create_tenant_conf_none_or_blank_data(self):
        """Test config creation with null and blank field values."""
        data = self.tenant_conf_none_or_blank_data()
        tenant = self.tenant.test_tenant_create()
        response = self.client.post(
            self.path.format(tenant_id=tenant["tenant_id"]), data=data
        )
        response_data = response.json()
        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "authentication_type")
        self.assertEqual(response_data["errors"][0]["code"], "NULL")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field may not be null."
        )

        self.assertEqual(response_data["errors"][1]["field"], "database_strategy")
        self.assertEqual(response_data["errors"][1]["code"], "INVALID_CHOICE")
        self.assertEqual(
            response_data["errors"][1]["message"], '"" is not a valid choice.'
        )

        return True

    def test_get_tenant_conf(self):
        """Test fetching config for an existing tenant."""
        config_data = self.test_create_tenant_configuration()

        response = self.client.get(
            self.path.format(tenant_id=config_data["tenant"]["tenant_id"])
        )
        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertEqual(response_data["data"]["database_strategy"], "SHARED")
        self.assertEqual(response_data["data"]["authentication_type"], "JWT_TOKEN")

        return True

    def test_get_no_data_found(self):
        """Test fetching tenant config with invalid tenant ID."""
        non_existing_id = get_uuid()
        response = self.client.get(self.path.format(tenant_id=non_existing_id))
        response_data = response.json()
        self.data_not_found_404(response_data)

        return True

    def test_get_tenant_details(self, tenant_conf=None):
        """
        Test case to verify the retrieval of tenant configuration details via GET request.
        Validates the tenant's host, base path, subdomain and API host settings.
        """

        if not tenant_conf:
            tenant_conf = self.test_create_tenant_configuration()

        response = self.client.get(
            self.path_details.format(tenant_code=tenant_conf["tenant"]["tenant_code"])
        )
        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertEqual(response_data["data"]["host"], "testserver")
        self.assertEqual(response_data["data"]["base_path"], "api")
        self.assertEqual(response_data["data"]["sub_domain"], "test")
        self.assertEqual(response_data["data"]["api_host"], "http://test.testserver")

        return {**response_data["data"], "tenant_conf": tenant_conf}

    def test_not_tenant_details_found(self):
        """Test to verify 404 response when tenant details are not found for invalid tenant code.
        Checks if API returns proper 404 response when querying tenant details with non-existent tenant code.
        """

        response = self.client.get(self.path_details.format(tenant_code="invalid"))

        self.data_not_found_404(response.json())

        return True
