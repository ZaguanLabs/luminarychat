# Zaguán LuminaryChat

A welcoming, lightweight, OpenAI-compatible chat API that brings historical personas to life. LuminaryChat exposes `/v1/models` and `/v1/chat/completions` endpoints and injects well-crafted, historically grounded system prompts for each persona so the responses stay in-character. It supports both standard and streaming responses.

## Highlights
- Personas included out of the box (model IDs):
  - `luminary/confucius`
  - `luminary/leonardo_da_vinci`
  - `luminary/marie_curie`
  - `luminary/socrates`
  - `luminary/sun_tzu`
- OpenAI-compatible endpoints: easy to integrate with existing clients and SDKs.
- Streaming support: `text/event-stream` with chunk rewriting to match requested model (persona) ID.
- Sensible defaults: configuration via `.env`, structured JSON logs, health and optional metrics endpoints.

## Quick start
1. Clone this repo and enter the project folder.
2. Create your local environment file:
   - Copy `.env.example` to `.env` and set `API_KEY` (or `ZAGUANAI_API_KEY`).
3. Install dependencies (Python 3.10+ recommended):
   ```bash
   pip install -U fastapi "uvicorn[standard]" aiohttp pydantic python-dotenv
   ```
4. Run the server:
   ```bash
   python luminarychat.py
   ```
5. You should see a startup banner like:
   ```
   Starting Zaguán LuminaryChat 1.0.0
   - https://labs.zaguanai.com/
   ```

## Configuration
Configuration is read from environment variables (preferably via `.env`). See `.env.example` for full list. Key settings:
- `API_URL` (default: `https://api.zaguanai.com/v1`)
- `API_KEY` or `ZAGUANAI_API_KEY` (required)
- `MODEL_NAME` upstream model (default: `promptshield/gemini-flash-lite-latest`)
- `PORT` (default: `8000`)
- `HOST` (default: `0.0.0.0`)
- `MAX_WORKERS`, `REQUEST_TIMEOUT`, `KEEPALIVE_TIMEOUT`
- `LOG_LEVEL` (DEBUG|INFO|WARNING|ERROR|CRITICAL)
- `RATE_LIMIT_PER_MINUTE`
- `ENABLE_METRICS` (true/false)
- `MAX_RETRIES`, `RETRY_DELAY`

### OpenAI-compatible providers (Choice!)
LuminaryChat speaks the OpenAI API dialect. That means you can point it at any OpenAI-compatible provider, not just ZaguanAI.

- Set `API_URL` to your provider's base URL (ending with `/v1`).
- Set `API_KEY` to the provider's API key (header is sent as `Authorization: Bearer <API_KEY>`).

Example `.env` for another provider:
```
API_URL=https://api.example.com/v1
API_KEY=sk-your-provider-key
MODEL_NAME=some/upstream-model
```

Everything else in LuminaryChat continues to work the same: you still call `/v1/models` to see personas and `/v1/chat/completions` with `model` set to a persona like `luminary/socrates`.

## API overview
- `GET /health`
  - Simple health check.
- `GET /metrics` (enabled when `ENABLE_METRICS=true`)
  - Exposes basic counters and latency averages.
- `GET /v1/models`
  - Lists available personas as model entries. Use these `id`s (e.g., `luminary/socrates`) in requests to switch personas.
- `POST /v1/chat/completions`
  - OpenAI-compatible chat completions endpoint.
  - Non-streaming returns JSON.
  - Streaming returns `text/event-stream` with `data:` chunks and a final `data: [DONE]`.

### Example: list models
```bash
curl -s http://localhost:8000/v1/models | jq
```

### Example: non-streaming chat
```bash
curl -s http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "luminary/socrates",
    "messages": [
      {"role": "user", "content": "What is wisdom?"}
    ]
  }' | jq
```

### Example: streaming chat
```bash
curl -N http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "luminary/sun_tzu",
    "stream": true,
    "messages": [
      {"role": "user", "content": "How to prepare for conflict?"}
    ]
  }'
```

## How personas work
- Persona definitions live in `personas/` and provide:
  - A concise biography and worldview
  - Communication style and tone
  - Guardrails and signature behaviors
  - A generated `system` prompt assembled with shared pre-instructions
- On each request, the server:
  1. Verifies the requested `model` corresponds to a known persona
  2. Injects that persona’s system prompt (if the client didn’t provide one)
  3. Proxies the request to the upstream LLM with your configured `MODEL_NAME`
  4. Optionally streams the response and rewrites `model` in chunks to your requested persona ID

## Technical notes
- Framework: FastAPI + Uvicorn
- HTTP client: aiohttp with connection pooling, timeouts, and keepalive
- Validation: Pydantic models for chat requests
- Config: `.env` via `python-dotenv` and environment variables
- Logging: Structured JSON to stdout with request IDs and timing
- Rate limiting: simple token bucket per-client-IP
- Reliability: retries with exponential backoff for upstream requests
- Metrics: in-memory counters and averages (enabled via `ENABLE_METRICS`)

## Development tips
- Add or edit personas in `personas/` and they’ll be auto-loaded at startup.
- Adjust `.env` to tune performance (workers, timeouts) and logging verbosity.
- If you change upstream providers/models, update `MODEL_NAME` and `API_URL`.

---

Welcome to LuminaryChat — where timeless thinkers meet modern interfaces. If you have ideas for new personas or features, contributions are always appreciated!
