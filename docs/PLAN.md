# Implementation Plan

## Phase 1: Foundation (Complete)
- [x] Project initialization with `uv`.
- [x] Git repository setup.
- [x] Streamlined dependencies.
- [x] Core configuration and base models.
- [x] AI-Readiness documentation.

## Phase 2: Polling Core (v0.1.0) - COMPLETE
Goal: Reliable synchronization engine.

### 1. Models & Storage (Complete)
- [x] Define rich normalized product schema.
- [x] Implement safe getters for nested API data.
- [x] SQLite storage (seen items with metadata).

### 2. Fetcher (Complete)
- [x] Implement async `httpx` client with browser-impersonating headers.
- [x] Bypassed anti-bot blocks via HTTP/1.1 and header optimization.
- [x] Response validation and rich data extraction.

### 3. Olx Genie Web UI (Complete)
- [x] Monochromatic, minimal aesthetic with 'Olx Genie' branding.
- [x] Responsive layout with RHS sidebar (Desktop) and Slide-over (Mobile).
- [x] Dynamic configuration (Query, Price, Sort) with HTMX live refetch.
- [x] Synchronized Heartbeat: Server-side polling with randomized intervals.
- [x] High-density information display (4x grid desktop, 2x mobile).

### 4. Telegram Alerts (Complete)
- [x] Bot notification loop integrated into PollingManager.
- [x] Strategy 1 (Emoji access) + Heart key implementation.
- [x] High-density HTML message formatting with images.
- [x] Strategy B (ID Tracking) to prevent duplicate alerts.

### 5. Quality & Branding (Complete)
- [x] Comprehensive test suite (Models, Config, Database).
- [x] Programmatic bot description and profile branding.

## Phase 3: Deliverable Checkpoint (Complete)
- [x] v0.1.0 — Polling Core Finalized.
- [x] Stable continuous polling architecture verified.

## Phase 4: Resilience & Monitoring (Complete)
- [x] Implementation of `/health` and `/stats` endpoints for Render.com keep-alive.
- [x] Asynchronous dashboard loading via HTMX to prevent local/prod lag.
- [x] Graceful `TelegramConflictError` handling for multi-instance safety.

## Phase 5: Genie Reforged (In Progress)
Goal: High-performance engine with stealth fetching and delta updates.

### 1. Stealth Fetcher (Paused)
- [x] Poisson Distribution logic for truly human jittered polling intervals.
- [ ] Browser Fingerprint Mimicry (Refining detection bypass).

### 2. Nexus Delta-UI (Complete)
- [x] JSON-payload broadcasting over SSE (ID, Title, Price, Image).
- [x] HTMX "Prepend" logic for single-item discovery updates with animations.
- [x] In-memory DiscoveryFilter for $O(1)$ seen-item checks.

### 3. Stateful Guardian (Bot) (In Progress)
- [x] aiogram FSM for per-user session management.
- [x] Jinja2 template-based HTML message rendering.
- [x] Pure Stream Logic: Individual alerts filtered by subscription timestamp.
- [x] 30-minute discovery window enforced.

### 4. System Integrity
- [ ] Write-Ahead Logging (WAL) for SQLite concurrency.
- [ ] Structured JSON logging for production diagnostics.
