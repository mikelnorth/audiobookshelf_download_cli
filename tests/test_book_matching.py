#!/usr/bin/env python3
"""
Test script for debugging book matching in server comparison
"""

import sys
import os
# Add parent directory to path so we can import from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server_diff import ServerDiff
from audiobookshelf_downloader import AudiobookshelfDownloader

def test_book_matching():
    """Test book matching with sample data"""

    # Create a dummy ServerDiff instance for testing
    dummy_server = None  # We don't need actual servers for testing normalization
    diff_tool = ServerDiff(dummy_server, dummy_server)

    print("🔍 Book Matching Test Tool")
    print("=" * 50)
    print("This tool helps debug why books might not be matching between servers.")
    print()

    while True:
        print("Enter book details to test matching:")
        print()

        # Get first book
        title1 = input("Book 1 Title: ").strip()
        if not title1:
            break
        author1 = input("Book 1 Author: ").strip()

        print()

        # Get second book
        title2 = input("Book 2 Title: ").strip()
        if not title2:
            break
        author2 = input("Book 2 Author: ").strip()

        print()
        print("-" * 50)

        # Test matching
        diff_tool.debug_book_matching(title1, author1, title2, author2)

        print("-" * 50)
        print()

        continue_test = input("Test another pair? (y/n): ").strip().lower()
        if continue_test != 'y':
            break
        print()

def test_steelheart_examples():
    """Test specific Steelheart scenarios"""

    diff_tool = ServerDiff(None, None)

    print("🔍 Testing Steelheart Scenarios")
    print("=" * 50)

    test_cases = [
        # Original Steelheart scenarios
        ("Steelheart", "Brandon Sanderson", "Steelheart: A Reckoners Novel", "Brandon Sanderson"),
        ("Steelheart: The Reckoners Book 1", "Brandon Sanderson", "Steelheart", "Brandon Sanderson"),
        ("The Way of Kings", "Brandon Sanderson", "The Way of Kings: The Stormlight Archive Book 1", "Brandon Sanderson"),
        ("Mistborn", "Brandon Sanderson", "Mistborn: The Final Empire", "Brandon Sanderson"),
        ("The Name of the Wind", "Patrick Rothfuss", "Name of the Wind", "Patrick Rothfuss"),

        # New edition and dash subtitle scenarios
        ("Be Useful - Sieben einfache Regeln für ein besseres Leben", "Arnold Schwarzenegger", "Be Useful (German edition)", "Arnold Schwarzenegger"),
        ("Harry Potter and the Philosopher's Stone", "J.K. Rowling", "Harry Potter and the Philosopher's Stone (Illustrated Edition)", "J.K. Rowling"),
        ("Atomic Habits - An Easy & Proven Way to Build Good Habits", "James Clear", "Atomic Habits", "James Clear"),
        ("Dune", "Frank Herbert", "Dune (Movie Tie-In Edition)", "Frank Herbert"),

        # Author initial spacing scenarios
        ("The Girl Who Cried Monster", "R. L. Stine", "The Girl Who Cried Monster", "R.L. Stine"),
        ("Harry Potter and the Sorcerer's Stone", "J. K. Rowling", "Harry Potter and the Sorcerer's Stone", "J.K. Rowling"),
        ("The Fellowship of the Ring", "J. R. R. Tolkien", "The Fellowship of the Ring", "J.R.R. Tolkien"),
    ]

    for i, (title1, author1, title2, author2) in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        match = diff_tool.debug_book_matching(title1, author1, title2, author2)
        print()
        if not match:
            print("❌ This case needs improvement!")
        print("-" * 50)
        print()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "steelheart":
        test_steelheart_examples()
    else:
        print("Usage:")
        print("  python test_book_matching.py           - Interactive testing")
        print("  python test_book_matching.py steelheart - Test Steelheart scenarios")
        print()

        choice = input("Run interactive test? (y/n): ").strip().lower()
        if choice == 'y':
            test_book_matching()
        else:
            test_steelheart_examples()
