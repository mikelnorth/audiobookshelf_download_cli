#!/usr/bin/env python3
"""
Debug tool for analyzing book data from servers to find hidden differences
"""

import re
import unicodedata

def analyze_string(s, label):
    """Analyze a string for hidden characters and encoding issues"""
    print(f"📊 {label}:")
    print(f"   Text: '{s}'")
    print(f"   Length: {len(s)}")
    print(f"   Bytes: {s.encode('utf-8')}")

    # Check for different types of spaces and characters
    special_chars = []
    for i, char in enumerate(s):
        if ord(char) > 127 or char in ['\u00A0', '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005', '\u2006', '\u2007', '\u2008', '\u2009', '\u200A', '\u200B', '\u200C', '\u200D', '\u2060', '\uFEFF']:
            try:
                name = unicodedata.name(char)
            except ValueError:
                name = f"U+{ord(char):04X}"
            special_chars.append(f"pos {i}: '{char}' ({name})")

    if special_chars:
        print(f"   Special chars: {special_chars}")
    else:
        print(f"   Special chars: None")

    # Show hex representation
    hex_chars = ' '.join(f'{ord(c):02x}' for c in s)
    print(f"   Hex: {hex_chars}")
    print()

def compare_books(title1, author1, title2, author2):
    """Compare two books and show detailed analysis"""
    print("🔍 Book Comparison Analysis")
    print("=" * 60)

    analyze_string(title1, "Title 1")
    analyze_string(title2, "Title 2")
    analyze_string(author1, "Author 1")
    analyze_string(author2, "Author 2")

    # Test normalization
    from server_diff import ServerDiff
    diff_tool = ServerDiff(None, None)

    norm_title1 = diff_tool._normalize_title(title1)
    norm_title2 = diff_tool._normalize_title(title2)
    norm_author1 = diff_tool._normalize_author(author1)
    norm_author2 = diff_tool._normalize_author(author2)

    print("🔧 After Normalization:")
    print(f"   Title 1: '{norm_title1}'")
    print(f"   Title 2: '{norm_title2}'")
    print(f"   Author 1: '{norm_author1}'")
    print(f"   Author 2: '{norm_author2}'")
    print()

    key1 = f"{norm_author1}|{norm_title1}"
    key2 = f"{norm_author2}|{norm_title2}"

    print("🔑 Final Keys:")
    print(f"   Key 1: '{key1}'")
    print(f"   Key 2: '{key2}'")
    print(f"   Match: {'✅ YES' if key1 == key2 else '❌ NO'}")

    if key1 != key2:
        print()
        print("🔍 Differences Found:")
        if norm_title1 != norm_title2:
            print(f"   Title difference: '{norm_title1}' vs '{norm_title2}'")
        if norm_author1 != norm_author2:
            print(f"   Author difference: '{norm_author1}' vs '{norm_author2}'")

def main():
    """Interactive tool for debugging book matching issues"""
    print("🛠️  Book Data Debug Tool")
    print("=" * 40)
    print("This tool helps identify hidden characters and encoding issues")
    print("that might prevent books from matching between servers.")
    print()

    while True:
        print("Enter the book data from both servers:")
        print()

        title1 = input("Server 1 - Title: ")
        if not title1:
            break
        author1 = input("Server 1 - Author: ")

        print()
        title2 = input("Server 2 - Title: ")
        if not title2:
            break
        author2 = input("Server 2 - Author: ")

        print()
        print("-" * 60)

        compare_books(title1, author1, title2, author2)

        print("-" * 60)
        print()

        continue_test = input("Analyze another book? (y/n): ").strip().lower()
        if continue_test != 'y':
            break
        print()

if __name__ == "__main__":
    # Test with the Scott Trench example
    print("🧪 Testing Scott Trench Example:")
    compare_books(
        "Set for Life, Revised Edition", "Scott Trench",
        "Set for Life, Revised Edition", "Scott Trench"
    )

    print("\n" + "="*60)
    print("💡 If you're seeing books that look identical but don't match,")
    print("run this script interactively to copy-paste the actual data:")
    print("python debug_book_data.py")
