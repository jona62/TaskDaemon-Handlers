# TaskDaemon Node.js SDK

## Installation

```bash
npm install @taskdaemon/handler
```

## Usage

```typescript
import { run, success, error, Task } from '@taskdaemon/handler';

run((task: Task) => {
  const message = task.task_data.message as string || '';
  return success({ reversed: message.split('').reverse().join('') });
});
```

## Dockerfile

```dockerfile
FROM node:20-slim
WORKDIR /app
RUN npm install @taskdaemon/handler
COPY handler.js .
CMD ["node", "handler.js"]
```
