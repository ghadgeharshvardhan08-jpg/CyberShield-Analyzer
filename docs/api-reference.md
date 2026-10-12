# API endpoint reference

All routes are mounted below `/api`. Browser sessions use the signed HttpOnly `cybershield_session` cookie; protected routes return `401` if the caller is not signed in. Account-owned objects are always scoped to the authenticated user.

The authoritative OpenAPI contract is `lib/api-spec/openapi.yaml`. Interactive documentation is served at `/api/docs`.

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| `GET` | `/healthz` | No | Service health |
| `GET` | `/auth/session` | No | Current session state; returns unauthenticated state when signed out |
| `POST` | `/auth/register` | No | Register and establish a session |
| `POST` | `/auth/login` | No | Sign in with email and password |
| `POST` | `/auth/logout` | No | Clear the session |
| `DELETE` | `/auth/account` | Yes | Delete account, analyses, and learning progress |
| `GET` | `/dashboard` | Yes | Stored totals, category counts, 14-day scan trend, and recent results |
| `GET` | `/analyses` | Yes | Private history; optional `search`, `category`, `limit`, and `offset` |
| `POST` | `/analyses` | Yes | Analyze and persist a URL without visiting it |
| `GET` | `/analyses/{analysisId}` | Yes | Private analysis details |
| `GET` | `/analyses/{analysisId}/report` | Yes | Download a private PDF report |
| `GET` | `/learning/modules` | Yes | Lesson list and per-user completion/best score |
| `GET` | `/learning/modules/{slug}` | Yes | Lesson text and quiz questions, without answer keys |
| `POST` | `/learning/modules/{slug}/quiz` | Yes | Submit quiz answers and persist best score/progress |
| `GET` | `/learning/progress` | Yes | Current user's course progress summary |
| `GET` | `/settings` | Yes | Current account settings |
| `PATCH` | `/settings` | Yes | Update display name |

## Request examples

```json
POST /api/auth/register
{
  "email": "learner@example.com",
  "displayName": "Security Learner",
  "password": "a-unique-password-with-12+-chars"
}
```

```json
POST /api/analyses
{
  "url": "https://example.test/account/verify"
}
```

```json
POST /api/learning/modules/phishing/quiz
{
  "answers": [
    { "questionId": "p1", "selectedOption": 1 },
    { "questionId": "p2", "selectedOption": 2 },
    { "questionId": "p3", "selectedOption": 0 }
  ]
}
```

## Response and error notes

- Analysis JSON includes the sanitized submitted/display URL, normalized URL, score, category, findings, recommendation, and UTC timestamp.
- Sensitive query values and fragments are removed before URL persistence and report generation.
- PDF downloads use `Content-Type: application/pdf` and `Content-Disposition: attachment`.
- Errors use a safe `{ "detail": "..." }` body. Common statuses include `400` for invalid URL/quiz input, `401` for missing session, `403` for disallowed request origin, `404` for missing or not-owned analysis, `413` for oversized request, `422` for invalid request shape, and `429` for rate limits.
- Quiz answer keys are absent from lesson responses; correctness and explanations are returned only after submission.
