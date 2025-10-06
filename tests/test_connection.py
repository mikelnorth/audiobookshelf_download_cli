#!/usr/bin/env python3
"""
Test script to validate Audiobookshelf API connection step by step.
"""

import asyncio
import aiohttp
import json
from audiobookshelf_downloader import AudiobookshelfDownloader


async def test_step_by_step():
    """Test each step of the API interaction."""
    import logging

    # Check if we have stored API keys first
    try:
        from api_key_manager import APIKeyManager
        manager = APIKeyManager()
        keys = manager.list_keys()

        if keys:
            print("\n🔑 Choose how to test:")
            print("1. Use stored API key")
            print("2. Enter manually")
            print("-" * 30)

            choice = input("Enter choice (1-2): ").strip()

            if choice == "1":
                # Use stored key
                if len(keys) == 1:
                    # Only one key, use it automatically
                    key = keys[0]
                    key_data = manager.get_key(key['name'])
                    server_url = key_data[0]  # server_url
                    api_key = key_data[1]     # api_key
                    print(f"🔑 Using API key: {key['name']}")
                else:
                    # Multiple keys, let user choose
                    print("\nAvailable stored keys:")
                    for i, key in enumerate(keys, 1):
                        print(f"{i}. {key['name']} ({key['server_url']})")

                    try:
                        key_choice = int(input("\nEnter number to test: ")) - 1
                        if 0 <= key_choice < len(keys):
                            key = keys[key_choice]
                            key_data = manager.get_key(key['name'])
                            server_url = key_data[0]  # server_url
                            api_key = key_data[1]     # api_key
                            print(f"🔑 Using API key: {key['name']}")
                        else:
                            print("❌ Invalid choice!")
                            return
                    except ValueError:
                        print("❌ Invalid input!")
                        return
            elif choice == "2":
                # Manual input
                server_url = input("Enter your Audiobookshelf server URL (e.g., your-server.com or https://your-server.com): ").strip()
                api_key = input("Enter your API key: ").strip()

                if not server_url or not api_key:
                    print("❌ Server URL and API key are required!")
                    return

                # Automatically add https:// if not provided
                if not server_url.startswith(('http://', 'https://')):
                    server_url = f"https://{server_url}"
                    print(f"🔧 Added https:// prefix: {server_url}")
            else:
                print("❌ Invalid choice!")
                return
        else:
            # No stored keys, manual input only
            server_url = input("Enter your Audiobookshelf server URL (e.g., your-server.com or https://your-server.com): ").strip()
            api_key = input("Enter your API key: ").strip()

            if not server_url or not api_key:
                print("❌ Server URL and API key are required!")
                return

            # Automatically add https:// if not provided
            if not server_url.startswith(('http://', 'https://')):
                server_url = f"https://{server_url}"
                print(f"🔧 Added https:// prefix: {server_url}")

    except ImportError:
        # Fallback to manual input if API key manager not available
        server_url = input("Enter your Audiobookshelf server URL (e.g., your-server.com or https://your-server.com): ").strip()
        api_key = input("Enter your API key: ").strip()

        if not server_url or not api_key:
            print("❌ Server URL and API key are required!")
            return

        # Automatically add https:// if not provided
        if not server_url.startswith(('http://', 'https://')):
            server_url = f"https://{server_url}"
            print(f"🔧 Added https:// prefix: {server_url}")

    # Temporarily disable logging for cleaner output
    logging.getLogger().setLevel(logging.ERROR)

    print(f"\n🔧 Testing connection to: {server_url}")
    print("=" * 60)

    async with AudiobookshelfDownloader(server_url, api_key) as downloader:

        # Step 1: Test basic connection
        print("\n📡 Step 1: Testing basic connection...")
        if await downloader.test_connection():
            print("✅ Connection successful!")
        else:
            print("❌ Connection failed!")
            return

        # Step 2: Get libraries
        print("\n📚 Step 2: Fetching libraries...")
        libraries = await downloader.get_libraries()
        if libraries:
            print(f"✅ Found {len(libraries)} libraries:")
            for i, lib in enumerate(libraries):
                print(f"  {i+1}. {lib.get('name', 'Unknown')} (ID: {lib.get('id', 'Unknown')})")
        else:
            print("❌ No libraries found!")
            return

        # Step 3: Get books from first library
        if libraries:
            library_id = libraries[0]['id']
            library_name = libraries[0]['name']
            print(f"\n📖 Step 3: Fetching books from '{library_name}'...")

            books = await downloader.get_library_items(library_id)
            if books:
                # Check if we got the full count or just a limited set
                total_count = len(books)
                if total_count == 1000:
                    print(f"✅ Found {total_count} books (showing first 1000 - there may be more):")
                else:
                    print(f"✅ Found {total_count} books:")

                for i, book in enumerate(books[:5]):  # Show first 5 books
                    # Extract title and author from nested structure
                    media = book.get('media', {})
                    metadata = media.get('metadata', {})
                    title = metadata.get('title', book.get('title', 'Unknown Title'))
                    author = metadata.get('authorName', book.get('author', 'Unknown Author'))
                    print(f"  {i+1}. {title} by {author}")
                if len(books) > 5:
                    print(f"  ... and {len(books) - 5} more books")
            else:
                print("❌ No books found in library!")
                return

        # Step 4: Test getting details for first book
        if books:
            first_book = books[0]
            print(f"\n🔍 Step 4: Testing book details retrieval...")

            book_id = first_book.get('id', 'unknown')
            book_title = first_book.get('title', first_book.get('name', 'Unknown Title'))

            book_details = await downloader.get_item_details(book_id)
            if book_details:
                print("✅ Book details retrieved successfully!")

                # Show media files - check multiple possible locations for tracks
                tracks = []
                media = book_details.get('media', {})

                # Try different possible locations for tracks
                if 'tracks' in media:
                    tracks = media['tracks']
                elif 'audioTracks' in media:
                    tracks = media['audioTracks']
                elif 'files' in media:
                    tracks = media['files']

                # If still no tracks, check if it's a different structure
                if not tracks and 'mediaFiles' in book_details:
                    tracks = book_details['mediaFiles']

                print(f"  📁 Found {len(tracks)} audio tracks")

                # Show first few track names if available
                if tracks and len(tracks) > 0:
                    for i, track in enumerate(tracks[:3]):
                        filename = track.get('filename', track.get('name', f'Track {i+1}'))
                        print(f"    {i+1}. {filename}")
                    if len(tracks) > 3:
                        print(f"    ... and {len(tracks) - 3} more tracks")

                # Show cover info
                cover_path = book_details.get('coverPath')
                if cover_path:
                    print(f"  🖼️ Cover image available")
                else:
                    print(f"  🖼️ No cover image")

            else:
                print("❌ Failed to get book details!")
                return

        print("\n🎉 All tests passed! Your configuration is working correctly.")
        print("\nNext steps:")
        print("1. Choose 'Select Books to Download' or 'Download All Books' from main menu")
        print("2. Start downloading your audiobooks!")

        # Restore logging level
        logging.getLogger().setLevel(logging.INFO)


def show_test_menu():
    """Show the test connection menu."""
    print("\n" + "=" * 50)
    print("🧪 Test Connection Menu")
    print("=" * 50)
    print("\nChoose an option:")
    print("1. Test stored API key")
    print("2. Test manual input")
    print("3. Exit to main menu")
    print("-" * 50)


async def main():
    """Main function with menu loop."""
    while True:
        show_test_menu()
        choice = input("Enter choice (1-3): ").strip()

        if choice == "1":
            await test_stored_key()
        elif choice == "2":
            await test_manual_input()
        elif choice == "3":
            print("\n👋 Returning to main menu...")
            break
        else:
            print("❌ Invalid choice! Please try again.")

        input("\nPress Enter to continue...")
        print("\n" + "=" * 50)


async def test_stored_key():
    """Test using a stored API key."""
    try:
        from api_key_manager import APIKeyManager
        manager = APIKeyManager()
        keys = manager.list_keys()

        if not keys:
            print("\n❌ No stored API keys found!")
            print("Please add an API key first using the main menu.")
            return

        if len(keys) == 1:
            # Only one key, use it automatically
            key = keys[0]
            key_data = manager.get_key(key['name'])
            server_url = key_data[0]
            api_key = key_data[1]
            print(f"\n🔑 Using API key: {key['name']}")
        else:
            # Multiple keys, let user choose
            print("\nAvailable stored keys:")
            for i, key in enumerate(keys, 1):
                print(f"{i}. {key['name']} ({key['server_url']})")

            try:
                key_choice = int(input("\nEnter number to test: ")) - 1
                if 0 <= key_choice < len(keys):
                    key = keys[key_choice]
                    key_data = manager.get_key(key['name'])
                    server_url = key_data[0]
                    api_key = key_data[1]
                    print(f"\n🔑 Using API key: {key['name']}")
                else:
                    print("❌ Invalid choice!")
                    return
            except ValueError:
                print("❌ Invalid input!")
                return

        await run_test(server_url, api_key)

    except ImportError:
        print("\n❌ API key manager not available!")
        print("Please use manual input instead.")


async def test_manual_input():
    """Test using manual input."""
    server_url = input("\nEnter your Audiobookshelf server URL (e.g., your-server.com or https://your-server.com): ").strip()
    api_key = input("Enter your API key: ").strip()

    if not server_url or not api_key:
        print("❌ Server URL and API key are required!")
        return

    # Automatically add https:// if not provided
    if not server_url.startswith(('http://', 'https://')):
        server_url = f"https://{server_url}"
        print(f"🔧 Added https:// prefix: {server_url}")

    await run_test(server_url, api_key)


async def run_test(server_url, api_key):
    """Run the actual test with given credentials."""
    import logging

    # Temporarily disable logging for cleaner output
    logging.getLogger().setLevel(logging.ERROR)

    print(f"\n🔧 Testing connection to: {server_url}")
    print("=" * 60)

    async with AudiobookshelfDownloader(server_url, api_key) as downloader:
        # Step 1: Test basic connection
        print("\n📡 Step 1: Testing basic connection...")
        if await downloader.test_connection():
            print("✅ Connection successful!")
        else:
            print("❌ Connection failed!")
            return

        # Step 2: Get libraries
        print("\n📚 Step 2: Fetching libraries...")
        libraries = await downloader.get_libraries()
        if libraries:
            print(f"✅ Found {len(libraries)} libraries:")
            for i, lib in enumerate(libraries):
                print(f"  {i+1}. {lib.get('name', 'Unknown')} (ID: {lib.get('id', 'Unknown')})")
        else:
            print("❌ No libraries found!")
            return

        # Step 3: Get books from first library
        if libraries:
            library_id = libraries[0]['id']
            library_name = libraries[0]['name']
            print(f"\n📖 Step 3: Fetching books from '{library_name}'...")

            books = await downloader.get_library_items(library_id)
            if books:
                # Check if we got the full count or just a limited set
                total_count = len(books)
                if total_count == 1000:
                    print(f"✅ Found {total_count} books (showing first 1000 - there may be more):")
                else:
                    print(f"✅ Found {total_count} books:")

                for i, book in enumerate(books[:5]):  # Show first 5 books
                    # Extract title and author from nested structure
                    media = book.get('media', {})
                    metadata = media.get('metadata', {})
                    title = metadata.get('title', book.get('title', 'Unknown Title'))
                    author = metadata.get('authorName', book.get('author', 'Unknown Author'))
                    print(f"  {i+1}. {title} by {author}")
                if len(books) > 5:
                    print(f"  ... and {len(books) - 5} more books")
            else:
                print("❌ No books found in library!")
                return

        # Step 4: Test getting details for first book
        if books:
            first_book = books[0]
            print(f"\n🔍 Step 4: Testing book details retrieval...")

            book_id = first_book.get('id', 'unknown')
            book_title = first_book.get('title', first_book.get('name', 'Unknown Title'))

            book_details = await downloader.get_item_details(book_id)
            if book_details:
                print("✅ Book details retrieved successfully!")

                # Show media files - check multiple possible locations for tracks
                tracks = []
                media = book_details.get('media', {})

                # Try different possible locations for tracks
                if 'tracks' in media:
                    tracks = media['tracks']
                elif 'audioTracks' in media:
                    tracks = media['audioTracks']
                elif 'files' in media:
                    tracks = media['files']

                # If still no tracks, check if it's a different structure
                if not tracks and 'mediaFiles' in book_details:
                    tracks = book_details['mediaFiles']

                print(f"  📁 Found {len(tracks)} audio tracks")

                # Show first few track names if available
                if tracks and len(tracks) > 0:
                    for i, track in enumerate(tracks[:3]):
                        filename = track.get('filename', track.get('name', f'Track {i+1}'))
                        print(f"    {i+1}. {filename}")
                    if len(tracks) > 3:
                        print(f"    ... and {len(tracks) - 3} more tracks")

                # Show cover info
                cover_path = book_details.get('coverPath')
                if cover_path:
                    print(f"  🖼️ Cover image available")
                else:
                    print(f"  🖼️ No cover image")

            else:
                print("❌ Failed to get book details!")
                return

        print("\n🎉 All tests passed! Your configuration is working correctly.")
        print("\nNext steps:")
        print("1. Choose 'Select Books to Download' or 'Download All Books' from main menu")
        print("2. Start downloading your audiobooks!")

        # Restore logging level
        logging.getLogger().setLevel(logging.INFO)


if __name__ == "__main__":
    asyncio.run(main())
