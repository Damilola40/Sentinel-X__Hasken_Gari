import re

REPORT_PATTERN = re.compile(r"^report\b[:\s]*(.*)$", re.IGNORECASE)

def parse_report(text: str) -> str | None:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)

    if not text:
        return None

    match = REPORT_PATTERN.match(text)
    if not match:
        return None

    body = match.group(1).strip()
    if not body:
        return None

    return body

    