#!/usr/bin/env python3
"""
Main entry point for Audiobookshelf Downloader
"""

import sys
import os
import asyncio
from config import DOWNLOAD_PATH

def show_menu():
    """Show the main menu."""
    print("\n" + "=" * 60)
    print("🎧 Audiobookshelf Bulk Downloader")
    print("=" * 60)
    print("\nChoose an option:")
    print("1. 🔧 Setup (Configure Server + Get API Key)")
    print("2. 🔑 Manage API Keys")
    print("3. 🧪 Test Connection")
    print("4. 🎯 Select Books to Download")
    print("5. 🔄 Compare Servers (Find Missing Books)")
    print("6. 📥 Download All Books")
    print("0. ❌ Exit")
    print("-" * 60)


def run_setup():
    """Run setup only."""
    print("\n🔧 Setup")
    print("-" * 10)
    os.system("python setup.py")

def manage_api_keys():
    """Manage API keys."""
    print("\n🔑 Manage API Keys")
    print("-" * 25)
    result = os.system("python api_key_manager.py")
    # If the user exited normally (choice 6), don't show the continue prompt
    return result == 0


def test_connection():
    """Test connection."""
    print("\n🧪 Test Connection")
    print("-" * 20)
    result = os.system("python tests/test_connection.py")
    # If the user exited normally (choice 3), don't show the continue prompt
    return result == 0

def download_books():
    """Download all books."""
    print("\n📥 Download All Books")
    print("-" * 25)

    # Check if we have stored API keys with download paths
    try:
        from api_key_manager import APIKeyManager
        manager = APIKeyManager()
        keys = manager.list_keys()

        if keys:
            print("🔑 Using stored API key configuration...")
            # Use stored configuration (download path is included)
            os.system("python audiobookshelf_downloader.py")
        else:
            # No stored keys, ask for download path
            download_path = input(f"Enter download path (or press Enter for default: {DOWNLOAD_PATH}): ").strip()
            if download_path:
                os.system(f"python audiobookshelf_downloader.py --download-path '{download_path}'")
            else:
                os.system("python audiobookshelf_downloader.py")
    except ImportError:
        # Fallback to asking for download path
        download_path = input(f"Enter download path (or press Enter for default: {DOWNLOAD_PATH}): ").strip()
        if download_path:
            os.system(f"python audiobookshelf_downloader.py --download-path '{download_path}'")
        else:
            os.system("python audiobookshelf_downloader.py")

def select_books():
    """Select books to download."""
    print("\n🎯 Select Books to Download")
    print("-" * 30)

    # Check if we have stored API keys with download paths
    try:
        from api_key_manager import APIKeyManager
        manager = APIKeyManager()
        keys = manager.list_keys()

        if keys:
            print("🔑 Using stored API key configuration...")
            # Use stored configuration (download path is included)
            os.system("python book_selector.py")
        else:
            # No stored keys, ask for download path
            download_path = input(f"Enter download path (or press Enter for default: {DOWNLOAD_PATH}): ").strip()
            if download_path:
                os.system(f"python book_selector.py --download-path '{download_path}'")
            else:
                os.system("python book_selector.py")
    except ImportError:
        # Fallback to asking for download path
        download_path = input(f"Enter download path (or press Enter for default: {DOWNLOAD_PATH}): ").strip()
        if download_path:
            os.system(f"python book_selector.py --download-path '{download_path}'")
        else:
            os.system("python book_selector.py")



async def open_book_selector_for_missing(server, missing_books, title, library_id=None):
    """Open the interactive book selector for missing books."""
    try:
        from book_selector import BookSelector

        print(f"\n🔍 {title}")
        print("=" * 50)
        print(f"📚 Found {len(missing_books)} missing books")
        print("🎯 Use the book selector to view details, filter, and select books to download")
        print()

        # Extract the actual book data from the missing books structure
        # missing_books has format: [{'book': actual_book_data, 'library_id': ..., 'library_name': ...}, ...]
        # book selector expects: [actual_book_data, ...]
        books_for_selector = []
        for item in missing_books:
            if isinstance(item, dict) and 'book' in item:
                books_for_selector.append(item['book'])
            else:
                # Fallback: assume it's already in the right format
                books_for_selector.append(item)

        # Create book selector with the extracted books
        selector = BookSelector(server, library_id)

        # Run the interactive selector with the properly formatted books
        await selector.select_books_interactive(books_for_selector)

    except Exception as e:
        print(f"❌ Error opening book selector: {e}")
        print("📋 Falling back to simple list:")
        for i, item in enumerate(missing_books, 1):
            # Handle both formats
            if isinstance(item, dict) and 'book' in item:
                book = item['book']
            else:
                book = item

            media = book.get('media', {})
            metadata = media.get('metadata', {})
            title = metadata.get('title', 'Unknown Title')
            author = metadata.get('authorName', 'Unknown Author')
            print(f"  {i}. {title} by {author}")
        input("\nPress Enter to continue...")


async def select_library_for_server(server, server_label: str):
    """Select a single library for the given server."""
    libraries = await server.get_libraries()
    if not libraries:
        print(f"❌ No libraries found on '{server_label}'")
        return None, None, None

    if len(libraries) == 1:
        library = libraries[0]
        print(
            f"📚 '{server_label}' library: {library.get('name', 'Unknown')} (ID: {library.get('id', 'Unknown')})"
        )
        return {library['id']}, library['id'], library.get('name', 'Unknown')

    print(f"\n📚 Libraries available on '{server_label}':")
    for idx, library in enumerate(libraries, 1):
        print(f"  {idx}. {library.get('name', 'Unknown')} (ID: {library.get('id', 'Unknown')})")

    while True:
        choice = input(f"Select library for '{server_label}' (1-{len(libraries)}): ").strip()
        try:
            choice_idx = int(choice) - 1
        except ValueError:
            print("❌ Invalid input! Enter the library number.")
            continue

        if 0 <= choice_idx < len(libraries):
            library = libraries[choice_idx]
            print(f"✅ Selected '{library.get('name', 'Unknown')}' on '{server_label}'")
            return {library['id']}, library['id'], library.get('name', 'Unknown')

        print("❌ Invalid choice! Please try again.")

async def run_server_comparison(source_key_name: str, target_key_name: str):
    """Run server comparison using stored API keys."""
    try:
        from api_key_manager import APIKeyManager
        from audiobookshelf_downloader import AudiobookshelfDownloader
        from server_diff import ServerDiff

        manager = APIKeyManager()

        # Get source server details
        source_url, source_key, source_download_path = manager.get_key(source_key_name)
        target_url, target_key, target_download_path = manager.get_key(target_key_name)

        print(f"\n🔌 Connecting to servers...")
        print(f"📥 Source: {source_url}")
        print(f"📊 Target: {target_url}")

        # Create server connections
        source_server = AudiobookshelfDownloader(source_url, source_key, source_download_path)
        target_server = AudiobookshelfDownloader(target_url, target_key, target_download_path)

        async with source_server, target_server:
            # Test connections
            print("🔍 Testing connections...")
            if not await source_server.test_connection():
                print("❌ Failed to connect to source server!")
                input("Press Enter to continue...")
                return

            if not await target_server.test_connection():
                print("❌ Failed to connect to target server!")
                input("Press Enter to continue...")
                return

            print("✅ Connected to both servers!")

            source_library_ids, source_preferred_library_id, source_library_name = await select_library_for_server(
                source_server,
                source_key_name,
            )
            if source_library_ids is None:
                input("Press Enter to continue...")
                return

            target_library_ids, target_preferred_library_id, target_library_name = await select_library_for_server(
                target_server,
                target_key_name,
            )
            if target_library_ids is None:
                input("Press Enter to continue...")
                return

            print(
                f"\n🎯 Comparing libraries:\n"
                f"  📥 Source ({source_key_name}): {source_library_name}\n"
                f"  📊 Target ({target_key_name}): {target_library_name}"
            )

            # Create diff tool and compare
            diff_tool = ServerDiff(
                source_server,
                target_server,
                source_library_ids=source_library_ids,
                target_library_ids=target_library_ids,
                source_preferred_library_id=source_preferred_library_id,
                target_preferred_library_id=target_preferred_library_id,
            )
            results = await diff_tool.compare_servers()

            # Print results
            diff_tool.print_comparison_results(results)

            # Handle missing books
            missing_in_target = results['missing_in_target']
            missing_in_source = results['missing_in_source']

            print(f"\n📊 Comparison Results:")
            print(f"📚 {source_key_name}: {results['source_total']} books")
            print(f"📚 {target_key_name}: {results['target_total']} books")

            # Calculate total common books
            primary_matches = len(results['common_books'])
            author_overlap = results.get('author_overlap_matches', 0)
            fallback = results.get('fallback_matches', 0)
            total_common = primary_matches + author_overlap + fallback

            print(f"📚 Common books: {total_common}")
            if author_overlap > 0 or fallback > 0:
                print(f"   ├─ Primary matches (author+title): {primary_matches}")
                if author_overlap > 0:
                    print(f"   ├─ Author overlap matches: {author_overlap}")
                if fallback > 0:
                    print(f"   └─ Fallback matches (title+duration+size): {fallback}")

            if not missing_in_target and not missing_in_source:
                print("✅ No missing books found! Servers are perfectly in sync.")

            if missing_in_target or missing_in_source or total_common:
                options = []

                if missing_in_target:
                    options.append(
                        (
                            'browse_missing_in_target',
                            f"Browse & select FROM '{source_key_name}' ({len(missing_in_target)} books missing in '{target_key_name}')",
                        )
                    )
                    options.append(
                        (
                            'download_missing_in_target',
                            f"Download ALL {len(missing_in_target)} books FROM '{source_key_name}' (missing in '{target_key_name}')",
                        )
                    )

                if missing_in_source:
                    options.append(
                        (
                            'browse_missing_in_source',
                            f"Browse & select FROM '{target_key_name}' ({len(missing_in_source)} books missing in '{source_key_name}')",
                        )
                    )
                    options.append(
                        (
                            'download_missing_in_source',
                            f"Download ALL {len(missing_in_source)} books FROM '{target_key_name}' (missing in '{source_key_name}')",
                        )
                    )

                if total_common:
                    match_label = f"View matched books ({total_common} total)"
                else:
                    match_label = "View matched books (none found)"
                options.append(('view_matches', match_label))
                options.append(('exit', "Exit"))

                while True:
                    print("\nWhat would you like to do?")
                    for idx, (_, label) in enumerate(options, 1):
                        print(f"{idx}. {label}")

                    choice = input(f"Enter choice (1-{len(options)}): ").strip()

                    try:
                        choice_num = int(choice)
                        if not 1 <= choice_num <= len(options):
                            raise ValueError
                    except ValueError:
                        print("❌ Invalid choice!")
                        continue

                    action_key = options[choice_num - 1][0]

                    if action_key == 'browse_missing_in_target':
                        print(
                            f"\n📚 Opening book selector for books in '{source_key_name}' missing from '{target_key_name}'..."
                        )
                        await open_book_selector_for_missing(
                            source_server,
                            missing_in_target,
                            f"Books missing from '{target_key_name}'",
                            library_id=source_preferred_library_id,
                        )
                        break
                    if action_key == 'download_missing_in_target':
                        print(
                            f"🚀 Downloading {len(missing_in_target)} books FROM '{source_key_name}' (missing in '{target_key_name}')..."
                        )
                        await diff_tool.download_missing_books(
                            source_server,
                            missing_in_target,
                            preferred_library_id=source_preferred_library_id,
                        )
                        break
                    if action_key == 'browse_missing_in_source':
                        print(
                            f"\n📚 Opening book selector for books in '{target_key_name}' missing from '{source_key_name}'..."
                        )
                        await open_book_selector_for_missing(
                            target_server,
                            missing_in_source,
                            f"Books missing from '{source_key_name}'",
                            library_id=target_preferred_library_id,
                        )
                        break
                    if action_key == 'download_missing_in_source':
                        print(
                            f"🚀 Downloading {len(missing_in_source)} books FROM '{target_key_name}' (missing in '{source_key_name}')..."
                        )
                        await diff_tool.download_missing_books(
                            target_server,
                            missing_in_source,
                            preferred_library_id=target_preferred_library_id,
                        )
                        break
                    if action_key == 'view_matches':
                        diff_tool.print_match_details(results)
                        input("\nPress Enter to return to the comparison menu...")
                        continue
                    if action_key == 'exit':
                        break
                # End while loop

            input("\nPress Enter to continue...")

    except Exception as e:
        print(f"❌ Error during server comparison: {e}")
        input("Press Enter to continue...")

def compare_servers():
    """Compare two Audiobookshelf servers."""
    print("\n🔄 Compare Servers")
    print("-" * 20)

    try:
        from api_key_manager import APIKeyManager
        manager = APIKeyManager()
        keys = manager.list_keys()

        if not keys:
            print("❌ No API keys found! Add servers with: python api_key_manager.py")
            input("Press Enter to continue...")
            return

        if len(keys) == 1:
            print("❌ Only one API key found. You need at least 2 servers to compare.")
            print("Add another server with: python api_key_manager.py")
            input("Press Enter to continue...")
            return

        print("\n📋 Available servers:")
        for i, key in enumerate(keys):
            print(f"  {i+1}. {key['name']}")

        print(f"  {len(keys)+1}. Use manual server entry (server_diff.py)")

        try:
            choice = int(input(f"\nSelect source server (1-{len(keys)+1}): ")) - 1

            if choice == len(keys):
                # Manual entry
                os.system("python server_diff.py")
                return
            elif 0 <= choice < len(keys):
                # Use stored servers - run the book selector with server comparison
                source_key = keys[choice]
                print(f"🔑 Using source server: {source_key['name']}")

                # Get target server
                print("\n📋 Select target server:")
                for i, key in enumerate(keys):
                    if i != choice:  # Don't show the source server
                        print(f"  {i+1}. {key['name']}")

                target_choice = int(input(f"Select target server: ")) - 1
                if target_choice == choice:
                    print("❌ Cannot compare server with itself!")
                    input("Press Enter to continue...")
                    return
                elif 0 <= target_choice < len(keys):
                    target_key = keys[target_choice]
                    print(f"🔑 Using target server: {target_key['name']}")

                    # Run server comparison with stored keys
                    asyncio.run(run_server_comparison(source_key['name'], target_key['name']))
                else:
                    print("❌ Invalid target server choice!")
                    input("Press Enter to continue...")
            else:
                print("❌ Invalid choice!")
                input("Press Enter to continue...")

        except ValueError:
            print("❌ Invalid input!")
            input("Press Enter to continue...")

    except ImportError:
        print("⚠️  API key manager not available, using manual entry...")
        os.system("python server_diff.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Falling back to manual entry...")
        os.system("python server_diff.py")


def main():
    """Main function."""
    try:
        while True:
            show_menu()
            choice = input("Enter your choice (0-6): ").strip()

            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                run_setup()
            elif choice == "2":
                # API key manager handles its own exit flow
                if manage_api_keys():
                    continue  # Skip the "Press Enter to continue..." prompt
            elif choice == "3":
                # Test connection handles its own exit flow
                if test_connection():
                    continue  # Skip the "Press Enter to continue..." prompt
            elif choice == "4":
                select_books()
            elif choice == "5":
                compare_servers()
            elif choice == "6":
                download_books()
            else:
                print("❌ Invalid choice! Please try again.")

            input("\nPress Enter to continue...")
            print("\n" + "=" * 60)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
