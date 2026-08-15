import re
import validators


def validate_email(email):
    """
    Validate an email address.
    Returns:
        bool: True if valid, otherwise False.
    """

    if email is None:
        return False

    email = str(email).strip()

    if email == "":
        return False

    return bool(validators.email(email))


def validate_phone(phone):
    """
    Validate a phone number.
    A valid phone number must contain at least 7 digits.

    Returns:
        bool: True if valid, otherwise False.
    """

    if phone is None:
        return False

    phone = str(phone).strip()

    if phone == "":
        return False

    # Keep only digits
    digits = re.sub(r"\D", "", phone)

    return 7 <= len(digits) <= 15


def validate_website(url):
    """
    Validate a website URL.

    Returns:
        bool: True if valid, otherwise False.
    """

    if url is None:
        return False

    url = str(url).strip()

    if url == "":
        return False

    return bool(validators.url(url))