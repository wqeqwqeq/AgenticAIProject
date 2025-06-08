"""
Image processing utilities for the GPT-4 Vision API integration.
"""

import os
import base64
from io import BytesIO
from typing import Union, Tuple, Optional
from PIL import Image
import requests


class ImageProcessor:
    """Handles image loading, validation, and processing for API transmission."""
    
    def __init__(self, max_size_mb: int = 10):
        """
        Initialize the image processor.
        
        Args:
            max_size_mb: Maximum allowed image size in megabytes
        """
        self.max_size_mb = max_size_mb
        self.supported_formats = {'JPEG', 'PNG', 'GIF', 'BMP', 'WEBP'}
    
    def load_image(self, image_source: Union[str, bytes]) -> Image.Image:
        """
        Load an image from file path, URL, or bytes.
        
        Args:
            image_source: Path to image file, URL, or image bytes
            
        Returns:
            PIL Image object
            
        Raises:
            ValueError: If image cannot be loaded or is invalid
            FileNotFoundError: If local file doesn't exist
        """
        try:
            if isinstance(image_source, str):
                if image_source.startswith(('http://', 'https://')):
                    # Load from URL
                    response = requests.get(image_source, timeout=30)
                    response.raise_for_status()
                    image = Image.open(BytesIO(response.content))
                else:
                    # Load from file path
                    if not os.path.exists(image_source):
                        raise FileNotFoundError(f"Image file not found: {image_source}")
                    image = Image.open(image_source)
            else:
                # Load from bytes
                image = Image.open(BytesIO(image_source))
            
            # Validate format
            if image.format not in self.supported_formats:
                raise ValueError(f"Unsupported image format: {image.format}")
            
            return image
            
        except Exception as e:
            raise ValueError(f"Failed to load image: {str(e)}")
    
    def validate_image_size(self, image: Image.Image) -> bool:
        """
        Validate that image size is within acceptable limits.
        
        Args:
            image: PIL Image object
            
        Returns:
            True if image size is acceptable
            
        Raises:
            ValueError: If image is too large
        """
        # Calculate image size in bytes
        buffer = BytesIO()
        image.save(buffer, format=image.format or 'JPEG')
        size_bytes = buffer.tell()
        size_mb = size_bytes / (1024 * 1024)
        
        if size_mb > self.max_size_mb:
            raise ValueError(f"Image size ({size_mb:.2f}MB) exceeds maximum allowed size ({self.max_size_mb}MB)")
        
        return True
    
    def optimize_image(self, image: Image.Image, max_dimension: int = 1024) -> Image.Image:
        """
        Optimize image for API transmission by resizing if necessary.
        
        Args:
            image: PIL Image object
            max_dimension: Maximum width or height in pixels
            
        Returns:
            Optimized PIL Image object
        """
        width, height = image.size
        
        # Resize if image is too large
        if max(width, height) > max_dimension:
            if width > height:
                new_width = max_dimension
                new_height = int((height * max_dimension) / width)
            else:
                new_height = max_dimension
                new_width = int((width * max_dimension) / height)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary (for JPEG encoding)
        if image.mode in ('RGBA', 'P'):
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = rgb_image
        
        return image
    
    def encode_image_to_base64(self, image: Image.Image, format: str = 'JPEG', quality: int = 85) -> str:
        """
        Encode image to base64 string for API transmission.
        
        Args:
            image: PIL Image object
            format: Output format (JPEG, PNG)
            quality: JPEG quality (1-100)
            
        Returns:
            Base64 encoded image string
        """
        buffer = BytesIO()
        
        if format.upper() == 'JPEG':
            image.save(buffer, format='JPEG', quality=quality, optimize=True)
        else:
            image.save(buffer, format=format, optimize=True)
        
        buffer.seek(0)
        image_bytes = buffer.read()
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def process_image(self, image_source: Union[str, bytes], 
                     optimize: bool = True) -> Tuple[str, dict]:
        """
        Complete image processing pipeline.
        
        Args:
            image_source: Path to image file, URL, or image bytes
            optimize: Whether to optimize the image for API transmission
            
        Returns:
            Tuple of (base64_encoded_image, image_info)
        """
        # Load image
        image = self.load_image(image_source)
        
        # Store original dimensions
        original_size = image.size
        original_format = image.format
        
        # Optimize if requested
        if optimize:
            image = self.optimize_image(image)
        
        # Validate size
        self.validate_image_size(image)
        
        # Encode to base64
        base64_image = self.encode_image_to_base64(image)
        
        # Prepare image info
        image_info = {
            'original_size': original_size,
            'processed_size': image.size,
            'format': original_format,
            'optimized': optimize,
            'base64_size_kb': len(base64_image) / 1024
        }
        
        return base64_image, image_info


def get_image_info(image_path: str) -> dict:
    """
    Get basic information about an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with image information
    """
    try:
        with Image.open(image_path) as img:
            return {
                'filename': os.path.basename(image_path),
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height,
                'file_size_bytes': os.path.getsize(image_path)
            }
    except Exception as e:
        return {'error': str(e)} 