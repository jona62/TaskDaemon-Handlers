# TaskDaemon Rust SDK

## Installation

This crate is not published on crates.io. Clone the source into your handler project:

```bash
git clone https://github.com/jona62/TaskDaemon-Handlers.git vendor/TaskDaemon-Handlers
```

```toml
[dependencies]
taskdaemon-handler = { path = "vendor/TaskDaemon-Handlers/rust" }
serde = { version = "1", features = ["derive"] }
```

## Usage

```rust
use taskdaemon_handler::{run, success, Task};
use serde::Serialize;

#[derive(Serialize)]
struct Output { upper: String }

fn main() {
    run(|task: Task| {
        let msg = task.task_data["message"].as_str().unwrap_or("");
        success(Output { upper: msg.to_uppercase() })
    });
}
```

## Dockerfile

```dockerfile
FROM rust:1.91-alpine AS builder
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
COPY vendor/TaskDaemon-Handlers/rust ./vendor/TaskDaemon-Handlers/rust
RUN cargo build --release

FROM alpine:latest
COPY --from=builder /app/target/release/handler /handler
CMD ["/handler"]
```

<Note>
Use the source path dependency above and name the example application package `handler` so its binary matches the Dockerfile.
</Note>

## Protocol and execution

The runner reads JSON request lines from stdin and writes one flushed JSON response line per task. Keep application logs on stderr. Successful responses use `status: "success"` and `result`; failures use `status: "error"`, `error`, and optional `retryable` (default: false). Retries require `retryable: true` and remaining retry budget. `attempt` starts at `1` and increases on retries.

Set timeouts in the daemon's handler configuration. Omitting `timeout` inherits `DAEMON_TASK_TIMEOUT`, which defaults to 30 seconds.
