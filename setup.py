#!/usr/bin/env python3
"""
Setup script for Audiobookshelf Downloader
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def setup_api_keys():
    """Setup API keys using the new management system."""
    print("\n🔑 API Key Setup")
    print("=" * 30)
    print("We'll help you set up secure API key storage.")
    print("You can add multiple keys for different Audiobookshelf servers.")

    try:
        from api_key_manager import APIKeyManager
        manager = APIKeyManager()

        # Check if keys already exist
        existing_keys = manager.list_keys()
        if existing_keys:
            print(f"\n📋 Found {len(existing_keys)} existing API keys:")
            for key in existing_keys:
                print(f"  - {key['name']} ({key['server_url']})")

            choice = input("\nAdd another key? (y/N): ").strip().lower()
            if choice != 'y':
                print("✅ Using existing API keys!")
                return True

        # Add new key
        print("\n➕ Adding New API Key")
        print("-" * 25)

        name = input("Enter a name for this server (e.g., 'home', 'work'): ").strip()
        if not name:
            print("❌ Name is required!")
            return False

        server_url = input("Enter server URL (e.g., audiobooks.example.com or https://audiobooks.example.com): ").strip()
        if not server_url:
            print("❌ Server URL is required!")
            return False

        # Automatically add https:// if not provided
        if not server_url.startswith(('http://', 'https://')):
            server_url = f"https://{server_url}"
            print(f"🔧 Added https:// prefix: {server_url}")

        print("\n🔑 Getting API Key:")
        print("1. Open your Audiobookshelf web interface")
        print("2. Go to Settings → API Keys")
        print("3. Create a new API key")
        print("4. Copy the key (it's only shown once!)")

        api_key = input("\nEnter API key: ").strip()
        if not api_key:
            print("❌ API key is required!")
            return False

        if manager.add_key(name, server_url, api_key):
            print(f"\n✅ Successfully added '{name}'!")
            test = input("Test connection now? (y/N): ").strip().lower()
            if test == 'y':
                manager._test_connection(name)
            return True
        else:
            return False

    except ImportError:
        print("❌ API key manager not available. Using legacy setup...")
        return print_api_key_instructions_legacy()

def print_api_key_instructions_legacy():
    """Print step-by-step instructions for getting an API key (legacy method)."""
    print("\n🔑 How to Get Your Audiobookshelf API Key")
    print("=" * 50)

    print("\n📋 Step-by-Step Instructions:")
    print("\n1. 🌐 Open your Audiobookshelf web interface")
    print("   (Usually: http://your-server-ip:port or https://your-domain.com)")

    print("\n2. 🔐 Log in with your username and password")

    print("\n3. ⚙️  Go to Settings")
    print("   (Look for a gear icon or 'Settings' in the menu)")

    print("\n4. 🔑 Click on 'API Keys'")
    print("   (This might be a tab or section)")

    print("\n5. ➕ Click 'Create API Key' or 'Add New'")
    print("   - Name: 'Bulk Download Script' (or any name you like)")
    print("   - User: Select your user account")
    print("   - Expiration: Leave blank for no expiration (or set a date)")
    print("   - Save the key")


    print("\n6. 📋 COPY THE API KEY IMMEDIATELY!")
    print("   ⚠️  WARNING: The key is only shown once!")
    print("   ⚠️  Copy it now and save it somewhere safe!")

    print("\n7. 🔧 Update your config.py file:")
    print("    - Open config.py in a text editor")
    print("    - Replace 'your_api_key_here' with your actual API key")
    print("    - Replace 'https://your-audiobookshelf-server.com' with your server URL")

    print("\n" + "=" * 50)
    print("💡 Tips:")
    print("- Keep your API key secure and don't share it")
    print("- If you lose the key, you'll need to create a new one")
    print("- The API key acts as your password, so treat it carefully")
    print("- You can create multiple API keys for different purposes")
    return True

def check_config():
    """Check if configuration is set up."""
    print("\n🔧 Checking configuration...")

    # First check if we have API keys stored
    try:
        from api_key_manager import APIKeyManager
        manager = APIKeyManager()
        keys = manager.list_keys()
        if keys:
            print(f"✅ Found {len(keys)} stored API keys!")
            return True
    except ImportError:
        pass

    # No configuration found
    print("⚠️  No API keys configured yet.")
    print("   Please set up API keys using the setup process.")
    return False

def main():
    """Main setup function."""
    print("🎧 Audiobookshelf Downloader Setup")
    print("=" * 40)

    # Install requirements
    if not install_requirements():
        return

    # Check configuration
    config_ok = check_config()

    if not config_ok:
        print("\n🔧 Configuration Setup Required")
        print("-" * 35)

        # Setup API keys using new system
        if setup_api_keys():
            print("\n✅ Setup Complete!")
            print("\nPress Enter to return to the main menu where you can:")
            print("  • Test your connection")
            print("  • Manage API keys")
            print("  • Download audiobooks")
        else:
            print("\n⚠️  Setup incomplete.")
            print("\nPress Enter to return to the main menu where you can:")
            print("  • Manage API keys")
            print("  • Test your connection")

        input("\nPress Enter to continue...")
    else:
        print("\n✅ Configuration looks good!")
        print("\nPress Enter to return to the main menu where you can:")
        print("  • Test your connection")
        print("  • Manage API keys")
        print("  • Download audiobooks")

    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled!")
        sys.exit(0)
