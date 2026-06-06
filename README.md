# Discord Research Assistant Bot

A clean-architecture-based Discord bot that assists with scientific research by taking article links (HTML/PDF), downloading them, converting them to Markdown, and answering questions about them using the Gemini API.

## Project Architecture

This project is built following the principles of **Clean Architecture**:

- **Domain Layer (`app/domain`)**: Contains the core business interfaces (`pdf_converter`, `markdown_extractor`, `llm_service`).
- **Service Layer (`app/services`)**: Implements interfaces defined in the domain layer using Playwright (HTML-to-PDF conversion), PyMuPDF4LLM (PDF-to-Markdown extraction), and Google GenAI SDK (Gemini API with fallback handling).
- **Presentation Layer (`app/presentation`)**: Implements the Discord bot interface.
- **Core Layer (`app/core`)**: Handles Dependency Injection (`dependency-injector`) and settings configuration (`pydantic-settings`).

---

## Getting Started with Docker

Docker is the easiest way to run the bot, as it self-packages all required browser rendering engines and OS-level dependencies (Playwright, Chromium dependencies, and Python 3.13).

### 1. Configure Environment Variables

Create a `.env` file in the root directory and add your API keys:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

### 2. Build the Docker Image

Run the following command to build the image:

```bash
docker build -t discord-research-assistant:latest .
```

### 3. Run the Container

Run the bot container, mapping the `.env` file for configuration:

```bash
docker run --env-file .env -d --name discord-research-bot discord-research-assistant:latest
```

To view the bot logs:

```bash
docker logs -f discord-research-bot
```

---

## Local Development (with `uv`)

If you want to run the project locally without Docker:

### 1. Install dependencies

Ensure you have `uv` installed, then run:

```bash
# Create virtual environment and install dependencies
uv sync

# Install Playwright Chromium and dependencies
uv run playwright install chromium
```

### 2. Run the application

Start the bot:

```bash
uv run main.py
```
