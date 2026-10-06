# TaskDaemon Rust SDK

## Installation

Create a binary project with `cargo init --bin --name handler`, then add the published [crates.io package](https://crates.io/crates/taskdaemon-handler/0.1.2):

```toml
[dependencies]
taskdaemon-handler = "=0.1.2"
serde = { version = "1", features = ["derive"] }
```

For a source installation, replace the crate dependency with the immutable release tag:

```toml
[dependencies]
taskdaemon-handler = { git = "https://github.com/jona62/TaskDaemon-Handlers.git", tag = "v0.1.2" }
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

Save the example as `src/main.rs` and run `cargo build`. Commit the generated `Cargo.lock` with your handler project so deployments use the resolved dependency versions.

## Dockerfile

```dockerfile
FROM rust:1.91-alpine AS builder
RUN apk add --no-cache musl-dev
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release --locked

FROM alpine:latest
COPY --from=builder /app/target/release/handler /handler
CMD ["/handler"]
```

The example application package is named `handler`, matching the binary copied into the image. Build the application once before building the image so `Cargo.lock` is present.

## Protocol and execution

The runner reads JSON request lines from stdin and writes one flushed JSON response line per task. Keep application logs on stderr. Successful responses use `status: "success"` and `result`; failures use `status: "error"`, `error`, and optional `retryable` (default: false). Retries require `retryable: true` and remaining retry budget. A handler request uses `attempt = stored attempts + 1`, initially `1`. The daemon's stored counter increments on retry scheduling or a Failed marking and is unchanged by success. Recovery can repeat the same request attempt.

Set timeouts in the daemon's handler configuration. Omitting `timeout` inherits `DAEMON_TASK_TIMEOUT`, which defaults to 30 seconds.
