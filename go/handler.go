package taskdaemon

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
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
	if err := run(os.Stdin, os.Stdout, handler); err != nil {
		fmt.Fprintln(os.Stderr, "TaskDaemon handler:", err)
	}
}

func run(input io.Reader, output io.Writer, handler Handler) error {
	reader := bufio.NewReader(input)
	encoder := json.NewEncoder(output)

	for {
		// Scanner's default 64 KiB token limit rejects valid daemon requests.
		line, readErr := reader.ReadBytes('\n')
		if len(line) > 0 {
			var task Task
			var result Result
			if err := json.Unmarshal(line, &task); err != nil {
				result = Error(err.Error(), false)
			} else {
				result = handler(task)
			}
			if err := encoder.Encode(result); err != nil {
				return err
			}
		}
		if readErr == io.EOF {
			return nil
		}
		if readErr != nil {
			return readErr
		}
	}
}
