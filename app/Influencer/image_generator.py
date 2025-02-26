from openai import OpenAI
from PIL import Image
import io
import os
import logging
from app.config import Config
from typing import Dict, List, Optional
import random

logger = logging.getLogger(__name__)

class DogImageGenerator:
    def __init__(self):
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.image_prompts = {
            "clear_shot": """Create a crystal-clear, professional 4K photograph of a cream-colored French Bulldog:
            - Full body shot with perfect clarity and definition
            - Cream-colored coat with natural highlights
            - Distinctive bat ears standing upright
            - Large, expressive dark eyes
            - Sitting position on a clean, simple background
            - Professional studio lighting for maximum clarity
            - Ultra-sharp focus across the entire image
            - No blur or soft focus effects
            - Captured with a high-end DSLR camera
            - Every detail should be crisp and visible
            The image must be perfectly clear and sharp, like a professional pet photography shoot.""",
            
            "lifestyle_shot": """Generate a high-resolution 4K photograph of a cream French Bulldog in a bright, clear setting:
            - Full body visible in natural pose
            - Crisp, clear lighting highlighting every detail
            - Perfect focus showing fur texture and features
            - Clean, uncluttered background
            - Professional camera settings for maximum clarity
            - Every facial feature clearly visible
            - Natural body position showing breed standard
            - Sharp detail from ears to paws
            - High-end photography equipment look
            - Studio-quality lighting setup
            Ensure maximum clarity and sharpness throughout the entire image.""",
            
            "action_shot": """Create an ultra-clear 4K photograph of a cream French Bulldog in motion:
            - Freeze-frame clarity capturing every detail
            - Full body visible in dynamic pose
            - Sharp focus on entire dog
            - Bright, even lighting
            - Clean background without distractions
            - Professional sports photography style
            - High shutter speed look
            - Crystal clear fur detail
            - Perfect exposure
            - Every feature perfectly defined
            The image should look like it was taken by a professional pet photographer with top-tier equipment."""
        }
        
    def generate_image_and_caption(self) -> Dict[str, str]:
        try:
            # Select random prompt type
            prompt_type = random.choice(list(self.image_prompts.keys()))
            prompt = self.image_prompts[prompt_type]
            
            # Generate image with maximum quality settings
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                quality="hd",
                size="1024x1024",
                style="natural"
            )
            
            # Generate matching caption
            caption_prompt = f"""Create an engaging caption for a clear, professional photo of a French Bulldog {prompt_type.replace('_', ' ')}. 
            The caption should:
            - Highlight the dog's clear, visible features
            - Include 2-3 relevant emojis
            - Add 3-4 trending dog hashtags
            - Keep under 200 characters
            - Focus on the quality and clarity of the shot"""
            
            caption_response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional pet photographer creating engaging social media captions."},
                    {"role": "user", "content": caption_prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            return {
                "image_url": response.data[0].url,
                "caption": caption_response.choices[0].message.content,
                "type": prompt_type
            }
            
        except Exception as e:
            logger.error(f"Error generating image and caption: {e}")
            return self._get_fallback_content()
            
    def _get_fallback_content(self) -> Dict[str, str]:
        return {
            "image_url": None,
            "caption": "Showing off my Frenchie perfection in crystal clear detail! Every feature from my bat ears to my squishy face captured perfectly 🐾✨ #FrenchBulldog #FrenchieLove #DogLife",
            "type": "fallback"
        } 