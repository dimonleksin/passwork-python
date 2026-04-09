#!/usr/bin/env python3
import sys
from .base import PassworkCommand, ItemBaseCommand
from passwork_client.utils import generate_totp, generate_totp_by_url


class GetCommandStrategy(PassworkCommand, ItemBaseCommand):

    def execute(self, client, args):
        try:
            # Get passwords based on provided parameters
            password = self._get_password(client, args)
            if not password:
                print("Error: Password not found", file=sys.stderr)
                return 1

            if args.totp_code:
                secret = self._extract_field(password, args.totp_code)
                if not secret:
                    print("Error: TOTP secret not found", file=sys.stderr)
                    return 1

                print(self._generate_totp(secret))
                return 0

            if args.field:
                print(self._extract_field(password, args.field))
            else:

                if "password" in password and password["password"]:
                    print(password["password"])
                else:
                    print("The password is not filled in or is empty", file=sys.stderr)
                    return 1

            return 0

        except Exception as e:
            print(f"Error getting password command: {e}", file=sys.stderr)
            return 1

    def _extract_field(self, data, field_name):
        customs = data.get("customs") or []
        if customs:
            for custom in customs:
                if custom["name"] == field_name:
                    return custom["value"]

        if field_name in data:
            return data[field_name]

        # Field not found
        return None

    def _generate_totp(self, secret: str):

        if "otpauth://" in secret.lower():
            return generate_totp_by_url(secret)

        return generate_totp(secret)

    @staticmethod
    def add_command(subparsers):
        parser = subparsers.add_parser("get", help="Get password/shortcut from Passwork")

        params = PassworkCommand.base_params() | {
            "--field": {"help": "Show item field"},
            "--totp-code": {"help": "Returned TOTP code"}
        }
        for key, value in params.items():
            parser.add_argument(key, **value)

        group_param = {
            "--password-id": {"help": "ID of password to retrieve"},
            "--shortcut-id": {"help": "ID of shortcut to retrieve"},
        }

        group = parser.add_argument_group("Password identification (at least one required)")
        for key, value in group_param.items():
            group.add_argument(key, **value)
