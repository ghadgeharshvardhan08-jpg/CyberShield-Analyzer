"""Deterministic URL pattern checks. Submitted URLs are parsed locally, never fetched."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit


WEIGHTS = {
    "insecure_transport": 15,
    "ip_address_host": 25,
    "excessive_subdomains": 10,
    "suspicious_keywords": 8,
    "misleading_domain": 20,
    "encoded_obfuscation": 12,
    "punycode_host": 15,
    "unusual_port": 6,
}
CATEGORY_BANDS = ((20, "Medium"), (45, "High"), (70, "Critical"))
SUSPICIOUS_WORDS = {
    "account", "banking", "confirm", "login", "password", "secure",
    "signin", "support", "update", "verify", "wallet",
}
IMPERSONATED_BRANDS = {
    "amazon": "amazon.com",
    "apple": "apple.com",
    "chase": "chase.com",
    "facebook": "facebook.com",
    "google": "google.com",
    "instagram": "instagram.com",
    "microsoft": "microsoft.com",
    "netflix": "netflix.com",
    "paypal": "paypal.com",
}
SENSITIVE_QUERY_KEYS = {
    "access_token", "account", "apikey", "authorization", "auth", "bearer",
    "code", "csrf", "email", "id_token", "key", "password", "passwd",
    "phone", "refresh_token", "secret", "session", "sessionid", "signature",
    "token", "user", "user_id", "username",
}


class InvalidSubmittedUrl(ValueError):
    """A URL cannot be safely parsed for local indicator checks."""


def _category(score: int) -> str:
    result = "Low"
    for minimum, label in CATEGORY_BANDS:
        if score >= minimum:
            result = label
    return result


def _redact_query(query: str) -> str:
    # Preserve benign query parameters, but never persist common credential values.
    try:
        pairs = parse_qsl(query, keep_blank_values=True, max_num_fields=100)
    except ValueError as exc:
        raise InvalidSubmittedUrl("The web address contains too many query parameters.") from exc
    redacted = [
        (key, "[REDACTED]" if key.casefold() in SENSITIVE_QUERY_KEYS else value)
        for key, value in pairs
    ]
    return urlencode(redacted, doseq=True, quote_via=quote)


def analyze_url(raw_url: str) -> dict:
    """Normalize and score a URL without making any network request.

    Points are additive and capped at 100. Each scored indicator appears as a
    user-facing finding with its exact contribution.
    """
    if not isinstance(raw_url, str):
        raise InvalidSubmittedUrl("Enter a valid web address.")
    candidate = raw_url.strip()
    if not candidate or len(candidate) > 2048:
        raise InvalidSubmittedUrl("Enter a web address between 1 and 2,048 characters.")
    if any(ord(char) < 32 or ord(char) == 127 for char in candidate):
        raise InvalidSubmittedUrl("The web address contains unsupported control characters.")

    if "://" not in candidate:
        candidate = "https://" + candidate
    try:
        parsed = urlsplit(candidate)
        scheme = parsed.scheme.casefold()
        raw_host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise InvalidSubmittedUrl("That web address could not be parsed.") from exc

    if scheme not in {"http", "https"} or not raw_host:
        raise InvalidSubmittedUrl("Enter a complete HTTP or HTTPS web address with a hostname.")

    # User-info in URLs can be used to disguise the real destination, but may
    # itself contain credentials. Score it and remove it before any persistence.
    has_userinfo = parsed.username is not None or parsed.password is not None
    host = raw_host.rstrip(".").casefold()
    try:
        ip = ipaddress.ip_address(host)
        normalized_host = ip.compressed
        host_is_ip = True
    except ValueError:
        try:
            normalized_host = host.encode("idna").decode("ascii").casefold()
        except UnicodeError as exc:
            raise InvalidSubmittedUrl("The hostname is not valid.") from exc
        host_is_ip = False

    if not normalized_host or len(normalized_host) > 253:
        raise InvalidSubmittedUrl("The hostname is not valid.")
    if any(not label or len(label) > 63 for label in normalized_host.split(".")):
        raise InvalidSubmittedUrl("The hostname is not valid.")

    if ":" in normalized_host:  # IPv6 must be bracketed in a URL authority.
        authority_host = f"[{normalized_host}]"
    else:
        authority_host = normalized_host
    if port is not None:
        authority_host = f"{authority_host}:{port}"

    safe_url = urlunsplit(
        (
            scheme,
            authority_host,
            parsed.path or "",
            _redact_query(parsed.query),
            "",  # Fragments are not sent to a server and may contain private data.
        )
    )
    host_labels = normalized_host.split(".")
    findings: list[dict] = []

    def add(code: str, title: str, description: str, severity: str) -> None:
        findings.append(
            {
                "code": code,
                "title": title,
                "description": description,
                "points": WEIGHTS[code],
                "severity": severity,
            }
        )

    if scheme == "http":
        add(
            "insecure_transport",
            "Connection is not encrypted",
            "This address uses HTTP, so information sent to it may not be protected in transit.",
            "medium",
        )
    if host_is_ip:
        add(
            "ip_address_host",
            "Uses an IP address instead of a domain",
            "A numeric network address can hide who operates the destination and is uncommon for trusted consumer sign-in pages.",
            "high",
        )
    if len(host_labels) > 4 and not host_is_ip:
        add(
            "excessive_subdomains",
            "Many nested subdomains",
            "Several hostname levels can make the actual registered domain harder to spot.",
            "medium",
        )

    url_text = f"{normalized_host}{parsed.path}".casefold()
    keyword_matches = sorted(word for word in SUSPICIOUS_WORDS if re.search(rf"(?<![a-z]){re.escape(word)}(?![a-z])", url_text))
    if keyword_matches:
        add(
            "suspicious_keywords",
            "Account or verification wording",
            f"The address includes wording often used to prompt urgent sign-in or data entry ({', '.join(keyword_matches[:4])}). This wording alone does not prove harm.",
            "low",
        )

    brand_impersonation = False
    for brand, official_domain in IMPERSONATED_BRANDS.items():
        brand_in_host = any(brand in label for label in host_labels)
        if brand_in_host and normalized_host != official_domain and not normalized_host.endswith("." + official_domain):
            brand_impersonation = True
            break
    if has_userinfo or brand_impersonation:
        reason = (
            "The URL contains text before an @ sign that can make the real hostname easy to miss."
            if has_userinfo
            else "A familiar brand name appears in a hostname that does not end in its recognized domain."
        )
        add("misleading_domain", "Possible misleading domain pattern", reason, "high")

    encoded_sequences = re.findall(r"%[0-9a-fA-F]{2}", raw_url)
    encoded_delimiters = re.search(r"%(?:2e|2f|40|5c|00)", raw_url, flags=re.IGNORECASE)
    if len(encoded_sequences) >= 4 or encoded_delimiters:
        add(
            "encoded_obfuscation",
            "Unusual URL encoding",
            "Repeated encoded characters or encoded separators can obscure what an address contains.",
            "medium",
        )
    if any(label.startswith("xn--") for label in host_labels):
        add(
            "punycode_host",
            "Internationalized hostname",
            "This hostname uses an encoded form that can make visually similar characters difficult to distinguish.",
            "medium",
        )
    if port is not None and port not in {80, 443}:
        add(
            "unusual_port",
            "Non-standard web port",
            "The address uses a port that is less common for public web pages.",
            "low",
        )

    raw_score = sum(item["points"] for item in findings)
    score = min(raw_score, 100)
    category = _category(score)
    if score >= 70:
        recommendation = "Avoid opening this address or entering information. Verify the destination through a trusted, independently obtained channel."
    elif score >= 45:
        recommendation = "Treat this address with caution. Do not sign in or share personal information; check the domain through a trusted source."
    elif score >= 20:
        recommendation = "Review the findings and verify the domain independently before interacting with it."
    else:
        recommendation = "No listed warning patterns were detected. This limited check cannot verify the site or guarantee that it is safe."

    return {
        "submitted_url": safe_url,
        "normalized_url": safe_url,
        "score": score,
        "category": category,
        "findings": findings,
        "recommendation": recommendation,
    }
