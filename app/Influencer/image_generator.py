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
            "playful": """Generate a 4K ultra-detailed, hyper-realistic photograph of an adorable cream-colored French Bulldog 
            with distinctive bat ears and expressive eyes, similar to the reference. Capture the dog in a playful pose on a 
            plush couch or bed, with soft lighting and natural indoor setting. Ensure the facial features match the reference 
            image's cute and engaging expression. Add decorative pillows or blankets in the background for a cozy atmosphere.""",
            
            "outdoor": """Create a 4K ultra-realistic photograph of a cream French Bulldog, matching the reference image's 
            facial features and bat ears, enjoying an outdoor adventure. Show the dog exploring a scenic park or garden with 
            natural sunlight highlighting its cream-colored coat. Maintain the same adorable expression and head tilt as the 
            reference, while capturing a full-body shot that shows personality.""",
            
            "portrait": """Generate a 4K detailed portrait of a cream French Bulldog, exactly matching the reference image's 
            facial characteristics - the distinctive bat ears, soulful eyes, and slight head tilt. Capture an up-close shot 
            that emphasizes the dog's charming expression and unique features. Use soft, natural lighting to highlight the 
            cream-colored fur and create a warm, engaging atmosphere."""
        }
        
    def generate_image_and_caption(self) -> Dict[str, str]:
        try:
            # Select random prompt type
            prompt_type = random.choice(list(self.image_prompts.keys()))
            prompt = self.image_prompts[prompt_type]
            
            # Generate image
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            
            # Generate matching caption
            caption_prompt = f"Create a warm, engaging caption for a photo of a French Bulldog {prompt_type} scene. Include relevant emojis and hashtags."
            caption_response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a dog photography expert creating engaging social media captions."},
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
            "caption": "Just another pawsome day with this adorable Frenchie! 🐾 Living the good life and spreading joy! #FrenchBulldog #DogLife",
            "type": "fallback"
        } 