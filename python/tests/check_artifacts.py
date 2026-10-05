"""Install wheel/sdist archives in isolation and verify the handler protocol."""

import argparse
import json
from pathlib import Path
import select
import subprocess
import sys
import tempfile
import venv


HANDLER = """from taskdaemon import run, Task, Success, Error

def handle(task: Task):
    if task.task_type == 'retry':
        return Error('try again', retryable=True)
    if task.task_type == 'exception':
        raise ValueError('failed')
    return Success({'task_id': task.task_id, 'attempt': task.attempt})

run(handle)
"""


def check_archive(archive, version):
    archive = archive.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="taskdaemon-python-artifact-") as temp:
        directory = Path(temp)
        environment = directory / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        interpreter = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        subprocess.run([
            str(interpreter), "-m", "pip", "install", "--disable-pip-version-check",
            "--index-url", "https://pypi.org/simple", "--no-deps", str(archive),
        ], cwd=directory, check=True)
        installed_check = (
            "import importlib.metadata as md, pathlib, taskdaemon; "
            f"assert md.version('taskdaemon') == {version!r}; "
            f"assert pathlib.Path(taskdaemon.__file__).resolve().is_relative_to(pathlib.Path({str(environment)!r}).resolve())"
        )
        subprocess.run([str(interpreter), "-I", "-c", installed_check], cwd=directory, check=True)
        # Keep stdin open and leave Python buffering enabled to test SDK flushing.
        process = subprocess.Popen(
            [str(interpreter), "-I", "-c", HANDLER], cwd=directory,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            for attempt, kind in enumerate(["echo", "retry", "exception", "echo"], start=1):
                process.stdin.write(json.dumps({
                    "task_id": str(attempt), "task_type": kind,
                    "task_data": {}, "attempt": attempt,
                }) + "\n")
                process.stdin.flush()
                assert select.select([process.stdout], [], [], 3)[0], "response was not flushed"
                response = json.loads(process.stdout.readline())
                if kind == "echo":
                    expected = {"status": "success", "result": {"task_id": str(attempt), "attempt": attempt}}
                elif kind == "retry":
                    expected = {"status": "error", "error": "try again", "retryable": True}
                else:
                    expected = {"status": "error", "error": "failed", "retryable": False}
                assert response == expected, response
            process.stdin.close()
            assert process.wait(timeout=3) == 0
            assert process.stderr.read() == ""
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            if not process.stdin.closed:
                process.stdin.close()
            process.stdout.close()
            process.stderr.close()
        print(f"{archive.name}: isolated install and interactive protocol passed", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("archives", type=Path, nargs="+")
    args = parser.parse_args()
    for archive in args.archives:
        check_archive(archive, args.version)


if __name__ == "__main__":
    main()
