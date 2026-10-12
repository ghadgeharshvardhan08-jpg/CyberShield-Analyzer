# Implementation phases

The project was built in these phases:

1. **Contract and application scaffold — complete.** Establish the React/Vite artifact, API path, OpenAPI source, and generated query/mutation hooks.
2. **Private accounts and persistence — complete.** Create the FastAPI service, Argon2id password storage, signed sessions, account-scoped SQLAlchemy models, request guards, and Alembic migration.
3. **URL analysis and reports — complete.** Add normalization, static risk indicators, additive scoring, stored analysis history, dashboard aggregates, and PDF downloads.
4. **Learning and settings — complete.** Add six original learning modules, hidden quiz answer keys, persisted scores/completions, account settings, privacy information, and deletion.
5. **Verification and delivery docs — complete.** Add backend/frontend tests, endpoint and scoring references, architecture diagram, Windows setup, deployment notes, and a GitHub checklist.

Follow-on work that should be considered before operating this as a public production security product is listed in the README's known limitations.
