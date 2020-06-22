import re


def split_sentences(text, new_lines=False):
    if new_lines:
        return text.split("\n")
    delims = ["\n", ".", "!", "?"]
    return [s.strip() for s in re.split(r'(!|\?|\.|\n)*', text) if
            s not in delims and s.strip()]


def camel_case_split(identifier: str) -> str:
    """Split camel case string"""
    regex = '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)'
    matches = re.finditer(regex, identifier)
    return ' '.join([m.group(0) for m in matches])