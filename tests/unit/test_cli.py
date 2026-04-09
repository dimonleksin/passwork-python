import sys
import io
import json
import ssl
from base import Base
from unittest.mock import patch


class TestCli(Base):
    mock_result = None

    def run_command(self, params: list, return_code: int = 0):
        argv = ['passwork-cli'] + params

        with patch('passwork_client.modules.api_client.requests.request', side_effect=self.mocked_requests_get) as self.mock_result:
            with patch.object(sys, 'argv', argv):
                from cli import main as passwork_cli

                captured_output = io.StringIO()
                sys.stdout = captured_output
                sys.stderr = captured_output
                try:
                    passwork_cli()

                except SystemExit as e:
                    assert e.code == return_code

                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

                output_string = captured_output.getvalue()

        return output_string.strip()

    def response_by_method_and_url(self, method: str, url: str, args: dict):
        result = {}
        match method:
            case 'GET':
                if url.endswith('/api/v1/users/keys'):
                    result = self.load_mock_data('user_keys_response.json')

                if url.endswith(self.encrypted_item_id):
                    result = self.load_encrypted_item_data()

                if url.endswith(self.item_id):
                    result = self.load_item_data()

        return json.dumps(result)

    def mocked_requests_get(self, *args, **kwargs):
        from requests.models import Response

        response_content = self.response_by_method_and_url(*args, kwargs)

        response = Response()
        response.status_code = 200
        response._content = str.encode(response_content)
        return response

    def get_cli_params(self):
        return ['get', '--host', 'https://mock-passwork-api.local', '--token', '1234567890']

    def test_encrypted_cli_get(self, mock_master_key):

        command_params = self.get_cli_params() + ['--master-key', mock_master_key, '--password-id', self.encrypted_item_id]
        result = self.run_command(command_params)
        assert 'kzwugR]VH-9KF0:~d8h%' in result

        params = ['--field', 'login']
        result = self.run_command(command_params + params)
        assert 'login-test' in result

        params = ['--totp-code', 'test-totp-field']
        result = self.run_command(command_params + params, 1)
        assert 'Error: TOTP secret not found' in result

        params = ['--totp-code', 'Custom TOTP']
        result = self.run_command(command_params + params)
        assert len(result) == 6

    def test_cli_get(self):
        command_params = self.get_cli_params() + ['--password-id', self.item_id]

        result = self.run_command(command_params)

        assert 'kzwugR]VH-9KF0:~d8h%' in result

        params = ['--field', 'name']
        result = self.run_command(command_params + params)
        assert 'name-test' in result

        params = ['--field', 'url']
        result = self.run_command(command_params + params)
        assert 'https://example.com' in result

        params = ['--totp-code', 'test-totp-field']
        result = self.run_command(command_params + params, 1)
        assert 'Error: TOTP secret not found' in result

        params = ['--totp-code', 'Custom TOTP']
        result = self.run_command(command_params + params)
        assert len(result) == 6

    def test_cli_get_with_verify_sys_path(self):
        command_params = self.get_cli_params() + ['--password-id', self.item_id, '--ssl-verify']

        result = self.run_command(command_params)

        assert 'kzwugR]VH-9KF0:~d8h%' in result

        self.mock_result.assert_called_once()

        _, _, kwargs = self.mock_result.mock_calls[0]
        default_paths = ssl.get_default_verify_paths()
        expected_verify = default_paths.cafile or default_paths.capath or True
        assert kwargs["verify"] == expected_verify

    def test_cli_get_with_verify_custom_path(self):
        custom_verify_path = "/etc/ssl/certs"
        command_params = self.get_cli_params() + ['--password-id', self.item_id, '--ssl-verify', custom_verify_path]

        result = self.run_command(command_params)
        assert 'kzwugR]VH-9KF0:~d8h%' in result

        self.mock_result.assert_called_once()

        _, _, kwargs = self.mock_result.mock_calls[0]
        assert kwargs["verify"] == custom_verify_path

    def test_cli_get_with_verify_disabled(self):
        command_params = self.get_cli_params() + ['--password-id', self.item_id, '--ssl-verify', False]

        result = self.run_command(command_params)
        assert 'kzwugR]VH-9KF0:~d8h%' in result

        self.mock_result.assert_called_once()

        _, _, kwargs = self.mock_result.mock_calls[0]
        assert not kwargs["verify"]

    def test_cli_deprecated_no_ssl_verify(self):
        command_params = self.get_cli_params() + ['--password-id', self.item_id, '--no-ssl-verify']

        result = self.run_command(command_params)
        assert 'kzwugR]VH-9KF0:~d8h%' in result

        assert '--no-ssl-verify is deprecated' in result

        _, _, kwargs = self.mock_result.mock_calls[0]
        assert not kwargs["verify"]

    def test_cli_priority_ssl_verify_or_deprecated_no_ssl_verify(self):
        custom_verify_path = "/etc/ssl/certs"
        command_params = self.get_cli_params() + ['--password-id', self.item_id, '--ssl-verify', custom_verify_path, '--no-ssl-verify']

        result = self.run_command(command_params)
        assert 'kzwugR]VH-9KF0:~d8h%' in result

        _, _, kwargs = self.mock_result.mock_calls[0]
        assert kwargs["verify"] == custom_verify_path
