from utils.cache import cache
from auth_user.constants import RoleEnum

from tenant.utils.helpers import (
    set_request_tenant_aware,
    set_tenant_details_to_request_thread,
)

from test_utils.test_client import APITestClient
from test_utils.comm_assert import CommonTestCaseAssertsBase


class TestCaseBase(CommonTestCaseAssertsBase):

    def setUp(self, auth=True, role_id=None):

        cache.clear()

        self.http_host = "test.testserver"

        if auth:
            self.client: APITestClient = self.get_client(role_id=role_id)
        else:
            self.client: APITestClient = APITestClient()

        return self

    def get_client(self, role_id=None):

        tenant = self.setup_tenant()
        set_request_tenant_aware(True)
        set_tenant_details_to_request_thread(tenant_obj=tenant)

        self.setup_tenant_conf(tenant_id=tenant.tenant_id)

        self.setup_tenant_permissions(tenant_id=tenant.tenant_id)

        token = self.get_tenant_user_token(tenant_id=tenant.tenant_id, role_id=role_id)

        client = APITestClient()
        client = client.set_auth_header(token).set_host(self.http_host)

        return client

    def setup_tenant(self):
        from tenant.db_access import tenant_manager

        return tenant_manager.upsert(
            data={
                "tenant_code": "test",
                "tenant_name": "Test Tenant",
            },
            query={"tenant_code": "test"},
        )

    def setup_tenant_conf(self, tenant_id):
        from tenant.db_access import tenant_configuration_manager

        return tenant_configuration_manager.upsert(
            data={
                "tenant_id": tenant_id,
                "database_server": "SQLITE",
                "database_strategy": "SHARED",
                "authentication_type": "JWT_TOKEN",
            },
            query={"tenant_id": tenant_id},
        )

    def setup_tenant_permissions(self, tenant_id):
        from auth_user.utils.permission import load_permission

        load_permission.load_permissions_for_tenant(tenant_id=tenant_id)

    def get_tenant_user_token(self, tenant_id, role_id=None):

        from auth_user.db_access import user_manager

        _user_manager = user_manager.disable_tenant_aware()

        user = _user_manager.upsert(
            data={
                "last_name": "Sahni",
                "first_name": "Deepak",
                "phone_number": "9878786565",
                "email": "test.company.admin@gmail.com",
                "role_id": role_id or RoleEnum.COMPANY_ADMIN,
                "tenant_id": tenant_id,
            },
            query={"email": "test.company.admin@gmail.com"},
        )

        user.set_password("1234")
        user.save()

        response = (
            APITestClient()
            .set_host(self.http_host)
            .post(
                "/api/auth/login",
                data={"username": "test.company.admin@gmail.com", "password": "1234"},
            )
        )

        return response.json()["data"]
