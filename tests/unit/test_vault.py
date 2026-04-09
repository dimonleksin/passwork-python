import pytest
from base import Base


class TestVault (Base):
    @pytest.fixture
    def real_mock_encrypted_vault_data(self):
        """Load real vault mock data from saved response."""
        return self.load_mock_data('encrypted_vault_response.json')

    @pytest.fixture
    def real_mock_vault_data(self):
        """Load real vault mock data from saved response."""
        return self.load_mock_data('vault_response.json')

    def test_get_encrypted_vault(self, mock_encrypted_client, real_mock_encrypted_vault_data):
        # Setup mock_encrypted_client to use real mock data
        mock_encrypted_client._request.side_effect = [
            real_mock_encrypted_vault_data  # Return mock item data on request
        ]

        # Call the get_item method with the real item ID
        vault_id = '691c1ec0569fd4826e098512'
        vault = mock_encrypted_client.get_vault(vault_id)

        mock_encrypted_client._request.assert_called_once()
        args, kwargs = mock_encrypted_client._request.call_args
        assert args == ("GET", f"/api/v1/vaults/{vault_id}")
        assert kwargs.get("params", {}) == {}

        vault_password = mock_encrypted_client.get_vault_password(vault)

        assert vault_password == 'NhlTuNz2O4Qt!Y!y@hGRoWFNiPyPZBwncheCT7Es3i!EXur5DP8fRmib7tit1ruTUlw3zjO7d0zEid5AmVjdpoWxsu6H39Jx4rrM'

        expected_vault = self.get_expected_vault()

        self.assert_expected_vault(expected_vault, vault)

    def test_get_vault(self, mock_client, real_mock_vault_data):
        # Setup mock_encrypted_client to use real mock data
        mock_client._request.side_effect = [
            real_mock_vault_data  # Return mock item data on request
        ]

        # Call the get_item method with the real item ID
        vault_id = '6821d92cb9d649035b0894e2'
        vault = mock_client.get_vault(vault_id)

        mock_client._request.assert_called_once()
        args, kwargs = mock_client._request.call_args
        assert args == ("GET", f"/api/v1/vaults/{vault_id}")
        assert kwargs.get("params", {}) == {}

        vault_password = mock_client.get_vault_password(vault)

        assert vault_password == ''

        expected_vault = self.get_expected_vault({
            'id': '6821d92cb9d649035b0894e2',
            'typeId': '685cfa5a3d0ba75d2f041972',
            'masterKeyEncrypted': None,
        })

        self.assert_expected_vault(expected_vault, vault)

    def assert_expected_vault(self, expected_vault: dict, vault: dict):
        assert vault['name'] == expected_vault['name'], "Name field doesn't match"
        assert vault == expected_vault, "Decrypted vault object doesn't match expected value"

    def get_expected_vault(self, merge: dict = {}):
        return {
            'id': '691c1ec0569fd4826e098512',
            'name': 'Test',
            'typeId': '685cfa5a3d0ba75d2f041972',
            'masterKeyEncrypted': 'asXArz2xu5bRbl+vM+NMtHNvtharYoy1ny4Z6WwoVEeu9Cn1BANR3FK+B//DEOXJHIHOER//LdCo8jCibMJcwXcOTwYtG+zUZ4A50akohl1g3tZMKKR/Fp8rQmr1f37CG1XmpNbMBP5z5+uQOWRni7Ov8av0WSxjYAJsa5EojaU=',
            'isVisible': True,
            'directoryAccess': {
                'isViewingAccess': False,
                'access': 'admin',
                'accessName': 'Administrator'
            },
            'permissions': [
                'directory:read',
                'directory:edit',
                'directory:copy',
                'directory:move',
                'directory:delete',
                'directory:export',
                'directory:activityLog:read',
                'directory:security:analyse',
                'directory:access:read',
                'directory:access:manage',
                'vault:delete',
                'vault:leave',
                'object:createAndImport',
                'item:read',
                'item:edit',
                'item:delete',
                'item:move',
                'item:copy',
                'item:snapshot:read',
                'item:activityLog:read',
                'shortcut:create',
                'inboxItem:createForReading',
                'inboxItem:createForEditing',
                'link:create',
                'item:additionalAccess:read',
                'item:additionalAccess:manage',
                'bin:manage'
            ],
            'canLeaveVault': None,
            'canChangeVaultType': None
        } | merge
