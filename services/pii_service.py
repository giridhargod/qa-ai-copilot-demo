#pii_service.py

import re

def mask_email(text):
    return re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL_MASKED]', text)

def mask_phone(text):
    return re.sub(r'\b\d{10}\b', '[PHONE_MASKED]', text)

def mask_ids(text):
    return re.sub(r'\b\d{12}\b', '[ID_MASKED]', text)

def mask_urls(text):
    return re.sub(r'https?://\S+', '[URL_MASKED]', text)

def process_pii(user_input):
    masked = mask_email(user_input)
    masked = mask_phone(masked)
    masked = mask_ids(masked)
    masked = mask_urls(masked)

    count = 1 if masked != user_input else 0

    return {
        "sanitized": masked,
        "count": count
    }