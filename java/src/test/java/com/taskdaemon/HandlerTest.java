package com.taskdaemon;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class HandlerTest {
    @Test
    void writesFlushedResponsesAndContinuesAfterHandlerFailure() throws Exception {
        String input = """
            {"task_id":"1","task_type":"echo","task_data":{},"attempt":1}
            {"task_id":"2","task_type":"retry","task_data":{},"attempt":2}
            {"task_id":"3","task_type":"exception","task_data":{},"attempt":3}
            {"task_id":"4","task_type":"echo","task_data":{},"attempt":4}
            """;
        FlushOutput output = new FlushOutput();
        InputStream originalInput = System.in;
        PrintStream originalOutput = System.out;
        try {
            System.setIn(new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8)));
            System.setOut(new PrintStream(output, false, StandardCharsets.UTF_8));
            Handler.run(task -> switch (task.task_type()) {
                case "retry" -> new Handler.Error("try again", true);
                case "exception" -> throw new IllegalArgumentException("failed");
                default -> new Handler.Success(Map.of("task_id", task.task_id(), "attempt", task.attempt()));
            });
        } finally {
            System.setIn(originalInput);
            System.setOut(originalOutput);
        }
        String[] lines = output.toString(StandardCharsets.UTF_8).lines().toArray(String[]::new);
        assertEquals(4, lines.length);
        assertTrue(output.flushCount >= 4);
        ObjectMapper mapper = new ObjectMapper();
        for (int index = 0; index < lines.length; index++) {
            var response = mapper.readTree(lines[index]);
            if (index == 0 || index == 3) {
                assertEquals("success", response.get("status").asText());
                assertEquals(Integer.toString(index + 1), response.get("result").get("task_id").asText());
                assertEquals(index + 1, response.get("result").get("attempt").asInt());
            } else {
                assertEquals("error", response.get("status").asText());
                assertEquals(index == 1, response.get("retryable").asBoolean());
                assertEquals(index == 1 ? "try again" : "failed", response.get("error").asText());
            }
        }
    }

    private static class FlushOutput extends ByteArrayOutputStream {
        int flushCount;
        @Override
        public void flush() {
            flushCount++;
        }
    }
}
