# ⚙️ Configuration Guide

Customize download behavior, performance settings, and file organization options.

## 📁 Configuration File

Edit `config.py` to customize settings:

```python
# Download Configuration
DOWNLOAD_PATH = "./downloads"              # Default download location
MAX_CONCURRENT_DOWNLOADS = 2              # Concurrent downloads (be gentle!)
CHUNK_SIZE = 8192                         # Download chunk size in bytes
DOWNLOAD_DELAY = 1.0                      # Delay between downloads (seconds)
REQUEST_TIMEOUT = 30                      # API request timeout (seconds)
MAX_RETRIES = 3                           # Download retry attempts

# Logging Configuration
LOG_LEVEL = "INFO"                        # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# File Organization
ORGANIZE_BY_AUTHOR = True                 # Create author folders
INCLUDE_COVER_IMAGES = True               # Download cover images
SAFE_FILENAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ "
```

## 📥 Download Settings

### Download Path Options

**1. Configuration File (Default)**

```python
DOWNLOAD_PATH = "/Users/username/Audiobooks"
```

**2. Command Line Arguments**

```bash
python audiobookshelf_downloader.py --download-path /path/to/books
python book_selector.py --download-path /path/to/books
```

**3. Per-Server Settings**
Each API key can have its own download path:

```bash
python api_key_manager.py
# When adding/updating keys, specify download path
```

**4. Interactive Prompts**
The main menu will prompt for download paths when needed.

### Performance Tuning

#### Conservative (Recommended)

```python
MAX_CONCURRENT_DOWNLOADS = 1
DOWNLOAD_DELAY = 2.0
CHUNK_SIZE = 4096
```

- **Best for**: Shared servers, slow connections
- **Impact**: Gentle on server, slower downloads

#### Moderate (Default)

```python
MAX_CONCURRENT_DOWNLOADS = 2
DOWNLOAD_DELAY = 1.0
CHUNK_SIZE = 8192
```

- **Best for**: Most home servers
- **Impact**: Balanced performance and server load

#### Aggressive (Use Carefully)

```python
MAX_CONCURRENT_DOWNLOADS = 4
DOWNLOAD_DELAY = 0.5
CHUNK_SIZE = 16384
```

- **Best for**: Powerful dedicated servers
- **Impact**: Faster downloads, higher server load

### Timeout & Retry Settings

```python
REQUEST_TIMEOUT = 30        # API request timeout
MAX_RETRIES = 3            # Retry failed downloads
```

**Slow connections:**

```python
REQUEST_TIMEOUT = 60
MAX_RETRIES = 5
```

**Fast connections:**

```python
REQUEST_TIMEOUT = 15
MAX_RETRIES = 2
```

## 📁 File Organization

### Author Folders

```python
ORGANIZE_BY_AUTHOR = True
```

**Enabled (Default):**

```
downloads/
├── Terry Goodkind/
│   ├── Wizard's First Rule/
│   └── Stone of Tears/
└── Brandon Sanderson/
    └── The Way of Kings/
```

**Disabled:**

```
downloads/
├── Terry Goodkind - Wizard's First Rule/
├── Terry Goodkind - Stone of Tears/
└── Brandon Sanderson - The Way of Kings/
```

### Cover Images

```python
INCLUDE_COVER_IMAGES = True
```

Downloads `cover.jpg` for each book when available.

### Safe Filenames

```python
SAFE_FILENAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ "
```

Characters allowed in filenames. Others are removed for compatibility.

## 🔍 Logging Configuration

### Log Levels

```python
LOG_LEVEL = "DEBUG"    # Very verbose, shows all operations
LOG_LEVEL = "INFO"     # Default, shows progress and important events
LOG_LEVEL = "WARNING"  # Only warnings and errors
LOG_LEVEL = "ERROR"    # Only errors
```

### Log Format

```python
# Default format
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Minimal format
LOG_FORMAT = "%(levelname)s: %(message)s"

# Detailed format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
```

## 🎯 Use Case Configurations

### Home Media Server

```python
# Gentle on home server
MAX_CONCURRENT_DOWNLOADS = 2
DOWNLOAD_DELAY = 1.0
DOWNLOAD_PATH = "/media/audiobooks"
ORGANIZE_BY_AUTHOR = True
INCLUDE_COVER_IMAGES = True
LOG_LEVEL = "INFO"
```

### Powerful Dedicated Server

```python
# Faster downloads for powerful servers
MAX_CONCURRENT_DOWNLOADS = 4
DOWNLOAD_DELAY = 0.5
CHUNK_SIZE = 16384
REQUEST_TIMEOUT = 15
LOG_LEVEL = "WARNING"  # Less verbose
```

### Slow/Remote Connection

```python
# Conservative for slow connections
MAX_CONCURRENT_DOWNLOADS = 1
DOWNLOAD_DELAY = 3.0
REQUEST_TIMEOUT = 60
MAX_RETRIES = 5
CHUNK_SIZE = 4096
```

### Development/Testing

```python
# Verbose logging for debugging
LOG_LEVEL = "DEBUG"
MAX_CONCURRENT_DOWNLOADS = 1
DOWNLOAD_DELAY = 0.1
DOWNLOAD_PATH = "./test_downloads"
```

## 🔧 Advanced Settings

### Custom Download Paths by Server

You can set different download paths for different servers:

```bash
python api_key_manager.py
# Add/update server with custom download path
```

This overrides the default `DOWNLOAD_PATH` for that specific server.

### Environment Variables

You can override settings with environment variables:

```bash
export AUDIOBOOKSHELF_DOWNLOAD_PATH="/custom/path"
export AUDIOBOOKSHELF_LOG_LEVEL="DEBUG"
python audiobookshelf_downloader.py
```

### Temporary Overrides

Use command line arguments for one-time changes:

```bash
# Custom download path for this run only
python book_selector.py --download-path /tmp/test_downloads

# Different script with custom path
python audiobookshelf_downloader.py --download-path /backup/audiobooks
```

## 📊 Performance Monitoring

### Check Your Settings

```bash
python test_connection.py
# Shows connection speed and server response times
```

### Monitor Downloads

- Watch console output for download speeds
- Check for timeout errors or retries
- Monitor server CPU/memory usage if possible

### Adjust Based on Results

- **Frequent timeouts**: Increase `REQUEST_TIMEOUT`
- **Server struggling**: Reduce `MAX_CONCURRENT_DOWNLOADS`
- **Slow downloads**: Increase `CHUNK_SIZE`
- **Network errors**: Increase `MAX_RETRIES`

## 🔄 Configuration Backup

### Save Your Settings

```bash
# Backup your config
cp config.py config.py.backup
```

### Restore Defaults

```bash
# Reset to defaults (lose custom settings)
git checkout config.py
```

### Version Control

If using git, consider:

```bash
# Track config changes
git add config.py
git commit -m "Update download settings for home server"
```

## 🆘 Troubleshooting Config Issues

### "Import Error"

Make sure `config.py` has valid Python syntax:

```bash
python -c "import config; print('Config OK')"
```

### "Permission Denied"

Check download path permissions:

```bash
ls -la /path/to/download/directory
mkdir -p /path/to/download/directory
```

### "Invalid Settings"

Reset to defaults and gradually change settings:

```python
# Start with conservative defaults
MAX_CONCURRENT_DOWNLOADS = 1
DOWNLOAD_DELAY = 2.0
```

---

[← API Keys](API_KEYS.md) | [Back to Main README](README.md) | [Troubleshooting →](TROUBLESHOOTING.md)
