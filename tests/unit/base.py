import pytest


class Base:

    encrypted_item_id = "691c354719feeca0c603c2f2"
    item_id = "691d7dc8decc3f3da50349d2"

    def load_mock_data(self, key):
        return pytest.load_mock_data(key)

    def load_encrypted_item_data(self):
        return self.load_mock_data('encrypted_item_response.json')

    def load_item_data(self):
        return self.load_mock_data('item_response.json')
