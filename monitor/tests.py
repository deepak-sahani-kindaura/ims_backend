from utils.functions import get_uuid
from auth_user.constants import RoleEnum

from test_utils.base_super_admin import TestCaseBase


class MonitorTestCase(TestCaseBase):

    def setUp(self):
        self.path = "/api/health"
        return super().setUp()

    def test_health_check(self):
        """
        Test the health check endpoint to ensure the service is running.
        """
        response = self.client.get(self.path)
        response_data = response.json()

        self.success_ok_200(response_data)

        # Top-level keys
        self.assertIn("cpu", response_data["data"])
        self.assertIn("disk", response_data["data"])
        self.assertIn("memory", response_data["data"])

        # CPU data
        cpu_data = response_data["data"]["cpu"]
        self.assertIn("percent_per_core", cpu_data)
        self.assertIn("percent_total", cpu_data)
        self.assertIn("count_logical", cpu_data)
        self.assertIn("count_physical", cpu_data)
        self.assertIn("frequency_current", cpu_data)
        self.assertIn("frequency_min", cpu_data)
        self.assertIn("frequency_max", cpu_data)
        self.assertIn("times_user", cpu_data)
        self.assertIn("times_system", cpu_data)
        self.assertIn("times_idle", cpu_data)

        # Disk data
        disk_data = response_data["data"]["disk"]
        self.assertIn("total", disk_data)
        self.assertIn("used", disk_data)
        self.assertIn("free", disk_data)
        self.assertIn("percent", disk_data)
        self.assertIn("read_count", disk_data)
        self.assertIn("write_count", disk_data)

        # Memory data
        memory_data = response_data["data"]["memory"]
        self.assertIn("percent", memory_data)
        self.assertIn("total", memory_data)
        self.assertIn("used", memory_data)
        self.assertIn("free", memory_data)
        self.assertIn("available", memory_data)

        return True
