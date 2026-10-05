use serde::{Deserialize, Serialize};
use std::io::{self, BufRead, Write};

#[derive(Deserialize)]
pub struct Task {
    pub task_id: String,
    pub task_type: String,
    pub task_data: serde_json::Value,
    pub attempt: u32,
}

#[derive(Serialize)]
#[serde(tag = "status", rename_all = "lowercase")]
pub enum Result<T: Serialize> {
    Success { result: T },
    Error { error: String, retryable: bool },
}

pub fn success<T: Serialize>(result: T) -> Result<T> {
    Result::Success { result }
}

pub fn error<T: Serialize>(msg: impl Into<String>, retryable: bool) -> Result<T> {
    Result::Error {
        error: msg.into(),
        retryable,
    }
}

pub fn run<T, F>(handler: F)
where
    T: Serialize,
    F: Fn(Task) -> Result<T>,
{
    let stdin = io::stdin();
    let mut stdout = io::stdout();

    for line in stdin.lock().lines().flatten() {
        let result = match serde_json::from_str::<Task>(&line) {
            Ok(task) => handler(task),
            Err(e) => error(e.to_string(), false),
        };
        serde_json::to_writer(&mut stdout, &result).ok();
        writeln!(stdout).ok();
        stdout.flush().ok();
    }
}
