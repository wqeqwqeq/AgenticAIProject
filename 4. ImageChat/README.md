# Image Analysis Program using GPT-4 Vision API

A powerful Python application that analyzes images using OpenAI's GPT-4 Vision API. This program can describe images, answer questions about their content, count objects, extract text (OCR), and more.

## Features

- 🖼️ **Image Analysis**: Detailed descriptions of images with multiple detail levels
- ❓ **Question Answering**: Ask specific questions about image content
- 🔢 **Object Counting**: Count specific objects in images
- 📄 **Text Extraction**: OCR functionality to extract text from images
- 🔗 **Multiple Input Types**: Support for local files and URLs
- 📁 **Batch Processing**: Analyze multiple images or entire directories
- 💾 **Result Saving**: Save analysis results to JSON files
- 🎨 **Interactive Mode**: User-friendly command-line interface
- 🛡️ **Error Handling**: Robust error handling and retry mechanisms
- ⚡ **Rate Limiting**: Built-in API rate limiting to avoid quota issues

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for API calls

## Installation

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd ImageChat
```

### 2. Set Up Virtual Environment

Using `uv` (recommended):

```bash
# Install uv if you haven't already
pip install uv

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Using standard Python:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# With uv
uv pip install -r requirements.txt

# With pip
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
MAX_IMAGE_SIZE_MB=10
API_TIMEOUT_SECONDS=30
DEFAULT_MODEL=gpt-4-vision-preview
```

## Usage

### Command Line Interface

#### Basic Image Analysis

```bash
# Analyze a single image
python src/main.py photo.jpg

# Analyze with custom prompt
python src/main.py photo.jpg -p "What objects are visible in this image?"

# Different detail levels
python src/main.py photo.jpg -d brief
python src/main.py photo.jpg -d detailed
python src/main.py photo.jpg -d comprehensive
```

#### Specialized Analysis

```bash
# Count objects
python src/main.py photo.jpg --count "people"

# Extract text (OCR)
python src/main.py photo.jpg --text

# Get image file information
python src/main.py photo.jpg --info
```

#### Batch Processing

```bash
# Analyze multiple images
python src/main.py -m image1.jpg image2.jpg image3.jpg

# Analyze all images in a directory
python src/main.py --directory /path/to/images

# Recursive directory search
python src/main.py --directory /path/to/images -r

# Save results to files
python src/main.py photo.jpg -s
```

#### Interactive Mode

```bash
python src/main.py -i
```

In interactive mode, you can use these commands:
- `analyze <image_path>` - Analyze an image
- `describe <image_path>` - Get detailed description
- `ask <image_path> <question>` - Ask a specific question
- `count <image_path> <object>` - Count objects
- `text <image_path>` - Extract text
- `info <image_path>` - Show image information
- `help` - Show available commands
- `quit` - Exit the program

### Python API

```python
from src.main import ImageAnalyzer

# Initialize analyzer
analyzer = ImageAnalyzer()

# Analyze single image
result = analyzer.analyze_single_image('photo.jpg')
print(result['content'])

# Ask specific question
result = analyzer.analyze_single_image('photo.jpg', prompt="What colors are in this image?")

# Analyze multiple images
results = analyzer.analyze_multiple_images(['img1.jpg', 'img2.jpg'])

# Analyze directory
results = analyzer.analyze_directory('/path/to/images')
```

### Using Individual Components

```python
from src.image_processor import ImageProcessor
from src.api_client import VisionAPIClient

# Process image
processor = ImageProcessor()
base64_image, info = processor.process_image('photo.jpg')

# Analyze with API
client = VisionAPIClient(api_key='your-key')
result = client.analyze_image(base64_image, "What's in this image?")
print(result['content'])
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | Your OpenAI API key |
| `DEFAULT_MODEL` | `gpt-4-vision-preview` | GPT-4 Vision model to use |
| `MAX_IMAGE_SIZE_MB` | `10` | Maximum image size in MB |
| `API_TIMEOUT_SECONDS` | `30` | API request timeout |
| `MAX_RETRIES` | `3` | Maximum retry attempts |
| `RATE_LIMIT_DELAY` | `1` | Seconds between API requests |

### Supported Image Formats

- JPEG/JPG
- PNG
- GIF
- BMP
- WEBP

### Input Sources

- Local file paths
- HTTP/HTTPS URLs
- Directories (with recursive option)

## API Usage and Costs

This application uses OpenAI's GPT-4 Vision API, which charges based on:
- **Input tokens**: Text prompt and image processing
- **Output tokens**: Generated response

### Cost Estimation

- Images are processed at high detail by default
- Typical cost per image: $0.01 - $0.05
- Batch processing can accumulate costs quickly
- Monitor your usage in the OpenAI dashboard

### Rate Limits

- Built-in rate limiting (1 second between requests)
- Automatic retry with exponential backoff
- Respects OpenAI's API rate limits

## Error Handling

The application includes comprehensive error handling for:

- **Invalid API keys**: Validation before processing
- **Rate limiting**: Automatic retry with backoff
- **Network issues**: Timeout handling and retries
- **Invalid images**: Format and size validation
- **File not found**: Clear error messages
- **API errors**: Detailed error reporting

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_image_processor.py

# Run with coverage
python -m pytest tests/ --cov=src/
```

## Project Structure

```
ImageChat/
├── .env                    # Environment variables (create this)
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
├── env.example           # Environment template
├── README.md             # This file
├── src/                  # Source code
│   ├── __init__.py
│   ├── main.py           # Main application
│   ├── image_processor.py # Image processing utilities
│   ├── api_client.py     # OpenAI API client
│   └── utils.py          # Utility functions
└── tests/                # Test files
    ├── __init__.py
    ├── test_image_processor.py
    ├── test_api_client.py
    └── test_main.py
```

## Examples

### Basic Analysis

```bash
$ python src/main.py sample.jpg

📸 Processing image: sample.jpg
✅ Image processed: (1024, 768) pixels, 45.2 KB

This image shows a beautiful sunset over a mountain landscape. The sky is painted 
in vibrant shades of orange, pink, and purple, with wispy clouds scattered across 
the horizon. In the foreground, there are silhouettes of pine trees, and a small 
lake reflects the colorful sky. The scene conveys a sense of tranquility and 
natural beauty.

📊 Analysis Details:
- Model: gpt-4-vision-preview
- Tokens used: 89 (prompt: 12, completion: 77)
```

### Interactive Session

```bash
$ python src/main.py -i

🤖 Image Analysis Program - Interactive Mode
Type 'help' for available commands or 'quit' to exit.

📷 Enter command: analyze vacation.jpg
📸 Processing image: vacation.jpg
✅ Image processed: (800, 600) pixels, 32.1 KB

🔍 Analysis Result:
The image shows a tropical beach scene with crystal clear turquoise water...

📷 Enter command: ask vacation.jpg "How many people are in this photo?"
💬 Answer:
I can see 3 people in this photo - two adults and one child playing in the sand...
```

## Troubleshooting

### Common Issues

1. **"OpenAI API key is required"**
   - Ensure `.env` file exists with valid `OPENAI_API_KEY`
   - Check that the API key is active in your OpenAI account

2. **"Invalid image file"**
   - Verify the file exists and is a supported format
   - Check file permissions

3. **"Rate limit exceeded"**
   - The app will automatically retry with backoff
   - Consider increasing `RATE_LIMIT_DELAY` in `.env`

4. **"Image size too large"**
   - Reduce `MAX_IMAGE_SIZE_MB` or use smaller images
   - The app automatically optimizes images when possible

5. **Import errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

### Getting Help

- Check the logs for detailed error messages
- Use `--info` flag to inspect image properties
- Try interactive mode for step-by-step debugging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v1.0.0
- Initial release
- Basic image analysis functionality
- Interactive mode
- Batch processing
- Comprehensive error handling
- Full test suite

## Acknowledgments

- OpenAI for the GPT-4 Vision API
- PIL/Pillow for image processing
- The Python community for excellent libraries 