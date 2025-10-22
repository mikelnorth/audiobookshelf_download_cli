#!/usr/bin/env python3
"""
Interactive book selection interface for Audiobookshelf Downloader
"""

import asyncio
import os
import sys
import argparse
from typing import Dict, List, Optional, Set
from audiobookshelf_downloader import AudiobookshelfDownloader


class BookSelector:
    def __init__(self, downloader: AudiobookshelfDownloader, library_id: Optional[str] = None):
        self.downloader = downloader
        self.library_id = library_id
        self.selected_books: Set[str] = set()

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_books(self, books: List[Dict], page: int = 0, per_page: int = 20) -> List[Dict]:
        """Display books in pages with selection status."""
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_books = books[start_idx:end_idx]

        print(f"\n📚 Books (Page {page + 1}/{(len(books) + per_page - 1) // per_page})")
        print("=" * 95)
        print(f"{'#':<3} {'✓':<2} {'Title':<35} {'Author':<20} {'Duration':<13} {'Audio':^5} {'Ebook':^5}")
        print("-" * 95)

        for i, book in enumerate(page_books, start_idx):
            book_id = book.get('id', '')
            is_selected = book_id in self.selected_books

            # Extract title and author from nested structure
            media = book.get('media', {})
            metadata = media.get('metadata', {})
            title = metadata.get('title', book.get('title', 'Unknown'))
            author = metadata.get('authorName', book.get('author', 'Unknown'))

            # Truncate for display
            title = title[:32] + '...' if len(title) > 35 else title
            author = author[:17] + '...' if len(author) > 20 else author
            duration = self._format_duration(media.get('duration', book.get('duration', 0)))

            # Check format availability from the basic book data
            audio_available, ebook_available = self._check_format_availability_basic(book)

            status = "✓" if is_selected else " "
            print(f"{i+1:<3} {status:<2} {title:<35} {author:<20} {duration:<13} {audio_available:^5} {ebook_available:^5}")

        print("-" * 95)
        print(f"Selected: {len(self.selected_books)} books")
        return page_books

    def _check_format_availability_basic(self, book: Dict) -> tuple[str, str]:
        """Check format availability from basic book data (fast, no API calls)."""
        audio_available = "✗"
        ebook_available = "✗"

        media = book.get('media', {})

        # Check for audio files in basic data
        # Most audiobooks will have duration if they have audio
        duration = media.get('duration', book.get('duration', 0))
        if duration and duration > 0:
            audio_available = "✓"

        # Check for ebook indicators in basic data
        # Look for ebook-related fields that might be present
        if media.get('ebookFormat'):
            ebook_available = "✓"
        elif media.get('ebookFile'):
            ebook_available = "✓"

        # Check library files if available
        library_files = book.get('libraryFiles', [])
        if library_files:
            for lib_file in library_files:
                if isinstance(lib_file, dict):
                    file_type = lib_file.get('fileType', '').lower()
                    if file_type == 'ebook':
                        ebook_available = "✓"
                        break

        return audio_available, ebook_available

    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to readable format."""
        if not seconds:
            return "Unknown"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def get_selection_commands(self) -> str:
        """Display available commands."""
        return """
Commands:
  [num]      - Select/unselect book by its overall number (e.g., 25)
  n/next     - Next page
  p/prev     - Previous page
  g/goto     - Jump to a specific page number (e.g., g 5)
  a/all      - Select all books on current page
  u/unall    - Unselect all books on current page
  s/select   - Select books by absolute range (e.g., 21-30,35)
  f/filter   - Filter books by title/author (or 'f <term>' for direct filter)
  cf/clearfilter - Clear current filter and show all books
  c/clear    - Clear all selections
  v/view     - View details of selected books
  m/missing  - Select books missing from another server
  d/download - Start download
  q/quit     - Exit without downloading
"""

    async def select_books_interactive(self, books: List[Dict]) -> List[Dict]:
        """Interactive book selection interface."""
        if not books:
            print("❌ No books found!")
            return []

        filtered_books = books
        current_page = 0
        per_page = 20

        while True:
            self.clear_screen()
            print("🎧 Audiobookshelf Book Selector")
            print("=" * 50)

            # Display current page
            page_books = self.display_books(filtered_books, current_page, per_page)
            max_pages = max(1, (len(filtered_books) + per_page - 1) // per_page)

            # Show commands
            print(self.get_selection_commands())

            # Get user input
            command = input("Enter command: ").strip().lower()

            if command in ['q', 'quit']:
                return []
            elif command in ['d', 'download']:
                if not self.selected_books:
                    print("❌ No books selected!")
                    input("Press Enter to continue...")
                    continue

                # Download selected books
                selected_books = [book for book in filtered_books if book.get('id', '') in self.selected_books]
                download_success = await self._download_selected_books(selected_books)

                if download_success:
                    # If download was successful, exit the selection loop
                    return selected_books
                else:
                    # If download was cancelled, continue the selection loop
                    input("Press Enter to continue...")
                    continue
            elif command in ['n', 'next']:
                if current_page < max_pages - 1:
                    current_page += 1
            elif command in ['p', 'prev']:
                if current_page > 0:
                    current_page -= 1
            elif command in ['g', 'goto'] or command.startswith('g ') or command.startswith('goto '):
                if command in ['g', 'goto']:
                    page_input = input(f"Enter page number (1-{max_pages}): ").strip()
                else:
                    page_input = command.split(' ', 1)[1].strip()

                try:
                    page_number = int(page_input)
                    if 1 <= page_number <= max_pages:
                        current_page = page_number - 1
                    else:
                        print(f"❌ Page must be between 1 and {max_pages}!")
                        input("Press Enter to continue...")
                except ValueError:
                    print("❌ Invalid page number!")
                    input("Press Enter to continue...")
            elif command in ['a', 'all']:
                for book in page_books:
                    self.selected_books.add(book.get('id', ''))
            elif command in ['u', 'unall']:
                for book in page_books:
                    self.selected_books.discard(book.get('id', ''))
            elif command in ['c', 'clear']:
                self.selected_books.clear()
            elif command in ['cf', 'clearfilter']:
                filtered_books = books
                current_page = 0
                print("Filter cleared - showing all books")
                input("Press Enter to continue...")
            elif command in ['v', 'view']:
                await self._view_selected_books(books)
            elif command in ['m', 'missing']:
                await self._select_missing_books(books)
            elif command in ['f', 'filter'] or command.startswith('f '):
                if command.startswith('f '):
                    # Extract search term from command
                    search_term = command[2:].strip()
                    filtered_books = self._filter_books_with_term(books, search_term)
                else:
                    # Use interactive filter
                    filtered_books = self._filter_books(books)
                current_page = 0
            elif command.startswith('s') or command.startswith('select'):
                self._select_by_range(command, filtered_books)
            elif command.isdigit():
                # Toggle book selection by absolute number
                book_num = int(command) - 1
                if 0 <= book_num < len(filtered_books):
                    book = filtered_books[book_num]
                    book_id = book.get('id', '')
                    if book_id in self.selected_books:
                        self.selected_books.remove(book_id)
                    else:
                        self.selected_books.add(book_id)
            else:
                print("❌ Invalid command!")
                input("Press Enter to continue...")

        # Return selected books
        selected_books = [book for book in books if book.get('id', '') in self.selected_books]
        return selected_books

    def _select_by_range(self, command: str, all_books: List[Dict]):
        """Select books by absolute range (matching the displayed numbers)."""
        try:
            # Parse range command
            parts = command.split(' ', 1)
            if len(parts) > 1:
                range_str = parts[1]
            else:
                range_str = input("Enter range (e.g., 1-5,10,15-20): ").strip()

            # Parse ranges
            invalid_entries = []
            total_books = len(all_books)

            def resolve_index(selection_number: int) -> Optional[int]:
                """Resolve an absolute selection number to an index in all_books."""
                if selection_number <= 0:
                    return None

                idx = selection_number - 1

                if 0 <= idx < total_books:
                    return idx
                return None

            for part in range_str.split(','):
                part = part.strip()
                if not part:
                    continue

                if '-' in part:
                    start_str, end_str = part.split('-', 1)
                    start = int(start_str)
                    end = int(end_str)

                    if start > end:
                        start, end = end, start

                    for selection_number in range(start, end + 1):
                        idx = resolve_index(selection_number)
                        if idx is None:
                            invalid_entries.append(selection_number)
                            continue
                        self.selected_books.add(all_books[idx].get('id', ''))
                else:
                    selection_number = int(part)
                    idx = resolve_index(selection_number)
                    if idx is None:
                        invalid_entries.append(selection_number)
                        continue
                    self.selected_books.add(all_books[idx].get('id', ''))

            if invalid_entries:
                unique_invalids = sorted(set(invalid_entries))
                print(f"⚠️  Skipped invalid selections: {', '.join(map(str, unique_invalids))}")
                input("Press Enter to continue...")
        except (ValueError, IndexError):
            print("❌ Invalid range format!")
            input("Press Enter to continue...")

    def _filter_books(self, books: List[Dict]) -> List[Dict]:
        """Filter books by title or author."""
        filter_term = input("Enter search term (title or author): ").strip().lower()
        if not filter_term:
            return books

        return self._filter_books_with_term(books, filter_term)

    def _filter_books_with_term(self, books: List[Dict], filter_term: str, interactive: bool = True) -> List[Dict]:
        """Filter books by title or author with a given search term."""
        filter_term = filter_term.lower()
        if not filter_term:
            return books

        filtered = []
        for book in books:
            # Extract title and author from nested structure
            media = book.get('media', {})
            metadata = media.get('metadata', {})
            title = metadata.get('title', book.get('title', '')).lower()
            author = metadata.get('authorName', book.get('author', '')).lower()
            if filter_term in title or filter_term in author:
                filtered.append(book)

        print(f"Found {len(filtered)} books matching '{filter_term}'")
        if interactive:
            input("Press Enter to continue...")
        return filtered

    async def _view_selected_books(self, books: List[Dict]):
        """View details of selected books."""
        if not self.selected_books:
            print("❌ No books selected!")
            input("Press Enter to continue...")
            return

        selected_books = [book for book in books if book.get('id', '') in self.selected_books]

        print(f"\n📚 Selected Books ({len(selected_books)}):")
        print("=" * 60)

        total_duration = 0
        for i, book in enumerate(selected_books, 1):
            # Extract title and author from nested structure
            media = book.get('media', {})
            metadata = media.get('metadata', {})
            title = metadata.get('title', book.get('title', 'Unknown'))
            author = metadata.get('authorName', book.get('author', 'Unknown'))
            duration = media.get('duration', book.get('duration', 0))
            total_duration += duration

            print(f"{i:2d}. {title}")
            print(f"    Author: {author}")
            print(f"    Duration: {self._format_duration(duration)}")

            # Get detailed book information to show file types
            try:
                book_details = await self.downloader.get_item_details(book.get('id'))
                if book_details:
                    files_info = self._extract_files_info(book_details)
                    if files_info:
                        print(f"    Files: {files_info}")
                    else:
                        print(f"    Files: No file information available")
                else:
                    print(f"    Files: Unable to retrieve file details")
            except Exception as e:
                print(f"    Files: Error retrieving details ({str(e)[:50]}...)")

            print()

        print(f"Total Duration: {self._format_duration(total_duration)}")
        input("Press Enter to continue...")

    def _check_format_availability(self, book_details: Dict) -> tuple[str, str]:
        """Check if audiobook and ebook formats are available."""
        audio_available = "✗"
        ebook_available = "✗"

        media = book_details.get('media', {})

        # Check for audio files
        audio_files = media.get('audioFiles', [])
        if audio_files:
            audio_available = "✓"

        # Check for ebook files
        ebook_file = media.get('ebookFile')
        if ebook_file and isinstance(ebook_file, dict):
            ebook_format = ebook_file.get('ebookFormat', '').lower()
            if ebook_format in ['epub', 'pdf', 'mobi', 'azw3', 'fb2', 'lit', 'lrf', 'rtf', 'txt']:
                ebook_available = "✓"
            else:
                # Check filename extension
                filename = ebook_file.get('metadata', {}).get('filename', '').lower()
                if any(ext in filename for ext in ['.epub', '.pdf', '.mobi', '.azw3', '.fb2', '.lit', '.lrf', '.rtf', '.txt']):
                    ebook_available = "✓"

        # Check library files for additional ebook formats
        library_files = book_details.get('libraryFiles', [])
        if not ebook_available == "✓":  # Only check if we haven't found an ebook yet
            for lib_file in library_files:
                if isinstance(lib_file, dict):
                    file_type = lib_file.get('fileType', '').lower()
                    if file_type == 'ebook':
                        ebook_available = "✓"
                        break
                    # Check filename for ebook extensions
                    filename = lib_file.get('metadata', {}).get('filename', '').lower()
                    if any(ext in filename for ext in ['.epub', '.pdf', '.mobi', '.azw3', '.fb2', '.lit', '.lrf', '.rtf', '.txt']):
                        ebook_available = "✓"
                        break

        return audio_available, ebook_available

    def _extract_files_info(self, book_details: Dict) -> str:
        """Extract file information from book details."""
        files_info = []

        # Check for audio files
        media = book_details.get('media', {})
        audio_files = media.get('audioFiles', [])

        if audio_files:
            # Count audio file types
            audio_types = {}
            for audio_file in audio_files:
                if isinstance(audio_file, dict):
                    # Get format from the audio file metadata
                    format_info = audio_file.get('format', '')
                    mime_type = audio_file.get('mimeType', '')

                    # Extract format from mime type or format field
                    if mime_type:
                        if 'mp4' in mime_type or 'm4a' in mime_type:
                            audio_types['m4a'] = audio_types.get('m4a', 0) + 1
                        elif 'mp3' in mime_type:
                            audio_types['mp3'] = audio_types.get('mp3', 0) + 1
                        elif 'ogg' in mime_type:
                            audio_types['ogg'] = audio_types.get('ogg', 0) + 1
                        elif 'flac' in mime_type:
                            audio_types['flac'] = audio_types.get('flac', 0) + 1
                    elif format_info:
                        # Try to extract format from format field
                        format_lower = format_info.lower()
                        if 'mp4' in format_lower or 'm4a' in format_lower:
                            audio_types['m4a'] = audio_types.get('m4a', 0) + 1
                        elif 'mp3' in format_lower:
                            audio_types['mp3'] = audio_types.get('mp3', 0) + 1
                        else:
                            audio_types['audio'] = audio_types.get('audio', 0) + 1
                    else:
                        audio_types['audio'] = audio_types.get('audio', 0) + 1

            # Format audio file counts
            for ext, count in sorted(audio_types.items()):
                if count == 1:
                    files_info.append(f"{ext.upper()}")
                else:
                    files_info.append(f"{count}x {ext.upper()}")

        # Check for ebook files
        ebook_file = media.get('ebookFile')
        if ebook_file and isinstance(ebook_file, dict):
            ebook_format = ebook_file.get('ebookFormat', '').upper()
            if ebook_format:
                files_info.append(ebook_format)
            else:
                # Try to get format from filename
                filename = ebook_file.get('metadata', {}).get('filename', '')
                if filename:
                    ext = filename.split('.')[-1].upper() if '.' in filename else 'EBOOK'
                    files_info.append(ext)

        # Check for additional library files
        library_files = book_details.get('libraryFiles', [])
        if library_files:
            for lib_file in library_files:
                if isinstance(lib_file, dict):
                    file_type = lib_file.get('fileType', '')
                    if file_type and file_type not in ['audio', 'ebook']:  # Avoid duplicates
                        files_info.append(file_type.upper())

        return ", ".join(files_info) if files_info else ""

    async def _download_selected_books(self, selected_books: List[Dict]) -> bool:
        """Download selected books and return True if successful, False if cancelled."""
        if not selected_books:
            print("❌ No books selected!")
            return False

        # Show detailed download summary
        print(f"\n📋 Download Summary")
        print("=" * 50)
        print(f"📚 Total books selected: {len(selected_books)}")
        print(f"📁 Download location: {self.downloader.download_path}")

        # Show file organization example with first book
        if selected_books:
            first_book = selected_books[0]
            media = first_book.get('media', {})
            metadata = media.get('metadata', {})
            title = metadata.get('title', first_book.get('title', 'Unknown Title'))
            author = metadata.get('authorName', first_book.get('author', 'Unknown Author'))

            print(f"📂 File organization: Author/Book Title/")
            print(f"   Example: {author}/{title}/")

        total_duration = 0
        total_size = 0

        print(f"\n📖 Selected Books:")
        print("-" * 50)
        for i, book in enumerate(selected_books, 1):
            # Extract book details
            media = book.get('media', {})
            metadata = media.get('metadata', {})
            title = metadata.get('title', book.get('title', 'Unknown'))
            author = metadata.get('authorName', book.get('author', 'Unknown'))
            duration = media.get('duration', book.get('duration', 0))
            size = media.get('size', book.get('size', 0))

            total_duration += duration
            total_size += size

            # Format duration
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

            # Format size
            if size > 1024**3:  # GB
                size_str = f"{size / (1024**3):.1f} GB"
            elif size > 1024**2:  # MB
                size_str = f"{size / (1024**2):.1f} MB"
            else:  # KB
                size_str = f"{size / 1024:.1f} KB"

            print(f"{i:2d}. {title}")
            print(f"    Author: {author}")
            print(f"    Duration: {duration_str}")
            print(f"    Size: {size_str}")
            print()

        # Show totals
        total_hours = int(total_duration // 3600)
        total_minutes = int((total_duration % 3600) // 60)
        total_duration_str = f"{total_hours}h {total_minutes}m" if total_hours > 0 else f"{total_minutes}m"

        if total_size > 1024**3:  # GB
            total_size_str = f"{total_size / (1024**3):.1f} GB"
        elif total_size > 1024**2:  # MB
            total_size_str = f"{total_size / (1024**2):.1f} MB"
        else:  # KB
            total_size_str = f"{total_size / 1024:.1f} KB"

        print(f"📊 Totals:")
        print(f"  Total Duration: {total_duration_str}")
        print(f"  Total Size: {total_size_str}")
        print(f"  Estimated Time: {len(selected_books) * 2} minutes (rough estimate)")

        # Confirm download
        print(f"\n🚀 Ready to download {len(selected_books)} books!")
        response = input("Continue? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Download cancelled!")
            return False

        # Download selected books using concurrent download
        print("\n📥 Starting download...")

        # Use the downloader's concurrent download method
        results = await self.downloader.download_selected_books(selected_books, self.library_id)

        print(f"\n🎉 Download complete!")
        print(f"  ✅ Successfully downloaded: {results['success']}")
        print(f"  ❌ Failed: {results['failed']}")

        return results['success'] > 0

    async def _select_missing_books(self, books: List[Dict]):
        """Select books that are missing from another server."""
        print("\n🔄 Select Missing Books")
        print("=" * 30)
        print("This will compare with another Audiobookshelf server and select books that are missing.")

        # Try to get target server from API key manager
        target_url = None
        target_key = None
        target_download_path = None

        try:
            from api_key_manager import APIKeyManager
            manager = APIKeyManager()
            keys = manager.list_keys()

            if keys:
                if len(keys) == 1:
                    print("❌ Only one API key found. You need at least 2 servers to compare.")
                    print("Add another server with: python api_key_manager.py")
                    input("Press Enter to continue...")
                    return

                print("\n📋 Available servers:")
                for i, key in enumerate(keys):
                    print(f"  {i+1}. {key['name']}")

                print(f"  {len(keys)+1}. Enter manual connection details")

                try:
                    choice = int(input(f"\nSelect target server (1-{len(keys)+1}): ")) - 1
                    if 0 <= choice < len(keys):
                        # Use selected API key
                        selected_key = keys[choice]
                        target_url, target_key, target_download_path = manager.get_key(selected_key['name'])
                        print(f"🔑 Using server: {selected_key['name']}")
                    elif choice == len(keys):
                        # Manual entry
                        target_url = input("Target server URL (e.g., https://audiobooks.example.com): ").strip()
                        if not target_url.startswith(('http://', 'https://')):
                            target_url = f"https://{target_url}"
                        target_key = input("Target server API key: ").strip()
                    else:
                        print("❌ Invalid choice!")
                        input("Press Enter to continue...")
                        return
                except ValueError:
                    print("❌ Invalid input!")
                    input("Press Enter to continue...")
                    return
            else:
                print("❌ No API keys found! Add servers with: python api_key_manager.py")
                input("Press Enter to continue...")
                return

        except ImportError:
            # Fallback to manual entry if API key manager not available
            print("📝 API key manager not available, using manual entry...")
            target_url = input("Target server URL (e.g., https://audiobooks.example.com): ").strip()
            if not target_url.startswith(('http://', 'https://')):
                target_url = f"https://{target_url}"
            target_key = input("Target server API key: ").strip()

        if not target_url or not target_key:
            print("❌ Missing server details!")
            input("Press Enter to continue...")
            return

        print("\n🔌 Connecting to target server...")

        try:
            # Create target server connection
            target_downloader = AudiobookshelfDownloader(target_url, target_key, target_download_path)

            async with target_downloader:
                # Test connection
                if not await target_downloader.test_connection():
                    print("❌ Failed to connect to target server!")
                    input("Press Enter to continue...")
                    return

                print("✅ Connected to target server!")

                # Get target server books
                target_libraries = await target_downloader.get_libraries()
                if not target_libraries:
                    print("❌ No libraries found on target server!")
                    input("Press Enter to continue...")
                    return

                target_books = []
                for library in target_libraries:
                    library_books = await target_downloader.get_library_items(library['id'])
                    target_books.extend(library_books)

                print(f"📚 Found {len(target_books)} books on target server")

                # Create comparison keys
                def create_book_key(book):
                    media = book.get('media', {})
                    metadata = media.get('metadata', {})
                    title = metadata.get('title', book.get('title', 'Unknown Title'))
                    author = metadata.get('authorName', book.get('author', 'Unknown Author'))

                    # Normalize for comparison
                    import re
                    norm_title = re.sub(r'[^\w\s]', '', title.lower())
                    norm_title = ' '.join(norm_title.split())
                    norm_author = re.sub(r'[^\w\s]', '', author.lower())
                    norm_author = ' '.join(norm_author.split())

                    return f"{norm_author}|{norm_title}"

                # Create sets of book keys
                current_keys = {create_book_key(book) for book in books}
                target_keys = {create_book_key(book) for book in target_books}

                # Find missing books
                missing_keys = current_keys - target_keys
                missing_books = [book for book in books if create_book_key(book) in missing_keys]

                print(f"📥 Found {len(missing_books)} books missing from target server")

                if missing_books:
                    print("\n📋 Missing books:")
                    for i, book in enumerate(missing_books[:10], 1):  # Show first 10
                        media = book.get('media', {})
                        metadata = media.get('metadata', {})
                        title = metadata.get('title', book.get('title', 'Unknown'))
                        author = metadata.get('authorName', book.get('author', 'Unknown'))
                        print(f"   {i}. {title} by {author}")

                    if len(missing_books) > 10:
                        print(f"   ... and {len(missing_books) - 10} more")

                    response = input(f"\nSelect all {len(missing_books)} missing books? (y/N): ").strip().lower()
                    if response == 'y':
                        # Clear current selection and select missing books
                        self.selected_books.clear()
                        for book in missing_books:
                            self.selected_books.add(book.get('id', ''))
                        print(f"✅ Selected {len(missing_books)} missing books!")
                    else:
                        print("❌ Selection cancelled")
                else:
                    print("✅ No missing books found! All books are already on the target server.")

        except Exception as e:
            print(f"❌ Error: {e}")

        input("Press Enter to continue...")


async def main(download_path=None, server_url=None, api_key=None):
    """Main function for book selection."""
    print("🎧 Audiobookshelf Book Selector")
    print("=" * 40)

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

    # Initialize downloader with optional download path
    async with AudiobookshelfDownloader(server_url, api_key, download_path) as downloader:
        # Test connection
        if not await downloader.test_connection():
            print("❌ Failed to connect to server!")
            return

        # Get libraries
        libraries = await downloader.get_libraries()
        if not libraries:
            print("❌ No libraries found!")
            return

        # Choose library
        print("\n📚 Available Libraries:")
        for i, lib in enumerate(libraries):
            print(f"  {i+1}. {lib.get('name', 'Unknown')} (ID: {lib.get('id', 'Unknown')})")

        try:
            choice = int(input("\nSelect library (1-{}): ".format(len(libraries)))) - 1
            if not 0 <= choice < len(libraries):
                print("❌ Invalid choice!")
                return
        except ValueError:
            print("❌ Invalid input!")
            return

        library = libraries[choice]
        library_id = library['id']
        library_name = library['name']

        print(f"\n📖 Loading books from '{library_name}'...")

        # Get books
        books = await downloader.get_library_items(library_id)
        if not books:
            print("❌ No books found in library!")
            return

        # Select books
        selector = BookSelector(downloader, library_id)
        selected_books = await selector.select_books_interactive(books)

        if not selected_books:
            print("❌ No books selected!")
            return


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Select and download books from Audiobookshelf')
        parser.add_argument('--download-path', '-d', help='Directory to save downloaded books', default=None)
        args = parser.parse_args()

        asyncio.run(main(download_path=args.download_path))
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
