# Cursor OpenAI BYOK Bridge

[中文说明](./README.md)

A very small relay for Cursor BYOK.

## What it is

Cursor BYOK sends requests to `/v1/chat/completions`, but the request body is often closer to the Responses API format.
This Cursor behavior is discussed here:
[Cursor Agent sends Responses API format to Chat Completions endpoint](https://forum.cursor.com/t/cursor-agent-sends-responses-api-format-to-chat-completions-endpoint/153019).

That means:

- the path is Chat Completions: `/v1/chat/completions`
- the body looks like Responses API
- Cursor still expects a Chat Completions style response

This can break Responses-only models or gateways, and strict Chat Completions validators may fail on missing `messages`, `tools[].function`, or similar fields.
This project handles that conversion layer: it forwards Cursor's mismatched request to an upstream Responses API endpoint, then converts the upstream response back into the Chat Completions shape Cursor expects.

## Usage

```bash
git clone https://github.com/Pil0tXia/Cursor-OpenAI-BYOK-Bridge.git
cd Cursor-OpenAI-BYOK-Bridge
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

Edit `.env` before starting:

```env
UPSTREAM_BASE_URL=https://api.openai.com/v1/responses
UPSTREAM_API_KEY=sk-your-upstream-api-key
UPSTREAM_API_KEY_HEADER=authorization
RELAY_API_KEY=change-me-to-a-long-random-string

# Optional: override Responses API reasoning effort.
# REASONING_EFFORT=minimal|low|medium|high
# REASONING_MODELS=azure/gpt-5.4,gpt-5.5
# REASONING_OVERRIDE=true
```

`UPSTREAM_BASE_URL` is now a full endpoint URL, and `/v1/responses` is the recommended default.
If you set `/chat/completions`, the relay will map it to `/responses` when needed.

`UPSTREAM_API_KEY_HEADER` supports two modes:

- `authorization` (default): sends `Authorization: Bearer <UPSTREAM_API_KEY>`
- `x-api-key`: sends `x-api-key: <UPSTREAM_API_KEY>`

`REASONING_EFFORT` optionally overrides `reasoning.effort` on Responses API requests.
When `REASONING_MODELS` is empty, it applies to all models; otherwise it only applies to the comma-separated model list.
If Cursor already sends `reasoning`, set `REASONING_OVERRIDE=true` to replace it.

Default addresses:

- Service: `http://localhost:8082`
- Endpoint: `http://localhost:8082/v1/chat/completions`

One-command local startup:

```bash
./start.sh
```

The script starts Bridge and ngrok in the background, then prints the local dashboard and log paths.
ngrok's own agent log is written to `logs/ngrok-agent.log`.

Stop:

```bash
./stop.sh
```

In Cursor BYOK:

- Base URL: `http://your-server:8082/v1`
- API Key: your `RELAY_API_KEY`

## How it works

1. Cursor sends a request to `/v1/chat/completions`
2. This project listens on that endpoint
3. If the body looks like a Responses API payload, it forwards to `UPSTREAM_BASE_URL` (default `/v1/responses`)
4. When the upstream returns a Responses API result, this project converts it into Chat Completions format
5. The converted response is returned to Cursor

Streaming follows the same idea: Responses SSE events come in, Chat Completions chunks go out.

## Notes

- This is a small utility, not a highly configurable platform
- `.env` is required at runtime
- Do not commit `.env` to GitHub

## License

MIT. See `LICENSE`.
