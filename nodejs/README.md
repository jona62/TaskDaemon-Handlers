# TaskDaemon Node.js SDK

## Installation

```bash
npm install --save-exact @taskdaemon/handler@0.1.2
```

For a local source build from the same release:

```bash
git clone --branch v0.1.2 --depth 1 https://github.com/jona62/TaskDaemon-Handlers.git vendor/TaskDaemon-Handlers
npm ci --prefix vendor/TaskDaemon-Handlers/nodejs
npm pack ./vendor/TaskDaemon-Handlers/nodejs --pack-destination ./vendor
npm install ./vendor/taskdaemon-handler-0.1.2.tgz
```

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
RUN npm install --omit=dev @taskdaemon/handler@0.1.2
COPY handler.cjs .
CMD ["node", "handler.cjs"]
```

## Protocol and execution

The runner reads JSON request lines from stdin and writes one flushed JSON response line per task. Keep application logs on stderr. Successful responses use `status: "success"` and `result`; failures use `status: "error"`, `error`, and optional `retryable` (default: false). Retries require `retryable: true` and remaining retry budget. `attempt` starts at `1` and increases on retries.

Set timeouts in the daemon's handler configuration. Omitting `timeout` inherits `DAEMON_TASK_TIMEOUT`, which defaults to 30 seconds.

## Distribution checks

From this directory:

```bash
npm ci
npm test
mkdir -p artifacts
npm pack --pack-destination artifacts
node scripts/check-artifact.cjs artifacts/taskdaemon-handler-0.1.2.tgz
```

The artifact checker installs the tarball in a temporary consumer project and verifies the protocol, CommonJS and ESM imports, and TypeScript declarations.
