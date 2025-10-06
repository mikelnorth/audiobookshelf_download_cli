#!/usr/bin/env python3
"""
Command-line bulk downloader for Audiobookshelf
"""

import asyncio
import argparse
import sys
from audiobookshelf_downloader import AudiobookshelfDownloader
from config import DOWNLOAD_PATH

async def main():
    """Main function with command line arguments."""

    parser = argparse.ArgumentParser(description='Bulk download books from Audiobookshelf')
    parser.add_argument('--server', '-s', help='Audiobookshelf server URL')
    parser.add_argument('--api-key', '-k', help='API key for authentication')
    parser.add_argument('--output', '-o', help='Output directory for downloads', default=DOWNLOAD_PATH)
    parser.add_argument('--library', '-l', help='Specific library ID to download from')
    parser.add_argument('--list-libraries', action='store_true', help='List available libraries and exit')
    parser.add_argument('--list-books', action='store_true', help='List books in library and exit')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be downloaded without actually downloading')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    # Initialize downloader
    downloader_kwargs = {}
    if args.server:
        downloader_kwargs['server_url'] = args.server
    if args.api_key:
        downloader_kwargs['api_key'] = args.api_key
    if args.output:
        downloader_kwargs['download_path'] = args.output

    async with AudiobookshelfDownloader(**downloader_kwargs) as downloader:

        # Test connection
        print("🔌 Testing connection...")
        if not await downloader.test_connection():
            print("❌ Failed to connect to server!")
            sys.exit(1)

        # Get libraries
        print("📚 Fetching libraries...")
        libraries = await downloader.get_libraries()
        if not libraries:
            print("❌ No libraries found!")
            sys.exit(1)

        # Get items from first library
        library_id = libraries[0]['id']
        print(f"📚 Fetching items from library: {libraries[0]['name']}")
        items = await downloader.get_library_items(library_id)
        if not items:
            print("❌ No items found in library!")
            sys.exit(1)

        # List libraries if requested
        if args.list_libraries:
            print("\n📚 Available Libraries:")
            for i, lib in enumerate(libraries):
                print(f"  {i+1}. {lib.get('name', 'Unknown')} (ID: {lib.get('id', 'Unknown')})")
            return

        # Choose library
        if args.library:
            library_id = args.library
            library_name = next((lib['name'] for lib in libraries if lib['id'] == library_id), 'Unknown')
            # Re-fetch items for the specified library
            items = await downloader.get_library_items(library_id)
        else:
            library_id = libraries[0]['id']
            library_name = libraries[0]['name']
            # items already fetched above

        print(f"📖 Using library: {library_name} (ID: {library_id})")

        # Use the items we already fetched
        books = items
        if not books:
            print("❌ No books found in library!")
            sys.exit(1)

        print(f"📖 Found {len(books)} books")

        # List books if requested
        if args.list_books:
            print("\n📚 Books in library:")
            for i, book in enumerate(books):
                title = book.get('title', 'Unknown')
                author = book.get('author', 'Unknown')
                print(f"  {i+1}. {title} by {author}")
            return

        # Dry run
        if args.dry_run:
            print("\n🔍 Dry run - would download:")
            for book in books:
                title = book.get('title', 'Unknown')
                author = book.get('author', 'Unknown')
                print(f"  📖 {title} by {author}")
            print(f"\nTotal: {len(books)} books")
            return

        # Confirm download
        print(f"\n🚀 Ready to download {len(books)} books to: {args.output}")
        if not args.verbose:
            response = input("Continue? (y/N): ").strip().lower()
            if response != 'y':
                print("❌ Download cancelled")
                return

        # Download books
        print("\n📥 Starting download...")
        results = await downloader.download_all_books(library_id)

        # Show results
        print(f"\n📊 Download Complete!")
        print(f"  ✅ Successfully downloaded: {results['success']}")
        print(f"  ❌ Failed: {results['failed']}")
        print(f"  📚 Total books: {results['total']}")

        if results['failed'] > 0:
            print(f"\n⚠️  {results['failed']} books failed to download. Check the logs for details.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Download cancelled!")
        sys.exit(0)
