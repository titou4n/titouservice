"""
Input validation for Emergency Information forms.
Returns (cleaned_value, error_message | None).
"""

import re
from datetime import date, datetime
import extensions as ext


def validate_date_of_birth(value: str):
    """Parse YYYY-MM-DD; must be in the past and person < 130 years old."""
    if not value:
        return None, None
    try:
        dob = datetime.strptime(value.strip(), '%Y-%m-%d').date()
    except ValueError:
        return None, 'Invalid date format (expected YYYY-MM-DD).'
    today = date.today()
    if dob >= today:
        return None, 'Date of birth must be in the past.'
    if (today.year - dob.year) > 130:
        return None, 'Date of birth is too far in the past.'
    return dob, None


def validate_blood_type(value: str):
    if not value or value == "Unknown":
        return None, None
    value = value.strip().upper()
    if value not in ext.config.BLOOD_TYPES:
        return None, f'Invalid blood type. Choose one of: {", ".join(ext.config.BLOOD_TYPES)}'
    return value, None


def validate_height(value: str):
    if not value:
        return None, None
    try:
        h = int(value)
    except (ValueError, TypeError):
        return None, 'Height must be a whole number (cm).'
    if not (50 <= h <= 280):
        return None, 'Height must be between 50 and 280 cm.'
    return h, None


def validate_weight(value: str):
    if not value:
        return None, None
    try:
        w = round(float(value), 1)
    except (ValueError, TypeError):
        return None, 'Weight must be a number (kg).'
    if not (1.0 <= w <= 700.0):
        return None, 'Weight must be between 1 and 700 kg.'
    return w, None


def validate_phone(value: str):
    if not value:
        return None, None
    cleaned = re.sub(r'[\s\-\.\(\)]', '', value.strip())
    if not re.match(r'^\+?\d{6,20}$', cleaned):
        return None, 'Invalid phone number format.'
    if len(value) > ext.config.MAX_PHONE_FIELD:
        return None, f'Phone number too long (max {ext.config.MAX_PHONE_FIELD} chars).'
    return value.strip(), None


def validate_short_text(value: str, field_name: str = 'Field'):
    if not value:
        return None, None
    value = value.strip()
    if len(value) > ext.config.MAX_SHORT_FIELD:
        return None, f'{field_name} must not exceed {ext.config.MAX_SHORT_FIELD} characters.'
    return value, None


def validate_long_text(value: str, field_name: str = 'Field'):
    if not value:
        return None, None
    value = value.strip()
    if len(value) > ext.config.MAX_TEXT_FIELD:
        return None, f'{field_name} must not exceed {ext.config.MAX_TEXT_FIELD} characters.'
    return value, None


def validate_boolean(value) -> bool:
    """Coerce checkbox/form values to bool."""
    if isinstance(value, bool):
        return value
    return str(value).lower() in ('1', 'true', 'yes', 'on')


def validate_gender(value: str, gender_options: list):
    if not value:
        return None, None
    keys = [k for k, _ in gender_options]
    if value not in keys:
        return None, 'Invalid gender value.'
    return value, None
