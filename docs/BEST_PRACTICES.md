# Best Practices

## General
- **Type Hinting:** All functions and methods must include type hints.
- **Async First:** Use `async/await` for all I/O operations (HTTP, Database).
- **Clean Code:** Follow PEP 8 and use meaningful variable names.

## Development with AI
- **Context is King:** Always update `docs/PROGRESS.md` and `docs/PLAN.md` after significant changes.
- **Atomic Commits:** Commit small, logical changes with descriptive messages. Follow the branch-specific conventions:
    - `feat(models): add normalized product schema`
    - `feat(diff): implement hash comparison`
    - `fix(fetcher): handle 403 retry loop`
    - `refactor(storage): isolate sqlite session handling`
- **Model Validation:** Use Pydantic for all external data validation.

## v0.1.0 — Polling Core Goal
Reliable synchronization engine.
- **Fetcher:** OLX API calls, retries, async httpx client, response validation.
- **Product Normalization:** Convert raw JSON → internal object.
- **SQLite Storage:** Store products, hashes, timestamps.
- **Diff Engine:** Detect NEW and UPDATED items.
- **Telegram Alerts:** Simple formatted alerts.

## Branches
- `feature/fetcher`
- `feature/models`
- `feature/diff-engine`
- `feature/telegram-basic`

## Polling
- **Respect Rate Limits:** Ensure the polling interval is configurable and defaults to a safe value.
- **User-Agent:** Always use a realistic User-Agent for API requests.
- **Error Handling:** Implement exponential backoff for API failures.
