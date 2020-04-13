import re


def split_sentences(text, new_lines=False):
    if new_lines:
        return text.split("\n")
    delims = ["\n", ".", "!", "?"]
    return [s.strip() for s in re.split(r'(!|\?|\.|\n)*', text) if
            s not in delims and s.strip()]