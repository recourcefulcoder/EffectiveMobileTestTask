import unicodedata


def normalize(input: str) -> str:
    res: str = ""
    prev_letter = " "
    for letter in input.strip():
        if not (letter == " " and prev_letter == " "):
            res += letter
        prev_letter = letter

    return unicodedata.normalize("NFKD", res)
