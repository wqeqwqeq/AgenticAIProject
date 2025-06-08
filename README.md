# Agentic AI Project Collection

This repository contains 5 diverse Python projects showcasing different aspects of automation, web scraping, data processing, and computer vision. Each project demonstrates practical applications of AI and automation technologies.

## 📋 Projects Overview

### 1. CVPR Paper Extractor 📚
**Location**: `1. CVPR/`

A web scraping tool that extracts paper information from the CVPR (Computer Vision and Pattern Recognition) conference website. This project automates the process of collecting academic paper metadata for research purposes.

**Key Features**:
- Extracts paper titles, authors, and document links from CVPR HTML pages
- Parses PDF links, supplementary materials, and arXiv references
- Exports structured data to JSON format for further analysis
- Command-line interface with customizable input/output options
- Built-in error handling and data validation

**Technologies**: Python, BeautifulSoup, HTML parsing, JSON processing

---

### 2. Instagram Media Downloader 📸
**Location**: `2. Instagram/`

A sophisticated Instagram media downloader built with Playwright that simulates real browser behavior to bypass anti-bot measures. Features intelligent cookie management and carousel post support for comprehensive media extraction.

**Key Features**:
- **Playwright-based browser automation** - Simulates real user interactions
- **Cookie persistence** - Saves login session to avoid repeated logins
- **Carousel post support** - Clicks into posts to extract all images from multi-image posts
- **Intelligent scrolling** - Automatically scrolls to load more content
- **Rate limiting protection** - Built-in delays to respect Instagram's limits
- **Headless/visible modes** - Can run with or without browser window
- **Async downloads** - Efficient parallel image downloading with aiohttp
- **Command-line interface** - Flexible options for different use cases

**Main Scripts**:
- `instagram_scrape.py` - Core downloader with grid-based extraction
- `instagram_downloader_carousel.py` - Enhanced version that clicks into posts for carousel images

**Technologies**: Python, Playwright, aiohttp, asyncio, JSON cookie management

**Advanced Features**:
- Manual login support with automatic session detection
- Cookie expiration handling (30-day validity)
- Browser context with realistic user agents
- Error recovery and retry mechanisms
- Customizable output directories and file naming

**Note**: This tool uses browser automation (not web scraping APIs) and is designed for educational purposes. Use in compliance with Instagram's Terms of Service.

---

### 3. Search Engine Redirect Bookmarklet 🔍
**Location**: `3. Bookmarklet/`

A JavaScript bookmarklet that captures search queries from one search engine and redirects them to alternative search engines. Perfect for comparing search results across different platforms.

**Key Features**:
- Multi-engine support (Google, Bing, Yahoo, DuckDuckGo, Baidu)
- Automatic query extraction from different URL formats
- One-click redirection to alternative search engines
- Proper URL encoding for special characters
- Interactive demo page for easy installation

**Technologies**: JavaScript, Browser APIs, URL manipulation

**Supported Redirects**:
- Google → Baidu
- Bing → Google  
- Yahoo → DuckDuckGo
- DuckDuckGo → Google
- Baidu → Google

---

### 4. ImageChat - AI Vision Analysis 🖼️
**Location**: `4. ImageChat/`

A powerful image analysis application leveraging OpenAI's GPT-4 Vision API. This tool can describe images, answer questions about visual content, count objects, and extract text from images.

**Key Features**:
- Detailed image descriptions with multiple detail levels
- Question answering about image content
- Object counting and identification
- OCR (Optical Character Recognition) functionality
- Batch processing for multiple images
- Interactive command-line interface
- API rate limiting and error handling
- Support for local files and URLs

**Technologies**: Python, OpenAI GPT-4 Vision API, PIL/Pillow, Base64 encoding

**Use Cases**:
- Content analysis and description
- Accessibility applications
- Document digitization
- Visual question answering
- Research and data analysis

---

### 5. PiChallenge - Automated Drawing 🎨
**Location**: `5. PiChallenge/`

An automation script that uses pyautogui to draw perfect circles in graphics applications like Paint. This project demonstrates GUI automation and mathematical programming for creative applications.

**Key Features**:
- Automated circle drawing using mathematical calculations
- Configurable center position and radius
- Smooth drawing with adjustable steps for precision
- Built-in delay system for setup
- Cross-platform GUI automation

**Technologies**: Python, pyautogui, mathematical calculations (trigonometry)

**Applications**:
- Digital art automation
- GUI testing demonstrations
- Educational tool for programming concepts
- Accessibility assistance for drawing applications

---

## 🚀 Getting Started

Each project has its own requirements and setup instructions. Navigate to the individual project directories for detailed installation and usage guides.

### General Prerequisites
- Python 3.8+ (for Python projects)
- Modern web browser (for bookmarklet)
- Individual project dependencies (see each project's `requirements.txt`)

### Quick Setup Template
```bash
# Navigate to desired project
cd "1. CVPR"  # or any other project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the project (varies by project)
python main_script.py
```

## 🛡️ Important Notes

- **Ethics**: All tools should be used responsibly and in compliance with respective service terms
- **Rate Limits**: Web scraping projects include rate limiting to be respectful to servers
- **Privacy**: Only process public data and respect privacy guidelines
- **Education**: These projects are primarily for educational and research purposes

## 📄 License

Each project may have its own licensing terms. Please refer to individual project directories for specific license information.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

For project-specific contributions, refer to the individual project documentation. 