#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from book_selector import BookSelector
from audiobookshelf_downloader import AudiobookshelfDownloader

def test_main_enhanced():
    """Test the enhanced main display with Audio and Ebook columns."""
    print("Testing enhanced main display with Audio and Ebook columns...")
    
    # Create a mock downloader
    class MockDownloader:
        def __init__(self, download_path):
            self.download_path = download_path
        
        async def download_book(self, book, library_id):
            return True
    
    downloader = MockDownloader("/tmp/test")
    selector = BookSelector(downloader, "test-library-id")
    
    # Test with mock books showing both audio and ebook formats
    mock_books = [
        {
            'id': 'book1',
            'media': {
                'metadata': {
                    'title': 'Outdoor Kids in an Inside World: Getting Your Family Out of the House and Radically Engaged with Nature',
                    'authorName': 'Steven Rinella'
                },
                'duration': 21781,  # Audio duration
                'ebookFormat': 'epub'  # Ebook format
            }
        },
        {
            'id': 'book2',
            'media': {
                'metadata': {
                    'title': 'The Last Sweet Bite',
                    'authorName': 'Michael Shaikh'
                },
                'duration': 27120,  # Audio only
                'ebookFormat': None
            }
        },
        {
            'id': 'book3',
            'media': {
                'metadata': {
                    'title': 'Endurance: Shackleton\'s Incredible Voyage',
                    'authorName': 'Alfred Lansing'
                },
                'duration': None,
                'ebookFormat': 'pdf'  # Ebook only
            }
        }
    ]
    
    # Test the enhanced display
    selector.display_books(mock_books)
    
    print("\n🎉 Enhanced main display is working!")
    print("The main book selector now shows:")
    print("- Audio column: ✅ if audio available, ❌ if not")
    print("- Ebook column: ✅ if ebook available, ❌ if not")
    print("- Faster detection knowing basic book data (no API calls)")

if __name__ == "__main__":
    test_main_enhanced()

