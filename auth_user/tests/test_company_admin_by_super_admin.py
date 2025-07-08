from utils.functions import get_uuid
from auth_user.constants import RoleEnum

from test_utils.base_super_admin import TestCaseBase


class UserTestCase(TestCaseBase):

    def setUp(self):
        from tenant.tests.test_tenant_conf import TenantConfigurationTestCase

        self.tenant_conf = TenantConfigurationTestCase().setUp()
        self.path = "/api/user/company-admin"

        return super().setUp()

    @staticmethod
    def success_data():
        return {
            "last_name": "Borse",
            "first_name": "Bhushan",
            "email": "test.company.admin@gmail.com",
            "phone_number": "9878786565",
            "role_id": RoleEnum.COMPANY_ADMIN,
            "password": "1234",
        }

    def test_create_tenant_admin_user(self, tenant_config=None):
        """
        Test the creation of a tenant admin user by a super admin and validate the response data.
        """

        data = self.success_data()

        if not tenant_config:
            tenant_config = self.tenant_conf.test_create_tenant_configuration()

        data["tenant_id"] = tenant_config["tenant"]["tenant_id"]

        response = self.client.post(self.path, data=data)

        response_data = response.json()

        self.created_successfully_201(response_data)
        self.assertEqual(response_data["data"]["email"], "test.company.admin@gmail.com")
        self.assertEqual(response_data["data"]["role_id"], "COMPANY_ADMIN")
        self.assertEqual(response_data["data"]["phone_number"], 9878786565)
        self.assertEqual(response_data["data"]["first_name"], "Bhushan")
        self.assertEqual(response_data["data"]["last_name"], "Borse")
        self.assertEqual(response_data["data"]["full_name"], "Bhushan Borse")
        self.assertIsNone(response_data["data"]["profile_photo"])
        self.assertIn("user_id", response_data["data"])

        return {**response_data["data"], "tenant_config": tenant_config}

    @staticmethod
    def duplicate_and_invalid_role_data():
        return {
            "last_name": "Borse",
            "first_name": "Bhushan",
            "email": "test.company.admin@gmail.com",
            "phone_number": "9878786565",
            "role_id": RoleEnum.OPERATOR,
            "password": "1234",
        }

    def test_create_duplicate_tenant_admin_user(self):
        """
        Test that creating a duplicate tenant admin user with an invalid role returns appropriate validation errors.
        """

        tenant_config = self.test_create_tenant_admin_user()["tenant_config"]

        data = self.duplicate_and_invalid_role_data()

        data["tenant_id"] = tenant_config["tenant"]["tenant_id"]

        response = self.client.post(self.path, data=data)

        response_data = response.json()

        self.bad_request_404(response_data)
        self.assertEqual(len(response_data["errors"]), 2)
        self.assertEqual(response_data["errors"][0]["field"], "email")
        self.assertEqual(response_data["errors"][0]["code"], "DUPLICATE_ENTRY")
        self.assertEqual(response_data["errors"][0]["message"], "Already Exist.")

        self.assertEqual(response_data["errors"][1]["field"], "role_id")
        self.assertEqual(response_data["errors"][1]["code"], "INVALID_CHOICE")
        self.assertEqual(
            response_data["errors"][1]["message"], "Only COMPANY_ADMIN allowed."
        )

        return True

    @staticmethod
    def invalid_data():
        return {
            "last_name": "",
            "first_name": "",
            "email": "test.company.admin@com",
            "phone_number": "",
            "role_id": "STAFF",
            "password": "",
        }

    def test_create_tenant_admin_with_wrong_data(self):
        """
        Test that creating a tenant admin with invalid data returns appropriate validation errors.
        """

        data = self.invalid_data()

        data["tenant_id"] = get_uuid()

        response = self.client.post(self.path, data=data)

        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 7)

        self.assertEqual(response_data["errors"][0]["field"], "email")
        self.assertEqual(response_data["errors"][0]["code"], "INVALID")
        self.assertEqual(
            response_data["errors"][0]["message"], "Enter a valid email address."
        )

        self.assertEqual(response_data["errors"][1]["field"], "phone_number")
        self.assertEqual(response_data["errors"][1]["code"], "INVALID")
        self.assertEqual(
            response_data["errors"][1]["message"], "A valid integer is required."
        )

        self.assertEqual(response_data["errors"][2]["field"], "role_id")
        self.assertEqual(response_data["errors"][2]["code"], "INVALID_CHOICE")
        self.assertEqual(
            response_data["errors"][2]["message"], '"STAFF" is not a valid choice.'
        )

        self.assertEqual(response_data["errors"][3]["field"], "last_name")
        self.assertEqual(response_data["errors"][3]["code"], "BLANK")
        self.assertEqual(
            response_data["errors"][3]["message"], "This field may not be blank."
        )

        self.assertEqual(response_data["errors"][4]["field"], "first_name")
        self.assertEqual(response_data["errors"][4]["code"], "BLANK")
        self.assertEqual(
            response_data["errors"][4]["message"], "This field may not be blank."
        )

        self.assertEqual(response_data["errors"][5]["field"], "password")
        self.assertEqual(response_data["errors"][5]["code"], "BLANK")
        self.assertEqual(
            response_data["errors"][5]["message"], "This field may not be blank."
        )

        self.assertEqual(response_data["errors"][6]["field"], "tenant_id")
        self.assertEqual(response_data["errors"][6]["code"], "NO_DATA_FOUND")
        self.assertEqual(response_data["errors"][6]["message"], "No Data Found.")

        return True

    def test_get_list_tenant_admins(self):
        """
        Test retrieving the list of tenant admins for a given tenant and validate response data and pagination.
        """

        tenant = self.test_create_tenant_admin_user()["tenant_config"]["tenant"]

        response = self.client.get(self.path, data={"tenant_id": tenant["tenant_id"]})

        response_data = response.json()

        self.success_ok_200(response_data)

        user = response_data["data"]["list"][0]
        self.assertEqual(user["email"], "test.company.admin@gmail.com")
        self.assertEqual(user["role_id"], "COMPANY_ADMIN")
        self.assertEqual(user["phone_number"], "9878786565")
        self.assertEqual(user["first_name"], "Bhushan")
        self.assertEqual(user["last_name"], "Borse")
        self.assertEqual(user["full_name"], "Bhushan Borse")
        self.assertIsNone(user["profile_photo"])
        self.assertIn("user_id", user)

        pagination = response_data["data"]["pagination"]
        self.assertEqual(pagination["count"], 1)
        self.assertEqual(pagination["page_size"], 10)
        self.assertEqual(pagination["current_page"], 1)
        self.assertEqual(pagination["total_pages"], 1)

        return True

    def test_get_list_tenant_admin_wrong_tenant_id(self):
        """Test that requesting tenant admin list with an invalid tenant_id returns the correct error response."""

        self.test_create_tenant_admin_user()

        response = self.client.get(self.path, data={"tenant_id": get_uuid()})

        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 1)
        self.assertEqual(response_data["errors"][0]["field"], "tenant_id")
        self.assertEqual(response_data["errors"][0]["code"], "NO_DATA_FOUND")
        self.assertEqual(response_data["errors"][0]["message"], "No Data Found.")

        return True

    def test_get_list_tenant_admin_none_tenant_id(self):
        """
        Test that a GET request with an empty tenant_id returns a proper validation error.
        """

        self.test_create_tenant_admin_user()

        response = self.client.get(self.path, data={"tenant_id": ""})

        response_data = response.json()

        self.bad_request_404(response_data)
        self.assertEqual(len(response_data["errors"]), 1)
        self.assertEqual(response_data["errors"][0]["field"], "tenant_id")
        self.assertEqual(response_data["errors"][0]["code"], "NULL")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field may not be null."
        )

        return True

    def test_get_list_tenant_admin_no_users(self):
        """Test that getting the list of tenant admins returns 404 when no users exist."""

        tenant_id = self.tenant_conf.test_create_tenant_configuration()["tenant"][
            "tenant_id"
        ]
        response = self.client.get(self.path, data={"tenant_id": tenant_id})

        response_data = response.json()

        self.data_not_found_404(response_data)
        return True
