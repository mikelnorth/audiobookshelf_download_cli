#!/usr/bin/env python3
"""
Audiobookshelf Server Diff Tool

Compare two Audiobookshelf servers and identify missing books
"""

import asyncio
import aiohttp
import sys
import logging
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Optional, Set, Tuple
from audiobookshelf_downloader import AudiobookshelfDownloader
# Default logging configuration
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Configure logging
logging.basicConfig(level=getattr(logging, DEFAULT_LOG_LEVEL), format=DEFAULT_LOG_FORMAT)
logger = logging.getLogger(__name__)


class ServerDiff:
    def __init__(
        self,
        source_server: AudiobookshelfDownloader,
        target_server: AudiobookshelfDownloader,
        source_library_ids: Optional[Iterable[str]] = None,
        target_library_ids: Optional[Iterable[str]] = None,
        source_preferred_library_id: Optional[str] = None,
        target_preferred_library_id: Optional[str] = None,
    ):
        self.source_server = source_server
        self.target_server = target_server
        self.source_library_ids = self._normalize_library_ids(source_library_ids)
        self.target_library_ids = self._normalize_library_ids(target_library_ids)
        self.source_preferred_library_id = self._validate_preferred_library(
            self.source_library_ids, source_preferred_library_id
        )
        self.target_preferred_library_id = self._validate_preferred_library(
            self.target_library_ids, target_preferred_library_id
        )

    def _normalize_library_ids(self, library_ids: Optional[Iterable[str]]) -> Optional[Set[str]]:
        if not library_ids:
            return None
        return {lib_id for lib_id in library_ids if lib_id}

    def _validate_preferred_library(
        self,
        library_ids: Optional[Set[str]],
        preferred_id: Optional[str],
    ) -> Optional[str]:
        if library_ids is None or preferred_id is None:
            return preferred_id

        if preferred_id in library_ids:
            return preferred_id

        if library_ids:
            fallback = next(iter(library_ids))
            logger.warning(
                "⚠️  Preferred library %s not in selected library set; using %s instead.",
                preferred_id,
                fallback,
            )
            return fallback

        return None

    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison with improved subtitle handling"""
        import re
        import unicodedata

        # Normalize Unicode characters (handles different encodings)
        title = unicodedata.normalize('NFKD', title)

        # Convert to lowercase
        title = title.lower()

        # Replace various Unicode spaces and dashes with standard ones
        title = re.sub(r'[\u00A0\u2000-\u200B\u2060\uFEFF]', ' ', title)  # Various spaces
        title = re.sub(r'[\u2010-\u2015\u2212]', '-', title)  # Various dashes
        title = re.sub(r'[\u2018\u2019\u201C\u201D]', "'", title)  # Various quotes

        # Handle newline-separated titles (common in audiobook metadata)
        # "Scars and Stripes\nAn Unapologetically American Story..." -> "Scars and Stripes"
        if '\n' in title:
            lines = title.split('\n')
            # Use first non-empty line as the main title
            for line in lines:
                line = line.strip()
                if line:
                    title = line
                    break

        # Handle edition info in parentheses first (before other processing)
        # "Be Useful (German edition)" -> "Be Useful"
        # "Harry Potter (Illustrated Edition)" -> "Harry Potter"
        title = re.sub(r'\s*\([^)]*edition[^)]*\)\s*$', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\([^)]*version[^)]*\)\s*$', '', title, flags=re.IGNORECASE)

        # Handle subtitles separated by colon
        # "Steelheart: A Reckoners Novel" -> "Steelheart"
        if ':' in title:
            title = title.split(':')[0].strip()

        # Handle subtitles separated by dash (common in non-English titles and series info)
        # "Be Useful - Sieben einfache Regeln für ein besseres Leben" -> "Be Useful"
        # "Mitosis - A Reckoners Story" -> "Mitosis"
        # But be careful not to split hyphenated words
        if ' - ' in title:
            parts = title.split(' - ')
            # Use first part if we have exactly 2 parts and the second part looks like a subtitle
            # (2 or more words, or contains series-related keywords)
            if len(parts) == 2:
                second_part = parts[1].strip().lower()
                # Check if it's likely a subtitle/series info
                if (len(parts[1].split()) >= 2 or
                    any(keyword in second_part for keyword in ['story', 'novel', 'series', 'tale', 'book', 'edition'])):
                    title = parts[0].strip()

        # Handle series info in parentheses
        # "The Way of Kings (The Stormlight Archive, Book 1)" -> "The Way of Kings"
        title = re.sub(r'\s*\([^)]*\)\s*$', '', title)

        # Handle common series numbering variations
        title = re.sub(r'\s*\bbook\s+\d+\b\s*', '', title, flags=re.IGNORECASE)  # Remove "Book 1", etc.
        title = re.sub(r'\s*\bbk\s+\d+\b\s*', '', title, flags=re.IGNORECASE)  # Remove "bk 1", etc.
        title = re.sub(r'\s*#\d+\b\s*', '', title)  # Remove "#1", etc.
        title = re.sub(r'\s*\bvolume\s+\d+\b\s*', '', title, flags=re.IGNORECASE)  # Remove "Volume 1", etc.
        title = re.sub(r'\s*\bvol\.?\s+\d+\b\s*', '', title, flags=re.IGNORECASE)  # Remove "Vol 1", "Vol. 1", etc.
        title = re.sub(r'\s*\bpart\s+\d+\b\s*', '', title, flags=re.IGNORECASE)  # Remove "Part 1", etc.
        title = re.sub(r'\s*\bepisode\s+\d+\b\s*', '', title, flags=re.IGNORECASE)  # Remove "Episode 1", etc.

        # Handle series information in titles
        # "The Ghost Next Door - Goosebumps Series, Book 10" -> "The Ghost Next Door"
        title = re.sub(r'\s*-\s*[^-]*\bseries\b[^-]*$', '', title, flags=re.IGNORECASE)

        # Handle author names in titles (common in audiobook metadata)
        # "R.L. Stine - Goosebumps - The Haunted Mask II" -> "The Haunted Mask II"
        # Look for pattern: "Author Name - Series - Title" or "Author Name - Title"
        author_in_title_pattern = r'^[A-Za-z\.\s]+ - (?:[A-Za-z\s]+ - )?(.+)$'
        match = re.match(author_in_title_pattern, title)
        if match:
            title = match.group(1)

        # Remove articles at the beginning for better matching
        title = re.sub(r'^\s*(the|a|an)\s+', '', title, flags=re.IGNORECASE)

        # Remove special characters but keep spaces
        title = re.sub(r'[^\w\s]', '', title)

        # Normalize whitespace
        title = ' '.join(title.split())

        return title

    def _normalize_author(self, author: str) -> str:
        """Normalize author for comparison with better name handling"""
        import re
        import unicodedata

        # Normalize Unicode characters (handles different encodings)
        author = unicodedata.normalize('NFKD', author)

        # Convert to lowercase
        author = author.lower()

        # Replace various Unicode spaces and dashes with standard ones
        author = re.sub(r'[\u00A0\u2000-\u200B\u2060\uFEFF]', ' ', author)  # Various spaces
        author = re.sub(r'[\u2010-\u2015\u2212]', '-', author)  # Various dashes

        # Remove common suffixes
        author = re.sub(r'\s*(jr\.?|sr\.?|iii?|iv)\s*$', '', author, flags=re.IGNORECASE)

        # Handle multiple authors - use only the first author for matching
        # "R. L. Stine/Emily Eiden" -> "R. L. Stine"
        # "Robert Louis Stevenson, Marty Ross - adaptation" -> "Robert Louis Stevenson"
        if '/' in author:
            author = author.split('/')[0].strip()
        elif ',' in author:
            # Check if it's "Last, First" format or multiple authors
            parts = author.split(',')

            # Special handling for foreword/introduction contributors
            # "Chrissie Wellington, Lance Armstrong - foreward" -> "Chrissie Wellington"
            # "Lance Armstrong, Chrissie Wellington" -> need to detect primary author
            if len(parts) == 2:
                first_part = parts[0].strip()
                second_part = parts[1].strip()

                # Check if second part indicates a contribution type (foreword, introduction, etc.)
                if any(contrib in second_part.lower() for contrib in ['foreword', 'foreward', 'introduction', 'preface', 'afterword']):
                    # First author is the primary author
                    author = first_part
                # Check if it's "Last, First" format
                elif (len(second_part.split()) <= 2 and
                      len(first_part.split()) == 1 and  # Surname should be 1 word for "Last, First"
                      not any(word in second_part.lower() for word in ['adaptation', 'narrator', 'reader']) and
                      not any(word in first_part.lower() for word in ['author', 'writer'])):
                    # Likely "Last, First" format - convert to "First Last"
                    author = f"{second_part} {first_part}"
                else:
                    # Multiple authors - try to identify the primary author
                    # Special case: if one author appears to be a contributor in other contexts
                    # For "Lance Armstrong, Chrissie Wellington" vs "Chrissie Wellington, Lance Armstrong - foreward"
                    # We should normalize both to "Chrissie Wellington" since Lance is often the foreword contributor

                    # Create a set of both authors for comparison
                    author_set = {first_part.lower().strip(), second_part.lower().strip()}

                    # Known cases where author order varies but primary author is consistent
                    known_primary_authors = {
                        'chrissie wellington': ['lance armstrong'],  # Lance often writes forewords for Chrissie's books
                    }

                    # Check if we can identify a primary author from known patterns
                    primary_found = False
                    for primary, contributors in known_primary_authors.items():
                        if primary in author_set and any(contrib in author_set for contrib in contributors):
                            author = primary  # Use the known primary author (already lowercase)
                            primary_found = True
                            break

                    if not primary_found:
                        # Always use the first author as the primary author
                        # This handles cases like:
                        # "Spencer Johnson, Kenneth Blanchard" → "Spencer Johnson"
                        # "Tim S. Grover, Shari Wenk" → "Tim S. Grover"
                        # The first author is typically the main author
                        author = first_part.strip().lower()
            else:
                # More than 2 parts - use first author
                author = parts[0].strip()

        # Remove adaptation/narrator/translator credits
        # "Marty Ross - adaptation" -> "Marty Ross"
        # "Ken Liu - Translator Baoshu" -> "Baoshu" (extract actual author after translator)

        # Handle translator credits specially - extract the actual author after "translator"
        translator_match = re.search(r'\s*-\s*translator\s+(.+)$', author, flags=re.IGNORECASE)
        if translator_match:
            author = translator_match.group(1).strip()  # Use the actual author after "translator"
        else:
            # Handle other credits (adaptation, narrator, etc.)
            author = re.sub(r'\s*-\s*(adaptation|narrator|reader|performed by).*$', '', author, flags=re.IGNORECASE)

        # Remove publisher/audiobook company names
        # "Goosebumps Audiobooks!" -> "" (will be handled as unknown)
        audiobook_publishers = ['audiobooks?!?', 'audio books?', 'recorded books?', 'blackstone audio']
        for publisher in audiobook_publishers:
            if re.search(publisher, author, re.IGNORECASE):
                author = ''  # Clear author if it's just a publisher
                break

        # Normalize initials - handle spacing variations in initials
        # "R. L. Stine" -> "R L Stine", "R.L. Stine" -> "R L Stine"
        # This handles patterns like "J.K.", "J. K.", "J.R.R.", "J. R. R.", etc.

        # First, standardize periods and spaces in initial patterns
        # Match sequences of 1-3 letters followed by optional periods and spaces
        def normalize_initials(match):
            text = match.group(0)
            # Extract just the letters, removing periods and extra spaces
            letters = re.findall(r'[a-zA-Z]', text)
            # Join with single spaces: "R.L." or "R. L." -> "R L"
            return ' '.join(letters)

        # Pattern for initials: 1-3 capital letters with optional periods/spaces
        # Matches: "R.L.", "R. L.", "J.R.R.", "J. R. R.", etc.
        author = re.sub(r'\b[A-Za-z]\.?\s*[A-Za-z]\.?\s*[A-Za-z]?\.?\b', normalize_initials, author)

        # Remove any remaining special characters but keep spaces
        author = re.sub(r'[^\w\s]', '', author)

        # Normalize whitespace (remove extra spaces)
        author = ' '.join(author.split())

        return author

    def _extract_book_metadata(self, book: Dict) -> Dict:
        """Extract normalized metadata from book for comparison"""
        media = book.get('media', {})
        metadata = media.get('metadata', {})

        # Basic info
        title = metadata.get('title', book.get('title', 'Unknown Title'))
        author = metadata.get('authorName', book.get('author', 'Unknown Author'))

        # Duration (in seconds, converted from various formats)
        duration = 0

        # Try getting duration from media level first (this is where it usually is)
        if 'duration' in media:
            duration = media['duration']
        elif 'duration' in metadata:
            duration = metadata['duration']
        elif 'audioFile' in media and media['audioFile']:
            # Try to get duration from audio file
            audio_file = media['audioFile']
            if isinstance(audio_file, list) and audio_file:
                duration = audio_file[0].get('duration', 0)
            elif isinstance(audio_file, dict):
                duration = audio_file.get('duration', 0)

        # File size (in bytes)
        size = 0
        if 'size' in book:
            size = book['size']
        elif 'audioFile' in media and media['audioFile']:
            # Try to get size from audio file
            audio_file = media['audioFile']
            if isinstance(audio_file, list) and audio_file:
                size = sum(f.get('size', 0) for f in audio_file)
            elif isinstance(audio_file, dict):
                size = audio_file.get('size', 0)

        # Normalize for comparison
        norm_title = self._normalize_title(title)
        norm_author = self._normalize_author(author)

        return {
            'title': norm_title,
            'author': norm_author,
            'duration': duration,
            'size': size,
            'raw_title': title,
            'raw_author': author
        }

    def _extract_all_authors(self, author_string: str) -> set:
        """Extract all authors from an author string and return as a normalized set"""
        if not author_string:
            return {'unknown'}

        authors_list = []

        # Split by different separators to extract all authors
        if '/' in author_string:
            # Split by slash: "R. L. Stine/Emily Eiden"
            authors_list = [a.strip() for a in author_string.split('/')]
        elif ',' in author_string:
            parts = author_string.split(',')

            # Handle "Last, First" format detection
            if (len(parts) == 2 and
                len(parts[1].strip().split()) <= 2 and
                len(parts[0].strip().split()) == 1 and  # Surname should be 1 word for "Last, First"
                not any(word in parts[1].lower() for word in ['adaptation', 'narrator', 'reader', 'foreword', 'foreward', 'introduction']) and
                not any(word in parts[0].lower() for word in ['author', 'writer'])):
                # "Last, First" format - convert to "First Last"
                author = f"{parts[1].strip()} {parts[0].strip()}"
                authors_list = [author]
            else:
                # Multiple authors: "Spencer Johnson, Kenneth Blanchard"
                authors_list = [a.strip() for a in parts]
        else:
            # Single author
            authors_list = [author_string]

        # Normalize each author using the existing normalization logic
        normalized_authors = set()
        for auth in authors_list:
            # Use existing normalization but without the multi-author splitting
            normalized = self._normalize_single_author(auth)
            if normalized and normalized != 'unknown':
                normalized_authors.add(normalized)

        return normalized_authors if normalized_authors else {'unknown'}

    def _normalize_single_author(self, author: str) -> str:
        """Normalize a single author name (helper for _extract_all_authors)"""
        if not author:
            return 'unknown'

        import re
        import unicodedata

        # Normalize Unicode characters
        author = unicodedata.normalize('NFKD', author)
        author = author.lower()

        # Replace various Unicode spaces and dashes
        author = re.sub(r'[\u00A0\u2000-\u200B\u2060\uFEFF]', ' ', author)
        author = re.sub(r'[\u2010-\u2015\u2212]', '-', author)

        # Remove contribution indicators
        author = re.sub(r'\s*-\s*(foreword|foreward|introduction|preface|afterword|adaptation|narrator|reader|performed by).*$', '', author, flags=re.IGNORECASE)

        # Handle translator credits specially
        translator_match = re.search(r'\s*-\s*translator\s+(.+)$', author, flags=re.IGNORECASE)
        if translator_match:
            author = translator_match.group(1).strip()

        # Remove common suffixes
        author = re.sub(r'\s*(jr\.?|sr\.?|iii?|iv)\s*$', '', author, flags=re.IGNORECASE)

        # Remove publisher/audiobook company names
        audiobook_publishers = ['audiobooks?!?', 'audio books?', 'recorded books?', 'blackstone audio']
        if any(pub in author.lower() for pub in audiobook_publishers):
            return 'unknown'

        # Normalize initials
        def normalize_initials(match):
            initials = match.group(0)
            initials = re.sub(r'\.', '', initials)
            initials = re.sub(r'\s+', ' ', initials)
            return initials.strip()

        author = re.sub(r'\b[A-Za-z]\.?\s*[A-Za-z]\.?\s*[A-Za-z]?\.?\b', normalize_initials, author)

        # Remove remaining special characters
        author = re.sub(r'[^\w\s]', '', author)

        # Normalize whitespace
        author = ' '.join(author.split())

        return author if len(author) > 2 else 'unknown'

    def _authors_overlap(self, author1: str, author2: str) -> bool:
        """Check if two author strings have any authors in common"""
        authors1 = self._extract_all_authors(author1)
        authors2 = self._extract_all_authors(author2)

        # Check for any overlap
        return bool(authors1 & authors2)

    def _create_book_key(self, book: Dict) -> str:
        """Create a unique key for book comparison (primary matching)

        Returns normalized metadata key for cross-server comparison
        """
        metadata = self._extract_book_metadata(book)
        return f"{metadata['author']}|{metadata['title']}"

    def _create_title_key(self, book: Dict) -> str:
        """Create a title-only key for author overlap matching"""
        metadata = self._extract_book_metadata(book)
        return metadata['title']

    def _create_fallback_key(self, book: Dict) -> str:
        """Create a fallback key for books with same title+duration+size but different authors"""
        metadata = self._extract_book_metadata(book)
        # Use fallback if we have meaningful size (duration is optional)
        if metadata['size'] > 0:
            # Include duration if available, otherwise use 'unknown'
            duration_key = metadata['duration'] if metadata['duration'] > 0 else 'unknown'
            return f"{metadata['title']}|{duration_key}|{metadata['size']}"
        return None

    def _create_flexible_fallback_key(self, book: Dict) -> str:
        """Create a more flexible fallback key with tolerance ranges"""
        metadata = self._extract_book_metadata(book)

        if metadata['size'] > 0:
            # Round duration to nearest 5 minutes (300 seconds) for tolerance, or use 'unknown'
            if metadata['duration'] > 0:
                duration_rounded = round(metadata['duration'] / 300) * 300
            else:
                duration_rounded = 'unknown'

            # Round size to nearest 10MB for tolerance
            size_rounded = round(metadata['size'] / (10 * 1024 * 1024)) * (10 * 1024 * 1024)

            # Use first 3 significant words of title for fuzzy matching
            title_words = metadata['title'].split()[:3]
            title_key = ' '.join(title_words) if title_words else metadata['title']

            return f"{title_key}|{duration_rounded}|{size_rounded}"
        return None

    def debug_book_matching(self, title1: str, author1: str, title2: str, author2: str,
                          duration1: int = 0, size1: int = 0, duration2: int = 0, size2: int = 0) -> bool:
        """Debug helper to see how two books would match with enhanced criteria"""
        norm_title1 = self._normalize_title(title1)
        norm_author1 = self._normalize_author(author1)
        norm_title2 = self._normalize_title(title2)
        norm_author2 = self._normalize_author(author2)

        # Primary matching (author + title)
        primary_key1 = f"{norm_author1}|{norm_title1}"
        primary_key2 = f"{norm_author2}|{norm_title2}"
        primary_match = primary_key1 == primary_key2

        print(f"📚 Enhanced Book Matching Debug:")
        print(f"   Book 1: '{title1}' by '{author1}'")
        print(f"   → Normalized: '{norm_title1}' by '{norm_author1}'")
        print(f"   → Primary Key: '{primary_key1}'")
        if duration1 > 0 or size1 > 0:
            print(f"   → Duration: {duration1}s, Size: {size1} bytes")
        print()
        print(f"   Book 2: '{title2}' by '{author2}'")
        print(f"   → Normalized: '{norm_title2}' by '{norm_author2}'")
        print(f"   → Primary Key: '{primary_key2}'")
        if duration2 > 0 or size2 > 0:
            print(f"   → Duration: {duration2}s, Size: {size2} bytes")
        print()

        # Check primary match
        print(f"   Primary Match (author+title): {'✅ YES' if primary_match else '❌ NO'}")

        # Check fallback match if primary fails
        fallback_match = False
        if not primary_match and norm_title1 == norm_title2:
            if duration1 > 0 and size1 > 0 and duration2 > 0 and size2 > 0:
                if duration1 == duration2 and size1 == size2:
                    fallback_match = True
                    print(f"   Fallback Match (title+duration+size): ✅ YES")
                else:
                    print(f"   Fallback Match (title+duration+size): ❌ NO")
                    print(f"      Title match: {'✅' if norm_title1 == norm_title2 else '❌'}")
                    print(f"      Duration match: {'✅' if duration1 == duration2 else '❌'} ({duration1} vs {duration2})")
                    print(f"      Size match: {'✅' if size1 == size2 else '❌'} ({size1} vs {size2})")
            else:
                print(f"   Fallback Match: ❌ NO (insufficient duration/size data)")

        final_match = primary_match or fallback_match
        print(f"   Final Result: {'✅ MATCH' if final_match else '❌ NO MATCH'}")

        return final_match

    async def download_missing_books(
        self,
        server: AudiobookshelfDownloader,
        missing_books: List[Dict],
        preferred_library_id: Optional[str] = None,
    ):
        """Download missing books to a server."""
        if not missing_books:
            print("✅ No books to download!")
            return

        print(f"🚀 Starting download of {len(missing_books)} books...")

        # Prepare books for download
        books_to_download = []
        for item in missing_books:
            books_to_download.append(item['book'])

        # Get the library ID (use the first library)
        if preferred_library_id is None:
            if server is self.source_server:
                preferred_library_id = self.source_preferred_library_id
            elif server is self.target_server:
                preferred_library_id = self.target_preferred_library_id

        libraries = await server.get_libraries()
        if not libraries:
            print("❌ No libraries found on target server!")
            return

        library_id = None

        if preferred_library_id:
            for library in libraries:
                if library['id'] == preferred_library_id:
                    library_id = library['id']
                    break
            if library_id is None:
                print(
                    "⚠️  Preferred library not found on server, defaulting to first available library."
                )

        if library_id is None:
            library_id = libraries[0]['id']

        # Download the books
        success_count = 0
        for i, book in enumerate(books_to_download, 1):
            # Extract book details
            media = book.get('media', {})
            metadata = media.get('metadata', {})
            title = metadata.get('title', book.get('title', 'Unknown'))
            author = metadata.get('authorName', book.get('author', 'Unknown'))

            print(f"\n📖 Downloading {i}/{len(books_to_download)}: {title} by {author}")

            if await server.download_book(book, library_id):
                success_count += 1
                print(f"✅ Successfully downloaded: {title}")
            else:
                print(f"❌ Failed to download: {title}")

        print(f"\n🎉 Download complete!")
        print(f"  ✅ Successfully downloaded: {success_count}")
        print(f"  ❌ Failed: {len(books_to_download) - success_count}")

    async def get_server_books(
        self,
        server: AudiobookshelfDownloader,
        library_filter: Optional[Set[str]] = None,
    ) -> Dict[str, Dict]:
        """Get all books from a server, indexed by unique item ID

        Each item is stored separately (no collapsing of editions)
        """
        books = {}

        try:
            libraries = await server.get_libraries()
            if not libraries:
                logger.warning("No libraries found on server")
                return books

            for library in libraries:
                library_id = library['id']
                if library_filter is not None and library_id not in library_filter:
                    logger.info(
                        f"⏭️  Skipping library {library.get('name', 'Unknown Library')} ({library_id})"
                    )
                    continue
                library_books = await server.get_library_items(library_id)

                for book in library_books:
                    # Use unique book ID as storage key (never collapses anything)
                    book_id = book.get('id')
                    if not book_id:
                        logger.warning("⚠️  Book without ID found, skipping")
                        continue

                    books[book_id] = {
                        'book': book,
                        'library_id': library_id,
                        'library_name': library.get('name', 'Unknown Library')
                    }

            logger.info(f"📚 Loaded {len(books)} items from server")

        except Exception as e:
            logger.error(f"Error getting books from server: {e}")

        return books

    async def compare_servers(self) -> Dict[str, List[Dict]]:
        """Compare two servers and return missing books with enhanced matching

        Compares ALL items individually, groups by normalized metadata for matching
        """
        logger.info("🔍 Comparing servers...")

        # Get ALL items from both servers (by unique ID, no collapsing)
        source_books = await self.get_server_books(
            self.source_server,
            self.source_library_ids,
        )
        target_books = await self.get_server_books(
            self.target_server,
            self.target_library_ids,
        )

        logger.info(f"📚 Source server: {len(source_books)} items")
        logger.info(f"📚 Target server: {len(target_books)} items")

        # Group items by normalized metadata key for comparison
        source_by_metadata = {}  # normalized_key -> [list of item IDs]
        target_by_metadata = {}

        # Track detailed match information
        primary_match_groups: List[Dict] = []
        author_overlap_details: List[Dict] = []
        fallback_exact_details: List[Dict] = []
        fallback_flexible_details: List[Dict] = []

        for item_id, item_data in source_books.items():
            metadata_key = self._create_book_key(item_data['book'])
            if metadata_key not in source_by_metadata:
                source_by_metadata[metadata_key] = []
            source_by_metadata[metadata_key].append(item_id)

        for item_id, item_data in target_books.items():
            metadata_key = self._create_book_key(item_data['book'])
            if metadata_key not in target_by_metadata:
                target_by_metadata[metadata_key] = []
            target_by_metadata[metadata_key].append(item_id)

        # Primary matching: items with same normalized metadata
        matched_source_ids = set()
        matched_target_ids = set()

        for metadata_key in source_by_metadata:
            if metadata_key in target_by_metadata:
                source_ids = source_by_metadata[metadata_key]
                target_ids = target_by_metadata[metadata_key]

                # This book exists on both servers - mark ALL versions as matched
                matched_source_ids.update(source_ids)
                matched_target_ids.update(target_ids)

                # Capture detailed match information
                representative_source = source_books[source_ids[0]] if source_ids else None
                normalized_info = None
                if representative_source:
                    normalized_info = self._extract_book_metadata(representative_source['book'])

                primary_match_groups.append({
                    'match_type': 'primary',
                    'source_items': [source_books[item_id] for item_id in source_ids],
                    'target_items': [target_books[item_id] for item_id in target_ids],
                    'reason': 'Matched by normalized author and title',
                    'normalized': {
                        'title': normalized_info['title'] if normalized_info else None,
                        'author': normalized_info['author'] if normalized_info else None,
                        'key': metadata_key,
                    },
                })

        # Items that don't have a metadata match
        missing_in_target_primary = set(source_books.keys()) - matched_source_ids
        missing_in_source_primary = set(target_books.keys()) - matched_target_ids

        logger.info(f"🎯 Primary matches (author+title): {len(matched_source_ids)} items")
        logger.info(f"📤 Initially missing in target: {len(missing_in_target_primary)} items")
        logger.info(f"📥 Initially missing in source: {len(missing_in_source_primary)} items")

        # Author overlap matching: Check if books with same title have overlapping authors
        # This handles cases like "Spencer Johnson" vs "Spencer Johnson, Kenneth Blanchard"
        source_by_title = {}
        target_by_title = {}

        # Group unmatched books by title
        for key in missing_in_target_primary:
            book = source_books[key]
            title_key = self._create_title_key(book['book'])
            if title_key not in source_by_title:
                source_by_title[title_key] = []
            source_by_title[title_key].append((key, book))

        for key in missing_in_source_primary:
            book = target_books[key]
            title_key = self._create_title_key(book['book'])
            if title_key not in target_by_title:
                target_by_title[title_key] = []
            target_by_title[title_key].append((key, book))

        # Find author overlap matches
        author_overlap_matched_source = set()
        author_overlap_matched_target = set()

        for title_key in source_by_title:
            if title_key in target_by_title:
                # Same title exists in both - check for author overlap
                for source_key, source_book in source_by_title[title_key]:
                    if source_key in author_overlap_matched_source:
                        continue  # Already matched

                    source_metadata = self._extract_book_metadata(source_book['book'])
                    for target_key, target_book in target_by_title[title_key]:
                        if target_key in author_overlap_matched_target:
                            continue  # Already matched

                        target_metadata = self._extract_book_metadata(target_book['book'])

                        # IMPORTANT: Only match if BOTH same normalized title AND overlapping authors
                        if (source_metadata['title'] == target_metadata['title'] and
                            self._authors_overlap(source_metadata['raw_author'], target_metadata['raw_author'])):
                            author_overlap_matched_source.add(source_key)
                            author_overlap_matched_target.add(target_key)
                            author_overlap_details.append({
                                'match_type': 'author_overlap',
                                'source_items': [source_books[source_key]],
                                'target_items': [target_books[target_key]],
                                'reason': 'Matched by normalized title with overlapping authors',
                                'normalized': {
                                    'title': source_metadata['title'],
                                    'source_author': source_metadata['author'],
                                    'target_author': target_metadata['author'],
                                    'source_key': self._create_book_key(source_books[source_key]['book']),
                                    'target_key': self._create_book_key(target_books[target_key]['book']),
                                },
                            })
                            break  # Found a match for this source book

        # Remove author overlap matches from missing lists
        missing_in_target_primary -= author_overlap_matched_source
        missing_in_source_primary -= author_overlap_matched_target

        author_overlap_matches = len(author_overlap_matched_source)
        logger.info(f"👥 Author overlap matches: {author_overlap_matches}")
        logger.info(f"📤 After author overlap - missing in target: {len(missing_in_target_primary)}")
        logger.info(f"📥 After author overlap - missing in source: {len(missing_in_source_primary)}")

        # Fallback matching (title + duration + size) for remaining books
        fallback_matches = 0

        # Create exact fallback key mappings for unmatched books
        source_fallback_exact = {}
        target_fallback_exact = {}
        source_fallback_flexible = {}
        target_fallback_flexible = {}

        for key in missing_in_target_primary:
            book_data = source_books[key]
            metadata = self._extract_book_metadata(book_data['book'])


            # Exact fallback
            exact_key = self._create_fallback_key(book_data['book'])
            if exact_key:
                source_fallback_exact[exact_key] = key

            # Flexible fallback
            flexible_key = self._create_flexible_fallback_key(book_data['book'])
            if flexible_key:
                source_fallback_flexible[flexible_key] = key

        for key in missing_in_source_primary:
            book_data = target_books[key]
            metadata = self._extract_book_metadata(book_data['book'])


            # Exact fallback
            exact_key = self._create_fallback_key(book_data['book'])
            if exact_key:
                target_fallback_exact[exact_key] = key

            # Flexible fallback
            flexible_key = self._create_flexible_fallback_key(book_data['book'])
            if flexible_key:
                target_fallback_flexible[flexible_key] = key

        # Find exact fallback matches first
        exact_matched_keys = set(source_fallback_exact.keys()) & set(target_fallback_exact.keys())

        # Find flexible fallback matches (excluding already matched books)
        flexible_matched_keys = set(source_fallback_flexible.keys()) & set(target_fallback_flexible.keys())

        # Remove books already matched exactly from flexible matching
        already_matched_source = set()
        already_matched_target = set()

        for exact_key in exact_matched_keys:
            already_matched_source.add(source_fallback_exact[exact_key])
            already_matched_target.add(target_fallback_exact[exact_key])

        # Filter flexible matches to exclude already matched books
        flexible_matched_keys = {
            k for k in flexible_matched_keys
            if (source_fallback_flexible[k] not in already_matched_source and
                target_fallback_flexible[k] not in already_matched_target)
        }

        fallback_matched_keys = exact_matched_keys | flexible_matched_keys



        if fallback_matched_keys:
            logger.info(f"🔄 Checking fallback matches (title+duration+size)...")

            # Process exact matches
            for exact_key in exact_matched_keys:
                source_key = source_fallback_exact[exact_key]
                target_key = target_fallback_exact[exact_key]

                # Get book metadata for logging
                source_metadata = self._extract_book_metadata(source_books[source_key]['book'])
                target_metadata = self._extract_book_metadata(target_books[target_key]['book'])

                logger.info(f"✅ Exact fallback match: '{source_metadata['raw_title']}'")
                logger.info(f"   Source author: '{source_metadata['raw_author']}'")
                logger.info(f"   Target author: '{target_metadata['raw_author']}'")
                logger.info(f"   Duration: {source_metadata['duration']}s, Size: {source_metadata['size']} bytes")

                fallback_exact_details.append({
                    'match_type': 'fallback_exact',
                    'source_items': [source_books[source_key]],
                    'target_items': [target_books[target_key]],
                    'reason': 'Matched by title with identical duration and size',
                    'normalized': {
                        'title': source_metadata['title'],
                        'source_key': self._create_book_key(source_books[source_key]['book']),
                        'target_key': self._create_book_key(target_books[target_key]['book']),
                    },
                    'extra_details': {
                        'source_duration': source_metadata['duration'],
                        'target_duration': target_metadata['duration'],
                        'source_size': source_metadata['size'],
                        'target_size': target_metadata['size'],
                    },
                })

                # Remove from missing lists
                missing_in_target_primary.discard(source_key)
                missing_in_source_primary.discard(target_key)
                fallback_matches += 1

            # Process flexible matches
            for flexible_key in flexible_matched_keys:
                source_key = source_fallback_flexible[flexible_key]
                target_key = target_fallback_flexible[flexible_key]

                # Get book metadata for logging
                source_metadata = self._extract_book_metadata(source_books[source_key]['book'])
                target_metadata = self._extract_book_metadata(target_books[target_key]['book'])

                logger.info(f"✅ Flexible fallback match: '{source_metadata['raw_title']}'")
                logger.info(f"   vs '{target_metadata['raw_title']}'")
                logger.info(f"   Source author: '{source_metadata['raw_author']}'")
                logger.info(f"   Target author: '{target_metadata['raw_author']}'")
                logger.info(f"   Duration: ~{source_metadata['duration']}s, Size: ~{source_metadata['size']} bytes")

                fallback_flexible_details.append({
                    'match_type': 'fallback_flexible',
                    'source_items': [source_books[source_key]],
                    'target_items': [target_books[target_key]],
                    'reason': 'Matched by title with similar duration and size (tolerance applied)',
                    'normalized': {
                        'title': source_metadata['title'],
                        'source_key': self._create_book_key(source_books[source_key]['book']),
                        'target_key': self._create_book_key(target_books[target_key]['book']),
                    },
                    'extra_details': {
                        'source_duration': source_metadata['duration'],
                        'target_duration': target_metadata['duration'],
                        'source_size': source_metadata['size'],
                        'target_size': target_metadata['size'],
                    },
                })

                # Remove from missing lists
                missing_in_target_primary.discard(source_key)
                missing_in_source_primary.discard(target_key)
                fallback_matches += 1

        logger.info(f"🎯 Total matches: {len(matched_source_ids)} primary + {author_overlap_matches} author overlap + {fallback_matches} fallback = {len(matched_source_ids) + author_overlap_matches + fallback_matches}")

        result = {
            'missing_in_target': [source_books[key] for key in missing_in_target_primary],
            'missing_in_source': [target_books[key] for key in missing_in_source_primary],
            'common_books': [source_books[key] for key in matched_source_ids],
            'author_overlap_matches': author_overlap_matches,
            'fallback_matches': fallback_matches,
            'source_total': len(source_books),
            'target_total': len(target_books),
            'source_library_ids': self.source_library_ids,
            'target_library_ids': self.target_library_ids,
            'match_details': {
                'primary': primary_match_groups,
                'author_overlap': author_overlap_details,
                'fallback_exact': fallback_exact_details,
                'fallback_flexible': fallback_flexible_details,
            },
        }

        return result


    def print_comparison_results(self, results: Dict[str, List[Dict]]):
        """Pretty-print server comparison results."""
        if results is None:
            print("ℹ️ No results to display.")
            return

        missing_in_target = results.get('missing_in_target') or []
        missing_in_source = results.get('missing_in_source') or []
        common_books = results.get('common_books') or []
        author_overlap_matches = results.get('author_overlap_matches', 0)
        fallback_matches = results.get('fallback_matches', 0)
        source_total = results.get('source_total')
        target_total = results.get('target_total')

        print("\n📊 Comparison Summary")
        print("=" * 40)
        if source_total is not None and target_total is not None:
            print(f"  📥 Source items: {source_total}")
            print(f"  📊 Target items: {target_total}")
        print(f"  🤝 Common items: {len(common_books)}")
        print(f"  👥 Author overlap matches: {author_overlap_matches}")
        print(f"  🔄 Fallback matches: {fallback_matches}")
        print(f"  📤 Missing in target: {len(missing_in_target)}")
        print(f"  📥 Missing in source: {len(missing_in_source)}")

        def summarize_by_library(items: List[Dict]) -> Dict[str, int]:
            summary = defaultdict(int)
            for item in items:
                library_name = item.get('library_name') or 'Unknown Library'
                summary[library_name] += 1
            return dict(sorted(summary.items(), key=lambda kv: kv[0].lower()))

        def print_sample(items: List[Dict], label: str):
            if not items:
                return

            summary = summarize_by_library(items)
            print(f"\n{label} (by library):")
            for library_name, count in summary.items():
                print(f"  • {library_name}: {count}")

            max_preview = 10
            print(f"\nFirst {min(len(items), max_preview)} entries:")
            for idx, item in enumerate(items[:max_preview], 1):
                book = item.get('book', {})
                media = book.get('media', {})
                metadata = media.get('metadata', {})
                title = metadata.get('title', book.get('title', 'Unknown Title'))
                author = metadata.get('authorName', book.get('author', 'Unknown Author'))
                library_name = item.get('library_name', 'Unknown Library')
                print(f"  {idx}. {title} — {author} ({library_name})")

            if len(items) > max_preview:
                print(f"  … and {len(items) - max_preview} more")

        print_sample(missing_in_target, "📤 Missing on target")
        print_sample(missing_in_source, "📥 Missing on source")

        if not missing_in_target and not missing_in_source:
            print("\n✅ No missing books found! Both servers are in sync.")

    def print_match_details(self, results: Dict[str, List[Dict]], max_entries_per_type: int = 25):
        """Pretty-print detailed match information by match type."""
        match_details = results.get('match_details') if results else None
        if not match_details:
            print("ℹ️ No match details available.")
            return

        sections = [
            ('primary', "Primary matches (normalized author + title)"),
            ('author_overlap', "Author overlap matches"),
            ('fallback_exact', "Fallback matches (exact duration + size)"),
            ('fallback_flexible', "Fallback matches (fuzzy duration + size)"),
        ]

        print("\n🤝 Matched Items")
        print("=" * 50)

        for key, label in sections:
            entries = match_details.get(key, [])
            print(f"\n{label}: {len(entries)}")
            if not entries:
                continue

            limit = min(len(entries), max_entries_per_type)
            for idx in range(limit):
                entry = entries[idx]
                self._print_match_entry(idx + 1, entry)

            if len(entries) > max_entries_per_type:
                remaining = len(entries) - max_entries_per_type
                print(f"  … and {remaining} more")

    def _print_match_entry(self, index: int, entry: Dict):
        """Print a single match entry with context."""
        source_items = entry.get('source_items') or []
        target_items = entry.get('target_items') or []
        reason = entry.get('reason', '')
        normalized = entry.get('normalized', {}) or {}
        extra_details = entry.get('extra_details', {}) or {}

        display_item = source_items[0] if source_items else (target_items[0] if target_items else None)
        title = "Unknown Title"
        normalized_info = None
        if display_item:
            book = display_item.get('book', {})
            media = book.get('media', {})
            metadata = media.get('metadata', {})
            title = metadata.get('title', book.get('title', 'Unknown Title'))
            normalized_info = self._extract_book_metadata(book)

        print(f"  {index}. {title}")

        if source_items:
            print(f"     Source: {self._format_item_summary(source_items)}")
        if target_items:
            print(f"     Target: {self._format_item_summary(target_items)}")

        if normalized:
            normalized_title = normalized.get('title')
            normalized_author = normalized.get('author')
            source_author_norm = normalized.get('source_author')
            target_author_norm = normalized.get('target_author')
            normalized_key = normalized.get('key')
            source_key = normalized.get('source_key')
            target_key = normalized.get('target_key')

            normalized_segments = []
            if normalized_author or source_author_norm or target_author_norm:
                if normalized_author:
                    normalized_segments.append(f"author='{normalized_author}'")
                else:
                    if source_author_norm:
                        normalized_segments.append(f"source_author='{source_author_norm}'")
                    if target_author_norm:
                        normalized_segments.append(f"target_author='{target_author_norm}'")
            if normalized_title:
                normalized_segments.append(f"title='{normalized_title}'")
            if normalized_key:
                normalized_segments.append(f"key='{normalized_key}'")
            else:
                if source_key:
                    normalized_segments.append(f"source_key='{source_key}'")
                if target_key:
                    normalized_segments.append(f"target_key='{target_key}'")

            if normalized_segments:
                print(f"     Normalized: {', '.join(normalized_segments)}")
        elif normalized_info:
            print(
                f"     Normalized: author='{normalized_info['author']}', title='{normalized_info['title']}'"
            )

        if extra_details:
            duration_source = extra_details.get('source_duration')
            duration_target = extra_details.get('target_duration')
            size_source = extra_details.get('source_size')
            size_target = extra_details.get('target_size')

            detail_segments = []
            if duration_source is not None or duration_target is not None:
                detail_segments.append(
                    f"duration={duration_source}s vs {duration_target}s"
                )
            if size_source is not None or size_target is not None:
                detail_segments.append(
                    f"size={size_source} bytes vs {size_target} bytes"
                )
            if detail_segments:
                print(f"     Details: {', '.join(detail_segments)}")

        if reason:
            print(f"     Match reason: {reason}")

    def _format_item_summary(self, items: List[Dict]) -> str:
        """Summarize a list of items (from one server) for display."""
        if not items:
            return "(none)"

        primary = items[0]
        book = primary.get('book', {})
        media = book.get('media', {})
        metadata = media.get('metadata', {})
        author = metadata.get('authorName', book.get('author', 'Unknown Author'))

        libraries = [item.get('library_name', 'Unknown Library') for item in items]
        counts = Counter(libraries)
        library_summary = ', '.join(f"{name}×{count}" for name, count in counts.items())

        return f"{author} — {library_summary}"

async def select_library_for_server(server: AudiobookshelfDownloader, server_label: str):
    """Prompt the user to select a library for the given server."""
    libraries = await server.get_libraries()
    if not libraries:
        print(f"❌ No libraries found on '{server_label}'")
        return None, None, None

    if len(libraries) == 1:
        library = libraries[0]
        name = library.get('name', 'Unknown')
        print(f"📚 '{server_label}' library: {name} (ID: {library.get('id', 'Unknown')})")
        return {library['id']}, library['id'], name

    print(f"\n📚 Libraries available on '{server_label}':")
    for index, library in enumerate(libraries, 1):
        name = library.get('name', 'Unknown')
        library_id = library.get('id', 'Unknown')
        print(f"  {index}. {name} (ID: {library_id})")

    while True:
        choice = input(f"Select library for '{server_label}' (1-{len(libraries)}): ").strip()
        try:
            choice_index = int(choice) - 1
        except ValueError:
            print("❌ Invalid input! Enter the library number.")
            continue

        if 0 <= choice_index < len(libraries):
            library = libraries[choice_index]
            name = library.get('name', 'Unknown')
            print(f"✅ Selected '{name}' on '{server_label}'")
            return {library['id']}, library['id'], name

        print("❌ Invalid choice! Please try again.")


async def get_server_config(prompt: str) -> Tuple[str, str]:
    """Get server configuration from user"""
    print(f"\n{prompt}")
    server_url = input("Server URL (e.g., audiobooks.example.com or https://audiobooks.example.com): ").strip()
    if not server_url.startswith(('http://', 'https://')):
        server_url = f"https://{server_url}"
        print(f"🔧 Added https:// prefix: {server_url}")

    api_key = input("API Key: ").strip()

    return server_url, api_key


async def main():
    """Main function for server diff tool"""
    print("🔄 Audiobookshelf Server Diff Tool")
    print("=" * 40)
    print("Compare two Audiobookshelf servers and find missing books")

    try:
        # Get source server (where books will be downloaded from)
        print("\n📥 SOURCE SERVER (where to download books from)")
        source_url, source_key = await get_server_config("Enter source server details:")

        # Get target server (where books will be compared against)
        print("\n📊 TARGET SERVER (to compare against)")
        target_url, target_key = await get_server_config("Enter target server details:")

        # Create server connections
        print("\n🔌 Connecting to servers...")
        source_server = AudiobookshelfDownloader(source_url, source_key)
        target_server = AudiobookshelfDownloader(target_url, target_key)

        async with source_server, target_server:
            # Test connections
            if not await source_server.test_connection():
                print("❌ Failed to connect to source server!")
                return

            if not await target_server.test_connection():
                print("❌ Failed to connect to target server!")
                return

            print("✅ Connected to both servers!")

            source_library_ids, source_preferred_library_id, source_library_name = await select_library_for_server(
                source_server,
                "source",
            )
            if source_library_ids is None:
                return

            target_library_ids, target_preferred_library_id, target_library_name = await select_library_for_server(
                target_server,
                "target",
            )
            if target_library_ids is None:
                return

            print(
                f"\n🎯 Comparing libraries:\n"
                f"  📥 Source: {source_library_name}\n"
                f"  📊 Target: {target_library_name}"
            )

            # Create diff tool
            diff_tool = ServerDiff(
                source_server,
                target_server,
                source_library_ids=source_library_ids,
                target_library_ids=target_library_ids,
                source_preferred_library_id=source_preferred_library_id,
                target_preferred_library_id=target_preferred_library_id,
            )

            # Compare servers
            results = await diff_tool.compare_servers()

            # Print results
            diff_tool.print_comparison_results(results)

            # Ask what to do with missing books
            if results['missing_in_target']:
                print(f"\n🚀 Found {len(results['missing_in_target'])} books missing in target server!")
                print("Options:")
                print("1. Download missing books to source server")
                print("2. Download missing books to target server")
                print("3. Just show the list")
                print("4. Exit")

                choice = input("Enter choice (1-4): ").strip()

                if choice == "1":
                    # Download missing books to source server
                    print(f"\n📥 Downloading {len(results['missing_in_target'])} books to source server...")
                    await diff_tool.download_missing_books(source_server, results['missing_in_target'])
                elif choice == "2":
                    # Download missing books to target server
                    print(f"\n📥 Downloading {len(results['missing_in_target'])} books to target server...")
                    await diff_tool.download_missing_books(target_server, results['missing_in_target'])
                elif choice == "3":
                    print("\n📋 Complete list of missing books:")
                    for i, item in enumerate(results['missing_in_target'], 1):
                        book = item['book']
                        media = book.get('media', {})
                        metadata = media.get('metadata', {})
                        title = metadata.get('title', book.get('title', 'Unknown'))
                        author = metadata.get('authorName', book.get('author', 'Unknown'))
                        print(f"   {i}. {title} by {author}")
                else:
                    print("👋 Goodbye!")
            else:
                print("\n✅ No missing books found! Both servers have the same books.")

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
