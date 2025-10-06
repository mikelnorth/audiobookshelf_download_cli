# 🛠️ Troubleshooting Guide

Common issues and solutions for the Audiobookshelf Bulk Downloader.

## 🚀 Quick Fixes

### "No API keys found"

```bash
python setup.py
# or
python api_key_manager.py
```

### Connection Issues

```bash
python test_connection.py
# Test your connection and API key
```

### Reset Everything

```bash
rm .audiobookshelf_keys
python setup.py
```

## 🔑 API Key Issues

### "Authentication failed"

**Symptoms:** Login errors, 401/403 responses

**Solutions:**

1. **Verify API key in Audiobookshelf:**

   - Go to Settings → Users → Your User → API Keys
   - Check if key still exists and is active
   - Regenerate if needed

2. **Update stored key:**

   ```bash
   python api_key_manager.py
   # Choose: Update existing API key
   ```

3. **Test the key:**
   ```bash
   python test_connection.py
   ```

### "No API keys found"

**Symptoms:** Tool asks for setup on every run

**Solutions:**

1. **Run initial setup:**

   ```bash
   python setup.py
   ```

2. **Check file permissions:**

   ```bash
   ls -la .audiobookshelf_keys
   chmod 600 .audiobookshelf_keys
   ```

3. **Verify file format:**
   ```bash
   python -c "import json; json.load(open('.audiobookshelf_keys'))"
   ```

## 🌐 Connection Problems

### "Connection failed" / "Timeout"

**Symptoms:** Can't reach server, timeout errors

**Solutions:**

1. **Check server URL:**

   - Verify URL is correct and accessible
   - Try opening in web browser
   - Check HTTPS vs HTTP

2. **Network connectivity:**

   ```bash
   ping your-server.com
   curl -I https://your-server.com
   ```

3. **Increase timeout:**

   ```python
   # In config.py
   REQUEST_TIMEOUT = 60
   ```

4. **Check firewall/VPN:**
   - Disable VPN temporarily
   - Check firewall rules
   - Try from different network

### "SSL Certificate Error"

**Symptoms:** Certificate verification errors

**Solutions:**

1. **Check certificate:**

   ```bash
   curl -I https://your-server.com
   ```

2. **Update server URL:**

   - Use IP address instead of domain
   - Check if certificate is valid

3. **Temporary workaround:**
   - Use HTTP instead of HTTPS (less secure)

## 📥 Download Issues

### "Download failed" / "File not found"

**Symptoms:** Individual files fail to download

**Solutions:**

1. **Check book availability:**

   - Verify book exists in Audiobookshelf
   - Check if files are present on server

2. **Retry with different settings:**

   ```python
   # In config.py - more conservative
   MAX_CONCURRENT_DOWNLOADS = 1
   DOWNLOAD_DELAY = 2.0
   MAX_RETRIES = 5
   ```

3. **Check disk space:**

   ```bash
   df -h
   ```

4. **Verify download path:**
   ```bash
   ls -la /path/to/downloads
   mkdir -p /path/to/downloads
   ```

### "Permission denied"

**Symptoms:** Can't write to download directory

**Solutions:**

1. **Check directory permissions:**

   ```bash
   ls -la /path/to/downloads
   chmod 755 /path/to/downloads
   ```

2. **Create directory:**

   ```bash
   mkdir -p /path/to/downloads
   ```

3. **Use different path:**
   ```bash
   python book_selector.py --download-path ~/Downloads/Audiobooks
   ```

### Slow Downloads

**Symptoms:** Very slow download speeds

**Solutions:**

1. **Reduce concurrent downloads:**

   ```python
   MAX_CONCURRENT_DOWNLOADS = 1
   ```

2. **Increase chunk size:**

   ```python
   CHUNK_SIZE = 16384
   ```

3. **Check network speed:**

   ```bash
   speedtest-cli
   ```

4. **Monitor server load:**
   - Check if server is busy
   - Try during off-peak hours

## 🖥️ Interface Issues

### "Invalid command" in Book Selector

**Symptoms:** Commands not recognized

**Solutions:**

1. **Check command format:**

   ```bash
   f terry          # ✅ Correct
   f terry goodkind # ❌ Wrong - too many words
   filter terry     # ✅ Also correct
   ```

2. **Use single letters:**

   ```bash
   n    # next page
   p    # previous page
   d    # download
   ```

3. **Check for typos:**
   - Commands are case-insensitive
   - Use exact command names from help

### Book Selector Crashes

**Symptoms:** Python errors, crashes during selection

**Solutions:**

1. **Check Python version:**

   ```bash
   python --version  # Should be 3.7+
   ```

2. **Update dependencies:**

   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Run with debug logging:**
   ```python
   # In config.py
   LOG_LEVEL = "DEBUG"
   ```

## 🐍 Python Environment Issues

### "Module not found"

**Symptoms:** Import errors, missing modules

**Solutions:**

1. **Activate virtual environment:**

   ```bash
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Check Python path:**
   ```bash
   which python
   python -c "import sys; print(sys.path)"
   ```

### "Python not found"

**Symptoms:** Command not recognized

**Solutions:**

1. **Try different commands:**

   ```bash
   python3 setup.py
   py setup.py        # Windows
   ```

2. **Install Python:**

   - Download from python.org
   - Use package manager (brew, apt, etc.)

3. **Check PATH:**
   ```bash
   echo $PATH
   which python3
   ```

## 📁 File Organization Issues

### Weird Characters in Filenames

**Symptoms:** Strange characters, encoding issues

**Solutions:**

1. **Update safe characters:**

   ```python
   # In config.py - more restrictive
   SAFE_FILENAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
   ```

2. **Check filesystem:**
   - Some filesystems don't support Unicode
   - Consider different download location

### Books Not Organized Correctly

**Symptoms:** Files in wrong folders, poor organization

**Solutions:**

1. **Check organization settings:**

   ```python
   # In config.py
   ORGANIZE_BY_AUTHOR = True
   ```

2. **Verify book metadata:**
   - Check if books have proper author/title info
   - Some books may have missing metadata

## 🔍 Debugging Steps

### Enable Debug Logging

```python
# In config.py
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
```

### Test Individual Components

```bash
# Test API connection
python test_connection.py

# Test API key management
python api_key_manager.py

# Test book listing (without download)
python -c "
import asyncio
from audiobookshelf_downloader import AudiobookshelfDownloader
# Add test code here
"
```

### Check System Resources

```bash
# Disk space
df -h

# Memory usage
free -h  # Linux
top      # macOS

# Network connectivity
ping google.com
```

## 🆘 Getting More Help

### Collect Information

Before asking for help, collect:

1. **Error messages** (full text)
2. **Python version:** `python --version`
3. **Operating system:** `uname -a` (Linux/macOS) or `ver` (Windows)
4. **Config settings** (without API keys!)
5. **Steps to reproduce** the issue

### Check Logs

Look for detailed error messages in the console output when `LOG_LEVEL = "DEBUG"`.

### Test with Minimal Setup

Try with a fresh configuration:

```bash
# Backup current config
mv .audiobookshelf_keys .audiobookshelf_keys.backup
mv config.py config.py.backup

# Start fresh
python setup.py
```

### Common Error Patterns

**"JSONDecodeError":** Corrupted keys file

```bash
rm .audiobookshelf_keys
python setup.py
```

**"ConnectionError":** Network/server issues

```bash
python test_connection.py
```

**"PermissionError":** File/directory permissions

```bash
chmod 755 /download/path
```

**"TimeoutError":** Server too slow

```python
REQUEST_TIMEOUT = 60  # In config.py
```

---

[← Configuration](CONFIGURATION.md) | [Back to Main README](README.md)
