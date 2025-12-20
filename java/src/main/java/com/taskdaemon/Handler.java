package com.taskdaemon;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

public class Handler {
    private static final ObjectMapper mapper = new ObjectMapper();

    public record Task(String task_id, String task_type, Map<String, Object> task_data, int attempt) {}

    public sealed interface Result permits Success, Error {}
    public record Success(Object result) implements Result {}
    public record Error(String error, boolean retryable) implements Result {}

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
