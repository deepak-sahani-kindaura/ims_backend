from test_utils.test_client import APITestClient
from test_utils.comm_assert import CommonTestCaseAssertsBase
from test_utils.auth import create_super_admin_test_token


class TestCaseBase(CommonTestCaseAssertsBase):

    def setUp(self, auth=True):

        if auth:
            self.client: APITestClient = self.get_client(auth)

        return self

    def get_client(self, auth):
        client = APITestClient()

        if auth:
            client = client.set_auth_header(create_super_admin_test_token())

        return client
