## Summary

- dedupe `/v1` when combining `UPSTREAM_RESPONSES_API_URL` base with Cursor `/v1/...` request paths
- add regression tests for responses-compat and chat-completions routing

## Problem

`resolve_upstream_url()` could generate `/v1/v1/...` URLs when the configured upstream endpoint already included `/v1/responses`. This caused upstream `404 Not found` even though the relay and Cursor path were otherwise correct.

## Test plan

```bash
python -m unittest discover -s tests -v
```

Manual smoke test:

```bash
curl http://127.0.0.1:8082/healthz
curl -X POST "http://127.0.0.1:8082/v1/chat/completions" \
  -H "Authorization: Bearer $RELAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"<allowed-model>","messages":[{"role":"user","content":"hi"}],"stream":false}'
```
