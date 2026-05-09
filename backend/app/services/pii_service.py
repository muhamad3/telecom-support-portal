import re

# below is regular expression for iraqi numbers for all possible combinations and email and credit card number just in case someone writes it
_PATTERNS = {
    "phone": re.compile(
        r"(?<!\d)((?:\+?964[-.\s]?|0)?7\d{2}[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2})(?!\d)"
    ),
    "email": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    ),
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
}

# like the name suggests it removes the matched patterns
def mask_pii(text: str) -> str:
    masked = text
    for pii_type, pattern in _PATTERNS.items():
        masked = pattern.sub(f"[{pii_type.upper()}_REDACTED]", masked)
    return masked
