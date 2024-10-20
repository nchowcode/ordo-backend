from dotenv import load_dotenv
load_dotenv()  # take environment variables
import os
from groq import Groq
from typing import TypedDict

# before: llama3-8b-8192
# super fast and cheap: llama-3.2-1b-preview
# fast and cheap: llama-3.1-8b-instant 
# heavy duty: llama-3.1-70b-versatile

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class email(TypedDict):
    From: str
    To: str
    Subject: str
    Body: str

async def detect_junk(email_data: email) -> str:
    prompt = f"""
    Please determine whether the following email is "Junk" or "Not Junk". Respond with either "Junk" or "Not Junk" only.

    ---

    From: {email_data['From']}
    To: {email_data['To']}
    Subject: {email_data['Subject']}
    Body: {email_data['Body']}

    ---
    """

    chat_completion = client.chat.completions.create(
        model="llama-3.2-1b-preview",  
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=5,        # Small number since the expected response is short
        temperature=0,       # For deterministic output
        top_p=1,             # To consider all tokens with non-zero probability
        frequency_penalty=0, # No penalty for token frequency
        presence_penalty=0,  # No penalty for presence of tokens
        stop=None,           # No stop tokens required
        stream=False         
    )

    return chat_completion.choices[0].message.content

# look at existing labels, and determine if the email belongs to it, but if not
def assign_label(email_data: email, label: list[str]) -> str:
    prompt = f"""
    Determine whether the following email belongs to the following labels: {label}. If it does not belong to any of the labels, please create a new label for the email. Respond with the label(s) that the email belongs to.

    ---

    From: {email_data['From']}
    To: {email_data['To']}
    Subject: {email_data['Subject']}
    Body: {email_data['Body']}

    ---
    """

    chat_completion = client.chat.completions.create(
        model="llama-3.2-1b-preview",  
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=5,        # Small number since the expected response is short
        temperature=0,       # For deterministic output
        top_p=1,             # To consider all tokens with non-zero probability
        frequency_penalty=0, # No penalty for token frequency
        presence_penalty=0,  # No penalty for presence of tokens
        stop=None,           # No stop tokens required
        stream=False         
    )

    return chat_completion.choices[0].message.content






# chat_completion = client.chat.completions.create(

#     model="llama-3.2-1b-preview", 
#     messages=[
#         # {
#         #     "role": "system",
#         #     "content": "you are a helpful assistant."
#         # },
#         # {
#         #     "role": "user",
#         #     "content": "Explain the importance of fast language models",
#         # }

#         # prefilling is literally starting the ai response with specific text
#         {
#             "role": "user",
#             "content": "Write a Python function to calculate the factorial of a number."
#         },
#         {
#             "role": "assistant",
#             "content": "```python"
#         }
#     ],
#     stop="```",
#     stream=True,
# )

# # print(chat_completion.choices[0].message.content)
# for chunk in chat_completion:
#     print(chunk.choices[0].delta.content or "", end="")

