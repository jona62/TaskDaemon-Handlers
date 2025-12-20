# TaskDaemon Go SDK

## Installation

```bash
go get github.com/taskdaemon/handler-go
```

## Usage

```go
package main

import (
    "strings"
    taskdaemon "github.com/taskdaemon/handler-go"
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
COPY . .
RUN go build -o handler .

FROM alpine:latest
COPY --from=builder /app/handler /handler
CMD ["/handler"]
```
