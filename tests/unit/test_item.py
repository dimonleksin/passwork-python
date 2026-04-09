from base import Base


class TestItem(Base):

    def test_get_encrypted_item(self, mock_encrypted_client):
        """
            Test get_item method using real mock data saved from API responses.
            This test verifies that the item object is properly decrypted and
            matches the expected result.
        """
        # Setup mock_encrypted_client to use real mock data
        mock_encrypted_client._request.side_effect = [
            self.load_encrypted_item_data()  # Return mock item data on request
        ]

        # Call the get_item method with the real item ID
        item_id = self.encrypted_item_id
        item = mock_encrypted_client.get_item(item_id)

        # Verify the method made the correct request
        mock_encrypted_client._request.assert_called_once()
        args, kwargs = mock_encrypted_client._request.call_args
        assert args == ("GET", f"/api/v1/items/{item_id}")
        assert kwargs.get("params", {}) == {}
        # Expected item object after decryption
        expected_item = self.get_expected_item()
        self.assert_expected_item(expected_item, item)

    def test_get_item(self, mock_client):
        """
        Test get_item method using real mock data saved from API responses.
        """

        mock_client._request.side_effect = [
            self.load_item_data()  # Return mock item data on request
        ]

        item_id = self.item_id
        item = mock_client.get_item(item_id)

        # Verify the method made the correct request
        mock_client._request.assert_called_once()
        args, kwargs = mock_client._request.call_args
        assert args == ("GET", f"/api/v1/items/{item_id}")
        assert kwargs.get("params", {}) == {}

        # Expected item object after decryption
        expected_item = self.get_expected_item({
            'id': '691d7dc8decc3f3da50349d2',
            'vaultId': '6821d92cb9d649035b0894e2',
            'passwordEncrypted': 'a3p3dWdSXVZILTlLRjA6fmQ4aCU=',
            'keyEncrypted': None,
            'attachments': [
                {
                    'id': '691d7dc8decc3f3da50349d3',
                    'encryptedKey': 'YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWE=',
                    'name': 'test.txt'
                }
            ],
            'vaultMasterKeyEncrypted': None,
            'urls': ['https://example.com', 'https://example.local'],
        })

        self.assert_expected_item(expected_item, item)

    def assert_expected_item(self, expected_item: dict, item: dict):

        assert 'password' in item, "Password field should be present in the result"
        assert item['password'] == expected_item['password'], "Decrypted password doesn't match expected value"

        # Check that the customs fields are decrypted
        assert len(item['customs']) == len(expected_item['customs']), "Number of customs fields doesn't match"
        for i, custom in enumerate(item['customs']):
            assert custom['name'] == expected_item['customs'][i]['name'], f"Custom field name {i} doesn't match"
            assert custom['value'] == expected_item['customs'][i]['value'], f"Custom field value {i} doesn't match"
            assert custom['type'] == expected_item['customs'][i]['type'], f"Custom field type {i} doesn't match"

        # Check basic fields
        assert item['name'] == expected_item['name'], "Name field doesn't match"
        assert item['login'] == expected_item['login'], "Login field doesn't match"
        assert item['description'] == expected_item['description'], "Description field doesn't match"

        # Check that the entire item object matches the expected result
        assert item == expected_item, "Decrypted item object doesn't match expected value"

    def get_expected_item(self, merge: dict = {}):
        return {
            'id': '691c354719feeca0c603c2f2',
            'vaultId': '691c1ec0569fd4826e098512',
            'folderId': None,
            'passwordEncrypted': 'amt4cwv48xb6pp1h71wmyebk8nn7mw3r6hd3gdup998njy9tc5mp6pj375d48dka9x0p4w34eru58hjgdwrpjrudd4upaubt71x7gx0',
            'keyEncrypted': 'amt4cwv48xb6pp1h5wtq2ca2f0rmcphh5xw5em9h85mp6hu89mt64w1p9ta7mrbuddu6wcud5ctmuh9m5xc5md2t8995mmv1amt54wu171x58wk9d50nchb169d6pyj9f92m2wvp9nj4wju48du3gvuqdtr7maujatjp2j2ue14m6kv2e1h72y1f8twn2wbg9n63cgj4f5j6upht8xbq8vbq7592ydjk9humwn1pe9p6wy3e8t344ubra5t38tk398qpmtbb8ncqmwatamyg',
            'customs': [
                {'type': 'text', 'value': 'custom-login', 'name': 'Custom name'},
                {'type': 'password', 'value': 'lANeOlEzJ9f2isl$60=q', 'name': 'Custom password'},
                {'type': 'totp', 'value': 'RNYGXTPKMNW53KSCMLCMMYQ3Z6', 'name': 'Custom TOTP'}
            ],
            'attachments': [
                {
                    'id': '691c354719feeca0c603c2f3',
                    'encryptedKey': 'amt4cwv48xb6pp1h5dq4em1kdx7p8kbg8xrmuxug5x430hv7b1cpmwa4d9aqggu68h97mtkh5x75ggk4dxkm4c2461r4rk9bd5anec38b1j50gbpcx1mwt38a524an2gf55pyn9mf53q0hkmb9d42rbncmtq8kv1cd5qehahf5jmpwtbc5unmdbc6gqk0j3nanp38e1ta9342gtmch34ycv6ddm5ev9nehrq8h2a6gu66htj8dp6au9qa1npcdb8f1cpayk9dnukauupa4yg',
                    'name': 'test.txt'
                }
            ],
            'name': 'name-test',
            'login': 'login-test',
            'url': 'https://example.com',
            'urls': ['https://example.com', 'https://example.local'],
            'description': 'notes test',
            'tags': ['test', 'test-2'],
            'fieldsOrder': None,
            'isDeleted': False,
            'color': 5,
            'isFavorite': True,
            'vaultMasterKeyEncrypted': 'asXArz2xu5bRbl+vM+NMtHNvtharYoy1ny4Z6WwoVEeu9Cn1BANR3FK+B//DEOXJHIHOER//LdCo8jCibMJcwXcOTwYtG+zUZ4A50akohl1g3tZMKKR/Fp8rQmr1f37CG1XmpNbMBP5z5+uQOWRni7Ov8av0WSxjYAJsa5EojaU=',
            'password': 'kzwugR]VH-9KF0:~d8h%'
        } | merge
