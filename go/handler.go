package taskdaemon

import (
	"bufio"
	"encoding/json"
	"os"
)

type Task struct {
	TaskID   string                 `json:"task_id"`
	TaskType string                 `json:"task_type"`
	TaskData map[string]interface{} `json:"task_data"`
	Attempt  int                    `json:"attempt"`
}

type Result struct {
	Status    string      `json:"status"`
	Result    interface{} `json:"result,omitempty"`
	Error     string      `json:"error,omitempty"`
	Retryable bool        `json:"retryable,omitempty"`
}

func Success(result interface{}) Result {
	return Result{Status: "success", Result: result}
}

func Error(err string, retryable bool) Result {
	return Result{Status: "error", Error: err, Retryable: retryable}
}

type Handler func(Task) Result

func Run(handler Handler) {
	scanner := bufio.NewScanner(os.Stdin)
	encoder := json.NewEncoder(os.Stdout)

	for scanner.Scan() {
		var task Task
		if err := json.Unmarshal(scanner.Bytes(), &task); err != nil {
			encoder.Encode(Error(err.Error(), false))
			continue
		}
		result := handler(task)
		encoder.Encode(result)
	}
}
