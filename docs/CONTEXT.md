# Project Context: OLX.in API Bot

## Overview
A lightweight Telegram Bot that polls a specific OLX.in API endpoint at regular intervals (15, 30, or 60 seconds) and notifies users of new listings.

## Core Tech Stack
- **Backend Framework:** Litestar (ASGI)
- **Bot Framework:** aiogram 3.x
- **Dependency Management:** uv
- **HTTP Client:** httpx
- **Configuration:** pydantic-settings
- **Models:** pydantic

## Architecture
- `src/core/`: Configuration and global settings.
- `src/models/`: Data structures for API responses and internal state.
- `src/bot/`: Telegram bot handlers and message formatting.
- `src/api/`: Litestar application for lifecycle management and potential dashboard.
- `src/scraper/`: The polling logic (fetching and diffing API responses).

## Integration Strategy
- The Litestar app will manage the `aiogram` dispatcher lifecycle.
- A background task (worker) will run within the Litestar event loop to poll the OLX API.
- New items will be identified by comparing IDs against a local cache (or database).
