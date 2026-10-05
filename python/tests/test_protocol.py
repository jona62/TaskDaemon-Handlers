import json
import os
from pathlib import Path
import select
import subprocess
import sys
import unittest


class ProtocolTests(unittest.TestCase):
    def test_runner_flushes_each_response_and_keeps_processing_after_errors(self):
        code = """from taskdaemon import run, Task, Success, Error

def handle(task: Task):
    if task.task_type == 'retry':
        return Error('try again', retryable=True)
    if task.task_type == 'exception':
        raise ValueError('failed')
    return Success({'task_id': task.task_id, 'attempt': task.attempt})

run(handle)
"""
        environment = os.environ.copy()
        environment['PYTHONPATH'] = str(Path(__file__).resolve().parents[1])
        process = subprocess.Popen([sys.executable, '-c', code], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=environment)
        try:
            for number, task_type in enumerate(['echo', 'retry', 'exception', 'echo'], start=1):
                process.stdin.write(json.dumps({'task_id': str(number), 'task_type': task_type,
                                                'task_data': {}, 'attempt': number}) + '\n')
                process.stdin.flush()
                self.assertTrue(select.select([process.stdout], [], [], 3)[0], 'response was not flushed')
                response = json.loads(process.stdout.readline())
                if task_type == 'echo':
                    self.assertEqual(response, {'status': 'success', 'result': {'task_id': str(number), 'attempt': number}})
                elif task_type == 'retry':
                    self.assertEqual(response, {'status': 'error', 'error': 'try again', 'retryable': True})
                else:
                    self.assertEqual(response, {'status': 'error', 'error': 'failed', 'retryable': False})
            process.stdin.close()
            process.wait(timeout=3)
            self.assertEqual(process.returncode, 0)
            self.assertEqual(process.stderr.read(), '')
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            process.stdout.close()
            process.stderr.close()


if __name__ == '__main__':
    unittest.main()
