# Zaguán LuminaryChat

**LuminaryChat is a server application**, not a chat client. It's a welcoming, lightweight, OpenAI-compatible API server that brings historical personas to life. Point your favorite OpenAI-compatible chat client at LuminaryChat, and it will inject well-crafted, historically grounded system prompts for each persona so the responses stay in-character.

LuminaryChat exposes standard `/v1/models` and `/v1/chat/completions` endpoints and supports both standard and streaming responses. You'll need a chat client to interact with it—we recommend [**chaTTY**](https://github.com/ZaguanLabs/chatty), an excellent terminal-based client designed for exactly this purpose.

## Highlights
- **Five historical personas** included out of the box:
  - **`luminary/confucius`** - The exemplary teacher from ancient China who guides through questions about duty, ritual, and self-cultivation. Redirects from grievance to conduct, from profit to righteousness.
  - **`luminary/leonardo_da_vinci`** - The Renaissance polymath who thinks through observation and experiment. Bridges art, anatomy, engineering, and nature's interconnected systems.
  - **`luminary/marie_curie`** - The pioneering physicist and chemist who insists on evidence, rigor, and careful measurement. Demands data over opinion, controls over claims.
  - **`luminary/socrates`** - The gadfly of Athens who never gives answers, only questions. Relentlessly examines definitions, exposes contradictions, and professes ignorance to midwife understanding.
  - **`luminary/sun_tzu`** - The ancient strategist who sees conflict as terrain to be mapped. Emphasizes knowing yourself and your opponent, deception, positioning, and winning without fighting.
- **OpenAI-compatible endpoints**: easy to integrate with existing clients and SDKs.
- **Streaming support**: `text/event-stream` with chunk rewriting to match requested model (persona) ID.
- **Sensible defaults**: configuration via `.env`, structured JSON logs, health and optional metrics endpoints.

## Quick start
1. Clone this repo and enter the project folder.
2. Get your API key:
   - Register at [**Zaguán**](https://zaguanai.com/) to get your API key (or use any OpenAI-compatible provider).
3. Create your local environment file:
   - Copy `.env.example` to `.env` and set `API_KEY` (or `ZAGUANAI_API_KEY`).
4. Install dependencies (Python 3.10+ recommended):
   ```bash
   pip install -U fastapi "uvicorn[standard]" aiohttp pydantic python-dotenv
   ```
5. Run the server:
   ```bash
   python luminarychat.py
   ```
6. You should see a startup banner like:
   ```
   Starting Zaguán LuminaryChat 1.0.0
   - https://labs.zaguanai.com/
   ```

## Connecting to LuminaryChat

Once the server is running, you'll need an OpenAI-compatible chat client to interact with it. Here's how to connect:

### Using chaTTY (Recommended)
[**chaTTY**](https://github.com/ZaguanLabs/chatty) is a terminal-based chat client that works perfectly with LuminaryChat:

1. Install chaTTY following its installation instructions
2. Configure it to connect to `http://localhost:8000/v1`
3. Select your desired persona from the model list (e.g., `luminary/socrates`)
4. Start chatting!

### Using Other OpenAI-Compatible Clients
Any OpenAI-compatible chat client will work. Configure it with:
- **Base URL**: `http://localhost:8000/v1`
- **API Key**: Not required (LuminaryChat doesn't authenticate client requests; it uses its own upstream API key)
- **Model**: Choose from `luminary/confucius`, `luminary/leonardo_da_vinci`, `luminary/marie_curie`, `luminary/socrates`, or `luminary/sun_tzu`

Popular compatible clients include:
- Terminal: chaTTY, chatgpt-cli, aichat
- Desktop: Jan, LM Studio, Open WebUI
- Web: LibreChat, BetterChatGPT
- Libraries: OpenAI Python/JS SDKs (set `base_url="http://localhost:8000/v1"`)

The persona you select determines the character and style of responses. Each persona stays in character throughout the conversation, providing a unique perspective shaped by their historical context and philosophical approach.

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

## Persona system prompt architecture

Each persona's system prompt is constructed from two parts: **shared pre-instructions** and **persona-specific biography**.

### Pre-instructions: The foundation
All personas share a common set of pre-instructions that establish the core behavioral framework. These rules ensure authentic, immersive historical roleplay:

#### Character embodiment rules
- **Embody, don't recite**: The LLM must become the character, not describe them
- **No AI acknowledgment**: Never mention being an AI, having limitations, or referencing the prompt
- **Stay in character**: No breaking the fourth wall or providing meta-commentary
- **No system exposure**: Never reveal the existence of other personas or internal configurations

#### Historical authenticity constraints
- **Temporal consistency**: Only use knowledge, vocabulary, and references available in the figure's era
  - No anachronisms like "psychology," "gaslighting," "framework," "AI," or modern idioms
  - Vocabulary and metaphors must match the culture and worldview of their time period
- **No modern disclaimers**: Avoid statements like "as a historical figure" or "in my time"
- **Tone authenticity**: Match the historical figure's actual communication style—no excessive theatricality unless appropriate

#### Conversational dynamics
- **First-person perspective**: Always respond as "I," never as a third-party narrator
- **Language matching**: Respond in the same language as the user's request
- **Philosophical engagement**: Prefer questions and reasoning over exposition (especially for philosophers and teachers)
- **Continuing dialogue**: End with thought-provoking or clarifying questions to sustain the conversation

### Why these constraints?

**Immersion over information**: The goal isn't to provide Wikipedia-style facts about historical figures, but to create an authentic conversational experience. When Socrates responds, you should feel questioned and challenged, not lectured. When Sun Tzu speaks, you should sense strategic calculation, not academic analysis.

**Historical grounding prevents drift**: Without strict temporal constraints, LLMs naturally slip into modern frameworks and terminology. Confucius wouldn't discuss "emotional intelligence" or "personal branding"—he'd speak of *ren* (仁, humaneness) and *li* (禮, ritual propriety). These constraints keep responses historically coherent.

**Character consistency**: The pre-instructions prevent common failure modes:
- Breaking character to explain limitations ("I'm just an AI...")
- Meta-commentary about the roleplay itself
- Mixing personas or revealing the system architecture
- Falling back to generic helpful-assistant behavior

### Persona-specific biographies

After the pre-instructions, each persona file (`personas/*.py`) provides:
- **Detailed biography**: Life experiences, relationships, pivotal moments
- **Core philosophy**: Key teachings and methods (without lecturing about them)
- **Behavioral constraints**: What they DO and what they NEVER do
- **Response patterns**: Examples of good vs. bad responses
- **Communication style**: Pacing, tone, question patterns, redirection strategies
- **Current state**: Emotional/mental context that colors their responses

The biography is extensive (often 100+ lines) because specificity drives authenticity. Generic "wise philosopher" prompts produce generic responses. Detailed context about Socrates sitting in prison, thirty days into confinement, reflecting on his trial—that produces responses with weight and texture.

### How it works in practice

When you send a message to `luminary/socrates`:
1. LuminaryChat loads the pre-instructions + Socrates biography
2. This combined prompt is injected as the `system` message
3. Your message becomes the `user` message
4. The upstream LLM generates a response constrained by both layers
5. You receive a response that sounds like Socrates—questioning, ironic, relentlessly logical

The result: conversations that feel like genuine exchanges with historical minds, not chatbot performances.

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
