"""
Main application for the Image Analysis Program using GPT-4 Vision API.
"""

import argparse
import sys
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from image_processor import ImageProcessor, get_image_info
from api_client import VisionAPIClient
from utils import (
    format_response, validate_image_path, validate_image_url, 
    get_config_from_env, save_analysis_result, print_colored,
    progress_bar, extract_image_paths_from_directory, create_summary_report
)


class ImageAnalyzer:
    """Main application class for image analysis."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Image Analyzer.
        
        Args:
            config: Configuration dictionary (if None, loads from environment)
        """
        self.config = config or get_config_from_env()
        
        if not self.config.get('api_key'):
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY environment variable.")
        
        # Initialize components
        self.image_processor = ImageProcessor(max_size_mb=self.config['max_image_size_mb'])
        self.api_client = VisionAPIClient(
            api_key=self.config['api_key'],
            model=self.config['model'],
            timeout=self.config['api_timeout'],
            max_retries=self.config['max_retries']
        )
        
        # Validate API key
        if not self.api_client.validate_api_key():
            raise ValueError("Invalid OpenAI API key. Please check your API key.")
    
    def analyze_single_image(self, image_source: str, prompt: str = None, 
                           detail_level: str = "detailed", save_result: bool = False) -> Dict[str, Any]:
        """
        Analyze a single image.
        
        Args:
            image_source: Path to image file or URL
            prompt: Custom prompt for analysis
            detail_level: Level of detail for description
            save_result: Whether to save the result to file
            
        Returns:
            Analysis result dictionary
        """
        try:
            print_colored(f"📸 Processing image: {image_source}", "cyan")
            
            # Process image
            base64_image, image_info = self.image_processor.process_image(image_source)
            
            print_colored(f"✅ Image processed: {image_info['processed_size']} pixels, "
                         f"{image_info['base64_size_kb']:.1f} KB", "green")
            
            # Analyze image
            if prompt:
                result = self.api_client.ask_about_image(base64_image, prompt)
            else:
                result = self.api_client.get_image_description(base64_image, detail_level)
            
            # Add image info to result
            result['image_info'] = image_info
            result['source'] = image_source
            
            if save_result:
                output_file = save_analysis_result(result)
                print_colored(f"💾 Result saved to: {output_file}", "yellow")
            
            return result
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': 'Processing failed',
                'message': str(e),
                'source': image_source
            }
            
            if save_result:
                output_file = save_analysis_result(error_result)
                print_colored(f"💾 Error result saved to: {output_file}", "yellow")
            
            return error_result
    
    def analyze_multiple_images(self, image_sources: List[str], prompt: str = None,
                               batch_size: int = 1, save_results: bool = False) -> List[Dict[str, Any]]:
        """
        Analyze multiple images.
        
        Args:
            image_sources: List of image paths or URLs
            prompt: Custom prompt for analysis
            batch_size: Number of images to process in each batch (currently supports 1)
            save_results: Whether to save results to files
            
        Returns:
            List of analysis results
        """
        results = []
        total_images = len(image_sources)
        
        print_colored(f"🔄 Starting analysis of {total_images} images", "cyan")
        
        for i, image_source in enumerate(image_sources, 1):
            print(f"\n{progress_bar(i-1, total_images)} Processing image {i}/{total_images}")
            
            result = self.analyze_single_image(
                image_source, 
                prompt, 
                save_result=save_results
            )
            
            results.append(result)
            
            # Show progress
            if result.get('success'):
                print_colored("✅ Analysis completed", "green")
            else:
                print_colored("❌ Analysis failed", "red")
        
        print(f"\n{progress_bar(total_images, total_images)} Complete!")
        
        # Generate summary
        summary = create_summary_report(results)
        print_colored(f"\n{summary}", "white")
        
        return results
    
    def analyze_directory(self, directory_path: str, prompt: str = None,
                         recursive: bool = False, save_results: bool = False) -> List[Dict[str, Any]]:
        """
        Analyze all images in a directory.
        
        Args:
            directory_path: Path to the directory
            prompt: Custom prompt for analysis
            recursive: Whether to search subdirectories
            save_results: Whether to save results to files
            
        Returns:
            List of analysis results
        """
        if not os.path.isdir(directory_path):
            raise ValueError(f"Directory not found: {directory_path}")
        
        # Extract image paths
        image_paths = extract_image_paths_from_directory(directory_path, recursive)
        
        if not image_paths:
            print_colored("No images found in the directory.", "yellow")
            return []
        
        print_colored(f"📁 Found {len(image_paths)} images in directory", "cyan")
        
        return self.analyze_multiple_images(image_paths, prompt, save_results=save_results)
    
    def interactive_mode(self):
        """Run the application in interactive mode."""
        print_colored("🤖 Image Analysis Program - Interactive Mode", "cyan")
        print_colored("Type 'help' for available commands or 'quit' to exit.\n", "white")
        
        while True:
            try:
                command = input("📷 Enter command: ").strip().lower()
                
                if command in ['quit', 'exit', 'q']:
                    print_colored("👋 Goodbye!", "cyan")
                    break
                
                elif command == 'help':
                    self._show_help()
                
                elif command.startswith('analyze '):
                    image_path = command[8:].strip()
                    self._interactive_analyze(image_path)
                
                elif command.startswith('describe '):
                    image_path = command[9:].strip()
                    self._interactive_describe(image_path)
                
                elif command.startswith('ask '):
                    parts = command[4:].split(' ', 1)
                    if len(parts) == 2:
                        image_path, question = parts
                        self._interactive_ask(image_path.strip(), question.strip())
                    else:
                        print_colored("Usage: ask <image_path> <question>", "yellow")
                
                elif command.startswith('count '):
                    parts = command[6:].split(' ', 1)
                    if len(parts) == 2:
                        image_path, object_type = parts
                        self._interactive_count(image_path.strip(), object_type.strip())
                    else:
                        print_colored("Usage: count <image_path> <object_type>", "yellow")
                
                elif command.startswith('text '):
                    image_path = command[5:].strip()
                    self._interactive_extract_text(image_path)
                
                elif command.startswith('info '):
                    image_path = command[5:].strip()
                    self._show_image_info(image_path)
                
                else:
                    print_colored("Unknown command. Type 'help' for available commands.", "yellow")
            
            except KeyboardInterrupt:
                print_colored("\n👋 Goodbye!", "cyan")
                break
            except Exception as e:
                print_colored(f"❌ Error: {str(e)}", "red")
    
    def _show_help(self):
        """Show help information."""
        help_text = """
📋 Available Commands:
  analyze <image_path>           - Analyze an image with default description
  describe <image_path>          - Get detailed description of an image
  ask <image_path> <question>    - Ask a specific question about an image
  count <image_path> <object>    - Count specific objects in an image
  text <image_path>              - Extract text from an image (OCR)
  info <image_path>              - Show image file information
  help                           - Show this help message
  quit/exit/q                    - Exit the program

📝 Examples:
  analyze photo.jpg
  ask photo.jpg "What colors are prominent in this image?"
  count photo.jpg "people"
  text screenshot.png
        """
        print_colored(help_text, "white")
    
    def _interactive_analyze(self, image_path: str):
        """Interactive image analysis."""
        if not self._validate_image_input(image_path):
            return
        
        result = self.analyze_single_image(image_path)
        response = format_response(result, include_metadata=True)
        print_colored(f"\n🔍 Analysis Result:\n{response}\n", "white")
    
    def _interactive_describe(self, image_path: str):
        """Interactive image description."""
        if not self._validate_image_input(image_path):
            return
        
        result = self.analyze_single_image(image_path, detail_level="comprehensive")
        response = format_response(result)
        print_colored(f"\n📝 Description:\n{response}\n", "white")
    
    def _interactive_ask(self, image_path: str, question: str):
        """Interactive question answering."""
        if not self._validate_image_input(image_path):
            return
        
        result = self.analyze_single_image(image_path, prompt=question)
        response = format_response(result)
        print_colored(f"\n💬 Answer:\n{response}\n", "white")
    
    def _interactive_count(self, image_path: str, object_type: str):
        """Interactive object counting."""
        if not self._validate_image_input(image_path):
            return
        
        try:
            base64_image, _ = self.image_processor.process_image(image_path)
            result = self.api_client.count_objects(base64_image, object_type)
            response = format_response(result)
            print_colored(f"\n🔢 Count Result:\n{response}\n", "white")
        except Exception as e:
            print_colored(f"❌ Error: {str(e)}", "red")
    
    def _interactive_extract_text(self, image_path: str):
        """Interactive text extraction."""
        if not self._validate_image_input(image_path):
            return
        
        try:
            base64_image, _ = self.image_processor.process_image(image_path)
            result = self.api_client.extract_text(base64_image)
            response = format_response(result)
            print_colored(f"\n📄 Extracted Text:\n{response}\n", "white")
        except Exception as e:
            print_colored(f"❌ Error: {str(e)}", "red")
    
    def _show_image_info(self, image_path: str):
        """Show image file information."""
        if not os.path.exists(image_path):
            print_colored(f"❌ File not found: {image_path}", "red")
            return
        
        info = get_image_info(image_path)
        if 'error' in info:
            print_colored(f"❌ Error: {info['error']}", "red")
            return
        
        print_colored(f"\n📊 Image Information:", "cyan")
        for key, value in info.items():
            print_colored(f"  {key}: {value}", "white")
        print()
    
    def _validate_image_input(self, image_path: str) -> bool:
        """Validate image input."""
        if image_path.startswith(('http://', 'https://')):
            if not validate_image_url(image_path):
                print_colored(f"❌ Invalid image URL: {image_path}", "red")
                return False
        else:
            if not validate_image_path(image_path):
                print_colored(f"❌ Invalid image file: {image_path}", "red")
                return False
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Image Analysis Program using GPT-4 Vision API")
    parser.add_argument("image", nargs="?", help="Path to image file or URL")
    parser.add_argument("-p", "--prompt", help="Custom prompt for analysis")
    parser.add_argument("-d", "--detail", choices=["brief", "detailed", "comprehensive"], 
                       default="detailed", help="Detail level for description")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("-m", "--multiple", nargs="+", help="Analyze multiple images")
    parser.add_argument("--directory", help="Analyze all images in directory")
    parser.add_argument("-r", "--recursive", action="store_true", help="Search directories recursively")
    parser.add_argument("-s", "--save", action="store_true", help="Save results to files")
    parser.add_argument("--count", help="Count specific objects in the image")
    parser.add_argument("--text", action="store_true", help="Extract text from image (OCR)")
    parser.add_argument("--info", action="store_true", help="Show image file information only")
    
    args = parser.parse_args()
    
    try:
        # Show image info only (no API call needed)
        if args.info and args.image:
            info = get_image_info(args.image)
            if 'error' in info:
                print_colored(f"❌ Error: {info['error']}", "red")
                return 1
            
            print_colored("📊 Image Information:", "cyan")
            for key, value in info.items():
                print(f"  {key}: {value}")
            return 0
        
        # Initialize analyzer (requires API key)
        analyzer = ImageAnalyzer()
        
        # Interactive mode
        if args.interactive:
            analyzer.interactive_mode()
            return 0
        
        # Directory analysis
        if args.directory:
            results = analyzer.analyze_directory(
                args.directory, 
                args.prompt, 
                recursive=args.recursive,
                save_results=args.save
            )
            return 0
        
        # Multiple images
        if args.multiple:
            results = analyzer.analyze_multiple_images(
                args.multiple,
                args.prompt,
                save_results=args.save
            )
            return 0
        
        # Single image analysis
        if args.image:
            if args.count:
                # Count objects
                base64_image, _ = analyzer.image_processor.process_image(args.image)
                result = analyzer.api_client.count_objects(base64_image, args.count)
            elif args.text:
                # Extract text
                base64_image, _ = analyzer.image_processor.process_image(args.image)
                result = analyzer.api_client.extract_text(base64_image)
            else:
                # Regular analysis
                result = analyzer.analyze_single_image(
                    args.image, 
                    args.prompt, 
                    args.detail,
                    save_result=args.save
                )
            
            # Display result
            response = format_response(result, include_metadata=True)
            print_colored(response, "white")
            
            return 0 if result.get('success', False) else 1
        
        # No arguments provided
        print_colored("No image specified. Use --help for usage information or --interactive for interactive mode.", "yellow")
        return 1
        
    except KeyboardInterrupt:
        print_colored("\n👋 Operation cancelled by user.", "yellow")
        return 1
    except Exception as e:
        print_colored(f"❌ Error: {str(e)}", "red")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 