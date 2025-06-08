# Instagram Picture Downloader

A Python script to download pictures from Instagram profiles using multiple methods and robust error handling.

## 🚀 Features

- **Multiple Download Methods**: Choose from different approaches based on your needs
- **Rate Limiting Protection**: Built-in delays to avoid Instagram's restrictions
- **Command-line Interface**: Easy to use with various options
- **Error Recovery**: Handles common Instagram API issues gracefully
- **Metadata Support**: Option to save post metadata along with images

## 📋 Available Methods

### 1. instaloader (Recommended)
- **Best for**: Public profiles, reliable downloads
- **Pros**: Handles Instagram's restrictions, saves metadata
- **Cons**: May hit rate limits, requires patience

### 2. requests (Basic/Educational)
- **Best for**: Learning, experimentation
- **Pros**: Fast, lightweight
- **Cons**: Instagram actively blocks this, needs constant updates

### 3. selenium (Future Implementation)
- **Best for**: Private profiles (with login), complex scenarios
- **Pros**: Works like real browser, handles dynamic content
- **Cons**: Slower, requires browser driver

## 🛠️ Installation

1. **Create virtual environment** (using uv):
   ```bash
   uv venv
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

## 📖 Usage

### Basic Usage

Download 5 pictures from a profile:
```bash
uv run instagram_downloader_v2.py --username grapeot --count 5
```

Download from URL:
```bash
uv run instagram_downloader_v2.py --url https://www.instagram.com/grapeot/ --count 5
```

### Advanced Options

Download with videos:
```bash
uv run instagram_downloader_v2.py --username grapeot --count 10 --download-videos
```

Specify output directory:
```bash
uv run instagram_downloader_v2.py --username grapeot --output-dir ./my_downloads
```

Use different method:
```bash
uv run instagram_downloader_v2.py --username grapeot --method requests
```

View all available methods:
```bash
uv run instagram_downloader_v2.py --method info
```

### Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--username` | `-u` | Instagram username | Required* |
| `--url` | | Instagram profile URL | Required* |
| `--count` | `-c` | Number of posts to download | 5 |
| `--method` | `-m` | Download method (`instaloader`, `requests`, `info`) | `instaloader` |
| `--download-videos` | | Include videos in download | False |
| `--output-dir` | `-o` | Output directory | `downloads` |

*Either `--username` or `--url` is required

## 🔧 Troubleshooting

### Common Issues

1. **Rate Limiting (403/401 errors)**
   - Wait a few minutes between attempts
   - Use smaller batch sizes (`--count 3`)
   - Instagram increasingly restricts anonymous access

2. **Profile Not Found**
   - Verify the username is correct
   - Check if the profile is public
   - Some profiles may require login

3. **Download Failures**
   - Try with a different method
   - Check your internet connection
   - Consider using a VPN if blocked

### Tips for Success

- **Start small**: Begin with `--count 5` or less
- **Be patient**: Add delays between downloads
- **Respect limits**: Don't abuse Instagram's servers
- **Check Terms**: Follow Instagram's Terms of Service

## 📁 Output Structure

Downloaded files are organized as:
```
downloads/
└── username/
    ├── 2024-01-01_12-34-56_UTC.jpg
    ├── 2024-01-01_12-34-56_UTC.json  (metadata)
    └── ...
```

## ⚠️ Important Notes

- **Instagram's Terms**: Always respect Instagram's Terms of Service
- **Rate Limits**: Instagram actively prevents automated access
- **Privacy**: Only download from public profiles you have permission to access
- **Personal Use**: This tool is intended for personal, educational, or research purposes

## 🐛 Known Issues

- Instagram frequently changes their API, which may break some methods
- Rate limiting is increasingly strict
- Some profiles may require authentication even if public

## 📝 License

This project is for educational purposes. Users are responsible for complying with Instagram's Terms of Service and applicable laws.

## 🤝 Contributing

Issues and lessons learned are tracked in `.knowledge` file. Feel free to contribute improvements and alternative methods. 