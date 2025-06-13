import os


def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "response-generation.prompt")

    with open(prompt_path, "r") as file:
        return file.read()