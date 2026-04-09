import pytest
import os
import json
from unittest.mock import MagicMock, patch
import hashlib


@pytest.fixture
def mock_client():
    """Create a mock PassworkClient with mocked _request method."""
    from passwork_client import PassworkClient

    with patch('passwork_client.modules.api_client.requests.request'):
        client = PassworkClient('https://mock-passwork-api.com')
        client._request = MagicMock()
        client.is_encrypt = False
        yield client


@pytest.fixture
def mock_master_key():
    return "/SzdXs1hNVP1H1+8m7AGrcVpbN2AaBV/cEdWYtF7TQwfizY+K1ukUNX6j6rNHvLG0v/wCICkDXSd6yQiD0ou9w=="


@pytest.fixture
def mock_encrypted_client(mock_client, mock_master_key):
    """Create a mock PassworkClient with encryption enabled."""
    from passwork_client.crypto import decrypt_aes

    with patch('passwork_client.modules.api_client.requests.request'):
        mock_client.is_encrypt = True
        # Set encryption-related attributes
        mock_client.master_key = mock_master_key

        keys_data = load_mock_data('user_keys_response.json')
        mock_client.user_private_key = decrypt_aes(
            keys_data["keys"]["privateEncrypted"],
            mock_client.master_key
        )
        mock_client.user_public_key = keys_data["keys"]["public"]
        mock_client.master_key_hash = hashlib.sha256(mock_client.master_key.encode()).hexdigest()

        yield mock_client


def load_mock_data(filename):
    """Load mock data from JSON files."""
    mock_data_dir = os.path.join(os.path.dirname(__file__), 'mock_data')
    file_path = os.path.join(mock_data_dir, filename)
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as f:
        return json.load(f)


pytest.load_mock_data = load_mock_data
