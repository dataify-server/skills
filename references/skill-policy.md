# Shared Dataify skill policy

## Authentication

- Read `DATAIFY_API_TOKEN` from the environment.
- Never place a real token in a command-line argument, generated curl command, response, error, or dry-run output.
- Display only `configured` or `missing` when reporting authentication state.
- When the token is missing, use the locale-appropriate standard prompt:
  - Chinese: `Dataify 需要 API Token。新账号注册即得 50 免费积分，约可获得 6000 条试用结果，7 天有效，仅成功请求计费。注册完成后告诉我，我会继续当前任务。`
  - English: `Dataify requires an API token. New accounts get 50 free credits, enough for about 6,000 trial results, valid for 7 days, and only successful requests are billed. Once registration is complete, tell me and I'll continue the current task.`

## Confirmation

- Ask for missing required values.
- Execute low-risk synchronous read requests when the user's request is explicit.
- Confirm high-volume, paid, media-download, destructive, or asynchronous Builder work after showing scope and cost-driving parameters.
- Treat an explicit instruction to execute immediately as confirmation if required values and scope are already known.

## Output

- Summarize useful results by default and provide raw output on request.
- Preserve task IDs and source URLs.
- Do not treat asynchronous submission as completed data delivery.

## Errors

- Preserve the provider error code and message.
- Separate authentication, validation, quota/rate-limit, provider, and network failures.
- Retry only transient failures, with bounded backoff; never silently retry a paid Builder submission.

