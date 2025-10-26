"""
Gemini Model
Google Gemini API integration
"""

import os
import logging
import time
from google import genai
from google.genai import types
from models.base_model import BaseModel

logger = logging.getLogger(__name__)


class GeminiModel(BaseModel):
    """
    Google Gemini model implementation
    """
    
    def __init__(self, model_name="gemini-2.0-flash", api_key=None):
        """
        Initialize Gemini model
        
        Args:
            model_name: Gemini model name
            api_key: Gemini API key (if None, reads from environment)
        """
        super().__init__(
            name=model_name,
            provider="Google",
            cost_per_token=0.00001  # Approximate cost
        )
        
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name
        
        logger.info(f"Gemini model initialized: {model_name}")
    
    def generate(self, prompt, temperature=1.0, max_tokens=1000, **kwargs):
        """
        Generate text from prompt
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with response, tokens, latency, cost
        """
        try:
            start_time = time.time()
            
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            ]
            
            generate_content_config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=generate_content_config
            )
            
            latency = time.time() - start_time
            response_text = response.text
            
            # Count tokens
            prompt_tokens = self.count_tokens(prompt)
            response_tokens = self.count_tokens(response_text)
            total_tokens = prompt_tokens + response_tokens
            
            # Calculate cost
            cost = self.calculate_cost(total_tokens)
            
            logger.info(f"Generated response: {total_tokens} tokens, {latency:.2f}s")
            
            return {
                'response': response_text,
                'tokens': total_tokens,
                'latency': latency,
                'cost': cost
            }
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise
    
    def generate_stream(self, prompt, temperature=1.0, max_tokens=1000, **kwargs):
        """
        Generate text with streaming
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Yields:
            Text chunks
        """
        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            ]
            
            generate_content_config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            for chunk in self.client.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=generate_content_config
            ):
                if chunk.text:
                    yield chunk.text
            
            logger.info("Streaming generation completed")
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise
