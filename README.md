# 🧞‍♂️ Olx Genie

**Autonomous Search Intelligence & Real-time Discovery Engine.**

Olx Genie is a professional-grade, automated synchronization platform designed to find the best deals on OLX.in. It combines a robust server-side polling engine with a high-end monochromatic Web Dashboard and a secure Telegram notification bot.

---

## ⚡ Core Features (v0.1.0)

### 1. Autonomous Sync Engine
- **Strategy B (High-Water Mark):** Efficient ID-based tracking ensures zero duplicate alerts.
- **Dynamic Heartbeat:** Randomized polling intervals (15, 30, 60s) to mimic human behavior and mitigate anti-bot detection.
- **TLS Fingerprint Bypass:** Optimized `httpx` configuration and rotating User-Agents for reliable API connectivity.

### 2. Olx Genie Web Dashboard
- **Monochromatic Aesthetic:** Minimalist, high-contrast off-white/off-black design.
- **Dynamic Configuration:** Real-time search, price filtering, and sorting powered by **HTMX** (no page reloads).
- **High-Density Feed:** 4-column desktop and 2-column mobile views with full location and temporal visibility.
- **Interactive Details:** Full-resolution image galleries and comprehensive technical spec audits.

### 3. Secure Telegram Alerts
- **Private Access:** Secured via a single-heart emoji access key (`❤️`).
- **Multi-Subscriber Broadcast:** Real-time push notifications to all verified, subscribed users.
- **Rich Notifications:** High-density HTML alerts featuring product images and direct Genie Dashboard integration.

---

## 🛠 Tech Stack

- **Backend:** [Litestar](https://litestar.dev/) (ASGI)
- **Bot:** [aiogram 3.x](https://docs.aiogram.dev/)
- **Frontend:** HTMX, Tailwind CSS, Jinja2
- **Database:** SQLite with [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async)
- **Environment:** [uv](https://github.com/astral-sh/uv) (Dependency Management)
- **Testing:** Pytest & Pytest-Asyncio

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) installed

### Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd OlxBot
   ```
2. Create and configure your `.env` file:
   ```bash
   cp .env.example .env
   # Add your BOT_TOKEN and other settings
   ```
3. Install dependencies:
   ```bash
   uv sync
   ```

### Running the Genie
Start the unified Web UI and Telegram Bot engine:
```bash
uv run .\src\main.py
```
Visit the dashboard at: `http://127.0.0.1:8000`

### Testing
Run the comprehensive quality assurance suite:
```bash
uv run pytest
```

---

## 🛡 Security & Privacy
Olx Genie is designed for private use. Access to the Telegram bot requires a server-side verified access key. By default, this is a single heart emoji (`❤️`).

---

## 📝 Roadmap
- [x] v0.1.0: Polling Core & WebUI Finalization.
- [ ] v0.1.1: Hash-based Price Change Detection.
- [ ] v0.2.0: Multi-Search Task Management.

&copy; 2026 Olx Genie. Your Automated Intelligence.
