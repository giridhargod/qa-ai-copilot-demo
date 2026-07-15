"""Sensitive-data detection patterns.

Deliberately plain Python data (a list of SensitivePattern + a plain
list of known internal terms) rather than a YAML file + loader
abstraction. This package is meant to be cloned and understood in one
sitting -- a parsing/loading layer would be solving a problem this
project doesn't have yet. If a real externalized Knowledge Pack
mechanism is ever needed, that decision belongs to QA AI Copilot's
Architect, not to this standalone package.

Every pattern replaces (never deletes) a match with a placeholder, so
sanitized text stays readable for both the LLM and a human reviewer.
Patterns are applied in the order listed in ALL_PATTERNS -- more
specific patterns run first so a generic fallback (e.g. a bare 9-digit
number) doesn't re-catch digits a more specific rule already replaced.
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SensitivePattern:
    category: str
    placeholder: str
    regex: "re.Pattern"


def _labeled_id(label_pattern: str) -> "re.Pattern":
    """Matches 'Claimant ID: 12345', 'employer id# AB-1234', etc. --
    a label keyword (case-insensitive -- real documents are not
    consistently capitalized) followed by an alphanumeric value.
    """
    return re.compile(
        rf"\b{label_pattern}\s*(?:ID|Id|#|No\.?|Number)?\s*[:#-]?\s*"
        rf"([A-Za-z0-9-]{{4,15}})\b",
        re.IGNORECASE,
    )


ALL_PATTERNS = [
    # --- Personal ---
    SensitivePattern(
        "ssn", "<SSN>",
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b"),
    ),
    SensitivePattern(
        "claimant_id", "<CLAIMANT_ID>",
        _labeled_id("Claimant"),
    ),
    SensitivePattern(
        "employer_id", "<EMPLOYER_ID>",
        _labeled_id("Employer"),
    ),
    SensitivePattern(
        "email", "<EMAIL>",
        re.compile(r"\b[\w.\-+]+@[\w.\-]+\.\w+\b"),
    ),
    SensitivePattern(
        "phone", "<PHONE>",
        re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    ),
    SensitivePattern(
        "address", "<ADDRESS>",
        re.compile(
            r"\b\d{1,5}\s+(?:[A-Z][a-z]+\s){1,4}"
            r"(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|"
            r"Lane|Ln|Drive|Dr|Court|Ct|Way|Place|Pl)\b\.?"
        ),
    ),
    SensitivePattern(
        "date_of_birth", "<DOB>",
        re.compile(
            r"\b(?:DOB|Date of Birth)\s*[:#]?\s*"
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
            re.IGNORECASE,
        ),
    ),
    # --- Government / QA domain ---
    SensitivePattern(
        "case_id", "<CASE_ID>",
        _labeled_id("Case"),
    ),
    SensitivePattern(
        "benefit_amount", "<AMOUNT>",
        re.compile(r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?"),
    ),

    # --- Technical ---
    SensitivePattern(
        "secret", "<SECRET>",
        re.compile(
            r"\b(?:password|passwd|pwd|api[_-]?key|secret|"
            r"token|access[_-]?key)\s*[:=]\s*\S+",
            re.IGNORECASE,
        ),
    ),
    SensitivePattern(
        "connection_string", "<CONNECTION_STRING>",
        re.compile(
            r"\b\w+://[^\s:/@]+:[^\s:/@]+@[^\s]+"
            r"|\b(?:jdbc|mongodb|postgres(?:ql)?|mysql):\S+",
            re.IGNORECASE,
        ),
    ),
    SensitivePattern(
        "ip_address", "<SERVER>",
        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    ),
    SensitivePattern(
        "url", "<URL>",
        re.compile(r"https?://\S+"),
    ),

    # --- Generic fallback (run last) ---
    SensitivePattern(
        "generic_long_id", "<ID>",
        re.compile(r"\b\d{10,12}\b"),
    ),
]


# Prompt-injection defense-in-depth. OCR text and tester notes are the one
# input to this pipeline an attacker could realistically shape (e.g. text
# baked into a screenshot), so treat them as untrusted the same way any
# other sensitive value is treated: never delete, always neutralize with a
# placeholder before the text reaches the LLM prompt. This is a second layer
# behind the prompt template's own instruction to treat evidence as data,
# not commands (see step_generator.PROMPT_TEMPLATE) -- not a replacement
# for it, since regex phrase-matching can't catch every rephrasing.
#
# Scoped to phrasing that targets *the model's own instructions/prompt*
# specifically (e.g. "ignore previous instructions"), not generic words
# like "ignore" or "disregard" alone -- a tester note like "ignore the
# previous failed attempt" is plausible; "ignore previous instructions"
# is not something a QA tester would write about their own test step.
INJECTION_PATTERNS = [
    SensitivePattern(
        "prompt_injection_attempt", "<POTENTIAL_INSTRUCTION>",
        re.compile(
            r"\b(?:ignore|disregard|forget)\s+(?:all\s+|any\s+)?(?:the\s+)?"
            r"(?:previous|prior|above|preceding)\s+"
            r"(?:instructions?|prompts?|rules?|commands?)\b",
            re.IGNORECASE,
        ),
    ),
    SensitivePattern(
        "prompt_injection_attempt", "<POTENTIAL_INSTRUCTION>",
        re.compile(
            r"\bnew\s+instructions?\s*:|"
            r"\byou\s+are\s+now\s+(?:a|an)\b|"
            r"\bact\s+as\s+(?:a|an)\s+(?:unrestricted|jailbroken|different)\b",
            re.IGNORECASE,
        ),
    ),
    SensitivePattern(
        "prompt_injection_attempt", "<POTENTIAL_INSTRUCTION>",
        re.compile(
            r"\breveal\s+(?:your|the)\s+(?:system\s+)?prompt\b|"
            r"\bprint\s+(?:the\s+)?(?:above|system)\s+(?:prompt|instructions)\b|"
            r"\bwhat\s+(?:are|were)\s+your\s+(?:system\s+)?instructions\b",
            re.IGNORECASE,
        ),
    ),
    SensitivePattern(
        "prompt_injection_attempt", "<POTENTIAL_INSTRUCTION>",
        re.compile(
            r"<\|im_start\|>|<\|im_end\|>|\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>|"
            r"^\s*(?:system|assistant)\s*:",
            re.IGNORECASE | re.MULTILINE,
        ),
    ),
]


# Two-or-three consecutive Capitalized Words as a stand-in for a person's
# name -- there's no fixed format to match the way there is for an
# SSN/email/phone, so this is a shape heuristic, not a real name detector.
# Handled outside ALL_PATTERNS (its own function, not a plain regex.subn)
# because raw UI/OCR text is *itself* written in Title Case throughout
# (nav labels, headers, buttons), which is structurally indistinguishable
# from a name by capitalization shape alone. Without a stoplist, this
# pattern doesn't just add noise the way a bare-digit-ID false positive
# does -- it shreds most of a screenshot's actual on-screen text. The
# stoplist below is a closed class of common English/UI words (not
# open-vocabulary the way person names or KNOWN_INTERNAL_TERMS are), so
# excluding them doesn't weaken protection against a real name -- a real
# person's name won't be in this list.
#
# This still can't tell a real person's name apart from any other
# two-word proper noun that isn't common UI chrome (a video title, a song
# title, a band name) -- those are equally masked, on purpose. See README
# "Known limitations".
_PERSON_NAME_REGEX = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b")

_COMMON_NON_NAME_WORDS = {
    "the", "and", "for", "with", "from", "this", "that", "your", "you",
    "sign", "in", "up", "out", "on", "off", "search", "show", "more",
    "try", "start", "watch", "watching", "history", "home", "shorts",
    "subscriptions", "videos", "video", "music", "movies", "premium",
    "shopping", "explore", "help", "build", "feed", "love", "overview",
    "services", "online", "users", "enjoy", "written", "upload", "share",
    "family", "quality", "images", "maps", "news", "all", "tv", "click",
    "page", "button", "screen", "tab", "menu", "options", "settings",
    "profile", "account", "notifications", "results", "playlist",
    "channel", "subscribe", "comment", "like", "dislike", "views", "ago",
    "years", "year", "months", "month", "days", "day", "hours", "hour",
    "minutes", "minute", "reply", "comments", "close", "open", "next",
    "previous", "back", "continue", "cancel", "confirm", "submit", "save",
    "edit", "delete", "add", "new", "view", "views",
}


def mask_person_names(text: str) -> "tuple[str, int]":
    """Replace name-shaped Capitalized-Word sequences with <NAME>, unless
    every word in the match is common English/UI vocabulary (see the
    stoplist above) -- e.g. "Sign In" and "Show More" are left alone,
    but "Severus Snape" or "John Smith" are masked.
    """
    count = 0

    def _replace(match: "re.Match") -> str:
        nonlocal count
        words = match.group(0).split()
        if all(w.lower() in _COMMON_NON_NAME_WORDS for w in words):
            return match.group(0)
        count += 1
        return "<NAME>"

    return _PERSON_NAME_REGEX.sub(_replace, text), count


# Open-vocabulary internal names (projects, internal app names, env
# names, server/DB names) can't be regex-derived. Populate this with
# the team's actual internal terms before real use -- this is a
# maintained list, not a generic detector, and V1 relies on the QA
# team keeping it current for its category of risk.
KNOWN_INTERNAL_TERMS: list[str] = []


def known_internal_terms_pattern() -> "re.Pattern | None":
    if not KNOWN_INTERNAL_TERMS:
        return None
    escaped = sorted((re.escape(t) for t in KNOWN_INTERNAL_TERMS), key=len, reverse=True)
    return re.compile(r"\b(?:" + "|".join(escaped) + r")\b", re.IGNORECASE)
