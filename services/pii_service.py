#services/pii_service.py
import re

def mask_email(text):
    return re.subn(r'[\w\.-]+@[\w\.-]+', '[EMAIL_MASKED]', text)

def mask_phone(text):
    return re.subn(r'\b\d{10}\b', '[PHONE_MASKED]', text)

def mask_ids(text):
    return re.subn(r'\b\d{12}\b', '[ID_MASKED]', text)

def mask_urls(text):
    return re.subn(r'https?://\S+', '[URL_MASKED]', text)

def process_pii(user_input):
    masked, email_count = mask_email(user_input)
    masked, phone_count = mask_phone(masked)
    masked, id_count = mask_ids(masked)
    masked, url_count = mask_urls(masked)

    count = email_count + phone_count + id_count + url_count

    return {
        "sanitized": masked,
        "count": count
    }
