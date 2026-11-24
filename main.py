"""One Emoji, One Dream Vacation — make.fun entry.

Writes exactly one emoji and nothing else to <output>/entry.txt.

The chosen emoji is U+1F5FB MOUNT FUJI (🗻): a snow-capped mountain
against the sky — the single most photographed mountain on Earth, and
a named bucket-list destination, not just any mountain. A stranger
sees the place at a glance, like a postcard; it points at one
particular dream (Japan, Fuji) rather than any holiday; and it is a
fresh pick against a field of beaches and planes, while staying
instantly readable across cultures and screens — Fuji needs no
explaining. It is also one of the brief's own named examples of a
dream vacation: "a beach, a mountain, a plane, a hammock, a faraway
place".

Pure standard library only (os). Deterministic: every run writes the
same bytes. After writing, the program reads the file back and fails
if the bytes differ from the validated text.
"""

import os

# The single emoji this entry submits. One grapheme, one code point.
EMOJI = "\U0001F5FB"  # 🗻 MOUNT FUJI

# Code-point ranges that count as emoji for validation purposes.
_EMOJI_RANGES = (
    (0x1F600, 0x1F64F),  # emoticons
    (0x1F300, 0x1F5FF),  # symbols & pictographs
    (0x1F680, 0x1F6FF),  # transport & map symbols
    (0x1F700, 0x1F77F),  # alchemical symbols
    (0x1F780, 0x1F7FF),  # geometric shapes extended
    (0x1F800, 0x1F8FF),  # supplemental arrows-C
    (0x1F900, 0x1F9FF),  # supplemental symbols & pictographs
    (0x1FA70, 0x1FAFF),  # symbols & pictographs extended-A
    (0x2600, 0x26FF),    # miscellaneous symbols
    (0x2700, 0x27BF),    # dingbats
    (0xFE00, 0xFE0F),    # variation selectors
    (0x200D, 0x200D),    # zero-width joiner
)


def _is_emoji_char(ch):
    """True when a single character is an emoji code point."""
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in _EMOJI_RANGES)


def validate(text):
    """Enforce the entry gate: exactly one emoji, 1-8 chars, UTF-8.

    Accepts the text exactly as written to the file (emoji plus the
    single trailing newline the program writes). Raises ValueError on
    any violation; returns the emoji on success.
    """
    if not isinstance(text, str):
        raise ValueError("entry must be text")
    if not text:
        raise ValueError("entry is empty")
    if not text.endswith("\n") or text.count("\n") != 1:
        raise ValueError("entry must end with exactly one trailing newline")
    body = text[:-1]
    if not body:
        raise ValueError("entry is only whitespace")
    if body != body.strip():
        raise ValueError("entry has leading or trailing whitespace")
    if not 1 <= len(body) <= 8:
        raise ValueError("entry must be 1-8 characters, got %d" % len(body))
    if any(ch.isspace() for ch in body):
        raise ValueError("entry must not contain whitespace")
    if not all(_is_emoji_char(ch) for ch in body):
        raise ValueError("entry must contain only emoji characters")
    # Exactly one grapheme: a single base emoji, ignoring the joiners and
    # variation selectors that glue one compound emoji together.
    base_chars = [
        ch for ch in body
        if ord(ch) not in (0x200D,) and not 0xFE00 <= ord(ch) <= 0xFE0F
    ]
    if len(base_chars) != 1:
        raise ValueError("entry must be exactly one emoji grapheme")
    try:
        body.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("entry is not UTF-8 encodable") from exc
    return body


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    text = EMOJI + "\n"
    validate(text)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    # Read back and verify: the bytes on disk must be exactly what was
    # validated, or the entry fails loudly instead of shipping bad bytes.
    with open(path, "rb") as fh:
        written = fh.read()
    if written != text.encode("utf-8"):
        raise ValueError("entry.txt bytes differ from validated text")
    return path


if __name__ == "__main__":
    print(main())
