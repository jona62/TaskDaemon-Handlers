# TaskDaemon Handler SDK for C#

Build persistent TaskDaemon handlers with .NET 8. The SDK reads task requests from stdin and writes one flushed JSON response to stdout for each request.

```csharp
using TaskDaemon;

Handler.Run(task => new Success(new {
    echoed = task.task_data,
    task_id = task.task_id,
    attempt = task.attempt
}));
```

Return `new Error("message", true)` when an error may be retried. The daemon's retry budget controls whether another attempt is scheduled. Other errors use `new Error("message")`. The callback can handle multiple tasks during the lifetime of the process.

`task.attempt` starts at 1 and increases on retries. Keep application logs on stderr; stdout carries protocol responses. Execution timeouts belong to the daemon configuration. An omitted handler timeout inherits `DAEMON_TASK_TIMEOUT`, whose default is 30 seconds.

Source and examples: [TaskDaemon-Handlers](https://github.com/jona62/TaskDaemon-Handlers).
