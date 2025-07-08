from rest_framework import test


class APITestClient:

    def __init__(self, headers=None):
        self.client = test.APIClient()
        self.headers = headers or {}

    def set_auth_header(self, token=None):
        return self.set_header("HTTP_AUTHORIZATION", f"Bearer {token['token']}")

    def set_header(self, key, value):
        self.headers[key] = value
        return self

    def set_host(self, http_host):
        return self.set_header("HTTP_HOST", http_host)

    def get(self, path, data=None):
        return self.client.get(path, **self.headers, format="json", data=data)

    def post(self, path, data=None):
        return self.client.post(path, data=data, **self.headers, format="json")

    def put(self, path, data=None):
        return self.client.put(path, data=data, **self.headers, format="json")

    def patch(self, path, data=None):
        return self.client.patch(path, data=data, **self.headers, format="json")

    def delete(self, path, data=None):
        return self.client.delete(path, data=data, **self.headers, format="json")
