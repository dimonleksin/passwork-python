from ..crypto import rsa_decrypt, rsa_encrypt, get_hash, b64encode, generate_key, generate_salt
from ..exceptions import PassworkError

class Vault:

    def create_vault(self, vault_name: str, type_id: str = None):

        if self.find_feature("vaultType") and not type_id:
            raise PassworkError("The vault type(type_id) parameter is required")

        vault = {
            "name": vault_name,
        }

        vault_master_key = ''
        if self.is_encrypt:
            vault_master_key = generate_key()
            salt = generate_salt()

            master_key_encrypted = rsa_encrypt(vault_master_key, self.user_public_key)
            vault["masterKeyEncrypted"] = b64encode(master_key_encrypted).decode("utf-8")
            vault["masterKeyHash"] = get_hash(f"{vault_master_key}{salt}")
            vault["salt"] = salt

        if type_id:
            vault["typeId"] = type_id
            vault["administratorsKeys"] = self.get_vault_type_admins_keys(type_id, vault_master_key)

        response = self.call("POST", "/api/v1/vaults", vault)
        return response["id"]

    def get_vault(self, vault_id: str):
        return self.call("GET", f"/api/v1/vaults/{vault_id}")

    def get_vault_password(self, vault: dict):
        if not self.is_encrypt:
            return ''

        vault_key_encrypted = vault["masterKeyEncrypted"]
        return rsa_decrypt(vault_key_encrypted, self.user_private_key).decode()
