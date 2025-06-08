"""
Unit tests for the image processor module.
"""

import unittest
import tempfile
import os
from unittest.mock import patch, Mock
from PIL import Image
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from image_processor import ImageProcessor, get_image_info


class TestImageProcessor(unittest.TestCase):
    """Test cases for ImageProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = ImageProcessor(max_size_mb=5)
        
        # Create a temporary test image
        self.temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        image = Image.new('RGB', (100, 100), color='red')
        image.save(self.temp_image.name, 'JPEG')
        self.temp_image.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_image.name):
            os.unlink(self.temp_image.name)
    
    def test_load_image_from_file(self):
        """Test loading image from file path."""
        image = self.processor.load_image(self.temp_image.name)
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(image.size, (100, 100))
    
    def test_load_image_file_not_found(self):
        """Test loading non-existent image file."""
        with self.assertRaises(ValueError):
            self.processor.load_image('nonexistent.jpg')
    
    @patch('requests.get')
    def test_load_image_from_url(self, mock_get):
        """Test loading image from URL."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        
        # Create mock image content
        temp_image = Image.new('RGB', (50, 50), color='blue')
        from io import BytesIO
        buffer = BytesIO()
        temp_image.save(buffer, format='JPEG')
        mock_response.content = buffer.getvalue()
        
        mock_get.return_value = mock_response
        
        image = self.processor.load_image('https://example.com/test.jpg')
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(image.size, (50, 50))
    
    def test_validate_image_size_success(self):
        """Test successful image size validation."""
        image = Image.new('RGB', (100, 100), color='green')
        result = self.processor.validate_image_size(image)
        self.assertTrue(result)
    
    def test_optimize_image_resize(self):
        """Test image optimization with resizing."""
        # Create large image
        large_image = Image.new('RGB', (2000, 1500), color='yellow')
        optimized = self.processor.optimize_image(large_image, max_dimension=1024)
        
        # Should be resized
        self.assertLessEqual(max(optimized.size), 1024)
        # Aspect ratio should be preserved
        self.assertAlmostEqual(
            large_image.width / large_image.height,
            optimized.width / optimized.height,
            places=2
        )
    
    def test_optimize_image_no_resize_needed(self):
        """Test image optimization when no resize is needed."""
        small_image = Image.new('RGB', (500, 400), color='purple')
        optimized = self.processor.optimize_image(small_image, max_dimension=1024)
        
        # Should not be resized
        self.assertEqual(optimized.size, (500, 400))
    
    def test_encode_image_to_base64(self):
        """Test base64 encoding of image."""
        image = Image.new('RGB', (50, 50), color='orange')
        base64_str = self.processor.encode_image_to_base64(image)
        
        self.assertIsInstance(base64_str, str)
        self.assertTrue(len(base64_str) > 0)
        
        # Should be valid base64
        import base64
        try:
            base64.b64decode(base64_str)
        except Exception:
            self.fail("Generated string is not valid base64")
    
    def test_process_image_complete_pipeline(self):
        """Test complete image processing pipeline."""
        base64_image, image_info = self.processor.process_image(self.temp_image.name)
        
        # Check base64 output
        self.assertIsInstance(base64_image, str)
        self.assertTrue(len(base64_image) > 0)
        
        # Check image info
        self.assertIsInstance(image_info, dict)
        self.assertIn('original_size', image_info)
        self.assertIn('processed_size', image_info)
        self.assertIn('format', image_info)
        self.assertIn('optimized', image_info)
        self.assertIn('base64_size_kb', image_info)
        
        self.assertEqual(image_info['original_size'], (100, 100))


class TestGetImageInfo(unittest.TestCase):
    """Test cases for get_image_info function."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary test image
        self.temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        image = Image.new('RGBA', (200, 150), color='cyan')
        image.save(self.temp_image.name, 'PNG')
        self.temp_image.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_image.name):
            os.unlink(self.temp_image.name)
    
    def test_get_image_info_success(self):
        """Test successful image info extraction."""
        info = get_image_info(self.temp_image.name)
        
        self.assertIsInstance(info, dict)
        self.assertNotIn('error', info)
        
        # Check required fields
        expected_fields = ['filename', 'format', 'mode', 'size', 'width', 'height', 'file_size_bytes']
        for field in expected_fields:
            self.assertIn(field, info)
        
        # Check values
        self.assertEqual(info['format'], 'PNG')
        self.assertEqual(info['mode'], 'RGBA')
        self.assertEqual(info['size'], (200, 150))
        self.assertEqual(info['width'], 200)
        self.assertEqual(info['height'], 150)
        self.assertGreater(info['file_size_bytes'], 0)
    
    def test_get_image_info_file_not_found(self):
        """Test image info for non-existent file."""
        info = get_image_info('nonexistent.jpg')
        
        self.assertIsInstance(info, dict)
        self.assertIn('error', info)


if __name__ == '__main__':
    unittest.main() 