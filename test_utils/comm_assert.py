from rest_framework import test, status


class CommonTestCaseAssertsBase(test.APITestCase):

    def data_not_found_404(self, response_data):
        self.assertFalse(response_data["is_success"])
        self.assertEqual(response_data["status_code"], status.HTTP_404_NOT_FOUND)
        self.assertIsNone(response_data["data"])
        self.assertIsNone(response_data["messages"])
        self.assertEqual(response_data["errors"]["code"], "NO_DATA_FOUND")
        self.assertEqual(response_data["errors"]["message"], "No Data Found.")

        return True

    def created_successfully_201(self, response_data, message="Created Successfully."):
        self.assertTrue(response_data["is_success"])
        self.assertEqual(response_data["status_code"], status.HTTP_201_CREATED)
        self.assertEqual(response_data["messages"]["message"], message)
        self.assertIsNone(response_data["errors"])

        return True

    def bad_request_404(self, response_data):
        self.assertFalse(response_data["is_success"])
        self.assertEqual(response_data["status_code"], status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(response_data["data"])
        self.assertIsNone(response_data["messages"])

    def success_ok_200(self, response_data, cm=True):
        self.assertTrue(response_data["is_success"])
        self.assertEqual(response_data["status_code"], status.HTTP_200_OK)
        self.assertIsNone(response_data["errors"])
        if cm:
            self.assertIsNone(response_data["messages"])

        return True

    def update_success_ok_200(self, response_data):
        self.assertTrue(response_data["is_success"])
        self.assertEqual(response_data["status_code"], status.HTTP_200_OK)
        self.assertIsNone(response_data["errors"])
        self.assertEqual(response_data["messages"]["message"], "Updated Successfully.")

        return True

    def patch_data_not_provided_400(self, response_data):
        self.assertFalse(response_data["is_success"])
        self.assertEqual(response_data["status_code"], status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(response_data["data"])
        self.assertIsNone(response_data["messages"])

        self.assertEqual(response_data["errors"]["code"], "BAD_REQUEST")
        self.assertEqual(response_data["errors"]["message"], "Please provide the data.")

        return True

    def delete_success_204(self, status_code):
        self.assertEqual(status_code, status.HTTP_204_NO_CONTENT)
        return True

    def wrong_cred_unauthorize_401(self, response_data):
        self.assertIsNone(response_data["data"])
        self.assertIsNone(response_data["messages"])
        self.assertFalse(response_data["is_success"])
        self.assertEqual(response_data["errors"]["code"], "WRONG_CREDENTIALS")
        self.assertEqual(response_data["errors"]["message"], "Wrong Credentials.")
        self.assertEqual(response_data["status_code"], status.HTTP_401_UNAUTHORIZED)

        return True

    def unauthorize_401(self, response_data):
        self.assertIsNone(response_data["data"])
        self.assertFalse(response_data["is_success"])
        self.assertIsNone(response_data["messages"])
        self.assertEqual(response_data["status_code"], status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(response_data["errors"]["code"], "UNAUTHORIZED")
        self.assertEqual(response_data["errors"]["message"], "Unauthorized Access.")

        return True
