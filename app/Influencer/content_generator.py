from typing import Dict, List
import random
from datetime import datetime
import json
from openai import OpenAI
from app.config import Config

class DogContentGenerator:
    def __init__(self):
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.content_types = [
            "daily_tip", "dog_fact", "training_advice", 
            "health_tip", "dog_quote", "engagement_question",
            "breed_spotlight", "dog_care_tip"
        ]
        
    def generate_post(self) -> Dict[str, str]:
        content_type = random.choice(self.content_types)
        prompt = self._create_prompt(content_type)
        
        try:
            completion = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Generate a Twitter post"}
                ],
                temperature=0.9,
                max_tokens=100
            )
            
            content = completion.choices[0].message.content
            hashtags = self._get_relevant_hashtags(content_type)
            return {
                "content": f"{content}\n\n{hashtags}",
                "type": content_type
            }
        except Exception as e:
            return self._get_fallback_content()
            
    def _create_prompt(self, content_type: str) -> str:
        prompts = {
            "daily_tip": """You are a professional dog trainer. Create an engaging, practical daily tip for dog owners. 
            Make it actionable and valuable. Include emojis naturally. Keep it under 200 characters.""",
            
            "dog_fact": """You are a canine expert. Share an interesting, lesser-known fact about dogs that will 
            surprise and educate dog lovers. Make it engaging and memorable. Include relevant emojis.""",
            
            "training_advice": """As a dog behavior specialist, provide a specific, actionable training tip that 
            helps dog owners. Focus on positive reinforcement. Keep it practical and clear.""",
            
            "health_tip": """You are a veterinary expert. Share an important health tip for dog owners. 
            Make it preventive and practical. Use warm, caring language.""",
            
            "dog_quote": """Create an heartwarming, original quote about dogs and their impact on human lives. 
            Make it emotional and relatable. Keep it short and memorable.""",
            
            "engagement_question": """Create an engaging question about dogs that will encourage dog lovers to respond. 
            Make it fun and interactive. Focus on common experiences of dog owners."""
        }
        return prompts.get(content_type, prompts["daily_tip"])
        
    def _get_relevant_hashtags(self, content_type: str) -> str:
        hashtag_sets = {
            "daily_tip": "#DogTips #PawfectAdvice #DogTraining",
            "dog_fact": "#DogFacts #DidYouKnow #DogTrivia",
            "training_advice": "#DogTraining #PuppyTraining #DogBehavior",
            "health_tip": "#DogHealth #PetCare #DogWellness",
            "dog_quote": "#DogLove #DogLife #DogsOfTwitter",
            "engagement_question": "#DogCommunity #DogLovers #TellUs"
        }
        return hashtag_sets.get(content_type, "#DogLife #DogsOfTwitter #PawfectDay")
        
    def _get_fallback_content(self) -> Dict[str, str]:
        fallback_posts = [
            "Did you know? Dogs can understand over 150 words! What words does your furry friend know? 🐕 #DogFacts",
            "Remember: A tired dog is a happy dog! Make time for play today 🎾 #DogLife",
            "Positive reinforcement works wonders in dog training! Share your success stories 🦮 #DogTraining"
        ]
        return {
            "content": random.choice(fallback_posts),
            "type": "fallback"
        } 