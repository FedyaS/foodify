# python -m pip install python-dotenv
# python -m pip install openai

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_gpt5(prompt: str) -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY is not set. Check your .env file.")

    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""

print(get_gpt5("What are the best units in Fire Emblem: Three Houses?"))