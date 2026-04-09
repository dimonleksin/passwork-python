#!/usr/bin/env python3
import sys
from .base import PassworkCommand, ItemBaseCommand


class UpdateCommandStrategy(PassworkCommand, ItemBaseCommand):

    def execute(self, client, args):

        try:
            # Get passwords based on provided parameters
            password = self._get_password(client, args)
            if not password:
                print("Error: No password found", file=sys.stderr)
                return 1
            # update password
            updated_data = self.parse_args(vars(args))

            updated_data = self.prepare_update_data(updated_data, password)
            if updated_data.get("name") and not bool(updated_data.get("name")):
                print("Error: The password name must not be empty.", file=sys.stderr)
                return 1

            client.update_item(password['id'], updated_data)
            return 0

        except Exception as e:
            print(f"Error updating password command: {e}", file=sys.stderr)
            return 1

    def prepare_update_data(self, data, password):
        filtered_results = {}
        for key, value in data.items():
            if value is not None:
                filtered_results[key] = value

        if data["customs"]:
            filtered_results["customs"] = self.prepare_customs_data(password["customs"], data["customs"])
        else:
            filtered_results["customs"] = password["customs"]

        filtered_results["vaultId"] = password["vaultId"]
        return filtered_results

    def prepare_customs_data(self, item_customs, customs):
        result = []
        for item_custom in item_customs:
            for i, custom in enumerate(customs):
                if item_custom["name"] == custom["name"]:
                    if item_custom["type"] == "password":
                        item_custom["value"] = custom["value"]
                    customs.pop(i)

            result.append(item_custom)

        result = result + customs
        return result

    def parse_args(self, args: dict):
        parse_args = {}
        parse_args["password"] = args.get("password", None)
        parse_args["name"] = args.get("name", None)
        parse_args["login"] = args.get("login", None)
        parse_args["url"] = args.get("url", None)
        parse_args["description"] = args.get("description", None)
        parse_args["customs"] = args["customs"] if args["customs"] else None

        if args["tags"] or args["tags"] is not None:
            tags = args["tags"]
            if ',' in tags:
                tag_list = [tag.strip() for tag in tags.split(',')]
                tag_list = [tag for tag in tag_list if tag]

                if tag_list:
                    parse_args["tags"] = tag_list
            else:
                tags = tags.strip()
                parse_args["tags"] = []
                if tags:
                    parse_args["tags"] = [tags]
        else:
            parse_args["tags"] = None

        return parse_args

    @staticmethod
    def add_command(subparsers):
        parser = subparsers.add_parser("update", help="Update password/shortcut from Passwork")

        params = PassworkCommand.base_params() | {
            "--name": {"help": "Password name"},
            "--password": {"help": "Password"},
            "--login": {"help": "Password login"},
            "--url": {"help": "Password url"},
            "--description": {"help": "Password description"},
            "--tags": {"help": "Password tags(comma-separated for multiple)"},
            "--custom-*": {"help": "Password customs fields. * - custom field name(example: --custom-test_password \"value\")", "metavar": "VALUE"}
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
