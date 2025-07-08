from utils.functions import get_uuid
from auth_user.constants import RoleEnum
from test_utils.tenant_user_base import TestCaseBase


class RolePermissionTestCase(TestCaseBase):

    def setUp(self):
        self.path = "/api/role-permission"
        self.path_id = "/api/role-permission/{role_id}/{permission_id}"
        return super().setUp()

    def role_permission_data(self):
        from auth_user.tests.test_permissions import PermissionTestCase

        permissions = PermissionTestCase().setUp().test_get_permissions()

        return [
            {
                "role_id": RoleEnum.OPERATOR,
                "permission_id": permission["permission_id"],
            }
            for permission in permissions
        ]

    def test_create_role_permissions(self):
        """
        Test that the role permissions are correctly created.
        """

        data = self.role_permission_data()

        response = self.client.post(self.path, data=data)

        response_data = response.json()

        self.created_successfully_201(response_data)
        return True

    def test_already_exists_role_permissions(self):
        """
        Test that the role permissions already exist.
        """

        self.test_create_role_permissions()

        data = self.role_permission_data()
        response = self.client.post(self.path, data=data)

        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertGreater(len(response_data["errors"]), 0)
        for error in response_data["errors"]:
            self.assertEqual(error["field"], "role_permission")
            self.assertEqual(error["code"], "DUPLICATE_ENTRY")
            self.assertEqual(error["message"], "Already Exist.")

        return True

    def test_create_with_none_data(self):
        """
        Test that the role permissions are not created with wrong data.
        """

        response = self.client.post(self.path, data=[{}])

        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "permission_id")
        self.assertEqual(response_data["errors"][0]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][1]["field"], "role_id")
        self.assertEqual(response_data["errors"][1]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][1]["message"], "This field is required."
        )

        return True

    @staticmethod
    def get_invalid_data():
        """
        Returns a list of invalid role permission data.
        """
        return [
            {
                "role_id": "invalid_role",
                "permission_id": get_uuid(),
            },
            {
                "role_id": RoleEnum.OPERATOR,
                "permission_id": "invalid_permission",
            },
            {
                "role_id": RoleEnum.OPERATOR,
                "permission_id": get_uuid(),
            },
        ]

    def test_create_with_invalid_data(self):
        """
        Test that the role permissions are not created with invalid data.
        """

        response = self.client.post(self.path, data=self.get_invalid_data())

        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 4)

        self.assertEqual(response_data["errors"][0]["field"], "permission_id")
        self.assertEqual(response_data["errors"][0]["code"], "NO_DATA_FOUND")
        self.assertEqual(response_data["errors"][0]["message"], "No Data Found.")

        self.assertEqual(response_data["errors"][1]["field"], "role_id")
        self.assertEqual(response_data["errors"][1]["code"], "INVALID_CHOICE")
        self.assertEqual(
            response_data["errors"][1]["message"],
            '"invalid_role" is not a valid choice.',
        )

        self.assertEqual(response_data["errors"][2]["field"], "permission_id")
        self.assertEqual(response_data["errors"][2]["code"], "INVALID")
        self.assertEqual(response_data["errors"][2]["message"], "Must be a valid UUID.")

        self.assertEqual(response_data["errors"][3]["field"], "permission_id")
        self.assertEqual(response_data["errors"][3]["code"], "NO_DATA_FOUND")
        self.assertEqual(response_data["errors"][3]["message"], "No Data Found.")

        return True

    def test_get_role_permissions(self):
        """
        Test that the role permissions are correctly fetched.
        """

        self.test_create_role_permissions()

        response = self.client.get(self.path)

        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertIsInstance(response_data["data"], list)
        self.assertGreater(len(response_data["data"]), 0)

        for role_permission in response_data["data"]:
            self.assertIn("role_id", role_permission)
            self.assertIn("permission_id", role_permission)

        return True

    def test_get_role_permissions_no_data_found(self):
        """
        Test that no role permissions are returned when there are none.
        """

        response = self.client.get(self.path)

        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_delete_role_permission(self):
        """
        Test that the role permission is correctly deleted.
        """

        self.test_create_role_permissions()

        role_permission = self.role_permission_data()[0]

        response = self.client.delete(
            self.path_id.format(
                role_id=role_permission["role_id"],
                permission_id=role_permission["permission_id"],
            )
        )

        self.delete_success_204(response.status_code)

        return True

    def test_delete_non_existent_role_permission(self):
        """
        Test that trying to delete a non-existent role permission returns an error.
        """

        role_permission = self.role_permission_data()[0]

        response = self.client.delete(
            self.path_id.format(
                role_id=role_permission["role_id"],
                permission_id=get_uuid(),
            )
        )

        response_data = response.json()

        self.data_not_found_404(response_data)

        return True
