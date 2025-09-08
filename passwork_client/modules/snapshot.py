from ..utils import get_encryption_key, decrypt_and_save_item_attachment

class Snapshot:
    def get_snapshot(self, item_id: str, snapshot_id: str):
        snapshot_data = self.call("GET", f"/api/v1/items/{item_id}/snapshot/{snapshot_id}")

        encrypted_key = ''
        if self.is_encrypt:
            item_data = self.get_item(item_id)
            encrypted_key = get_encryption_key(
                item_data["vaultMasterKeyEncrypted"],
                snapshot_data["keyEncrypted"],
                self.user_private_key
            )

        self.decrypt_item(snapshot_data, encrypted_key)

        self.decrypt_item_customs(snapshot_data, encrypted_key)

        return snapshot_data

    def get_snapshot_attachment(self, snapshot_id: str, attachment_id: str):
         return self.call("GET", f"/api/v1/snapshots/{snapshot_id}/attachment/{attachment_id}")

    def download_snapshot_attachments(self, snapshot: dict, download_path: str):
        attachments = snapshot.get("attachments")

        attachments_data = []
        for attachment in attachments:
            attachments_data.append(self.get_snapshot_attachment(snapshot["id"], attachment["id"]))

        if not attachments_data:
            return None

        encrypted_key = ''
        if self.is_encrypt:
            item_data = self.get_item(snapshot["itemId"])
            encrypted_key = get_encryption_key(
                item_data["vaultMasterKeyEncrypted"],
                snapshot["keyEncrypted"],
                self.user_private_key
            )
        for attachment_data in attachments_data:
            decrypt_and_save_item_attachment(attachment_data, encrypted_key, download_path)