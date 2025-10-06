# Audiobookshelf Bulk Downloader

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: PEP8](https://img.shields.io/badge/code%20style-PEP8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)

A comprehensive Python tool to download books from your Audiobookshelf library using the API, with advanced book selection and server management features.

## ✨ Key Features

- 🔐 **Secure API key management** - Store multiple servers with encrypted keys
- 📚 **Interactive book selection** - Advanced table view with filtering and search
- 🎯 **Smart filtering** - Filter books by title/author with partial matching (`f terry`)
- ✓ **Visual indicators** - See audio/ebook availability at a glance
- 🔄 **Server comparison** - Find and download missing books between servers
- ⚡ **Async downloads** - Fast, concurrent downloads with load management

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- Git (for cloning)

### Setup Virtual Environment (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd audiobookshelf-downloader

# Create and activate virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Run setup (installs dependencies automatically)
python setup.py
```

### Alternative: Manual Installation

If you prefer to install dependencies manually:

```bash
# Install dependencies first
pip install -r requirements.txt

# Then run setup
python setup.py
```

## 🚀 Quick Start

After installation, you're ready to go:

1. **Run the interactive menu:**

   ```bash
   python run.py
   ```

2. **Or select specific books:**

   ```bash
   python book_selector.py
   ```

3. **Or download all books:**
   ```bash
   python audiobookshelf_downloader.py
   ```

The setup script automatically installs dependencies and guides you through API key configuration!

## 📖 Documentation

- **[📚 Book Selection Guide](docs/BOOK_SELECTION.md)** - Interactive book selector with filtering
- **[🔑 API Key Management](docs/API_KEYS.md)** - Managing multiple servers and keys
- **[⚙️ Configuration](docs/CONFIGURATION.md)** - Customizing download behavior
- **[🛠️ Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[📊 Server Load Guide](docs/SERVER_LOAD_GUIDE.md)** - Performance and load management

## 🎯 Common Usage

### Interactive Menu

```bash
python run.py
# Choose from setup, book selection, downloads, etc.
```

### Select Specific Books

```bash
python book_selector.py
# Use filtering: f terry
# Select books: 1,3,5-8
# Download: d
```

### Download All Books

```bash
python audiobookshelf_downloader.py
```

### Compare Servers

```bash
python run.py
# Choose option 6: Compare Servers
# Select from your stored API keys or use manual entry
```

## 📁 File Organization

Books are organized as:

```
downloads/
├── Author Name - Book Title/
│   ├── audio files...
│   └── cover.jpg
```

## 🆘 Need Help?

- **Setup issues**: Run `python setup.py`
- **Connection problems**: Run `python tests/test_connection.py`
- **Detailed help**: See [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

## ⚡ Quick Commands

| Command                           | Description                     |
| --------------------------------- | ------------------------------- |
| `python setup.py`                 | Initial setup and configuration |
| `python run.py`                   | Interactive menu                |
| `python book_selector.py`         | Select specific books           |
| `python tests/test_connection.py` | Test your connection            |
| `python api_key_manager.py`       | Manage API keys                 |

---

**📋 Requirements:** Python 3.7+, Audiobookshelf server with API access

**🔒 Security:** API keys use hybrid encryption (master password + hardware ID) stored in OS keychain

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🔐 Security

For security concerns, please see [SECURITY.md](SECURITY.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
