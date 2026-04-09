#!/usr/bin/env python3
import sys
import argparse
import shlex
import urllib3
from .utils import get_client_from_args, get_value_from_args_or_env
from .commands import COMMAND_STRATEGIES

# Suppress SSL certificate verification warnings
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)


class PassworkArgumentParser(argparse.ArgumentParser):
    """Custom argument parser that stops on first unrecognized argument."""
    def parse_known_args(self, args=None, namespace=None):
        # Parse only the known arguments, leave the rest for command
        return super().parse_known_args(args, namespace)


def main():
    """Main entry point for the Passwork CLI."""
    # Create the main parser
    parser = PassworkArgumentParser(
        description="Passwork CLI - Command line interface for Passwork password manager"
    )

    # Create subparsers for different modes
    subparsers = parser.add_subparsers(dest="command", help="Command mode")

    for strategy in COMMAND_STRATEGIES.values():
        strategy.add_command(subparsers)

    args, remaining = parser.parse_known_args()

    # Handle command for exec mode (Docker-like syntax)
    if args.command == "exec":
        if args.cmd and remaining:
            print("Error: Cannot use both --cmd and direct command at the same time", file=sys.stderr)
            sys.exit(1)
        elif remaining:
            # Join the remaining arguments as the command to execute
            args.cmd = " ".join(shlex.quote(arg) for arg in remaining)
        elif not args.cmd:
            print("Error: No command specified. Use --cmd or append command directly", file=sys.stderr)
            sys.exit(1)

    if args.command == "update":
        # Custom parsing for --custom-* arguments
        args.customs = []
        i = 0
        while i < len(remaining):
            if remaining[i].startswith("--custom-"):
                field_name = remaining[i][len("--custom-"):]
                if "=" in field_name:
                    args.customs.append({"name": field_name[:field_name.find("=")], "value": field_name[field_name.find("=") + 1:], "type": "password"})
                    i += 1
                elif i + 1 < len(remaining):
                    args.customs.append({"name": field_name, "value": remaining[i + 1], "type": "password"})
                    i += 2
                else:
                    print(f"Error: Missing value for custom field {field_name}", file=sys.stderr)
                    sys.exit(1)
            else:
                i += 1

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # Get values from args or environment variables
        args.host = get_value_from_args_or_env(args.host, "PASSWORK_HOST", required=True)
        args.token = get_value_from_args_or_env(args.token, "PASSWORK_TOKEN", required=True)
        args.refresh_token = get_value_from_args_or_env(args.refresh_token, "PASSWORK_REFRESH_TOKEN", required=False)
        args.master_key = get_value_from_args_or_env(args.master_key, "PASSWORK_MASTER_KEY", required=False)

        # Initialize the client
        client = get_client_from_args(args)

        # Create the strategy based on the command
        strategy_class = COMMAND_STRATEGIES.get(args.command)
        if not strategy_class:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            sys.exit(1)

        strategy = strategy_class()

        # Execute the strategy
        exit_code = strategy.execute(client, args)
        sys.exit(exit_code)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
