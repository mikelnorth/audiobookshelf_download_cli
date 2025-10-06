#!/usr/bin/env python3
"""
Audiobookshelf Bulk Downloader

This script downloads all books from an Audiobookshelf library using the API.
"""

import asyncio
import aiohttp
import os
import sys
import json
import zipfile
import argparse
from typing import List, Dict, Optional
from urllib.parse import urljoin
import logging
from config import (
    DOWNLOAD_PATH, MAX_CONCURRENT_DOWNLOADS, CHUNK_SIZE, LOG_LEVEL, LOG_FORMAT,
    ORGANIZE_BY_AUTHOR, INCLUDE_COVER_IMAGES, SAFE_FILENAME_CHARS,
    DOWNLOAD_DELAY, REQUEST_TIMEOUT, MAX_RETRIES
)

# Set up logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class AudiobookshelfDownloader:
    def __init__(self, server_url: str = None, api_key: str = None, download_path: str = None):
        """
        Initialize the Audiobookshelf downloader.

        Args:
            server_url: Base URL of your Audiobookshelf server (e.g., 'https://your-server.com')
            api_key: API key for authentication
            download_path: Local directory to save downloaded books
        """
        self.server_url = server_url.rstrip('/') if server_url else None
        self.api_key = api_key
        self.download_path = os.path.expanduser(download_path or DOWNLOAD_PATH)
        self.session = None

    async def __aenter__(self):
        """Async context manager entry."""
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    async def test_connection(self) -> bool:
        """Test the connection to the Audiobookshelf server."""
        try:
            url = f"{self.server_url}/api/libraries"
            async with self.session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    logger.info("✅ Successfully connected to Audiobookshelf server")
                    return True
                else:
                    logger.error(f"❌ Failed to connect. Status: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False

    async def get_libraries(self) -> List[Dict]:
        """Get list of all libraries."""
        try:
            url = f"{self.server_url}/api/libraries"
            async with self.session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    libraries = data.get('libraries', [])
                    logger.info(f"📚 Found {len(libraries)} libraries")
                    return libraries
                else:
                    logger.error(f"Failed to get libraries. Status: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting libraries: {e}")
            return []

    async def get_library_items(self, library_id: str, limit: int = 1000) -> List[Dict]:
        """Get all items (books) from a specific library."""
        try:
            url = f"{self.server_url}/api/libraries/{library_id}/items"
            params = {'limit': limit}

            logger.info(f"🔍 Fetching items from: {url}")
            logger.info(f"📋 Parameters: {params}")

            async with self.session.get(url, headers=self._get_headers(), params=params) as response:
                logger.info(f"📡 Response status: {response.status}")

                if response.status == 200:
                    data = await response.json()
                    logger.info(f"📊 Response data keys: {list(data.keys())}")

                    # Try both 'items' and 'results' fields
                    items = data.get('items', [])
                    if not items:
                        items = data.get('results', [])

                    total_items = data.get('total', 0)

                    logger.info(f"📖 Found {len(items)} items in library {library_id}")
                    logger.info(f"📊 Total items reported: {total_items}")

                    # If we have pagination, fetch all items
                    if total_items > len(items):
                        logger.info(f"⚠️  Pagination detected: {total_items} total items, but only got {len(items)}")
                        logger.info("🔄 Fetching remaining items...")

                        # Try different pagination approaches
                        all_items = items.copy()

                        # Try page-based pagination instead of offset-based
                        page = 1  # Start from page 1 since we already have page 0
                        max_pages = 10  # Safety limit

                        while page <= max_pages and len(all_items) < total_items:
                            page_params = {'limit': limit, 'page': page}
                            logger.info(f"📄 Fetching page {page} with limit {limit}")

                            async with self.session.get(url, headers=self._get_headers(), params=page_params) as page_response:
                                if page_response.status == 200:
                                    page_data = await page_response.json()
                                    page_items = page_data.get('items', [])
                                    if not page_items:
                                        page_items = page_data.get('results', [])

                                    if not page_items:
                                        logger.warning(f"No items returned for page {page}, stopping pagination")
                                        break

                                    # Prevent duplicates by checking if we already have these items
                                    new_items = []
                                    existing_ids = {item.get('id') for item in all_items if item.get('id')}

                                    for item in page_items:
                                        if item.get('id') not in existing_ids:
                                            new_items.append(item)

                                    if not new_items:
                                        logger.warning(f"All items on page {page} are duplicates, stopping pagination")
                                        break

                                    all_items.extend(new_items)
                                    page += 1
                                    logger.info(f"📚 Fetched {len(new_items)} new items from page {page-1}, running total: {len(all_items)}")

                                    # If we got fewer items than the limit, we've reached the end
                                    if len(page_items) < limit:
                                        logger.info(f"✅ Reached end of results (got {len(page_items)} < {limit})")
                                        break

                                    # Safety check to prevent infinite loops
                                    if len(all_items) >= total_items:
                                        logger.info(f"✅ Reached target count: {len(all_items)}/{total_items}")
                                        break
                                else:
                                    logger.error(f"Failed to fetch page {page}, status: {page_response.status}")
                                    break

                        logger.info(f"✅ Pagination complete: {len(all_items)}/{total_items} items fetched")
                        return all_items

                    return items
                else:
                    response_text = await response.text()
                    logger.error(f"Failed to get library items. Status: {response.status}")
                    logger.error(f"Response: {response_text}")
                    return []
        except Exception as e:
            logger.error(f"Error getting library items: {e}")
            return []

    async def get_item_details(self, item_id: str) -> Optional[Dict]:
        """Get detailed information about a specific item."""
        try:
            url = f"{self.server_url}/api/items/{item_id}"
            async with self.session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get item details for {item_id}. Status: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting item details for {item_id}: {e}")
            return None

    async def download_file(self, download_url: str, file_path: str, retries: int = MAX_RETRIES) -> bool:
        """Download a single file with retry logic."""
        for attempt in range(retries + 1):
            try:
                # Use a much longer timeout for downloads (or no timeout for file downloads)
                # Only connection/socket timeout applies, not total download time
                download_timeout = aiohttp.ClientTimeout(total=None, connect=30, sock_read=60)
                async with self.session.get(download_url, headers=self._get_headers(), timeout=download_timeout) as response:
                    if response.status == 200:
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(CHUNK_SIZE):
                                f.write(chunk)
                        return True
                    else:
                        logger.error(f"Failed to download file. Status: {response.status}")
                        if attempt < retries:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        return False
            except Exception as e:
                logger.error(f"Error downloading file (attempt {attempt + 1}): {e}")
                if attempt < retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return False
        return False

    def _create_safe_filename(self, text: str) -> str:
        """Create a safe filename from text."""
        return "".join(c for c in text if c in SAFE_FILENAME_CHARS).strip()

    async def _extract_zip_file(self, zip_path: str, extract_to: str) -> bool:
        """Extract a ZIP file to the specified directory (non-blocking)."""
        def _extract():
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
                    return len(zip_ref.namelist())
            except Exception as e:
                logger.error(f"Failed to extract ZIP: {e}")
                return None

        # Run the blocking extraction in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        num_files = await loop.run_in_executor(None, _extract)

        return num_files is not None

    async def download_book(self, book: Dict, library_id: str) -> bool:
        """Download all files for a single book."""
        book_id = book.get('id')

        # Extract title and author from nested structure
        media = book.get('media', {})
        metadata = media.get('metadata', {})
        title = metadata.get('title', book.get('title', 'Unknown Title'))
        author = metadata.get('authorName', book.get('author', 'Unknown Author'))

        # Create safe directory name
        safe_title = self._create_safe_filename(title)
        safe_author = self._create_safe_filename(author)

        if ORGANIZE_BY_AUTHOR:
            book_dir = os.path.join(self.download_path, safe_author, safe_title)
        else:
            book_dir = os.path.join(self.download_path, f"{safe_author} - {safe_title}")

        # Get detailed book information
        book_details = await self.get_item_details(book_id)
        if not book_details:
            logger.error(f"Failed to get details for: {title}")
            return False

        # Download the entire book as a ZIP file
        # Use the download endpoint which provides the complete book as a ZIP
        download_url = f"{self.server_url}/api/items/{book_id}/download?token={self.api_key}"

        # Create a temporary ZIP filename
        zip_filename = f"{safe_title}.zip"
        zip_path = os.path.join(book_dir, zip_filename)

        if await self.download_file(download_url, zip_path):
            # Extract the ZIP file
            if await self._extract_zip_file(zip_path, book_dir):
                success_count = 1
                # Remove the ZIP file after extraction
                os.remove(zip_path)
            else:
                logger.error(f"Failed to extract: {title}")
                return False
        else:
            logger.error(f"Failed to download: {title}")
            return False

        # Download cover image if available and enabled
        if INCLUDE_COVER_IMAGES:
            cover_path = book_details.get('coverPath')
            if cover_path:
                cover_url = f"{self.server_url}{cover_path}"
                cover_file_path = os.path.join(book_dir, "cover.jpg")
                await self.download_file(cover_url, cover_file_path)

        return success_count > 0

    async def download_all_books(self, library_id: str) -> Dict[str, int]:
        """Download all books from a library with concurrent downloads."""
        logger.info(f"🚀 Starting bulk download from library {library_id}")

        # Get all books
        books = await self.get_library_items(library_id)
        if not books:
            logger.error("No books found in library")
            return {"total": 0, "success": 0, "failed": 0}

        # Use the concurrent download implementation
        return await self.download_selected_books(books, library_id)

    async def download_selected_books(self, books: List[Dict], library_id: str) -> Dict[str, int]:
        """Download selected books with load management."""
        if not books:
            logger.warning("No books selected for download")
            return {"total": 0, "success": 0, "failed": 0}

        logger.info(f"🚀 Starting download of {len(books)} selected books")
        logger.info(f"⚙️  Load management: Max {MAX_CONCURRENT_DOWNLOADS} concurrent downloads, {DOWNLOAD_DELAY}s delay")

        # Create download directory
        os.makedirs(self.download_path, exist_ok=True)

        # Download books with concurrency control
        results = {"total": len(books), "success": 0, "failed": 0}

        # Use semaphore to limit concurrent downloads
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
        download_counter = 0
        completed_counter = 0

        async def download_with_semaphore(book, index):
            nonlocal download_counter, completed_counter
            import time
            title = book.get('media', {}).get('metadata', {}).get('title', 'Unknown')
            async with semaphore:
                download_counter += 1
                current_num = download_counter

                # Print immediately with flush to show real-time progress
                print(f"📥 [{current_num}/{len(books)}] Downloading: {title}", flush=True)

                start_time = time.time()
                result = await self.download_book(book, library_id)
                elapsed = time.time() - start_time

                completed_counter += 1
                remaining = len(books) - completed_counter
                # Calculate active: started but not yet completed (including those waiting to start)
                in_progress = min(MAX_CONCURRENT_DOWNLOADS, remaining) if remaining > 0 else 0

                if result:
                    print(f"✅ [{current_num}/{len(books)}] Completed: {title} ({elapsed:.1f}s)", flush=True)
                else:
                    print(f"❌ [{current_num}/{len(books)}] Failed: {title} ({elapsed:.1f}s)", flush=True)

                print(f"   📊 Progress: {completed_counter} done | {in_progress} active | {remaining} remaining", flush=True)

                # Add delay after download completes (not before)
                if DOWNLOAD_DELAY > 0:
                    await asyncio.sleep(DOWNLOAD_DELAY)

                return result

        # Create and schedule tasks for all books immediately
        tasks = [asyncio.create_task(download_with_semaphore(book, i)) for i, book in enumerate(books, 1)]

        print(f"\n📋 Starting concurrent download of {len(books)} books")
        print(f"⚙️  Up to {MAX_CONCURRENT_DOWNLOADS} downloads will run simultaneously\n")

        # Execute downloads with progress tracking
        for task in asyncio.as_completed(tasks):
            try:
                success = await task
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                results["failed"] += 1
                logger.error(f"Error in download task: {e}")

        print(f"\n🎉 Download complete! Success: {results['success']}, Failed: {results['failed']}", flush=True)
        return results


async def main(download_path=None, server_url=None, api_key=None):
    """Main function to run the downloader."""
    print("🎧 Audiobookshelf Bulk Downloader")
    print("=" * 50)

    # Try to get API key from management system first
    if not server_url or not api_key:
        try:
            from api_key_manager import APIKeyManager
            manager = APIKeyManager()
            keys = manager.list_keys()

            if keys:
                if len(keys) == 1:
                    # Only one key, use it automatically
                    key = keys[0]
                    server_url, api_key, stored_download_path = manager.get_key(key['name'])
                    print(f"🔑 Using API key: {key['name']}")
                    print(f"📁 Using download path: {stored_download_path}")
                    # Use stored download path if no download_path provided
                    if not download_path:
                        download_path = stored_download_path
                else:
                    # Multiple keys, let user choose
                    result = manager.select_key_interactive()
                    if result:
                        selected_key_name, server_url, api_key, stored_download_path = result
                        print(f"📁 Using download path: {stored_download_path}")
                        if not download_path:
                            download_path = stored_download_path
                    else:
                        print("❌ No API key selected!")
                        return
            else:
                print("❌ No API keys found!")
                print("\nTo get started:")
                print("1. Run: python setup.py")
                print("2. Or run: python api_key_manager.py")
                return
        except ImportError:
            # No API key manager available
            print("❌ No API keys found!")
            print("\nTo get started:")
            print("1. Run: python setup.py")
            print("2. Or run: python api_key_manager.py")
            return

    # Use provided download path or default
    actual_download_path = download_path or DOWNLOAD_PATH
    print(f"📁 Download path: {actual_download_path}")

    async with AudiobookshelfDownloader(server_url, api_key, actual_download_path) as downloader:
        # Test connection
        if not await downloader.test_connection():
            print("❌ Failed to connect to server. Please check your configuration.")
            return

        # Get libraries
        libraries = await downloader.get_libraries()
        if not libraries:
            print("❌ No libraries found.")
            return

        # Display libraries
        print("\n📚 Available Libraries:")
        for i, lib in enumerate(libraries):
            print(f"  {i+1}. {lib.get('name', 'Unknown')} (ID: {lib.get('id', 'Unknown')})")

        # For now, download from the first library
        # In a full implementation, you'd let the user choose
        library_id = libraries[0]['id']
        library_name = libraries[0]['name']

        print(f"\n🚀 Starting download from library: {library_name}")

        # Download all books
        results = await downloader.download_all_books(library_id)

        print(f"\n📊 Final Results:")
        print(f"  Total books: {results['total']}")
        print(f"  Successfully downloaded: {results['success']}")
        print(f"  Failed: {results['failed']}")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Download books from Audiobookshelf')
        parser.add_argument('--download-path', '-d', help='Directory to save downloaded books', default=None)
        args = parser.parse_args()

        asyncio.run(main(download_path=args.download_path))
    except KeyboardInterrupt:
        print("\n\n👋 Download cancelled!")
        sys.exit(0)
