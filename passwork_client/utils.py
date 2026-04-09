import os
import base64
import hashlib
import hmac
import time
import struct
from pathlib import Path
from .crypto import encrypt_aes, generate_string, decrypt_aes, rsa_decrypt


def is_valid_totp(totp_value: str):
    return True


def validate_item_customs(customs: list):
    if any(f["type"] == "totp" and not is_valid_totp(f["value"]) for f in customs):
        raise Exception({"code": "invalidTotpFormat"})


def encrypt_item_customs(custom_fields: dict, encryption_key: str):
    encrypted_fields = []
    for custom in custom_fields:
        encrypted_custom = {}
        for field, value in custom.items():
            if field not in ["name", "value", "type"]:
                encrypted_custom[field] = value  # Preserve these fields without encryption
            else:
                encrypted_custom[field] = encrypt_aes(value, encryption_key)
        encrypted_fields.append(encrypted_custom)
    return encrypted_fields


def format_item_attachments(attachments: list, encryption_key: str):
    result = []
    for attachment in attachments:
        path, name = attachment["path"], attachment["name"]
        if not path:
            continue

        file_buffer = read_file(path)

        result.append(
            {
                **encrypt_item_attachment(file_buffer, encryption_key),
                "name": name if name else Path(path).stem,
            }
        )
    return result


def encrypt_item_attachment(buffer: bytes, encryption_key: str):
    if len(buffer) > 1024 * 1024 * 5:
        raise ValueError("Attached file max size is 5MB")

    if encryption_key:
        key = generate_string(length=100)
        encrypted_key = encrypt_aes(key, encryption_key)
        encrypted_data = encode_attachment_file(buffer, key)
    else:
        key = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        encrypted_key = base64.b64encode(key.encode()).decode()
        encrypted_data = encode_attachment_file(buffer)

    blob_string = get_string_from_blob(buffer)
    computed_hash = hashlib.sha256(blob_string.encode()).hexdigest()
    return {
        "encryptedKey": encrypted_key,
        "encryptedData": encrypted_data,
        "hash": computed_hash,
    }


def encode_attachment_file(data: bytes, encryption_key: str | None = None):
    if encryption_key is None:
        return base64.b64encode(base64.b64encode(data)).decode()
    else:
        return encrypt_aes(base64.b64encode(data), encryption_key, True)


def get_string_from_blob(blob: bytes):
    result = "".join([chr(byte) for byte in blob])
    return result


def read_file(filepath: str):
    with open(filepath, "rb") as file:
        return file.read()


def get_encryption_key(vault_master_key_encrypted: str, key_encrypted: str, user_private_key: str) -> str:
    vault_master_key = rsa_decrypt(vault_master_key_encrypted, user_private_key).decode()
    return decrypt_aes(key_encrypted, vault_master_key)


def decrypt_item(password_encrypted: str, encrypted_key: str) -> str:
    if encrypted_key:
        return decrypt_aes(password_encrypted, encrypted_key)
    else:
        return base64.b64decode(password_encrypted.encode()).decode('utf-8')


def decrypt_item_attachments(attachment: dict, encrypted_key: str) -> str:
    return decrypt_aes(attachment["encryptedKey"], encrypted_key)


def decrypt_item_customs(custom: dict, password_key: str):
    if password_key:
        custom["name"] = decrypt_aes(custom["name"], password_key)
        custom["type"] = decrypt_aes(custom["type"], password_key)
        custom["value"] = decrypt_aes(custom["value"], password_key)
    else:
        custom["name"] = base64.b64decode(custom["name"].encode()).decode('utf-8')
        custom["type"] = base64.b64decode(custom["type"].encode()).decode('utf-8')
        custom["value"] = base64.b64decode(custom["value"].encode()).decode('utf-8')


def decrypt_and_save_item_attachment(attachment: dict, encrypted_key: str, download_path: str):
    if not attachment:
        return None

    if (encrypted_key):
        key = decrypt_aes(attachment["encryptedKey"], encrypted_key)
        byte_data = decode_file(attachment["encryptedData"], key)
    else:
        byte_data = decode_file(attachment["encryptedData"], encrypted_key)

    blob_string = get_string_from_blob(byte_data)
    computed_hash = hashlib.sha256(blob_string.encode()).hexdigest()

    if computed_hash != attachment["hash"]:
        raise Exception("Can't decrypt attachment: hashes are not equal")

    save_attachment(byte_data, attachment["name"], download_path)


def decode_file(data: str, encrypted_key: str | None = None):
    if not encrypted_key:
        decoded_data = base64.b64decode(base64.b64decode(data))
    else:
        decoded_data = base64.b64decode(decrypt_aes(data, encrypted_key, is_bytes=True))
    return decoded_data


def save_attachment(byte_data_content: bytes, filename: str, download_path: str):
    Path(download_path).mkdir(parents=True, exist_ok=True)
    download_path = os.path.join(download_path, filename)
    with open(download_path, "wb") as file:
        file.write(byte_data_content)


def generate_totp(secret: str, algorithm: object = hashlib.sha1, interval=30, digits=6):
    # Decode the base32 secret to bytes
    # Standard base32 decoding requires padding, which is assumed here.
    # For a robust solution, consider a more complete base32 decoder.
    secret_bytes = base64.b32decode(secret + "=" * ((8 - len(secret) % 8) % 8))

    # Get the current time step
    current_time = int(time.time())
    time_step = current_time // interval

    # Convert the time step to bytes (8-byte big-endian)
    time_step_bytes = struct.pack(">Q", time_step)

    # Calculate HMAC-SHA1 hash
    hmac_hash = hmac.new(secret_bytes, time_step_bytes, algorithm).digest()

    # Dynamic Truncation
    offset = hmac_hash[-1] & 0x0F
    truncated_hash = struct.unpack(">I", hmac_hash[offset:offset + 4])[0] & 0x7FFFFFFF

    # Generate the TOTP code
    totp_code = str(truncated_hash % (10 ** digits)).zfill(digits)
    return totp_code


def generate_totp_by_url(uri: str):
    # Secret (to be filled in later)
    secret = None

    # Data we'll parse to the correct constructor
    otp_data = {}

    parsed_uri = parse_url(uri)
    if parsed_uri["scheme"] != "otpauth":
        raise ValueError("Not an otpauth URI")

    # Parse values
    for key, value in parse_query(parsed_uri["query"]).items():
        if key == "secret":
            secret = value
        elif key == "algorithm":
            if value == "SHA1":
                otp_data["algorithm"] = hashlib.sha1
            elif value == "SHA256":
                otp_data["algorithm"] = hashlib.sha256
            elif value == "SHA512":
                otp_data["algorithm"] = hashlib.sha512
            else:
                raise ValueError("Invalid value for algorithm, must be SHA1, SHA256 or SHA512")
        elif key == "digits":
            digits = int(value)
            otp_data["digits"] = digits
        elif key == "period":
            otp_data["interval"] = int(value)

    if not secret:
        raise ValueError("No secret found in URI")

    # Create objects
    if parsed_uri["netloc"] == "totp":
        return generate_totp(secret, **otp_data)

    raise ValueError("Not a supported OTP type")


def parse_url(url: str):
    scheme = None
    netloc = None
    path = None
    query = None
    fragment = None

    # Extract scheme
    scheme_end = url.find("://")
    if scheme_end != -1:
        scheme = url[:scheme_end]
        url = url[scheme_end + 3:]

    # Extract fragment
    fragment_start = url.find("#")
    if fragment_start != -1:
        fragment = url[fragment_start + 1:]
        url = url[:fragment_start]

    # Extract query
    query_start = url.find("?")
    if query_start != -1:
        query = url[query_start + 1:]
        url = url[:query_start]

    # Extract netloc and path
    path_start = url.find("/")
    if path_start != -1:
        netloc = url[:path_start]
        path = url[path_start:]
    else:
        # If no path, the rest is netloc
        netloc = url

    return {
        "scheme": scheme,
        "netloc": netloc,
        "path": path,
        "query": query,
        "fragment": fragment,
    }


def parse_query(query_string):
    """
    Parses a URL query string into a dictionary without using external libraries.
    Handles basic key-value pairs and URL-decoded values.
    """
    params = {}
    if not query_string:
        return params

    # Split by '&' to get individual key-value pairs
    pairs = query_string.split('&')

    for pair in pairs:
        # Split by '=' to separate key and value
        # Use 1 to handle values with '='
        parts = pair.split('=', 1)
        key = parts[0]
        value = parts[1] if len(parts) > 1 else ''

        # Basic URL decoding (you might need a more robust implementation for complex cases)
        key = key.replace('+', ' ').replace('%20', ' ')
        value = value.replace('+', ' ').replace('%20', ' ')

        params[key] = value
    return params
