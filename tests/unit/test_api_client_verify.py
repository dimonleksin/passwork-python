from unittest.mock import MagicMock, patch
import os
import ssl

from passwork_client import PassworkClient


class TestApiClientVerify:
    certs_dir = "/etc/ssl/certs"

    def _mock_response(self, payload):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = payload
        response.raise_for_status.return_value = None
        return response

    def _extract_verify(self, request_mock, call_index=0):
        _, _, kwargs = request_mock.mock_calls[call_index]
        return kwargs["verify"]

    def test_request_uses_certificate_directory_from_client(self):
        client = PassworkClient("https://mock-passwork-api.com", verify_ssl=self.certs_dir)

        with patch(
            "passwork_client.modules.api_client.requests.request",
            return_value=self._mock_response({}),
        ) as request_mock:
            client.call("GET", "/api/v1/users/info")

        request_mock.assert_called_once()
        assert self._extract_verify(request_mock) == self.certs_dir

    def test_get_vault_types_uses_certificate_directory(self):
        client = PassworkClient("https://mock-passwork-api.com", verify_ssl=self.certs_dir)

        with patch(
            "passwork_client.modules.api_client.requests.request",
            return_value=self._mock_response({"items": [{"id": "vt-1", "name": "Private"}]}),
        ) as request_mock:
            result = client.get_vault_types()

        request_mock.assert_called_once()
        assert result["items"][0]["id"] == "vt-1"
        assert self._extract_verify(request_mock) == self.certs_dir

    def test_get_items_uses_certificate_directory(self):
        client = PassworkClient("https://mock-passwork-api.com", verify_ssl=self.certs_dir)
        client.is_encrypt = False

        payload = {
            "responses": [
                {
                    "statusCode": 200,
                    "body": {
                        "id": "item-1",
                        "customs": [],
                        "name": "Item 1",
                    },
                },
                {
                    "statusCode": 200,
                    "body": {
                        "id": "item-2",
                        "customs": [],
                        "name": "Item 2",
                    },
                },
            ]
        }

        with patch(
            "passwork_client.modules.api_client.requests.request",
            return_value=self._mock_response(payload),
        ) as request_mock:
            result = client.get_items(["item-1", "item-2"])

        request_mock.assert_called_once()
        assert [item["id"] for item in result] == ["item-1", "item-2"]
        assert self._extract_verify(request_mock) == self.certs_dir

    def test_search_items_uses_certificate_directory(self):
        client = PassworkClient("https://mock-passwork-api.com", verify_ssl=self.certs_dir)

        with patch(
            "passwork_client.modules.api_client.requests.request",
            return_value=self._mock_response({"items": [{"id": "item-1"}]}),
        ) as request_mock:
            result = client.search_items(query="test", tags=["tag-1", "tag-2"])

        request_mock.assert_called_once()
        assert result == [{"id": "item-1"}]
        assert self._extract_verify(request_mock) == self.certs_dir

    def test_uses_default_sys_certificate_directory(self):
        client = PassworkClient("https://mock-passwork-api.com", verify_ssl=True)

        with patch(
            "passwork_client.modules.api_client.requests.request",
            return_value=self._mock_response({}),
        ) as request_mock:
            client.call("GET", "/api/v1/users/info")

        request_mock.assert_called_once()
        verify_value = self._extract_verify(request_mock)
        assert isinstance(verify_value, str)
        assert os.path.isfile(verify_value)
