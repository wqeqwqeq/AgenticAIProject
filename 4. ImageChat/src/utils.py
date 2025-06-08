"""
Utility functions for the image analysis program.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
from dotenv import load_dotenv


def format_response(response_data: Dict[str, Any], include_metadata: bool = False) -> str:
    """
    Format API response for display.
    
    Args:
        response_data: Response from the Vision API
        include_metadata: Whether to include metadata in the output
        
    Returns:
        Formatted string response
    """
    if not response_data.get('success', False):
        error_msg = response_data.get('message', 'Unknown error')
        return f"❌ Error: {error_msg}"
    
    content = response_data.get('content', '')
    
    if not include_metadata:
        return content
    
    # Add metadata
    usage = response_data.get('usage', {})
    model = response_data.get('model', 'Unknown')
    
    metadata = f"\n\n📊 **Analysis Details:**\n"
    metadata += f"- Model: {model}\n"
    
    if usage:
        metadata += f"- Tokens used: {usage.get('total_tokens', 0)} "
        metadata += f"(prompt: {usage.get('prompt_tokens', 0)}, completion: {usage.get('completion_tokens', 0)})\n"
    
    return content + metadata


def validate_image_path(path: str) -> bool:
    """
    Validate if the given path is a valid image file.
    
    Args:
        path: Path to the image file
        
    Returns:
        True if valid image path, False otherwise
    """
    if not os.path.exists(path):
        return False
    
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    _, ext = os.path.splitext(path.lower())
    
    return ext in valid_extensions


def validate_image_url(url: str) -> bool:
    """
    Validate if the given URL appears to be an image URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if appears to be valid image URL, False otherwise
    """
    if not url.startswith(('http://', 'https://')):
        return False
    
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    
    # Check if URL ends with image extension
    for ext in valid_extensions:
        if url.lower().endswith(ext):
            return True
    
    # Check if URL contains image extension with parameters
    for ext in valid_extensions:
        if ext in url.lower():
            return True
    
    return False


def get_config_from_env() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Returns:
        Dictionary with configuration values
    """
    # Load environment variables from .env file
    load_dotenv()
    
    return {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': os.getenv('DEFAULT_MODEL', 'gpt-4o'),
        'max_image_size_mb': int(os.getenv('MAX_IMAGE_SIZE_MB', '10')),
        'api_timeout': int(os.getenv('API_TIMEOUT_SECONDS', '30')),
        'max_retries': int(os.getenv('MAX_RETRIES', '3')),
        'rate_limit_delay': int(os.getenv('RATE_LIMIT_DELAY', '1'))
    }


def save_analysis_result(result: Dict[str, Any], output_file: str = None) -> str:
    """
    Save analysis result to a JSON file.
    
    Args:
        result: Analysis result dictionary
        output_file: Output file path (if None, generates timestamp-based name)
        
    Returns:
        Path to the saved file
    """
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"analysis_result_{timestamp}.json"
    
    # Add timestamp to the result
    result['saved_at'] = datetime.now().isoformat()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return output_file


def load_analysis_result(input_file: str) -> Dict[str, Any]:
    """
    Load analysis result from a JSON file.
    
    Args:
        input_file: Path to the input JSON file
        
    Returns:
        Analysis result dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def clean_text(text: str) -> str:
    """
    Clean and normalize text output.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def create_summary_report(analyses: List[Dict[str, Any]]) -> str:
    """
    Create a summary report from multiple analyses.
    
    Args:
        analyses: List of analysis results
        
    Returns:
        Formatted summary report
    """
    if not analyses:
        return "No analyses to summarize."
    
    total_tokens = sum(
        analysis.get('usage', {}).get('total_tokens', 0) 
        for analysis in analyses 
        if analysis.get('success', False)
    )
    
    successful_analyses = sum(1 for analysis in analyses if analysis.get('success', False))
    failed_analyses = len(analyses) - successful_analyses
    
    report = f"📋 **Analysis Summary Report**\n"
    report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    report += f"📊 **Statistics:**\n"
    report += f"- Total analyses: {len(analyses)}\n"
    report += f"- Successful: {successful_analyses}\n"
    report += f"- Failed: {failed_analyses}\n"
    report += f"- Total tokens used: {total_tokens:,}\n\n"
    
    if successful_analyses > 0:
        report += f"✅ **Successful Analyses:**\n"
        for i, analysis in enumerate(analyses, 1):
            if analysis.get('success', False):
                content_preview = analysis.get('content', '')[:100]
                if len(content_preview) > 100:
                    content_preview += "..."
                report += f"{i}. {content_preview}\n"
    
    if failed_analyses > 0:
        report += f"\n❌ **Failed Analyses:**\n"
        for i, analysis in enumerate(analyses, 1):
            if not analysis.get('success', False):
                error_msg = analysis.get('message', 'Unknown error')
                report += f"{i}. Error: {error_msg}\n"
    
    return report


def print_colored(text: str, color: str = 'white') -> None:
    """
    Print colored text to console (basic ANSI colors).
    
    Args:
        text: Text to print
        color: Color name ('red', 'green', 'yellow', 'blue', 'cyan', 'magenta', 'white')
    """
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'magenta': '\033[95m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    
    color_code = colors.get(color.lower(), colors['white'])
    print(f"{color_code}{text}{colors['reset']}")


def progress_bar(current: int, total: int, width: int = 50) -> str:
    """
    Create a simple progress bar.
    
    Args:
        current: Current progress value
        total: Total progress value
        width: Width of the progress bar
        
    Returns:
        Progress bar string
    """
    if total == 0:
        return "[" + "=" * width + "] 100%"
    
    progress = current / total
    filled_width = int(progress * width)
    bar = "=" * filled_width + "-" * (width - filled_width)
    percentage = int(progress * 100)
    
    return f"[{bar}] {percentage}% ({current}/{total})"


def extract_image_paths_from_directory(directory: str, recursive: bool = False) -> List[str]:
    """
    Extract all image file paths from a directory.
    
    Args:
        directory: Directory path to search
        recursive: Whether to search subdirectories
        
    Returns:
        List of image file paths
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    image_paths = []
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            for file in files:
                _, ext = os.path.splitext(file.lower())
                if ext in image_extensions:
                    image_paths.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(file.lower())
                if ext in image_extensions:
                    image_paths.append(file_path)
    
    return sorted(image_paths) 