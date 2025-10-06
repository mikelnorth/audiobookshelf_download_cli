# 🔑 API Key Management Guide

The tool includes a secure API key management system for storing multiple Audiobookshelf server credentials.

## 🚀 Quick Setup

### Option 1: Setup Script (Recommended)

```bash
python setup.py
```

Guides you through the entire process including getting your API key.

### Option 2: Direct Management

```bash
python api_key_manager.py
```

## 🔐 Security Features

- **🔒 Hybrid Encryption**: API keys protected by master password + hardware UUID
- **🛡️ OS Keychain Storage**: Master password stored securely in macOS Keychain/Windows Credential Manager
- **🖥️ Hardware Binding**: Encryption tied to your specific machine's hardware identifier
- **🔐 Fernet + PBKDF2**: Industry-standard encryption with 100,000 iterations
- **🚫 No Weak Fallbacks**: Fails securely if hardware ID unavailable without keychain access
- **📋 Multiple Servers**: Store keys for different Audiobookshelf instances
- **🏷️ Named Keys**: Give each server a friendly name (e.g., 'home', 'work')
- **🔄 Easy Switching**: Choose which server to connect to when downloading
- **🧪 Connection Testing**: Test keys before using them

## 📖 Getting Your API Key

1. **Log into Audiobookshelf** web interface
2. **Go to Settings** → Users → Your User → API Keys
3. **Create new API key**
4. **Copy the key** (it's only shown once!)

## 🛠️ Managing API Keys

### Add New Server

```bash
python api_key_manager.py
# Choose: Add new API key
# Enter friendly name: home
# Enter server URL: https://audiobooks.example.com
# Enter API key: your_api_key_here
# Enter download path: ~/Downloads/Audiobooks
```

### List Stored Keys

```bash
python api_key_manager.py
# Choose: List stored API keys
```

### Update Existing Key

```bash
python api_key_manager.py
# Choose: Update existing API key
# Select key to update
# Choose what to update (API key, download path, or both)
```

### Delete Key

```bash
python api_key_manager.py
# Choose: Delete API key
# Select key to delete
```

### Test Connection

```bash
python api_key_manager.py
# Choose: Test API key connection
# Select key to test
```

## 🎯 Usage Examples

### Single Server Setup

```bash
python api_key_manager.py
# Add key named "main"
# Server: https://audiobooks.home.com
# Key: your_api_key_here
```

### Multiple Servers

```bash
# Add home server
python api_key_manager.py
# Name: home, URL: https://home.audiobooks.com

# Add work server
python api_key_manager.py
# Name: work, URL: https://work.company.com

# Add backup server
python api_key_manager.py
# Name: backup, URL: https://backup.audiobooks.com
```

### Using Multiple Servers

When you run download tools, you'll be prompted to choose:

```bash
python audiobookshelf_downloader.py

🔑 Available servers:
  1. home
  2. work
  3. backup

Select server (1-3): 1
🔑 Using server: home
```

## 📁 Manual Configuration

If you prefer to manually edit the configuration file:

### File Location

```
.audiobookshelf_keys
```

### File Format

```json
{
  "keys": {
    "home": {
      "server_url": "https://audiobooks.example.com",
      "api_key": "your_api_key_here",
      "download_path": "~/Downloads/Audiobooks",
      "created_at": "2025-01-01 12:00:00"
    },
    "work": {
      "server_url": "https://work.company.com",
      "api_key": "work_api_key_here",
      "download_path": "./downloads",
      "created_at": "2025-01-01 12:00:00"
    }
  },
  "version": "1.0"
}
```

### Manual Entry Notes

- **Raw API keys**: If manually added, use the raw API key from Audiobookshelf
- **Encryption**: Keys added via management tools should be encrypted (but may not always be)
- **Plain text risk**: Some keys may be stored in plain text - treat file as sensitive
- **Timestamps**: `created_at` and `updated` fields are optional
- **Download paths**: Can use `~` for home directory

## 🔒 Security Best Practices

### Check If Your Keys Are Encrypted

You can check if your API keys are properly encrypted:

```bash
# Look at your keys file
cat .audiobookshelf_keys

# If you see JWT tokens (starting with eyJ...) or readable text, they're NOT encrypted
# If you see random-looking base64 strings, they're likely encrypted
```

**Example of what you might see:**

- **❌ Not encrypted**: `"api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."`
- **✅ Encrypted**: `"api_key": "Z0FBQUFBQm8zaENUeEdyZHVPc0h0X0dYVUxpUlRGM054..."`

**To fix unencrypted keys:**

```bash
python api_key_manager.py
# Choose: Update existing API key
# Re-enter the same API key to trigger encryption
```

### File Permissions

The `.audiobookshelf_keys` file automatically gets restricted permissions (600):

```bash
-rw------- 1 user user .audiobookshelf_keys
```

### What to Protect

- ✅ **Keep secure**: `.audiobookshelf_keys` file
- ❌ **Never share**: The keys file or its contents
- ❌ **Don't commit**: Never add to version control
- 🔄 **Regenerate if compromised**: Create new keys in Audiobookshelf

### Backup Strategy

```bash
# Backup your keys (keep secure!)
cp .audiobookshelf_keys .audiobookshelf_keys.backup

# Restore from backup
cp .audiobookshelf_keys.backup .audiobookshelf_keys
```

## 🧪 Testing Connections

### Test All Keys

```bash
python test_connection.py
# Will show all stored keys and let you test them
```

### Test Specific Key

```bash
python api_key_manager.py
# Choose: Test API key connection
# Select the key to test
```

### What Gets Tested

- ✅ **Basic connection** to server
- ✅ **API key authentication**
- ✅ **Library access**
- ✅ **Download permissions**

## 🔄 Migration & Backup

### Moving to New Machine

1. **Copy the keys file**: `.audiobookshelf_keys`
2. **Set proper permissions**: `chmod 600 .audiobookshelf_keys`
3. **Test connections**: `python test_connection.py`

### Starting Fresh

```bash
# Remove all stored keys
rm .audiobookshelf_keys

# Run setup again
python setup.py
```

## 🆘 Troubleshooting

### "No API keys found"

```bash
python setup.py
# or
python api_key_manager.py
```

### "Authentication failed"

- Verify API key is correct in Audiobookshelf
- Check if key was disabled/expired
- Regenerate key if needed

### "Connection failed"

- Check server URL is accessible
- Verify HTTPS/HTTP protocol
- Test server in web browser

### "Permission denied"

```bash
chmod 600 .audiobookshelf_keys
```

### Corrupted Keys File

```bash
# Remove and recreate
rm .audiobookshelf_keys
python setup.py
```

---

[← Back to Main README](README.md) | [Book Selection →](BOOK_SELECTION.md) | [Configuration →](CONFIGURATION.md)
