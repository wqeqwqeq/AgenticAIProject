# Instagram Media Downloader with Playwright

A sophisticated Instagram media downloader that uses Playwright to simulate real browser behavior and bypass anti-bot measures. Features intelligent cookie management, carousel post support, and efficient async downloading.

## 🚀 Features

- **Playwright Browser Automation**: Simulates real user interactions instead of direct API calls
- **Cookie Persistence**: Saves login session to avoid repeated logins (30-day validity)
- **Carousel Post Support**: Clicks into individual posts to extract all images from multi-image posts
- **Intelligent Scrolling**: Automatically scrolls to load more content from profiles
- **Two Download Modes**:
  - **Grid Mode** (`instagram_scrape.py`): Downloads from profile grid view
  - **Carousel Mode** (`instagram_downloader_carousel.py`): Enhanced extraction by clicking into posts
- **Async Downloads**: Efficient parallel downloading with aiohttp
- **Rate Limiting**: Built-in delays to respect Instagram's restrictions
- **Headless/Visible Modes**: Can run with or without browser window
- **Error Recovery**: Robust error handling and retry mechanisms

## 📋 Requirements

- Python 3.8+
- Modern browser (Chromium will be installed by Playwright)
- Dependencies listed in `requirements.txt`:
  - `playwright` - Browser automation
  - `aiohttp` - Async HTTP client for downloads
  - `requests` - HTTP requests
  - `pillow` - Image processing
  - `argparse` - Command-line interface

## 🛠️ Installation

1. **Navigate to project directory**:
   ```bash
   cd "2. Instagram"
   ```

2. **Install Python dependencies**:
   ```bash
   uv pip install -r requirements.txt
   # or with regular pip:
   pip install -r requirements.txt
   ```

3. **Install Playwright browser**:
   ```bash
   playwright install
   ```

## 📖 Usage

### Basic Grid Mode (instagram_scrape.py)

Downloads images from the profile grid view:

```bash
# Download 5 images from a username
uv run instagram_scrape.py --username grapeot --count 5

# Download from URL
uv run instagram_scrape.py --url https://www.instagram.com/grapeot/ --count 10

# Show browser window (useful for debugging)
uv run instagram_scrape.py --username grapeot --count 5 --show-browser

# Force login first
uv run instagram_scrape.py --username grapeot --count 10 --login --show-browser
```

### Enhanced Carousel Mode (instagram_downloader_carousel.py)

Downloads more images by clicking into posts to extract carousel images:

```bash
# Download up to 100 images including carousel images
uv run instagram_downloader_carousel.py --username grapeot --count 100 --show-browser

# Use with login for better access
uv run instagram_downloader_carousel.py --username grapeot --count 200 --login
```

### Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--username` | `-u` | Instagram username | Required* |
| `--url` | | Instagram profile URL | Required* |
| `--count` | `-c` | Number of images to download | 5 (grid), 50 (carousel) |
| `--output-dir` | `-o` | Output directory | `downloads` |
| `--show-browser` | | Show browser window | Hidden |
| `--login` | | Force login to Instagram | Auto-detect |
| `--no-cookies` | | Disable cookie saving/loading | Enabled |
| `--clear-cookies` | | Clear saved cookies and exit | N/A |

*Either `--username` or `--url` is required

### Cookie Management

The downloader automatically manages Instagram login cookies:

```bash
# Clear saved cookies
uv run instagram_scrape.py --clear-cookies

# Force login without using saved cookies
uv run instagram_scrape.py --username grapeot --no-cookies --login --show-browser
```

## 🎯 How It Works

### Grid Mode (`instagram_scrape.py`)
1. **Browser Launch**: Starts Chromium with realistic user agent
2. **Cookie Loading**: Attempts to load saved login cookies
3. **Login Handling**: Prompts for manual login if needed (saves cookies)
4. **Profile Navigation**: Goes to Instagram profile page
5. **Content Loading**: Scrolls page to load more posts
6. **Image Extraction**: Finds and extracts image URLs from grid
7. **Async Download**: Downloads images in parallel with rate limiting

### Carousel Mode (`instagram_downloader_carousel.py`)
1. **Profile Analysis**: Same initial steps as Grid Mode
2. **Post Discovery**: Finds all post links on the profile
3. **Post Navigation**: Clicks into each individual post
4. **Carousel Extraction**: Navigates through carousel images in each post
5. **Enhanced Collection**: Collects significantly more images per profile
6. **Bulk Download**: Downloads all collected images

### Cookie System
- **Automatic Saving**: Cookies saved after successful login
- **30-Day Validity**: Cookies expire after 30 days
- **Session Persistence**: Avoid repeated logins for the same account
- **Secure Storage**: Stored in local JSON file (`instagram_cookies.json`)

## 📁 Output Structure

Downloaded images are organized as:
```
downloads/
└── username/
    ├── username_1234567890_1.jpg
    ├── username_1234567890_2.jpg
    └── username_carousel_1234567890_3.jpg  # From carousel mode
```

Filename format: `{username}_{timestamp}_{index}.jpg`

## 🔧 Troubleshooting

### Common Issues

**1. Login Required**
```bash
# Solution: Use login mode with visible browser
uv run instagram_scrape.py --username grapeot --login --show-browser
```

**2. No Images Found**
- Profile might be private
- Instagram may be blocking access
- Try with `--login` and `--show-browser`

**3. Download Failures**
- Check internet connection
- Instagram may have rate-limited your IP
- Try with longer delays or smaller batch sizes

**4. Browser Issues**
```bash
# Reinstall Playwright browser
playwright install --force
```

### Success Tips

- **Start Small**: Begin with `--count 5` to test
- **Use Login**: Login provides better access to content
- **Be Patient**: Use appropriate delays between requests
- **Monitor Progress**: Use `--show-browser` to see what's happening
- **Respect Limits**: Don't abuse Instagram's servers

## ⚠️ Important Notes

- **Instagram Terms of Service**: Always comply with Instagram's terms
- **Rate Limiting**: Built-in delays to be respectful to Instagram's servers
- **Public Content Only**: Only download from public profiles you have permission to access
- **Educational Purpose**: This tool is for educational and research purposes
- **No Warranty**: Use at your own risk - Instagram frequently changes their anti-bot measures

## 🐛 Known Limitations

- Instagram actively prevents automated access
- Some profiles may require login even if public
- Rate limiting becomes stricter over time
- Carousel mode is slower but gets more images
- Browser detection may occasionally fail

## 📝 Technical Details

**Dependencies**:
- `playwright`: Browser automation framework
- `aiohttp`: Async HTTP client for efficient downloads
- `requests`: Backup HTTP functionality
- `pillow`: Image processing capabilities
- `argparse`: Command-line argument parsing

**Browser Settings**:
- Realistic user agent strings
- Disabled automation detection
- Standard viewport size (1366x768)
- Proper cookie handling

**Performance**:
- Async downloads for speed
- Intelligent scrolling algorithms
- Memory-efficient image processing
- Configurable rate limiting

## 🤝 Contributing

Issues and improvements are welcome! The codebase includes:
- `instagram_scrape.py` - Main grid-based downloader
- `instagram_downloader_carousel.py` - Enhanced carousel version
- Cookie management system
- Error handling and retry logic

---

**Disclaimer**: This tool is for educational purposes only. Users are responsible for complying with Instagram's Terms of Service and applicable laws. 