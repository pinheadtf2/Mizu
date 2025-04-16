import re
from datetime import datetime

import discord
import requests
from rich.console import Console

console = Console()


def generate_response(character: dict, settings: dict, message: discord.Message) -> str:
    """
    hi i like nuts

    :param character: char string
    :param settings: settings you need to feed in
    :param message: the discord message
    :return: returns the ai's response
    """

    # this is probably horrifying to double nest but thats a later me issue

    def text_replacement(target_text: str) -> str:
        # the most optimal way i can think of to do text replacement is by detecting a {{}}, reading the value in between, and doing the replacement
        # for now i'll do this just so i can rapidly develop
        # trust me it pains me to leave it like this
        bindings = {
            "{{user}}": message.author.global_name,
            "{{char}}": character['name'],
            "{{currentdate}}": datetime.now().strftime("%A, %B %d, %Y, at %I:%M %p"),
            "{{server}}": message.guild.name,
        }

        # Create a regex pattern to match all keys case-insensitively
        pattern = re.compile("|".join(re.escape(k) for k in bindings.keys()), re.IGNORECASE)

        def replace_match(match):
            key = match.group(0)  # Extract matched key
            for binding_key in bindings:
                if key.lower() == binding_key.lower():
                    return bindings[binding_key]  # Return correct replacement
            return key  # Fallback (shouldn't occur)

        return pattern.sub(replace_match, target_text)

    example_dialogue = ""
    for example in character["example_dialogue"]:
        example_dialogue += f"{settings["new_roleplay_string"]}{example}\n"

    stop_strings = [f"\n{message.author.global_name}:", f"\n\n{message.author.global_name}:",
                    f"[{message.author.global_name}"]
    payload = {
        "prompt": text_replacement(f"### Instruction:\n"
                                   f"{settings["instruction"]}"
                                   "### Input:\n" +
                                   character["description"] +
                                   settings["scenario"] +
                                   character["personality"] +
                                   # end user info goes here (name, bio, etc.)
                                   f"{example_dialogue}" +
                                   settings["new_roleplay_string"] +
                                   f"[You are now chatting live with the members of \"{message.guild.name}\".]"
                                   # chat history & author note (doing this later)
                                   f"{message.author.global_name}: {message.content}"
                                   f"{character["name"]}: "),
        **settings["preset"],
        "stop": stop_strings,
        "stop_strings": stop_strings,
        "genamt": settings["max_generated_tokens"],
        "max_tokens": settings["max_generated_tokens"],
        "max_new_tokens": settings["max_generated_tokens"]  # im covering all my bases
    }
    console.log("Sent Prompt:", payload)

    response = requests.post(settings["url"], headers={"Content-Type": "application/json"}, json=payload, verify=False)
    response.raise_for_status()
    response_json = response.json()
    console.log("Received Response:", response_json)
    assistant_message = response_json['choices'][0]['text']
    return assistant_message
