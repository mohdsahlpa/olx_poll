# Implementation Plan

## Phase 1: Foundation (Current)
- [x] Project initialization with `uv`.
- [x] Git repository setup (main, develop, features branches).
- [x] Streamlined dependencies (removed playwright/BS4).
- [x] Core configuration and base models.
- [x] AI-Readiness documentation.

## Phase 2: Polling Core (v0.1.0)
Goal: Reliable synchronization engine.

### 1. Models & Storage (`feature/models`, `feature/storage`)
- [ ] Define normalized product schema.
- [ ] Implement SQLite storage (products, hashes, timestamps).
- [ ] Commit: `feat(models): add normalized product schema`

### 2. Fetcher (`feature/fetcher`)
- [ ] Implement async `httpx` client with retries.
- [ ] Response validation and error handling (403 retry loops).
- [ ] Commit: `feat(fetcher): implement async api caller`

### 3. Diff Engine (`feature/diff-engine`)
- [ ] Implement hash-based comparison for NEW/UPDATED items.
- [ ] Commit: `feat(diff): implement hash comparison`

### 4. Telegram Alerts (`feature/telegram-basic`)
- [ ] Simple formatted alerts for new items.
- [ ] Commit: `feat(telegram-basic): add simple formatted alerts`

## Phase 3: Deliverable Checkpoint
- [ ] Stable continuous polling for 24h+ without crashes, duplicate floods, or memory leaks.
