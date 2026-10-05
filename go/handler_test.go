package taskdaemon

import (
	"bytes"
	"encoding/json"
	"io"
	"strings"
	"testing"
)

func TestRunProcessesLargeRequestAndKeepsResponseOrder(t *testing.T) {
	first := Task{TaskID: "first", TaskType: "echo", TaskData: map[string]interface{}{"message": strings.Repeat("x", 128*1024)}, Attempt: 1}
	second := Task{TaskID: "second", TaskType: "echo", TaskData: map[string]interface{}{}, Attempt: 2}
	var input, output bytes.Buffer
	encoder := json.NewEncoder(&input)
	if err := encoder.Encode(first); err != nil {
		t.Fatal(err)
	}
	if err := encoder.Encode(second); err != nil {
		t.Fatal(err)
	}
	err := run(&input, &output, func(task Task) Result {
		return Success(map[string]interface{}{"task_id": task.TaskID, "attempt": task.Attempt})
	})
	if err != nil {
		t.Fatal(err)
	}
	decoder := json.NewDecoder(&output)
	for index, id := range []string{"first", "second"} {
		var response struct {
			Status string
			Result struct {
				TaskID  string `json:"task_id"`
				Attempt int
			}
		}
		if err := decoder.Decode(&response); err != nil {
			t.Fatal(err)
		}
		if response.Status != "success" || response.Result.TaskID != id || response.Result.Attempt != index+1 {
			t.Fatalf("unexpected response: %+v", response)
		}
	}
	var extra Result
	if err := decoder.Decode(&extra); err != io.EOF {
		t.Fatalf("expected exactly two response lines, got %+v (%v)", extra, err)
	}
}

func TestRunReturnsErrorForMalformedLineThenContinues(t *testing.T) {
	var output bytes.Buffer
	input := strings.NewReader("broken\n{\"task_id\":\"next\",\"task_type\":\"echo\",\"task_data\":{},\"attempt\":1}\n")
	if err := run(input, &output, func(task Task) Result { return Error("try again", true) }); err != nil {
		t.Fatal(err)
	}
	decoder := json.NewDecoder(&output)
	var first, second Result
	if err := decoder.Decode(&first); err != nil {
		t.Fatal(err)
	}
	if err := decoder.Decode(&second); err != nil {
		t.Fatal(err)
	}
	if first.Status != "error" || first.Retryable {
		t.Fatalf("unexpected malformed-line response: %+v", first)
	}
	if second.Status != "error" || !second.Retryable {
		t.Fatalf("unexpected retry response: %+v", second)
	}
}
