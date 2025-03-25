import requests

from rich.console import Console

console = Console()

headers = {
    "Content-Type": "application/json"
}
max_tokens = 180


def generate_response(settings: {}, chat_history: [], username: str, preferred_name: str) -> [str, []]:
    request = {
        "messages": chat_history,
        "mode": "chat-instruct",
        "max_tokens": max_tokens,
        "character": settings.character,
        "name1": f"{preferred_name}",
        "user_bio": f"Username: f{username}\nPreferred Name: {preferred_name}",
        "stop": ["\n\n\n", f"{username}:", f"{preferred_name}:", f"\n{username}:", f"\n{preferred_name}:",
                 f"\n\n{username}:", f"\n\n{preferred_name}:", f"\n[{username}", f"\n[{preferred_name}",
                 f"\n\n[{username}", f"\n\n[{preferred_name}",],
        "dry_sequence_breakers": '["\\n",":","\\"","*"]',
        "prompt": "test"
    }
    console.print(request)

    response = requests.post(settings.url, headers=headers, json=request, verify=False)
    if response.status_code == 200:
        response_json = response.json()
        assistant_message = response_json['choices'][0]['message']['content']
        console.print(response_json)
        chat_history.append({"role": "assistant", "content": assistant_message})
        return assistant_message, chat_history
    else:
        console.print(response)
        console.print(response.json())
