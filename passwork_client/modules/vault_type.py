from ..crypto import rsa_encrypt, b64encode

class VaultType:

    def get_vault_types(self):
        return self.call("GET", "/api/v1/vault-types/all")

    def find_vault_type(self, vault_type_code: str):
        vault_type = [r for r in self.get_vault_types()["items"] if r.get("code") == vault_type_code]
        if not vault_type:
            return None

        return vault_type[0]

    def get_vault_type_admins_keys(self, vault_type_id: str, vault_master_key: str):

        if not vault_type_id:
            return {}

        if not self.is_encrypt:
            return {}

        admins_response = self.call("GET", f"/api/v1/vault-types/{vault_type_id}/administrators")
        admins_keys = {}
        for admin in admins_response["items"]:
            master_key_encrypted = rsa_encrypt(vault_master_key, admin["publicKey"])
            admins_keys[admin["id"]] = b64encode(master_key_encrypted).decode("utf-8")

        return admins_keys