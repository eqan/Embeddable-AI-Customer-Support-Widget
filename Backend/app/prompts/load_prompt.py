import os


def load_prompt(prompt_name: str) -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), f"prompt_files/{prompt_name}.prompt")

    with open(prompt_path, "r") as file:
        return file.read()