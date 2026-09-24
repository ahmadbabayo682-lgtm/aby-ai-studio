_ENHANCEMENT_SUFFIX = (
    "Create a high-quality, detailed image with clear composition, natural lighting, "
    "and visually coherent elements."
)


def enhance_prompt(prompt: str) -> str:
    try:
        if not isinstance(prompt, str):
            return prompt

        normalized_prompt = prompt.strip()
        if not normalized_prompt:
            return prompt

        punctuation = "" if normalized_prompt.endswith((".", "!", "?")) else "."
        return f"{normalized_prompt}{punctuation} {_ENHANCEMENT_SUFFIX}"
    except Exception:
        return prompt