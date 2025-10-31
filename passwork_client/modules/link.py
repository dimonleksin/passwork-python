from ..crypto import generate_key, get_hash, encrypt_aes, decrypt_aes
from ..utils import get_encryption_key

class Link:

    def create_link(self, type: str, expiration_time: str, item_id: str = None, shortcut_id: str = None):

        if shortcut_id:
            shortcut = self.get_shortcut(shortcut_id)
            item = shortcut["password"]
        else:
            item = self.get_item(item_id)

        item_data = {
            "name": item["name"],
            "login": item["login"],
            "url": item["url"],
            "description": item["description"],
        }

        code = None
        link_key_hash = None
        link_key_encrypted = None
        if self.is_encrypt:
            code = generate_key()
            encrypted_key = get_encryption_key(
                item["vaultMasterKeyEncrypted"],
                item["keyEncrypted"],
                self.user_private_key
            )

            link_key_hash = get_hash(code)
            link_key_encrypted = encrypt_aes(code, encrypted_key)
            vault = self.get_vault(item["vaultId"])
            vault_password = self.get_vault_password(vault)
            self.encrypt_item(item, code, vault_password)
            if "passwordEncrypted" in item:
                item_data["passwordEncrypted"] = item["passwordEncrypted"]

            if "attachments" in item and len(item["attachments"]) > 0:
                link_attachments = []
                for attachment in item.get("attachments"):
                    key = decrypt_aes(attachment["encryptedKey"], encrypted_key)
                    link_attachments.append({"id": attachment["id"], "name": attachment["name"], "encryptedKey": encrypt_aes(key, code)})

                item_data["attachments"] = link_attachments
        else:
            item_data["passwordEncrypted"] = item["passwordEncrypted"]
            item_data["attachments"] = item["attachments"]

        self.encrypt_item_customs(item, code)
        if "customs" in item and len(item["customs"]) > 0:
            item_data["customs"] = item["customs"]

        payload = {
            "itemId": item['id'],
            "itemData": item_data,
            "keyHash": link_key_hash,
            "keyEncrypted": link_key_encrypted,
            "type": type,
            "expirationTime" : expiration_time
        }

        if shortcut_id:
            payload["shortcutId"] = shortcut_id

        response = self.call("POST", "/api/v1/links", payload)

        url = response["url"]
        if code:
            url = url + f"#code={code}"
        return url
