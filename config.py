"""
Configuration file for Audiobookshelf Downloader

Note: SERVER_URL and API_KEY are now managed through the API key manager.
Use 'python setup.py' or 'python api_key_manager.py' to configure servers.
"""

# Download Configuration
DOWNLOAD_PATH = "./downloads"  # Local directory to save downloaded books
MAX_CONCURRENT_DOWNLOADS = 3  # Number of books to download simultaneously (be gentle on server)
CHUNK_SIZE = 8192  # Size of chunks when downloading files
DOWNLOAD_DELAY = 1.0  # Delay between downloads in seconds
REQUEST_TIMEOUT = 30  # Timeout for API requests in seconds
MAX_RETRIES = 3  # Maximum number of retries for failed downloads

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# File Organization
ORGANIZE_BY_AUTHOR = True  # Create author folders
INCLUDE_COVER_IMAGES = True  # Download cover images
SAFE_FILENAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ "  # Allowed characters in filenames
