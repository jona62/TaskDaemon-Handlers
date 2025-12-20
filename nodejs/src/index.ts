import * as readline from 'readline';

export interface Task {
  task_id: string;
  task_type: string;
  task_data: Record<string, unknown>;
  attempt: number;
}

export type Result =
  | { status: 'success'; result: unknown }
  | { status: 'error'; error: string; retryable: boolean };

export type Handler = (task: Task) => Result | Promise<Result>;

export function run(handler: Handler): void {
  const rl = readline.createInterface({ input: process.stdin });

  rl.on('line', async (line) => {
    const task: Task = JSON.parse(line);
    try {
      const result = await handler(task);
      console.log(JSON.stringify(result));
    } catch (e) {
      console.log(JSON.stringify({
        status: 'error',
        error: String(e),
        retryable: false,
      }));
    }
  });
}

export const success = (result: unknown): Result => ({ status: 'success', result });
export const error = (msg: string, retryable = false): Result => ({ status: 'error', error: msg, retryable });
