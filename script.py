import re
import requests

OKVED_URL = "https://raw.githubusercontent.com/bergstar/testcase/master/okved.json"
MAX_OKVED_LEN = 6

# =========================
# Exceptions
# =========================

class NormalizationError(Exception):
    """Raised if phone number normalization fails."""

class MatchingError(Exception):
    """Raised if phone number doesn't have matches."""

# =========================
# Phone normalization
# =========================

def normalize_phone(raw_phone: str) -> str:
    """Normalize mobile phone number to +79XXXXXXXXX.

    :raises NormalizationError: on normalization errors
    """
    digits = re.sub(r"\D", "", raw_phone)

    if len(digits) == 11 and digits[0] in {"7", "8"}:
        digits = "7" + digits[1:]
    elif len(digits) == 10 and digits.startswith("9"):
        digits = "7" + digits
    else:
        raise NormalizationError("Invalid phone number")

    return f"+{digits}"

# =========================
# OKVED loading & parsing
# =========================

def fetch_okved() -> list:
    """
    Download okved.json via HTTPS.

    :raises requests.RequestException: on network errors
    """
    response = requests.get(OKVED_URL, timeout=10)
    response.raise_for_status()
    return response.json()


def build_okved_dict(tree: list) -> dict[str, str]:
    """
    Build hierarchical tree into a dict.
    """
    result: dict[str, str] = {}

    def walk(node: dict) -> None:
        code = node.get("code")
        name = node.get("name")

        if code and name:
            digits = re.sub(r"\D", "", code)
            if digits:
                result[digits] = name

        for child in node.get("items", []):
            walk(child)

    for root in tree:
        walk(root)

    return result

# =========================
# Rebuild okved index
# =========================

def rebuild_okved(digits: str) -> str:
    """
    Restore OKVED code formatting by inserting dots

    Example: 01111 -> 01.11.1
    """
    if len(digits) <= 2:
        return digits

    parts = []
    i = 0

    while i < len(digits):
        if len(digits) - i <= 2:
            parts.append(digits[i:])
            break

        parts.append(digits[i:i + 2])
        i += 2

    return ".".join(parts)

# =========================
# Index & matching
# =========================

def find_best_match(normalized_phone: str, okved_dict: dict[str, str]) -> tuple[str, str, int]:
    """Find best OKVED match by phone suffix."""
    phone_digits = re.sub(r"\D", "", normalized_phone)

    for length in range(min(len(phone_digits), MAX_OKVED_LEN), 0, -1):
        suffix = phone_digits[-length:]

        if suffix in okved_dict:
            code = rebuild_okved(suffix)
            return code, okved_dict[suffix], length

    raise MatchingError("Phone number doesn't have matches")

# =========================
# Pipeline
# =========================

def pipeline(raw_phone: str) -> dict:
    """Full processing pipeline."""
    normalized = normalize_phone(raw_phone)

    okved = fetch_okved()
    okved_dict = build_okved_dict(okved)

    index, name, match_len = find_best_match(normalized, okved_dict)

    return normalized, index, name, match_len

# =========================
# Entry point
# =========================

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python main.py <phone>")
        sys.exit(1)

    try:
        result = pipeline(sys.argv[1])
        print(*result, sep="\n")
    except NormalizationError as exc:
        print(f"false: {exc}")
        sys.exit(2)
    except MatchingError as exc:
        print(f"false: {exc}")
        sys.exit(2)
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(3)
