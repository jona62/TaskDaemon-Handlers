use taskdaemon_handler::{error, run, success, Task};

fn main() {
    run(|task: Task| {
        if task.task_type == "retry" {
            error("try again", true)
        } else {
            success(serde_json::json!({ "task_id": task.task_id, "attempt": task.attempt }))
        }
    });
}
