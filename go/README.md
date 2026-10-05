# TaskDaemon Go SDK

## Installation

```bash
go get github.com/jona62/TaskDaemon-Handlers/go@v0.1.2
```

## Usage

```go
package main

import (
    "strings"
    taskdaemon "github.com/jona62/TaskDaemon-Handlers/go"
)

func main() {
    taskdaemon.Run(func(task taskdaemon.Task) taskdaemon.Result {
        msg, _ := task.TaskData["message"].(string)
        return taskdaemon.Success(map[string]string{"upper": strings.ToUpper(msg)})
    })
}
```

## Dockerfile

```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o handler .

FROM alpine:latest
COPY --from=builder /app/handler /handler
CMD ["/handler"]
```

<Note>
Run `go mod init myhandler && go get github.com/jona62/TaskDaemon-Handlers/go@v0.1.2` to create go.mod/go.sum before building.
</Note>

## Protocol and execution

The runner reads JSON request lines from stdin and writes one flushed JSON response line per task. Keep application logs on stderr. Successful responses use `status: "success"` and `result`; failures use `status: "error"`, `error`, and optional `retryable` (default: false). Retries require `retryable: true` and remaining retry budget. `attempt` starts at `1` and increases on retries.

Set timeouts in the daemon's handler configuration. Omitting `timeout` inherits `DAEMON_TASK_TIMEOUT`, which defaults to 30 seconds.
