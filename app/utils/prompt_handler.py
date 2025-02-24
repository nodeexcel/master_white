from typing import Dict
import re

def is_dog_related(text: str) -> bool:
    """Check if the query is dog-related using keyword matching"""
    dog_keywords = {
        'dog', 'puppy', 'breed', 'canine', 'pet', 'bark', 'training',
        'leash', 'veterinary', 'grooming', 'vaccination', 'kennel'
    }
    
    text_words = set(re.findall(r'\w+', text.lower()))
    return bool(text_words.intersection(dog_keywords))

def create_prompt(text: str) -> Dict[str, str]:
    """Create appropriate prompt based on query type"""
    
    if is_dog_related(text):
        return {
            "role": "system",
            "content": """You are DoggyHelper, an expert AI assistant specializing in dogs. 
            Provide helpful, accurate, and concise information about dogs. Keep responses 
            friendly and under 280 characters. Include relevant emojis when appropriate."""
        }
    else:
        return {
            "role": "system",
            "content": """You are DoggyHelper. Politely inform the user that you specialize 
            in dog-related topics and encourage them to ask about dogs instead. Keep response 
            under 280 characters and friendly."""
        } 