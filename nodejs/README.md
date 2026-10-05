# TaskDaemon Node.js SDK

## Installation

```bash
git clone https://github.com/jona62/TaskDaemon-Handlers.git vendor/TaskDaemon-Handlers
npm install --prefix vendor/TaskDaemon-Handlers/nodejs
npm pack ./vendor/TaskDaemon-Handlers/nodejs --pack-destination ./vendor
npm install ./vendor/taskdaemon-handler-0.1.0.tgz
```

The npm package is not published. The local tarball retains the `@taskdaemon/handler` package name, so imports stay the same.

## Usage

```typescript
import { run, success, error, Task } from '@taskdaemon/handler';

run((task: Task) => {
  const message = task.task_data.message as string || '';
  return success({ reversed: message.split('').reverse().join('') });
});
```

## JavaScript

For the Dockerfile below, save this CommonJS handler as `handler.cjs`:

```javascript
const { run, success } = require('@taskdaemon/handler');

run(task => success({ echoed: task.task_data }));
```

## Dockerfile

```dockerfile
FROM node:20-slim
WORKDIR /app
COPY vendor/taskdaemon-handler-0.1.0.tgz ./vendor/
RUN npm install --omit=dev ./vendor/taskdaemon-handler-0.1.0.tgz
COPY handler.cjs .
CMD ["node", "handler.cjs"]
```

## Protocol and execution

The runner reads JSON request lines from stdin and writes one flushed JSON response line per task. Keep application logs on stderr. Successful responses use `status: "success"` and `result`; failures use `status: "error"`, `error`, and optional `retryable` (default: false). Retries require `retryable: true` and remaining retry budget. `attempt` starts at `1` and increases on retries.

Set timeouts in the daemon's handler configuration. Omitting `timeout` inherits `DAEMON_TASK_TIMEOUT`, which defaults to 30 seconds.
