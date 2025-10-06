# Tests

This directory contains test scripts and debugging utilities for the Audiobookshelf Downloader.

## 🧪 Test Files

### Connection & Setup Tests

- **`test_connection.py`** - Test API connection to your Audiobookshelf server
  - Verifies server URL and API key
  - Checks library access
  - Validates authentication

### Feature Tests

- **`test_book_matching.py`** - Test book matching algorithms

  - Tests normalization of titles and authors
  - Validates server comparison logic
  - Checks edge cases in book matching

- **`test_main_enhanced.py`** - Enhanced integration tests
  - Tests main application workflows
  - Validates end-to-end functionality

### Debugging Tools

- **`debug_book_data.py`** - Debug book metadata and API responses
  - Inspects raw API data
  - Helps troubleshoot book detection issues
  - Useful for debugging metadata problems

## 🚀 Running Tests

### Quick Connection Test

```bash
python tests/test_connection.py
```

This will verify your API key and server connection.

### Book Matching Tests

```bash
python tests/test_book_matching.py
```

Tests the book matching and normalization logic.

### Debug Book Data

```bash
python tests/debug_book_data.py
```

Interactive tool to inspect book metadata from your server.

## 📝 Adding New Tests

When adding new tests:

1. **Naming Convention**: Use `test_*.py` prefix
2. **Documentation**: Add docstrings to explain what's tested
3. **Independence**: Tests should be independent and not rely on each other
4. **Clear Output**: Use descriptive print statements or logging
5. **Update This README**: Add a description of your new test

## 🔧 Test Organization

```
tests/
├── README.md                 # This file
├── test_connection.py        # API connection tests
├── test_book_matching.py     # Book matching algorithm tests
├── test_main_enhanced.py     # Integration tests
└── debug_book_data.py        # Debugging utilities
```

## 💡 Tips

### For Users

- Run `test_connection.py` first when troubleshooting
- Use `debug_book_data.py` to inspect problematic books
- Check test output for specific error messages

### For Developers

- Add tests for new features
- Test edge cases and error conditions
- Keep tests focused and single-purpose
- Use meaningful test names

## 🐛 Debugging Workflow

1. **Connection Issues**:

   ```bash
   python tests/test_connection.py
   ```

2. **Book Not Found**:

   ```bash
   python tests/debug_book_data.py
   # Then inspect the book's metadata
   ```

3. **Matching Problems**:
   ```bash
   python tests/test_book_matching.py
   # Check normalization logic
   ```

## 📚 Related Documentation

- **[Troubleshooting Guide](../docs/TROUBLESHOOTING.md)** - Common issues
- **[Configuration](../docs/CONFIGURATION.md)** - Settings that affect tests
- **[API Keys](../docs/API_KEYS.md)** - Setting up test credentials

---

**Note**: These tests are designed for manual execution and debugging. For automated CI/CD testing, consider adding proper test frameworks like `pytest` or `unittest`.
