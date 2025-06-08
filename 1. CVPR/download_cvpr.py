#!/usr/bin/env python3

import argparse
import requests
from pathlib import Path
import sys
from datetime import datetime

def download_webpage(url: str, output_file: str = None) -> bool:
    """
    Download a webpage and save it to a file.
    
    Args:
        url (str): The URL to download
        output_file (str, optional): The output file path. If None, generates a filename based on timestamp.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Send GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Generate output filename if not provided
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"cvpr2024_{timestamp}.html"
        
        # Save the content to a file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"Successfully downloaded webpage to {output_file}")
        return True
        
    except requests.RequestException as e:
        print(f"Error downloading webpage: {e}", file=sys.stderr)
        return False
    except IOError as e:
        print(f"Error saving file: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description='Download CVPR 2024 webpage')
    parser.add_argument('--url', 
                       default='https://openaccess.thecvf.com/CVPR2024?day=all',
                       help='URL to download (default: CVPR 2024 webpage)')
    parser.add_argument('--output', '-o',
                       help='Output file path (default: cvpr2024_YYYYMMDD_HHMMSS.html)')
    
    args = parser.parse_args()
    
    success = download_webpage(args.url, args.output)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 