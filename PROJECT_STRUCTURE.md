# Project Structure

This document describes the organization of the Audiobookshelf Downloader repository.

## 📁 Directory Structure

```
audiobookshelf-downloader/
│
├── 📄 Core Files (Root)
│   ├── README.md                    # Main project documentation
│   ├── LICENSE                      # MIT License
│   ├── SECURITY.md                  # Security policy
│   ├── CONTRIBUTING.md              # Contribution guidelines
│   ├── requirements.txt             # Python dependencies
│   ├── config.py                    # Configuration settings
│   └── PROJECT_STRUCTURE.md         # This file
│
├── 🐍 Python Scripts
│   ├── run.py                       # Main entry point (interactive menu)
│   ├── setup.py                     # Setup and installation script
│   ├── audiobookshelf_downloader.py # Core downloader class
│   ├── api_key_manager.py          # API key management
│   ├── book_selector.py            # Interactive book selection
│   ├── bulk_download.py            # Command-line bulk downloader
│   └── server_diff.py              # Server comparison tool
│
├── 📚 docs/                         # Documentation
│   ├── README.md                    # Documentation overview
│   ├── API_KEYS.md                 # API key management guide
│   ├── BOOK_SELECTION.md           # Book selection guide
│   ├── CONFIGURATION.md            # Configuration guide
│   ├── SERVER_LOAD_GUIDE.md        # Performance guide
│   ├── TROUBLESHOOTING.md          # Troubleshooting guide
│   └── AUDIT_REPORT.md             # Security audit report
│
├── 🧪 tests/                        # Tests and debugging tools
│   ├── README.md                    # Test documentation
│   ├── test_connection.py          # Connection tests
│   ├── test_book_matching.py       # Book matching tests
│   ├── test_main_enhanced.py       # Integration tests
│   └── debug_book_data.py          # Debugging utilities
│
├── 🐙 .github/                      # GitHub-specific files
│   ├── FUNDING.yml                 # Sponsorship configuration
│   ├── PULL_REQUEST_TEMPLATE.md   # PR template
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md           # Bug report template
│       └── feature_request.md      # Feature request template
│
├── 📦 downloads/                    # Downloaded audiobooks (gitignored)
├── 🐍 venv/                        # Python virtual environment (gitignored)
└── 🗑️  __pycache__/                # Python cache (gitignored)
```

## 📖 File Organization Principles

### Root Level

Keep only essential files that users need to see first:

- README.md (first thing users see)
- LICENSE (legal requirements)
- SECURITY.md (security is important)
- CONTRIBUTING.md (community guidelines)
- Core config files (requirements.txt, config.py)

### Python Scripts

Core application `.py` files remain in the root for easy import and execution.
Test files are in the `tests/` directory to keep the root clean.
This follows Python packaging conventions.

### Documentation Directory (`docs/`)

All user-facing documentation in one place:

- Keeps root directory clean
- Easy to navigate
- Clear separation of concerns
- Standard convention for open source projects

### Tests Directory (`tests/`)

All test and debugging scripts organized together:

- Separates tests from production code
- Easy to find and run tests
- Follows Python testing conventions
- Includes helpful README for test documentation

### GitHub Directory (`.github/`)

GitHub-specific files for:

- Issue templates
- PR templates
- Funding information
- Actions/workflows (if added later)

## 🔍 Finding What You Need

### For Users

- **Getting started**: Start with `README.md`
- **Installation help**: `README.md` → `docs/TROUBLESHOOTING.md`
- **API keys**: `docs/API_KEYS.md`
- **Configuration**: `docs/CONFIGURATION.md`
- **Using the tool**: `README.md` Quick Start section

### For Contributors

- **How to contribute**: `CONTRIBUTING.md`
- **Security issues**: `SECURITY.md`
- **Code organization**: This file
- **Running tests**: `tests/` directory

### For Developers

- **Main entry point**: `run.py`
- **Core logic**: `audiobookshelf_downloader.py`
- **API management**: `api_key_manager.py`
- **Configuration**: `config.py`
- **Testing**: `tests/` directory
- **Debugging**: `tests/debug_book_data.py`

## 🎯 Design Decisions

### Why docs/ folder?

1. **Cleaner root directory** - Users see what matters first
2. **Standard practice** - Most open source projects use this
3. **Easy maintenance** - All docs in one place
4. **Better organization** - Clear separation from code

### Why tests/ folder?

1. **Clean separation** - Tests separated from production code
2. **Easy discovery** - All tests in one predictable location
3. **Python convention** - Standard practice in Python projects
4. **Prevents clutter** - Keeps root focused on main application

### Why keep main Python files in root?

1. **Import simplicity** - No need for package structure changes
2. **Easy execution** - `python run.py` instead of `python src/run.py`
3. **Convention** - Many Python projects do this for simple tools
4. **User-friendly** - Simpler for end users to run scripts

### Why separate .github/?

1. **GitHub convention** - Automatic recognition by GitHub
2. **Clean separation** - CI/CD and community files separate
3. **Easy to find** - Standard location everyone knows

## 📝 Naming Conventions

### Files

- **Markdown**: `UPPERCASE.md` for important docs, `lowercase.md` for regular docs
- **Python**: `lowercase_with_underscores.py`
- **Config**: Descriptive names (`.gitignore`, `requirements.txt`)

### Directories

- **lowercase**: `docs/`, `tests/`, `downloads/`, `venv/`
- **Special**: `.github/` (with dot for hidden)

## 🔄 When to Update This Document

Update `PROJECT_STRUCTURE.md` when:

- Adding new directories
- Changing organization structure
- Adding significant new files
- Reorganizing documentation
- Changing naming conventions

---

**Last Updated:** October 6, 2025
**Version:** 1.0
