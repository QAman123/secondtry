import os
from openai import OpenAI

def main():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if not client.api_key:
        raise ValueError("Please set OPENAI_API_KEY environment variable")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short poem about the sun and the sea."}
        ],
        max_tokens=100,
        temperature=0.7,
    )
    print(response.choices[0].message.content.strip())

if __name__ == "__main__":
    main()
