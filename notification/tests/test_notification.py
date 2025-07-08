from utils.functions import get_uuid
from test_utils.tenant_user_base import TestCaseBase


class NotificationTestCase(TestCaseBase):

    def setUp(self):
        self.path = "/api/notification"
        self.path_id = "/api/product/{product_id}"
        return super().setUp()

    def create_notification_by_creating_stock(self):
        """
        Helper method to create a notification by creating stock.
        """
        from stock.tests.test_stock import StockTestCase

        return StockTestCase().setUp().test_create_stock_out()

    def test_get_notification_list(self):
        """Test case to get the list of notifications."""

        self.create_notification_by_creating_stock()

        response = self.client.get(self.path)

        response_data = response.json()

        self.success_ok_200(response_data)

        # Check structure of data
        self.assertIn("list", response_data["data"])
        self.assertIn("pagination", response_data["data"])

        # Validate pagination keys
        pagination = response_data["data"]["pagination"]
        self.assertIn("count", pagination)
        self.assertIn("page_size", pagination)
        self.assertIn("current_page", pagination)
        self.assertIn("total_pages", pagination)

        # Validate each notification entry
        for notification_entry in response_data["data"]["list"]:
            self.assertIn("created_dtm", notification_entry)
            self.assertIn("sent_by", notification_entry)
            self.assertIn("notification", notification_entry)

            sent_by = notification_entry["sent_by"]
            self.assertIn("user_id", sent_by)
            self.assertIn("email", sent_by)
            self.assertIn("role_id", sent_by)
            self.assertIn("first_name", sent_by)
            self.assertIn("last_name", sent_by)
            self.assertIn("full_name", sent_by)
            self.assertIn("phone_number", sent_by)
            self.assertIn("profile_photo", sent_by)

            notification = notification_entry["notification"]
            self.assertIn("title", notification)
            self.assertIn("message", notification)
            self.assertIn("notification_id", notification)
            self.assertIn("notification_type", notification)
            self.assertIn("notification_data", notification)
            self.assertIn("stock_id", notification["notification_data"])

        return response_data["data"]["list"]

    def test_not_found_notification(self):
        """Test case to check the response when no notifications are found."""

        response = self.client.get(self.path)

        self.data_not_found_404(response.json())

        return True

    def test_mark_as_read_notification(self):
        """Test case to mark a notification as read."""

        notifications = self.test_get_notification_list()

        notification_id = notifications[0]["notification"]["notification_id"]

        response = self.client.put(
            self.path,
            data={"list_notification_id": [notification_id], "mark_all_as_read": False},
        )

        response_data = response.json()

        self.success_ok_200(response_data, cm=False)

        self.assertIn("messages", response_data)
        self.assertIn("message", response_data["messages"])
        self.assertEqual(
            response_data["messages"]["message"], "1 Notifications are mark as read."
        )

        return True

    def test_mark_all_as_read_notification(self):
        """Test case to mark all notifications as read."""

        self.test_get_notification_list()

        response = self.client.put(
            self.path,
            data={"list_notification_id": [], "mark_all_as_read": True},
        )

        response_data = response.json()

        self.success_ok_200(response_data, cm=False)

        self.assertIn("messages", response_data)
        self.assertIn("message", response_data["messages"])
        self.assertEqual(
            response_data["messages"]["message"], "2 Notifications are mark as read."
        )

        return True

    def test_mark_as_read_notification_not_provided(self):
        """Test case to check the response when no notification IDs are provided."""

        response = self.client.put(
            self.path, data={"list_notification_id": [], "mark_all_as_read": False}
        )

        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertIsInstance(response_data["errors"], list)
        self.assertEqual(response_data["errors"][0]["field"], "list_notification_id")
        self.assertEqual(response_data["errors"][0]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field is required."
        )

        return True

    def test_mark_as_read_notification_not_found(self):
        """Test case to check the response when no notifications are found to mark as read."""

        response = self.client.put(
            self.path,
            data={
                "list_notification_id": [get_uuid()],
                "mark_all_as_read": False,
            },
        )

        response_data = response.json()

        self.data_not_found_404(response_data)

        return True
