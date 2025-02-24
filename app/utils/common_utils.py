from openai import OpenAI

def create_openai_client(config):
    return OpenAI(api_key=config.OPENAI_API_KEY)


def generate_unique_response(openai_client, user_text):
    """Generate a unique response using OpenAI"""
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Generate a unique, thoughtful response to this tweet"},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7  # Add some variability
        )
        return str(completion.choices[0].message.content)
    except Exception as e:
        # logger.error(f"Error generating response: {e}")
        return None
    