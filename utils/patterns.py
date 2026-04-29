import re
from dataclasses import dataclass


@dataclass
class FilteredContent:
    content_type: str
    value: str

# Phone numbers testing: https://stackoverflow.com/questions/16699007/regular-expression-to-match-standard-10-digit-phone-number

# OTHER PHONE PATTERNS
# \b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|\b(?:\+52)[-\s]\d{2}[-\s]\d{2}[-\s]\d{2}[-\s]\d{2}[-\s]\d{2}\b
# ^\s*(?:\+?(\d{1,3}))?[\W\D\s]*(\d[\W\D\s]*?\d[\D\W\s]*?\d)[\W\D\s]*(\d[\W\D\s]*?\d[\D\W\s]*?\d)[\W\D\s]*(\d[\W\D\s]*?\d[\D\W\s]*?\d[\W\D\s]*?\d)(?: *x(\d+))?\s*$
# (?:(?:\+\d{1,3}[-.\ ]?)?(?:\d{1,4}[-.\ ]?)?(?:\(?\d{3}\)?[-.\ ]?\d{3}[-.\ ]?\d{4})|(?:\+\d{1,3}[-.\ ]?)?(?:\d{2}[-\ ]\d{2}[-\ ]\d{2}[-\ ]\d{2}[-\ ]\d{2}))


URL_PATTERN: str = r"(?:(?:https?|ftp|file)://|www\.|ftp\.)(?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[A-Z0-9+&@#/%=~_|$])"
EMAIL_PATTERN: str = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_PATTERN: str = r"(?<!\d)(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)"
IP_PATTERN: str = r"\b(?:\d{1,3}\.){3}\d{1,3}\b|(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}|::(?:[0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}|[0-9a-fA-F]{1,4}::(?:[0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}"
DISCORD_INVITE_PATTERN: str = r"discord(?:app)?\.com\/invite\/[a-zA-Z0-9]+|discord\.gg\/[a-zA-Z0-9]+"
MENTION_PATTERN: str = r"<@!?\d+>"


def get_all_matches(regex_pattern: str, content: str) -> list[str] | None:
    all_matches: list[str] = re.findall(regex_pattern, content)
    if all_matches:
        return all_matches
    return None


def get_phone_numbers(regex_pattern: str, content: str) -> list[str] | None:
    matches = [m.group(0) for m in re.finditer(regex_pattern, content)]
    return matches or None


def extract_all(content: str) -> list[FilteredContent]:
    results: list[FilteredContent] = []

    urls = get_all_matches(URL_PATTERN, content)
    for url in urls or []:
        results.append(FilteredContent("url", url))

    emails = get_all_matches(EMAIL_PATTERN, content)
    for email in emails or []:
        results.append(FilteredContent("email", email))

    phones = get_phone_numbers(PHONE_PATTERN, content)
    for phone in phones or []:
        results.append(FilteredContent("phone", phone))

    ips = get_all_matches(IP_PATTERN, content)
    for ip in ips or []:
        results.append(FilteredContent("ip", ip))

    discord_invites = get_all_matches(DISCORD_INVITE_PATTERN, content)
    for invite in discord_invites or []:
        results.append(FilteredContent("discord_invite", invite))

    mentions = get_all_matches(MENTION_PATTERN, content)
    for mention in mentions or []:
        results.append(FilteredContent("mention", mention))

    return results


def get_detected_types(content: str) -> dict[str, list[str]]:
    detected: dict[str, list[str]] = {}

    if urls := get_all_matches(URL_PATTERN, content):
        detected["urls"] = urls
    if emails := get_all_matches(EMAIL_PATTERN, content):
        detected["emails"] = emails
    if phones := get_phone_numbers(PHONE_PATTERN, content):
        detected["phones"] = phones
    if ips := get_all_matches(IP_PATTERN, content):
        detected["ips"] = ips
    if discord_invites := get_all_matches(DISCORD_INVITE_PATTERN, content):
        detected["discord_invites"] = discord_invites
    if mentions := get_all_matches(MENTION_PATTERN, content):
        detected["mentions"] = mentions

    return detected