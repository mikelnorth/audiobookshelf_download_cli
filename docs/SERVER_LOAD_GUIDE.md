# Server Load Management Guide

## 🚨 Understanding Server Load

When downloading 100+ audiobooks, you need to be considerate of your Audiobookshelf server's resources. Here's what to consider:

### What Happens During Bulk Downloads

1. **API Requests**: Each book requires multiple API calls (get details, get file list, download each file)
2. **File Transfers**: Large audio files being transferred simultaneously
3. **Database Queries**: Server needs to look up book metadata for each request
4. **Disk I/O**: Server reading files from storage

### Potential Server Impact

- **CPU Usage**: Processing multiple concurrent requests
- **Memory Usage**: Buffering multiple large files
- **Network Bandwidth**: Saturated upload bandwidth
- **Disk I/O**: Reading multiple files simultaneously
- **Database Load**: Multiple concurrent queries

## ⚙️ Load Management Features

### 1. Concurrent Download Limits

```python
# In config.py
MAX_CONCURRENT_DOWNLOADS = 2  # Start conservative
```

**Recommendations:**

- **1 download**: Very safe, slow but gentle
- **2 downloads**: Good balance for most servers
- **3+ downloads**: Only if server is powerful and network is fast

### 2. Download Delays

```python
# In config.py
DOWNLOAD_DELAY = 1.0  # 1 second between downloads
```

**Recommendations:**

- **2-5 seconds**: Very gentle, good for shared servers
- **1 second**: Moderate, good for dedicated servers
- **0.5 seconds**: Aggressive, only for powerful servers

### 3. Request Timeouts

```python
# In config.py
REQUEST_TIMEOUT = 30  # 30 seconds timeout
```

## 📊 Monitoring Server Health

### Use the Server Load Monitor

```bash
python server_load_monitor.py
```

This will:

- Test server response times
- Analyze server health
- Provide recommendations
- Estimate storage requirements

### Signs of Server Overload

**Good Signs:**

- Response times < 2 seconds
- No failed requests
- Consistent performance

**Warning Signs:**

- Response times > 5 seconds
- Occasional failed requests
- Inconsistent performance

**Danger Signs:**

- Response times > 10 seconds
- Many failed requests
- Server becomes unresponsive
- Other users can't access the server

## 🛡️ Best Practices

### 1. Start Small

- Begin with 5-10 books
- Monitor server performance
- Gradually increase batch size

### 2. Choose the Right Time

- **Off-peak hours**: Early morning, late night
- **Avoid peak usage**: When others are using the server
- **Weekend downloads**: Often better than weekdays

### 3. Monitor During Downloads

- Watch server response times
- Check if other users can access the server
- Stop if you notice problems

### 4. Use Appropriate Settings

**For Shared Servers:**

```python
MAX_CONCURRENT_DOWNLOADS = 1
DOWNLOAD_DELAY = 3.0
```

**For Dedicated Servers:**

```python
MAX_CONCURRENT_DOWNLOADS = 2
DOWNLOAD_DELAY = 1.0
```

**For Powerful Servers:**

```python
MAX_CONCURRENT_DOWNLOADS = 3
DOWNLOAD_DELAY = 0.5
```

## 📈 Download Strategies

### Strategy 1: Conservative (Recommended)

- 1-2 concurrent downloads
- 2-3 second delays
- 10-20 books per batch
- Monitor between batches

### Strategy 2: Moderate

- 2-3 concurrent downloads
- 1 second delays
- 20-50 books per batch
- Good for dedicated servers

### Strategy 3: Aggressive (Use with Caution)

- 3+ concurrent downloads
- 0.5 second delays
- 50+ books per batch
- Only for powerful servers

## 🔧 Troubleshooting

### Server Becomes Slow

1. **Stop downloads immediately**
2. **Wait 5-10 minutes**
3. **Reduce concurrent downloads**
4. **Increase delays**
5. **Try smaller batches**

### Downloads Keep Failing

1. **Check network connection**
2. **Verify server is accessible**
3. **Reduce concurrent downloads**
4. **Increase timeouts**
5. **Check server logs**

### Other Users Complain

1. **Stop downloads immediately**
2. **Use more conservative settings**
3. **Download during off-peak hours**
4. **Consider downloading fewer books at once**

## 📱 Alternative Approaches

### 1. Selective Downloads

- Use the book selector to choose specific books
- Download in smaller, targeted batches
- Focus on high-priority books first

### 2. Scheduled Downloads

- Set up downloads to run during off-peak hours
- Use cron jobs or task schedulers
- Download a few books each night

### 3. Progressive Downloads

- Download 10-20 books per day
- Spread the load over time
- Less impact on server performance

## 💡 Pro Tips

1. **Test First**: Always test with a small batch before large downloads
2. **Monitor Closely**: Watch server performance during downloads
3. **Be Flexible**: Adjust settings based on server response
4. **Communicate**: If sharing a server, coordinate with other users
5. **Backup Plan**: Have a plan to stop downloads if needed

## 🚨 Emergency Stop

If you need to stop downloads immediately:

1. **Press Ctrl+C** in the terminal
2. **Check server status** - is it responsive?
3. **Wait before resuming** - give server time to recover
4. **Use more conservative settings** when resuming

Remember: It's better to download slowly and safely than to overload your server!
