# 📚 Interactive Book Selection Guide

The book selector provides an advanced interface for choosing specific books to download with powerful filtering and selection features.

## 🚀 Getting Started

```bash
python book_selector.py
```

## 📊 Interface Overview

Books are displayed in a clean table format:

```
# ✓ Title                           Author               Duration     Audio Ebook
1   Outdoor Kids in an Inside World Steven Rinella        6h 3m        ✓     ✓
2   The Last Sweet Bite             Michael Shaikh        7h 32m       ✓     ✗
3   Endure (Unabridged)             Cameron Hanes         15h 25m      ✓     ✗
```

- **✓** = Available format
- **✗** = Not available
- **✓** in first column = Selected for download

## 🔍 Smart Filtering

### Quick Filter Commands

```bash
f terry          # Filter for "Terry Goodkind"
f wizards        # Find books with "wizards" in title
f erry           # Partial match - finds "Terry"
cf               # Clear filter, show all books
```

### How Filtering Works

- **Case insensitive**: `f TERRY` same as `f terry`
- **Partial matching**: `f good` matches "Goodkind"
- **Title and author**: Searches both fields
- **Instant results**: Filter applied immediately

## 🎯 Selection Commands

### Individual Selection

```bash
1                # Toggle book #1
5                # Toggle book #5
```

### Bulk Selection

```bash
a                # Select all books on current page
u                # Unselect all books on current page
c                # Clear all selections (entire library)
```

### Range Selection

```bash
s 1-5            # Select books 1 through 5
s 1,3,7          # Select books 1, 3, and 7
s 1-3,8-10       # Select books 1-3 and 8-10
```

### Interactive Range

```bash
s                # Will prompt for range
# Enter: 1-5,10,15-20
```

## 📄 Navigation

```bash
n / next         # Next page
p / prev         # Previous page
```

## 👁️ Preview & Actions

```bash
v / view         # View details of selected books
m / missing      # Compare with another server
d / download     # Start downloading selected books
q / quit         # Exit without downloading
```

## 🔄 Missing Books Feature

The missing books feature compares your current server with another server and automatically selects books that are missing.

### Usage

```bash
m                # Start missing books comparison
```

### Process

1. **Choose Target Server**: Select from stored API keys or enter manually
2. **Automatic Comparison**: Tool compares libraries
3. **Auto-Selection**: Missing books are automatically selected
4. **Review & Download**: Use `v` to review, `d` to download

### Perfect For

- **Syncing libraries** between home and work
- **Backup verification**
- **Server migration**

## 💡 Pro Tips

### Efficient Workflows

**Find and download specific author:**

```bash
f stephen king   # Filter for Stephen King
a               # Select all on page
d               # Download
```

**Download missing books:**

```bash
m               # Compare servers
d               # Download missing books
```

**Browse and select:**

```bash
f fantasy       # Filter genre
n               # Browse pages
1,3,5           # Select interesting books
v               # Preview selection
d               # Download
```

### Keyboard Shortcuts

- Most commands work with just the first letter: `f`, `n`, `p`, `a`, `u`, `c`, `v`, `m`, `d`, `q`
- Numbers work directly: `1`, `2`, `3`, etc.
- Use `cf` to quickly clear filters

## 📋 Complete Command Reference

| Command          | Description                                    |
| ---------------- | ---------------------------------------------- |
| `[1-20]`         | Select/unselect book (toggle)                  |
| `n/next`         | Next page                                      |
| `p/prev`         | Previous page                                  |
| `a/all`          | Select all books on current page               |
| `u/unall`        | Unselect all books on current page             |
| `s/select`       | Select by range (e.g., 1-5,10,15-20)           |
| `f/filter`       | Filter books (or `f <term>` for direct filter) |
| `cf/clearfilter` | Clear current filter                           |
| `c/clear`        | Clear all selections                           |
| `v/view`         | View details of selected books                 |
| `m/missing`      | Select books missing from another server       |
| `d/download`     | Start download                                 |
| `q/quit`         | Exit without downloading                       |

## 🎬 Example Session

```bash
$ python book_selector.py

📚 Books (Page 1/50)
# ✓ Title                           Author               Duration     Audio Ebook
1   Outdoor Kids in an Inside World Steven Rinella        6h 3m        ✓     ✓
2   The Last Sweet Bite             Michael Shaikh        7h 32m       ✓     ✗
...

Enter command: f terry
Found 12 books matching 'terry'

# ✓ Title                           Author               Duration     Audio Ebook
1   Wizard's First Rule             Terry Goodkind        32h 53m      ✓     ✗
2   Stone of Tears                  Terry Goodkind        38h 18m      ✓     ✗
...

Enter command: a
Enter command: v

📚 Selected Books (12):
1. Wizard's First Rule
   Author: Terry Goodkind
   Duration: 32h 53m
   Files: M4A

2. Stone of Tears
   Author: Terry Goodkind
   Duration: 38h 18m
   Files: M4A
...

Total Duration: 284h 15m

Enter command: d
🚀 Ready to download 12 books!
Continue? (y/N): y
```

---

[← Back to Main README](README.md) | [API Keys →](API_KEYS.md)
