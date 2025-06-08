"""
OpenAI API client for GPT-4 Vision integration.
"""

import os
import time
from typing import List, Dict, Any, Optional, Union
import openai
from openai import OpenAI
import requests
from dotenv import load_dotenv


class VisionAPIClient:
    """Client for interacting with OpenAI's GPT-4 Vision API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-vision-preview", 
                 timeout: int = 30, max_retries: int = 3):
        """
        Initialize the Vision API client.
        
        Args:
            api_key: OpenAI API key (if None, will load from environment)
            model: Model to use for vision analysis
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        # Load environment variables
        load_dotenv()
        
        # Set API key
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1  # Minimum seconds between requests
    
    def _wait_for_rate_limit(self):
        """Implement simple rate limiting."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def analyze_image(self, base64_image: str, prompt: str = "What's in this image?", 
                     max_tokens: int = 300, detail: str = "auto") -> Dict[str, Any]:
        """
        Analyze an image using GPT-4 Vision API.
        
        Args:
            base64_image: Base64 encoded image string
            prompt: Question or instruction about the image
            max_tokens: Maximum tokens in response
            detail: Image detail level ("low", "high", "auto")
            
        Returns:
            Dictionary containing the analysis response and metadata
            
        Raises:
            Exception: If API request fails after retries
        """
        self._wait_for_rate_limit()
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": detail
                        }
                    }
                ]
            }
        ]
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    timeout=self.timeout
                )
                
                return {
                    'success': True,
                    'content': response.choices[0].message.content,
                    'model': response.model,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    'finish_reason': response.choices[0].finish_reason,
                    'created': response.created
                }
                
            except openai.RateLimitError as e:
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 60  # Exponential backoff in minutes
                    print(f"Rate limit exceeded. Waiting {wait_time} seconds before retry {attempt + 1}/{self.max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    return {
                        'success': False,
                        'error': 'Rate limit exceeded',
                        'error_type': 'rate_limit',
                        'message': str(e)
                    }
            
            except openai.APIError as e:
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 5  # Exponential backoff in seconds
                    print(f"API error. Waiting {wait_time} seconds before retry {attempt + 1}/{self.max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    return {
                        'success': False,
                        'error': 'API error',
                        'error_type': 'api_error',
                        'message': str(e)
                    }
            
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 10  # Exponential backoff in seconds
                    print(f"Request timeout. Waiting {wait_time} seconds before retry {attempt + 1}/{self.max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    return {
                        'success': False,
                        'error': 'Request timeout',
                        'error_type': 'timeout',
                        'message': f'Request timed out after {self.timeout} seconds'
                    }
            
            except Exception as e:
                return {
                    'success': False,
                    'error': 'Unexpected error',
                    'error_type': 'unknown',
                    'message': str(e)
                }
        
        return {
            'success': False,
            'error': 'Max retries exceeded',
            'error_type': 'max_retries',
            'message': f'Failed after {self.max_retries} attempts'
        }
    
    def analyze_multiple_images(self, images_data: List[Dict[str, Any]], 
                               prompt: str = "Compare and describe these images.", 
                               max_tokens: int = 500) -> Dict[str, Any]:
        """
        Analyze multiple images in a single request.
        
        Args:
            images_data: List of dictionaries with 'base64' and optional 'description' keys
            prompt: Question or instruction about the images
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary containing the analysis response and metadata
        """
        self._wait_for_rate_limit()
        
        content = [{"type": "text", "text": prompt}]
        
        for i, img_data in enumerate(images_data):
            # Add image description if provided
            if 'description' in img_data:
                content.append({
                    "type": "text", 
                    "text": f"Image {i+1}: {img_data['description']}"
                })
            
            # Add image
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_data['base64']}",
                    "detail": img_data.get('detail', 'auto')
                }
            })
        
        messages = [{"role": "user", "content": content}]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                timeout=self.timeout
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'model': response.model,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'finish_reason': response.choices[0].finish_reason,
                'created': response.created,
                'images_count': len(images_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Failed to analyze multiple images',
                'error_type': 'api_error',
                'message': str(e)
            }
    
    def get_image_description(self, base64_image: str, detail_level: str = "detailed") -> Dict[str, Any]:
        """
        Get a description of an image with specified detail level.
        
        Args:
            base64_image: Base64 encoded image string
            detail_level: Level of detail ("brief", "detailed", "comprehensive")
            
        Returns:
            Dictionary containing the description and metadata
        """
        prompts = {
            "brief": "Provide a brief, one-sentence description of this image.",
            "detailed": "Describe this image in detail, including objects, people, actions, colors, and setting.",
            "comprehensive": "Provide a comprehensive analysis of this image, including: 1) Main subjects and objects, 2) Setting and environment, 3) Colors and lighting, 4) Activities or actions, 5) Mood or atmosphere, 6) Any text visible in the image."
        }
        
        prompt = prompts.get(detail_level, prompts["detailed"])
        max_tokens = {"brief": 50, "detailed": 200, "comprehensive": 400}.get(detail_level, 200)
        
        return self.analyze_image(base64_image, prompt, max_tokens)
    
    def ask_about_image(self, base64_image: str, question: str) -> Dict[str, Any]:
        """
        Ask a specific question about an image.
        
        Args:
            base64_image: Base64 encoded image string
            question: Specific question about the image
            
        Returns:
            Dictionary containing the answer and metadata
        """
        return self.analyze_image(base64_image, question, max_tokens=300)
    
    def count_objects(self, base64_image: str, object_type: str) -> Dict[str, Any]:
        """
        Count specific objects in an image.
        
        Args:
            base64_image: Base64 encoded image string
            object_type: Type of object to count
            
        Returns:
            Dictionary containing the count and metadata
        """
        prompt = f"Count the number of {object_type} in this image. Provide only the number and a brief explanation of what you counted."
        return self.analyze_image(base64_image, prompt, max_tokens=100)
    
    def extract_text(self, base64_image: str) -> Dict[str, Any]:
        """
        Extract text from an image (OCR functionality).
        
        Args:
            base64_image: Base64 encoded image string
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        prompt = "Extract and transcribe all visible text from this image. If no text is visible, say 'No text found'."
        return self.analyze_image(base64_image, prompt, max_tokens=500)
    
    def validate_api_key(self) -> bool:
        """
        Validate the OpenAI API key by making a simple request.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            # Make a simple request to validate the key
            self.client.models.list()
            return True
        except Exception:
            return False 