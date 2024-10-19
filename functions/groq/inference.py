from dotenv import load_dotenv
load_dotenv()  # take environment variables
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

chat_completion = client.chat.completions.create(
    # before: llama3-8b-8192
    # super fast and cheap: llama-3.2-1b-preview
    # fast and cheap: llama-3.1-8b-instant 
    # heavy duty: llama-3.1-70b-versatile
    model="llama-3.2-1b-preview", 
    messages=[
        # {
        #     "role": "system",
        #     "content": "you are a helpful assistant."
        # },
        # {
        #     "role": "user",
        #     "content": "Explain the importance of fast language models",
        # }
                {
            "role": "user",
            "content": "Write a Python function to calculate the factorial of a number."
        },
        {
            "role": "assistant",
            "content": "```python"
        }
    ],
    stop="```",
    stream=True,
)

# print(chat_completion.choices[0].message.content)
for chunk in chat_completion:
    print(chunk.choices[0].delta.content or "", end="")

