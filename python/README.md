# TaskDaemon Python SDK

## Installation

```bash
python3 -m pip install taskdaemon==0.1.2
```

## Usage

```python
from taskdaemon import run, Task, Success, Error

def handler(task: Task) -> Success:
    message = task.task_data.get("message", "")
    return Success({"echoed": message})

run(handler)
```

## Dockerfile

```dockerfile
FROM python:3.11-slim
RUN pip install --no-cache-dir taskdaemon==0.1.2
COPY handler.py /handler.py
CMD ["python", "-u", "/handler.py"]
```

## Protocol and execution

The runner reads JSON request lines from stdin and writes one flushed JSON response line per task. Keep application logs on stderr. Successful responses use `status: "success"` and `result`; failures use `status: "error"`, `error`, and optional `retryable` (default: false). Retries require `retryable: true` and remaining retry budget. `attempt` starts at `1` and increases on retries.

Set timeouts in the daemon's handler configuration. Omitting `timeout` inherits `DAEMON_TASK_TIMEOUT`, which defaults to 30 seconds.

## Distribution checks

From this directory, with `build` and `twine` installed in your development environment:

```bash
python3 -m build --outdir dist/0.1.2
python3 -m twine check --strict dist/0.1.2/*
python3 tests/check_artifacts.py --version 0.1.2 dist/0.1.2/*
```

The artifact checker installs the wheel and source archive in separate temporary environments and verifies imports, flushed responses, errors, and retry metadata.
