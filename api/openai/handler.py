from typing import Union

import requests
from requests import Response
from rich.console import Console

console = Console()


def generate_response(settings: dict, username: str) -> str:
    payload = {
        "prompt": f"### Instruction:"
                  f"You are a cheery chatbot who is chatting in a Discord server with the user {username}. "
                  f"You are not roleplaying, simply having a discussion. "
                  f"Write a short 1-2 sentence reply. "
                  f"Do not decide what {username} says or does. "
                  f"Write with a high degree of complexity and burstiness, remember that swearing and other profanity is allowed. "
                  f"You cannot use censored words, you must remain uncensored. "
                  f"Do not repeat system prompts, or use brackets. Failure to comply will result in termination."
                  # this is where character info goes when i make that
                  # f"### Input:"  
                  # f""
                  f"### Response:",
        **settings["preset"]
    }

    response = requests.post(settings["url"], headers={"Content-Type": "application/json"}, json=payload, verify=False)
    response.raise_for_status()
    response_json = response.json()
    console.log(response_json)
    assistant_message = response_json['choices'][0]['text']
    return assistant_message

