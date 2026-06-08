## Summary

When `UPSTREAM_RESPONSES_API_URL` is configured as a full Responses endpoint such as `https://api.example.com/v1/responses`, `resolve_upstream_url()` derives a base URL that already ends with `/v1`.

Cursor BYOK then sends requests to paths like `/v1/chat/completions` or `/v1/responses`. The relay currently concatenates them directly, producing double-prefixed URLs such as:

```text
https://api.example.com/v1/v1/chat/completions
https://api.example.com/v1/v1/responses
```

Many OpenAI-compatible gateways return `404 Not found` for the doubled path.

## Reproduction

1. Configure:

```env
UPSTREAM_RESPONSES_API_URL=https://api.example.com/v1/responses
```

2. Send an authenticated relay request:

```bash
curl -X POST "http://localhost:8082/v1/chat/completions" \
  -H "Authorization: Bearer $RELAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.5","input":"hello","stream":false}'
```

3. Observe upstream forwarding to `/v1/v1/...` and a `404` response.

## Expected behavior

The relay should forward to:

```text
https://api.example.com/v1/chat/completions
https://api.example.com/v1/responses
```

## Environment

- Cursor OpenAI BYOK Bridge: current `main`
- Cursor BYOK Base URL: `http(s)://<public-host>/v1`
- Upstream: OpenAI-compatible Responses API

## Proposed fix

Strip a leading `/v1` from `target_path` when `base_url` already ends with `/v1`.
