# TaskDaemon Rust SDK

## Installation

```toml
[dependencies]
taskdaemon-handler = "0.1"
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
FROM rust:1.75-alpine AS builder
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

FROM alpine:latest
COPY --from=builder /app/target/release/handler /handler
CMD ["/handler"]
```

<Note>
Add `taskdaemon-handler = "0.1"` to your Cargo.toml dependencies before building.
</Note>
