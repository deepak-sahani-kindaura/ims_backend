from utils.functions import get_uuid
from auth_user.constants import RoleEnum
from test_utils.tenant_user_base import TestCaseBase


class UserTestCase(TestCaseBase):

    def setUp(self):

        self.path = "/api/user"
        self.path_id = "/api/user/{user_id}"

        return super().setUp()

    @staticmethod
    def success_data():
        return {
            "last_name": "Borse",
            "first_name": "Bhushan",
            "email": "test.company.operator@gmail.com",
            "phone_number": "9878786565",
            "role_id": RoleEnum.OPERATOR,
            "password": "1234",
        }

    def test_create_user(self):
        """
        Test the creation of a user validate the response data.
        """

        data = self.success_data()

        response = self.client.post(self.path, data=data)

        response_data = response.json()

        self.created_successfully_201(response_data)
        self.assertEqual(
            response_data["data"]["email"], "test.company.operator@gmail.com"
        )
        self.assertEqual(response_data["data"]["role_id"], "OPERATOR")
        self.assertEqual(response_data["data"]["phone_number"], 9878786565)
        self.assertEqual(response_data["data"]["first_name"], "Bhushan")
        self.assertEqual(response_data["data"]["last_name"], "Borse")
        self.assertEqual(response_data["data"]["full_name"], "Bhushan Borse")
        self.assertIsNone(response_data["data"]["profile_photo"])
        self.assertIn("user_id", response_data["data"])

        return response_data["data"]

    @staticmethod
    def duplicate_and_invalid_role_data():
        return {
            "last_name": "Borse",
            "first_name": "Bhushan",
            "email": "test.company.operator@gmail.com",
            "phone_number": "9878786565",
            "role_id": RoleEnum.OPERATOR,
            "password": "1234",
        }

    def test_create_duplicate_user(self):
        """
        Test that creating a user with duplicate email and invalid role returns appropriate validation errors.
        """

        self.test_create_user()

        data = self.duplicate_and_invalid_role_data()

        response = self.client.post(self.path, data=data)

        response_data = response.json()

        self.bad_request_404(response_data)
        self.assertEqual(len(response_data["errors"]), 1)
        self.assertEqual(response_data["errors"][0]["field"], "email")
        self.assertEqual(response_data["errors"][0]["code"], "DUPLICATE_ENTRY")
        self.assertEqual(response_data["errors"][0]["message"], "Already Exist.")

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

    def test_create_user_with_wrong_data(self):
        """
        Test that creating a user with invalid data returns appropriate validation errors.
        """

        data = self.invalid_data()

        response = self.client.post(self.path, data=data)

        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 6)

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

        return True

    def test_get_list_users(self):
        """
        Test retrieving the list of users for a given tenant and validate response data and pagination.
        """

        self.test_create_user()

        response = self.client.get(self.path, data={"first_name": "Bhushan"})

        response_data = response.json()

        self.success_ok_200(response_data)

        user = response_data["data"]["list"][1]
        self.assertEqual(user["email"], "test.company.operator@gmail.com")
        self.assertEqual(user["role_id"], "OPERATOR")
        self.assertEqual(user["phone_number"], "9878786565")
        self.assertEqual(user["first_name"], "Bhushan")
        self.assertEqual(user["last_name"], "Borse")
        self.assertEqual(user["full_name"], "Bhushan Borse")
        self.assertIsNone(user["profile_photo"])
        self.assertIn("user_id", user)

        pagination = response_data["data"]["pagination"]
        self.assertEqual(pagination["count"], 2)
        self.assertEqual(pagination["page_size"], 10)
        self.assertEqual(pagination["current_page"], 1)
        self.assertEqual(pagination["total_pages"], 1)

        return True

    def test_get_list_users_no_data_found(self):
        """
        Test retrieving the list of users with no matching data and validate the response.
        """

        self.test_create_user()

        response = self.client.get(self.path, data={"first_name": "testing"})

        response_data = response.json()
        self.data_not_found_404(response_data)

        return True

    def test_get_user_by_id(self):
        """
        Test retrieving a user by ID and validate the response data.
        """

        user_data = self.test_create_user()

        response = self.client.get(self.path_id.format(user_id=user_data["user_id"]))

        response_data = response.json()

        self.success_ok_200(response_data)
        self.assertTrue(response_data["is_success"])

        self.assertEqual(
            response_data["data"]["email"], "test.company.operator@gmail.com"
        )
        self.assertEqual(response_data["data"]["role_id"], "OPERATOR")
        self.assertEqual(response_data["data"]["phone_number"], "9878786565")
        self.assertEqual(response_data["data"]["first_name"], "Bhushan")
        self.assertEqual(response_data["data"]["last_name"], "Borse")
        self.assertEqual(response_data["data"]["full_name"], "Bhushan Borse")
        self.assertIsNone(response_data["data"]["profile_photo"])
        self.assertIn("user_id", response_data["data"])

        return True

    def test_get_user_by_id_no_data_found(self):
        """
        Test retrieving a user by ID that does not exist and validate the response.
        """

        response = self.client.get(self.path_id.format(user_id=get_uuid()))

        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    @staticmethod
    def update_data():
        return {
            "password": "1234",
            "first_name": "User",
            "profile_photo": None,
            "last_name": "Updated",
            "phone_number": "9878786565",
            "role_id": RoleEnum.OPERATOR,
            "email": "test.company.operator@gmail.com",
        }

    def test_update_user(self):
        """
        Test updating a user and validate the response data.
        """

        user_data = self.test_create_user()
        data = self.update_data()
        response = self.client.put(
            self.path_id.format(user_id=user_data["user_id"]), data=data
        )
        response_data = response.json()
        self.update_success_ok_200(response_data)

        self.assertEqual(
            response_data["data"]["email"], "test.company.operator@gmail.com"
        )
        self.assertEqual(response_data["data"]["role_id"], "OPERATOR")
        self.assertEqual(response_data["data"]["phone_number"], 9878786565)
        self.assertEqual(response_data["data"]["first_name"], "User")
        self.assertEqual(response_data["data"]["last_name"], "Updated")
        self.assertEqual(response_data["data"]["full_name"], "User Updated")
        self.assertIsNone(response_data["data"]["profile_photo"])
        self.assertIn("user_id", response_data["data"])

        return True

    def test_update_user_no_data_found(self):
        """
        Test updating a user that does not exist and validate the response.
        """

        data = self.update_data()
        response = self.client.put(
            self.path_id.format(user_id=get_uuid()),
            data=data,
        )

        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_update_user_with_wrong_data(self):
        """
        Test updating a user with invalid data and validate the response.
        """

        user_data = self.test_create_user()

        data = self.invalid_data()

        response = self.client.put(
            self.path_id.format(user_id=user_data["user_id"]), data=data
        )

        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 6)

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

        return True

    def test_patch_user(self):
        """
        Test partially updating a user and validate the response data.
        """

        user_data = self.test_create_user()

        data = {
            "first_name": "Updated",
            "last_name": "User",
        }

        response = self.client.patch(
            self.path_id.format(user_id=user_data["user_id"]), data=data
        )

        response_data = response.json()
        self.update_success_ok_200(response_data)

        self.assertEqual(response_data["data"]["first_name"], "Updated")
        self.assertEqual(response_data["data"]["last_name"], "User")
        self.assertEqual(response_data["data"]["full_name"], "Updated User")

        return True

    def test_patch_user_no_data_found(self):
        """
        Test partially updating a user that does not exist and validate the response.
        """

        data = {
            "first_name": "Updated",
            "last_name": "User",
        }

        response = self.client.patch(
            self.path_id.format(user_id=get_uuid()),
            data=data,
        )

        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_delete_user(self):
        """
        Test deleting a user and validate the response.
        """

        user_data = self.test_create_user()

        response = self.client.delete(self.path_id.format(user_id=user_data["user_id"]))

        self.delete_success_204(response.status_code)

        return True

    def test_delete_user_no_data_found(self):
        """
        Test deleting a user that does not exist and validate the response.
        """

        response = self.client.delete(self.path_id.format(user_id=get_uuid()))

        response_data = response.json()

        self.data_not_found_404(response_data)

        return True
