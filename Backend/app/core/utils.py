import re

def normalize_phone_number(phone: str) -> str:
    phone = phone.strip().replace(" ", "").replace("-", "")

    if phone.startswith("0"):
        phone = "+234" + phone[1:]
    elif phone.startswith("234"):
        phone = "+" + phone

    if not re.fullmatch(r"\+234\d{10}", phone):
        raise ValueError("Invalid Nigerian phone number")

    return phone