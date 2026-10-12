# URL risk scoring methodology

## Purpose and limits

The analyzer performs static pattern checks on the submitted string and its parsed URL components. It does **not** open the URL, resolve DNS, establish TLS, inspect page content, compare against a threat feed, or confirm malicious activity.

Each item is an **indicator**, not a confirmed threat. A score of zero means no listed pattern was detected, not that a site is safe. Risk labels are educational triage aids, not calibrated probabilities.

## Normalization

1. Trim surrounding whitespace and reject empty, over-2,048-character, control-character, malformed-host, and non-HTTP(S) inputs.
2. If the scheme is omitted, treat the input as HTTPS for analysis.
3. Lowercase the scheme and hostname, encode internationalized hostnames using IDNA, and retain the path.
4. Strip URL user-info and fragments before storing the display/normalized value. Replace values for common credential-bearing query keys (for example `token`, `password`, `key`, `session`, `auth`, and `code`) with `[REDACTED]`.
5. Do not perform any outbound request using the submitted address.

## Weighted rules

| Indicator | Points | Rationale |
| --- | ---: | --- |
| HTTP instead of HTTPS | 15 | Traffic is not protected by HTTPS transport |
| Host is an IP literal | 25 | Destination identity is less readable and uncommon for trusted consumer sign-in pages |
| More than four hostname labels | 10 | The apparent brand/domain can be harder to distinguish from nested subdomains |
| Account/verification wording in host or path | 8 | Terms such as `login`, `verify`, `password`, or `wallet` can create urgency; wording alone is weak evidence |
| Possible misleading domain | 20 | User-info syntax or a known brand string outside its recognized domain may disguise the actual host |
| Repeated encoded characters or encoded separators | 12 | Encoding can obscure separators and the address's visible structure |
| Punycode hostname label | 15 | Internationalized hostnames can contain characters that visually resemble others |
| Non-standard web port | 6 | A public web address using a port other than 80 or 443 is less common |

For each detected rule, the finding displays its name, plain-language explanation, severity, and point contribution. A keyword group contributes once even if several terms match. A single rule cannot add more than its listed weight.

## Formula and categories

```text
raw_score = sum(points for each distinct detected indicator)
score = min(raw_score, 100)
```

| Score | Category |
| ---: | --- |
| 0–19 | Low |
| 20–44 | Medium |
| 45–69 | High |
| 70–100 | Critical |

Example: an HTTP URL hosted at an IP address with a `login` path scores `15 + 25 + 8 = 48`, or **High**. It is not a finding that the URL is malicious; it is a transparent score based on those patterns.

## Recommendations

- **Low:** No listed patterns were found. The app states that it cannot verify or guarantee the site's safety.
- **Medium:** Review findings and verify the domain independently before interacting.
- **High:** Treat the address cautiously; avoid signing in or sharing information until independently verified.
- **Critical:** Avoid opening or entering information; verify the destination through a trusted channel.

False positives and false negatives are expected. New rule changes should include updated weights, examples, tests, and documentation. Never describe the score as a probability or a guarantee.
