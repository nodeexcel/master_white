from openai import OpenAI
from app.Agent.utils.prompt_handler import create_prompt, is_dog_related

def create_openai_client(config):
    return OpenAI(api_key=config.OPENAI_API_KEY)

def generate_response(openai_client, user_text: str) -> str:
    """Generate appropriate response based on query type"""
    try:
        system_prompt = create_prompt(user_text)
        
        if not is_dog_related(user_text):
            return "🐕 Hi! I'm specialized in dog-related topics. While I'd love to help, I can best assist with questions about dogs, puppies, training, or pet care. Feel free to ask anything about our furry friends!"
        
        completion = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                system_prompt,
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=100  # Ensure Twitter character limit
        )
        
        return str(completion.choices[0].message.content)
    except Exception as e:
        return "Woof! 🐕 I'm having a temporary issue. Please try asking your dog-related question again in a few minutes!"
    