from test_utils import auth

from test_utils.test_client import APITestClient
from test_utils.base_super_admin import TestCaseBase


def success_data():
    return {
        "password": "1234",
        "username": auth.create_super_admin_test_user()["email"],
    }


class SuperAdminAuthTestCase(TestCaseBase):

    def setUp(self):
        self.client: APITestClient = APITestClient()
        return self

    def test_login_super_admin(self):
        """
        Test case for super admin login functionality.
        This test verifies that a super admin can successfully log in through the API endpoint.
        """

        data = success_data()

        response = self.client.post("/api/auth/admin/login", data=data)

        response_data = response.json()

        self.assertIn("token", response_data["data"])
        self.assertIn("created_dtm", response_data["data"])
        self.created_successfully_201(response_data, message="Logged in successfully.")

        return response_data["data"]

    @staticmethod
    def wrong_cred_data():
        return {"username": "wrong.cred.user@gmail.com", "password": "123467"}

    def test_wrong_cred_super_admin(self):
        """
        Test case for super admin login with wrong credentials.
        This test verifies that the login endpoint returns appropriate error response
        when incorrect credentials are provided for super admin login.
        """

        response = self.client.post(
            "/api/auth/admin/login", data=self.wrong_cred_data()
        )

        response_data = response.json()
        self.wrong_cred_unauthorize_401(response_data)

        return True

    @staticmethod
    def wrong_password_data():
        return {
            "username": auth.create_super_admin_test_user()["email"],
            "password": "12345",
        }

    def test_wrong_password_only_super_admin(self):
        """Test super admin login with wrong password.
        This test case verifies that attempting to login as super admin with wrong password returns
        appropriate error response with 401 unauthorized status code.
        """

        response = self.client.post(
            "/api/auth/admin/login", data=self.wrong_password_data()
        )

        response_data = response.json()

        self.wrong_cred_unauthorize_401(response_data)

        return True

    @staticmethod
    def wrong_data_format_data():
        return {"username": "eml", "password": ""}

    def test_wrong_email_format_super_admin(self):
        """Test super admin login with invalid email format and blank password."""

        response = self.client.post(
            "/api/auth/admin/login", data=self.wrong_data_format_data()
        )

        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "username")
        self.assertEqual(response_data["errors"][0]["code"], "INVALID")
        self.assertEqual(
            response_data["errors"][0]["message"], "Enter a valid email address."
        )

        self.assertEqual(response_data["errors"][1]["field"], "password")
        self.assertEqual(response_data["errors"][1]["code"], "BLANK")
        self.assertEqual(
            response_data["errors"][1]["message"], "This field may not be blank."
        )

        return True

    def test_logout_super_admin(self):
        """
        Test that a super admin can successfully log out via the admin logout endpoint.
        This test logs in as a super admin, sends a DELETE request to the logout endpoint with the appropriate authentication header,
        and asserts that the response status code indicates a successful logout (HTTP 204 No Content).
        """

        login = self.test_login_super_admin()

        response = self.client.set_auth_header(token=login).delete(
            "/api/auth/admin/logout"
        )

        self.delete_success_204(response.status_code)

        return True

    def test_logout_failed_super_admin(self):
        """
        Test that logout fails for a super admin with an invalid token.
        This test simulates a super admin login, replaces the valid token with a dummy token,
        and attempts to log out. It verifies that the response indicates unauthorized access (401).
        """

        login = self.test_login_super_admin()
        login["token"] = "dummy-token"

        response = self.client.set_auth_header(token=login).delete(
            "/api/auth/admin/logout"
        )

        response_data = response.json()

        self.unauthorize_401(response_data)

        return True

    def test_get_super_admin_profile(self):
        """
        Test retrieval of the super admin user's profile and validate response data.
        """

        login = self.test_login_super_admin()

        response = self.client.set_auth_header(token=login).get(
            "/api/user/super-admin/profile"
        )

        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertEqual(response_data["data"]["email"], "test.super.admin@gmail.com")
        self.assertEqual(response_data["data"]["role_id"], "SUPER_ADMIN")
        self.assertEqual(response_data["data"]["phone_number"], "9878786565")
        self.assertEqual(response_data["data"]["first_name"], "Deepak")
        self.assertEqual(response_data["data"]["last_name"], "Sahni")
        self.assertEqual(response_data["data"]["full_name"], "Deepak Sahni")
        self.assertIsNone(response_data["data"]["profile_photo"])
        self.assertIn("user_id", response_data["data"])

        return True

    def test_get_super_admin_profile_wrong_token(self):
        """Test that accessing the super admin profile with an invalid token returns a 401 Unauthorized response."""

        login = self.test_login_super_admin()
        login["token"] = "dummy-token"

        response = self.client.set_auth_header(token=login).get(
            "/api/user/super-admin/profile"
        )

        response_data = response.json()

        self.unauthorize_401(response_data)

        return True
