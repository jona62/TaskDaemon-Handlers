package com.taskdaemon;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

/** Runs persistent TaskDaemon handlers over line-delimited JSON stdin/stdout. */
public class Handler {
    private static final ObjectMapper mapper = new ObjectMapper();

    /**
     * A task received from the daemon.
     * @param task_id task UUID
     * @param task_type registered handler type
     * @param task_data application request data
     * @param attempt one-based execution attempt
     */
    public record Task(String task_id, String task_type, Map<String, Object> task_data, int attempt) {}

    /** A success or error response sent to the daemon. */
    public sealed interface Result permits Success, Error {}
    /** @param result JSON-serializable application result */
    public record Success(Object result) implements Result {}
    /**
     * @param error error message
     * @param retryable whether another attempt may be scheduled within the retry budget
     */
    public record Error(String error, boolean retryable) implements Result {}

    /**
     * Handles requests until stdin closes, flushing a JSON response for each request.
     * Application logs should use stderr. Callback exceptions produce non-retryable errors.
     * @param handler synchronous task callback
     * @throws Exception if reading requests or serializing a response fails
     */
    public static void run(Function<Task, Result> handler) throws Exception {
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        String line;

        while ((line = reader.readLine()) != null) {
            Result result;
            try {
                Task task = mapper.readValue(line, Task.class);
                result = handler.apply(task);
            } catch (Exception e) {
                result = new Error(e.getMessage(), false);
            }

            Map<String, Object> response = new HashMap<>();
            if (result instanceof Success s) {
                response.put("status", "success");
                response.put("result", s.result());
            } else if (result instanceof Error e) {
                response.put("status", "error");
                response.put("error", e.error());
                response.put("retryable", e.retryable());
            }
            System.out.println(mapper.writeValueAsString(response));
            System.out.flush();
        }
    }
}
