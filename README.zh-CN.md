# Cursor OpenAI BYOK Bridge

[English README](./README.md)

面向 Cursor OpenAI-compatible BYOK 场景的协议兼容层：修复 Cursor Agent 在 `/v1/chat/completions` 与 Responses API 之间的请求/响应格式错配，让 GPT-5 系列、Azure/OpenAI-compatible 网关和需要 Responses API 的模型可以稳定接入 Cursor。

## 这是什么

Cursor 的 BYOK 会把请求发到 `/v1/chat/completions`，但请求体实际更接近 Responses API 的格式。
这个问题在 Cursor 论坛里也有对应讨论：
[Cursor Agent sends Responses API format to Chat Completions endpoint](https://forum.cursor.com/t/cursor-agent-sends-responses-api-format-to-chat-completions-endpoint/153019)。

问题在于：

- 请求路径是 Chat Completions：`/v1/chat/completions`
- 请求体更像 Responses API
- Cursor 期望返回值还是 Chat Completions 格式

这会让只支持 Responses API 的模型或网关路由失败，也会让严格校验 Chat Completions schema 的上游报 `messages`、`tools[].function` 等字段错误。
这个项目就是处理中间这层转换：把 Cursor 发来的错配请求转到上游 Responses API，再把响应转换回 Cursor 期望的 Chat Completions 形态。

## 使用方法

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

启动前修改 `.env`：

```env
UPSTREAM_RESPONSES_API_URL=https://api.openai.com/v1/responses
UPSTREAM_API_KEY=sk-your-upstream-api-key
UPSTREAM_API_KEY_HEADER=authorization
RELAY_API_KEY=change-me-to-a-long-random-string

# Optional: override Responses API reasoning effort.
# REASONING_EFFORT=minimal|low|medium|high
# REASONING_MODELS=azure/gpt-5.4,gpt-5.5
# REASONING_OVERRIDE=true
```

`UPSTREAM_RESPONSES_API_URL` 是转换后 Cursor 请求使用的完整上游 Responses API endpoint。

`UPSTREAM_API_KEY_HEADER` 支持两种：

- `authorization`（默认）：上游请求头为 `Authorization: Bearer <UPSTREAM_API_KEY>`
- `x-api-key`：上游请求头为 `x-api-key: <UPSTREAM_API_KEY>`

`REASONING_EFFORT` 可选，用于覆盖 Responses API 请求中的 `reasoning.effort`。
`REASONING_MODELS` 为空时对所有模型生效；不为空时只对列表里的模型生效。
如果 Cursor 已经传了 `reasoning`，需要设置 `REASONING_OVERRIDE=true` 才会覆盖。

默认地址：

- 服务地址：`http://localhost:8082`
- 接口地址：`http://localhost:8082/v1/chat/completions`

不启动 ngrok 的本地一键启动：

```bash
./start.sh
```

脚本会在后台启动 Bridge，并输出本地 dashboard 和日志路径。

如果你希望通过 ngrok 暴露本地 Bridge，使用：

```bash
./start-with-ngrok.sh
```

ngrok 自身日志会写到 `logs/ngrok-agent.log`。

停止：

```bash
./stop.sh
```

如果你使用 ngrok 方式启动，用下面的命令同时停止 Bridge 和 ngrok：

```bash
./stop-with-ngrok.sh
```

在 Cursor BYOK 里填写：

- Base URL: `http://your-server:8082/v1`
- API Key: 你的 `RELAY_API_KEY`

Health Check Path:

```text
/health/liveliness
```

## How it works

1. Cursor 把请求发到 `/v1/chat/completions`
2. 这个项目监听这个接口
3. 如果请求体看起来是 Responses API 风格，就转发到 `UPSTREAM_RESPONSES_API_URL`
4. 上游返回 Responses API 的结果后，这个项目再把响应转换成 Chat Completions 格式
5. 最终返回给 Cursor，让它继续按 Completions 的方式处理

流式响应也是同样的思路：接收 Responses 的 SSE 事件，再转换成 Chat Completions 的 chunk 格式返回。

## 说明

- 本项目部署时必须使用公网可访问地址，因为 Cursor BYOK 的请求链路是：用户请求 -> Cursor 服务器 -> 你设置的 Base URL 服务器 -> OpenAI 服务器
- 因此你配置给 Cursor 的 Base URL 必须能被公网访问
- 运行时必须有 `.env`

## 致谢

感谢 [gaoyu06/Cursor-BYOK-Bridge](https://github.com/gaoyu06/Cursor-BYOK-Bridge) 为本项目提供的灵感。

## License

Apache License 2.0. See `LICENSE`.
