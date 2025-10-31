#!/usr/bin/env python3
from abc import ABC, abstractmethod

class PassworkCommand(ABC):
    """
    Abstract base class for Passwork CLI command strategies.
    """
    @abstractmethod
    def execute(self, client, args):
        """
        Execute the command strategy.
        
        Args:
            client (PassworkClient): Initialized Passwork client
            args (Namespace): Command line arguments
            
        Returns:
            int: Exit code
        """
        pass

    @staticmethod
    def add_command(subparsers):
        pass

    @staticmethod
    def base_params():
        return {
            "--host": {"help": "Passwork API host URL"},
            "--token": {"help": "Passwork access token"},
            "--refresh-token": {"help": "Passwork refresh token"},
            "--master-key": {"help": "Passwork master key for decryption"},
            "--no-ssl-verify": {"action": "store_true", "help": "Disable SSL certificate verification"},
        }

class ItemBaseCommand:
    def _get_password(self, client, args):
        """
        Get password based on the provided arguments.

        Strategy: If password_id is provided, get a single password
        If shortcut_id is provided, get a single password

        Returns:
            dict: password object or shortcut object
        """
        # Case 1: Password ID
        if hasattr(args, 'password_id') and args.password_id:
            # Trim the parameter
            password_id = args.password_id.strip()
            if not password_id:
                return {}

            # Single ID
            return client.get_item(password_id)

        # Case 1: Shortcut ID(s)
        if hasattr(args, 'shortcut_id') and args.shortcut_id:
            # Trim the parameter
            shortcut_id = args.shortcut_id.strip()
            if not shortcut_id:
                return {}

            # Single ID
            shortcut = client.get_shortcut(shortcut_id)
            if shortcut['password']:
                return shortcut['password']

            return {}

        raise ValueError("No password ID or shortcut ID criteria provided")