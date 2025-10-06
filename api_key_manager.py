#!/usr/bin/env python3
"""
API Key Management for Audiobookshelf Downloader

Manages multiple API keys for different Audiobookshelf servers using environment variables.
"""

import os
import sys
import json
import base64
import getpass
from typing import Dict, List, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from config import DOWNLOAD_PATH

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    print("⚠️  Warning: keyring not available. Using hardware ID only for encryption.")


class APIKeyManager:
    def __init__(self, config_file: str = ".audiobookshelf_keys"):
        self.config_file = config_file
        self.keys = {}
        self.load_keys()

    def _get_encryption_key(self) -> bytes:
        """Generate encryption key from user password + hardware ID."""
        # Get hardware identifier
        hardware_id = self._get_system_identifier()

        # Get or create master password
        master_password = self._get_master_password()

        # Combine password + hardware ID for maximum security
        combined_secret = f"{master_password}:{hardware_id}"
        salt = b'audiobookshelf_hybrid_2024'  # New salt for hybrid method

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(combined_secret.encode()))
        return key

    def _get_master_password(self) -> str:
        """Get master password from keychain or prompt user to create one."""
        service_name = "audiobookshelf-downloader"
        username = "master-key"

        if KEYRING_AVAILABLE:
            try:
                # Try to get existing password from keychain
                stored_password = keyring.get_password(service_name, username)
                if stored_password:
                    return stored_password
            except Exception as e:
                print(f"⚠️  Warning: Could not access keychain: {e}")

        # No stored password found, create new one
        print("\n🔐 Setting up master password for API key encryption")
        print("This password will be stored securely in your OS keychain and combined")
        print("with your hardware ID to encrypt your API keys.")
        print()

        while True:
            password = getpass.getpass("Enter master password (8+ characters): ")
            if len(password) < 8:
                print("❌ Password must be at least 8 characters long")
                continue

            confirm = getpass.getpass("Confirm master password: ")
            if password != confirm:
                print("❌ Passwords don't match")
                continue

            break

        # Store in keychain if available
        if KEYRING_AVAILABLE:
            try:
                keyring.set_password(service_name, username, password)
                print("✅ Master password stored securely in OS keychain")
            except Exception as e:
                print(f"⚠️  Warning: Could not store in keychain: {e}")
                print("⚠️  You'll need to enter this password each time")
        else:
            print("⚠️  Keychain not available - you'll need to enter this password each time")

        return password

    def _prompt_master_password(self) -> str:
        """Prompt for master password when keychain is not available."""
        print("\n🔐 Enter master password to decrypt API keys")
        return getpass.getpass("Master password: ")

    def _get_system_identifier(self) -> str:
        """Get a unique system identifier using secure fallbacks."""
        import platform
        import subprocess

        # Priority 1: Hardware UUID (macOS/Windows)
        try:
            if platform.system() == 'Darwin':  # macOS
                result = subprocess.run(['system_profiler', 'SPHardwareDataType'],
                                      capture_output=True, text=True, timeout=5)
                for line in result.stdout.split('\n'):
                    if 'Hardware UUID:' in line:
                        uuid = line.split(':')[1].strip()
                        return f"hw_uuid:{uuid}"
            elif platform.system() == 'Windows':
                result = subprocess.run(['wmic', 'csproduct', 'get', 'UUID'],
                                      capture_output=True, text=True, timeout=5)
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    uuid = lines[1].strip()
                    return f"hw_uuid:{uuid}"
        except Exception:
            pass

        # Priority 2: Machine ID (Linux/some Unix systems)
        try:
            machine_id_paths = ['/etc/machine-id', '/var/lib/dbus/machine-id']
            for path in machine_id_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        machine_id = f.read().strip()
                        if machine_id:
                            return f"machine_id:{machine_id}"
        except Exception:
            pass

        # No hardware identifier available - require user-generated system key
        return self._get_or_create_system_key()

    def _get_or_create_system_key(self) -> str:
        """Get or create a user-generated system key when hardware ID is not available."""
        service_name = "audiobookshelf-downloader"
        system_key_username = "system-identifier"

        if KEYRING_AVAILABLE:
            try:
                # Try to get existing system key from keychain
                stored_key = keyring.get_password(service_name, system_key_username)
                if stored_key:
                    return f"system_key:{stored_key}"
            except Exception as e:
                print(f"⚠️  Warning: Could not access keychain: {e}")

        # No stored system key found, create new one
        print("\n🔐 Hardware identifier not available on this system")
        print("Creating a unique system identifier for encryption...")
        print("This will be stored securely in your OS keychain.")
        print()

        while True:
            system_key = getpass.getpass("Enter system identifier password (12+ characters): ")
            if len(system_key) < 12:
                print("❌ System identifier must be at least 12 characters long")
                continue

            confirm = getpass.getpass("Confirm system identifier: ")
            if system_key != confirm:
                print("❌ System identifiers don't match")
                continue

            break

        # Store in keychain if available
        if KEYRING_AVAILABLE:
            try:
                keyring.set_password(service_name, system_key_username, system_key)
                print("✅ System identifier stored securely in OS keychain")
            except Exception as e:
                print(f"❌ Error: Could not store in keychain: {e}")
                print("❌ This system cannot securely store the identifier.")
                raise ValueError("Cannot create secure system identifier without keychain access")
        else:
            print("❌ Error: Keychain not available on this system")
            print("❌ Cannot securely store system identifier.")
            raise ValueError("Cannot create secure system identifier without keychain access")

        return f"system_key:{system_key}"

    def _encrypt_key(self, api_key: str) -> str:
        """Encrypt API key for storage."""
        try:
            fernet = Fernet(self._get_encryption_key())
            encrypted_key = fernet.encrypt(api_key.encode())
            return base64.urlsafe_b64encode(encrypted_key).decode()
        except Exception as e:
            # Fail securely - don't use insecure fallback
            raise ValueError(f"Failed to encrypt API key. This indicates a system configuration issue. Error: {e}")

    def _decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt API key from storage."""
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                fernet = Fernet(self._get_encryption_key())
                encrypted_data = base64.urlsafe_b64decode(encrypted_key.encode())
                decrypted_key = fernet.decrypt(encrypted_data)
                return decrypted_key.decode()
            except Exception as e:
                if attempt < max_attempts - 1:
                    print(f"❌ Decryption failed: {e}")
                    print("This might be due to an incorrect master password.")

                    # Clear cached password and try again
                    if KEYRING_AVAILABLE:
                        try:
                            # Force re-prompt by temporarily clearing keychain
                            service_name = "audiobookshelf-downloader"
                            username = "master-key"
                            stored = keyring.get_password(service_name, username)
                            if stored:
                                print("🔐 Please re-enter your master password")
                                new_password = self._prompt_master_password()
                                # Temporarily use the new password
                                keyring.set_password(service_name, username, new_password)
                        except Exception:
                            pass
                else:
                    # Final attempt failed
                    raise ValueError(f"Failed to decrypt API key after {max_attempts} attempts. "
                                   f"This may be due to wrong master password, different system, or corrupted data. "
                                   f"Error: {e}")

        # Should never reach here
        raise ValueError("Unexpected decryption failure")

    def load_keys(self):
        """Load API keys from config file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.keys = data.get('keys', {})
            except Exception as e:
                print(f"⚠️  Warning: Could not load API keys: {e}")
                self.keys = {}

    def save_keys(self):
        """Save API keys to config file."""
        try:
            data = {
                'keys': self.keys,
                'version': '1.0'
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            # Set restrictive permissions on the config file
            os.chmod(self.config_file, 0o600)
        except Exception as e:
            print(f"❌ Error saving API keys: {e}")

    def add_key(self, name: str, server_url: str, api_key: str, download_path: str = None) -> bool:
        """Add a new API key."""
        if not name or not server_url or not api_key:
            print("❌ Name, server URL, and API key are required")
            return False

        # Clean up server URL
        server_url = server_url.rstrip('/')
        if not server_url.startswith(('http://', 'https://')):
            server_url = f"https://{server_url}"

        encrypted_key = self._encrypt_key(api_key)
        self.keys[name] = {
            'server_url': server_url,
            'api_key': encrypted_key,
            'download_path': download_path or DOWNLOAD_PATH,
            'created_at': self._get_timestamp()
        }

        self.save_keys()
        print(f"✅ Added API key '{name}' for server: {server_url}")
        return True

    def get_key(self, name: str) -> Optional[Tuple[str, str, str]]:
        """Get server URL, API key, and download path by name."""
        if name not in self.keys:
            return None

        key_data = self.keys[name]
        server_url = key_data['server_url']
        api_key = self._decrypt_key(key_data['api_key'])
        download_path = key_data.get('download_path', DOWNLOAD_PATH)

        return server_url, api_key, download_path

    def list_keys(self) -> List[Dict[str, str]]:
        """List all stored API keys."""
        result = []
        for name, data in self.keys.items():
            result.append({
                'name': name,
                'server_url': data['server_url'],
                'download_path': data.get('download_path', DOWNLOAD_PATH),
                'created_at': data.get('created_at', 'Unknown')
            })
        return result

    def update_key(self, name: str, new_api_key: str = None, new_download_path: str = None) -> bool:
        """Update an existing API key and/or download path."""
        if name not in self.keys:
            print(f"❌ API key '{name}' not found")
            return False

        updated = False

        if new_api_key:
            self.keys[name]['api_key'] = self._encrypt_key(new_api_key)
            updated = True

        if new_download_path:
            self.keys[name]['download_path'] = new_download_path
            updated = True

        if updated:
            self.keys[name]['updated'] = self._get_timestamp()
            self.save_keys()
            print(f"✅ Updated '{name}'")
            return True
        else:
            print(f"❌ No changes made to '{name}'")
            return False

    def remove_key(self, name: str) -> bool:
        """Remove an API key."""
        if name not in self.keys:
            print(f"❌ API key '{name}' not found")
            return False

        del self.keys[name]
        self.save_keys()
        print(f"✅ Removed API key '{name}'")
        return True

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def interactive_setup(self):
        """Interactive setup for adding API keys."""
        print("\n" + "=" * 50)
        print("🔑 API Key Management")
        print("=" * 50)

        while True:
            print("\nChoose an option:")
            print("1. Add new API key")
            print("2. List existing keys")
            print("3. Update existing API key")
            print("4. Remove API key")
            print("5. Test connection with key")
            print("6. Exit")
            print("-" * 50)

            choice = input("\nEnter choice (1-6): ").strip()

            if choice == "1":
                self._add_key_interactive()
                print("\n" + "-" * 50)
            elif choice == "2":
                self._list_keys_interactive()
                print("\n" + "-" * 50)
            elif choice == "3":
                self._update_key_interactive()
                print("\n" + "-" * 50)
            elif choice == "4":
                self._remove_key_interactive()
                print("\n" + "-" * 50)
            elif choice == "5":
                self._test_key_interactive()
                print("\n" + "-" * 50)
            elif choice == "6":
                break
            else:
                print("❌ Invalid choice!")
                print("\n" + "-" * 50)

    def _update_key_interactive(self):
        """Interactive update key process."""
        print("\n🔄 Update Existing API Key")
        print("-" * 30)

        keys = self.list_keys()
        if not keys:
            print("❌ No API keys found to update!")
            return

        print("Available keys:")
        for i, key in enumerate(keys, 1):
            print(f"{i}. {key['name']} ({key['server_url']})")
            print(f"   Download Path: {key.get('download_path', DOWNLOAD_PATH)}")

        try:
            choice = int(input("\nEnter number to update: ")) - 1
            if 0 <= choice < len(keys):
                key_name = keys[choice]['name']
                current_download_path = keys[choice].get('download_path', DOWNLOAD_PATH)
                print(f"\nUpdating key: {key_name}")
                print(f"Current download path: {current_download_path}")

                # Ask what to update
                print("\nWhat would you like to update?")
                print("1. API Key only")
                print("2. Download Path only")
                print("3. Both API Key and Download Path")

                update_choice = input("Enter choice (1-3): ").strip()

                new_api_key = None
                new_download_path = None

                if update_choice in ['1', '3']:
                    # Get new API key
                    print("\n🔑 Getting New API Key:")
                    print("1. Open your Audiobookshelf web interface")
                    print("2. Go to Settings → Users → API Keys")
                    print("3. Create a new API key or copy existing one")
                    print("4. Copy the key (it's only shown once!)")

                    new_api_key = input("\nEnter new API key: ").strip()
                    if not new_api_key:
                        print("❌ API key is required!")
                        return

                if update_choice in ['2', '3']:
                    # Get new download path
                    new_download_path = input(f"\nEnter new download path (or press Enter for default: {DOWNLOAD_PATH}): ").strip()
                    if not new_download_path:
                        new_download_path = DOWNLOAD_PATH

                # Update the key
                if self.update_key(key_name, new_api_key, new_download_path):
                    print(f"✅ Successfully updated '{key_name}'!")

                    # Ask if user wants to test the updated key
                    if new_api_key:
                        test_now = input("Test connection now? (y/N): ").strip().lower()
                        if test_now == 'y':
                            self._test_connection(key_name)
                else:
                    print(f"❌ Failed to update '{key_name}'!")
            else:
                print("❌ Invalid choice!")
        except ValueError:
            print("❌ Invalid input!")

    def _add_key_interactive(self):
        """Interactive add key process."""
        print("\n➕ Add New API Key")
        print("-" * 25)

        name = input("Enter a name for this server (e.g., 'home', 'work'): ").strip()
        if not name:
            print("❌ Name is required!")
            return

        if name in self.keys:
            print(f"⚠️  Key '{name}' already exists!")
            overwrite = input("Overwrite? (y/N): ").strip().lower()
            if overwrite != 'y':
                return

        server_url = input("Enter server URL (e.g., audiobooks.example.com or https://audiobooks.example.com): ").strip()
        if not server_url:
            print("❌ Server URL is required!")
            return

        # Automatically add https:// if not provided
        if not server_url.startswith(('http://', 'https://')):
            server_url = f"https://{server_url}"
            print(f"🔧 Added https:// prefix: {server_url}")

        print("\n🔑 Getting API Key:")
        print("1. Open your Audiobookshelf web interface")
        print("2. Go to Settings → Users → API Keys")
        print("3. Create a new API key")
        print("4. Copy the key (it's only shown once!)")

        api_key = input("\nEnter API key: ").strip()
        if not api_key:
            print("❌ API key is required!")
            return

        # Ask for download path
        download_path = input(f"\nEnter download path (or press Enter for default: {DOWNLOAD_PATH}): ").strip()
        if not download_path:
            download_path = DOWNLOAD_PATH

        if self.add_key(name, server_url, api_key, download_path):
            print(f"\n✅ Successfully added '{name}'!")
            test = input("Test connection now? (y/N): ").strip().lower()
            if test == 'y':
                self._test_connection(name)

    def _list_keys_interactive(self):
        """Interactive list keys."""
        print("\n📋 Stored API Keys")
        print("-" * 20)

        keys = self.list_keys()
        if not keys:
            print("No API keys stored.")
            return

        for i, key in enumerate(keys, 1):
            print(f"{i}. {key['name']}")
            print(f"   Server: {key['server_url']}")
            print(f"   Download Path: {key.get('download_path', DOWNLOAD_PATH)}")
            print(f"   Added: {key['created_at']}")
            if 'updated' in key:
                print(f"   Updated: {key['updated']}")
            print()

    def _remove_key_interactive(self):
        """Interactive remove key."""
        print("\n🗑️  Remove API Key")
        print("-" * 20)

        keys = self.list_keys()
        if not keys:
            print("No API keys stored.")
            return

        print("Available keys:")
        for i, key in enumerate(keys, 1):
            print(f"{i}. {key['name']} ({key['server_url']})")

        try:
            choice = int(input("\nEnter number to remove: ")) - 1
            if 0 <= choice < len(keys):
                key_name = keys[choice]['name']
                confirm = input(f"Remove '{key_name}'? (y/N): ").strip().lower()
                if confirm == 'y':
                    self.remove_key(key_name)
            else:
                print("❌ Invalid choice!")
        except ValueError:
            print("❌ Invalid input!")

    def _test_key_interactive(self):
        """Interactive test key."""
        print("\n🧪 Test API Key")
        print("-" * 20)

        keys = self.list_keys()
        if not keys:
            print("No API keys stored.")
            return

        print("Available keys:")
        for i, key in enumerate(keys, 1):
            print(f"{i}. {key['name']} ({key['server_url']})")

        try:
            choice = int(input("\nEnter number to test: ")) - 1
            if 0 <= choice < len(keys):
                key_name = keys[choice]['name']
                self._test_connection(key_name)
            else:
                print("❌ Invalid choice!")
        except ValueError:
            print("❌ Invalid input!")

    def _test_connection(self, name: str):
        """Test connection with a specific key."""
        result = self.get_key(name)
        if not result:
            print(f"❌ Could not retrieve key '{name}'")
            return

        server_url, api_key, download_path = result
        if not server_url or not api_key:
            print(f"❌ Could not retrieve key '{name}'")
            return

        print(f"\n🔌 Testing connection to '{name}'...")

        try:
            import asyncio
            import logging
            from audiobookshelf_downloader import AudiobookshelfDownloader

            # Temporarily disable logging for cleaner output
            logging.getLogger().setLevel(logging.ERROR)

            async def test():
                async with AudiobookshelfDownloader(server_url, api_key) as downloader:
                    if await downloader.test_connection():
                        print("✅ Connection successful!")

                        # Get library info
                        libraries = await downloader.get_libraries()
                        if libraries:
                            print(f"📚 Found {len(libraries)} libraries:")
                            for lib in libraries:
                                lib_name = lib.get('name', 'Unknown')
                                lib_id = lib.get('id')

                                # Get book count for this library
                                try:
                                    # Get the total count from API response
                                    url = f"{downloader.server_url}/api/libraries/{lib_id}/items"
                                    params = {"limit": 1}  # Just get 1 item to get the total count

                                    async with downloader.session.get(url, headers=downloader._get_headers(), params=params) as response:
                                        if response.status == 200:
                                            data = await response.json()
                                            total_count = data.get('total', 0)
                                            print(f"  - {lib_name} ({total_count} books)")
                                        else:
                                            print(f"  - {lib_name}")
                                except:
                                    print(f"  - {lib_name}")
                        else:
                            print("📚 No libraries found")
                    else:
                        print("❌ Connection failed!")

            asyncio.run(test())

            # Restore logging level
            logging.getLogger().setLevel(logging.INFO)

        except Exception as e:
            print(f"❌ Error testing connection: {e}")

    def select_key_interactive(self) -> Optional[Tuple[str, str, str, str]]:
        """Interactive key selection."""
        keys = self.list_keys()
        if not keys:
            print("❌ No API keys stored. Run setup first!")
            return None

        if len(keys) == 1:
            # Only one key, use it automatically
            key = keys[0]
            result = self.get_key(key['name'])
            if result:
                server_url, api_key, download_path = result
                print(f"🔑 Using API key: {key['name']}")
                return key['name'], server_url, api_key, download_path
            else:
                print(f"❌ Could not retrieve key '{key['name']}'")
                return None

        print("\n🔑 Select API Key")
        print("-" * 20)
        print("Available keys:")
        for i, key in enumerate(keys, 1):
            print(f"{i}. {key['name']} ({key['server_url']})")

        try:
            choice = int(input("\nEnter number: ")) - 1
            if 0 <= choice < len(keys):
                key = keys[choice]
                result = self.get_key(key['name'])
                if result:
                    server_url, api_key, download_path = result
                    print(f"🔑 Selected: {key['name']}")
                    return key['name'], server_url, api_key, download_path
                else:
                    print(f"❌ Could not retrieve key '{key['name']}'")
                    return None
            else:
                print("❌ Invalid choice!")
                return None
        except ValueError:
            print("❌ Invalid input!")
            return None


def main():
    """Main function for API key management."""
    try:
        manager = APIKeyManager()
        manager.interactive_setup()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
