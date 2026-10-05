# TaskDaemon Java SDK

## Installation

This artifact is not published on Maven Central. Install the SDK into your local Maven repository first:

```bash
git clone https://github.com/jona62/TaskDaemon-Handlers.git vendor/TaskDaemon-Handlers
mvn -f vendor/TaskDaemon-Handlers/java/pom.xml install
```

Then add this dependency to your application's `pom.xml`:
```xml
<dependency>
    <groupId>com.taskdaemon</groupId>
    <artifactId>handler</artifactId>
    <version>0.1.0</version>
</dependency>
```

## Usage

```java
import com.taskdaemon.Handler;
import com.taskdaemon.Handler.Success;
import java.util.Map;

public class MyHandler {
    public static void main(String[] args) throws Exception {
        Handler.run(task -> {
            String msg = (String) task.task_data().getOrDefault("message", "");
            return new Success(Map.of("upper", msg.toUpperCase()));
        });
    }
}
```

## Dockerfile

```dockerfile
FROM maven:3.9-eclipse-temurin-17 AS builder
COPY vendor/TaskDaemon-Handlers/java /opt/taskdaemon-java
RUN mvn -f /opt/taskdaemon-java/pom.xml install -q -DskipTests
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn package -q dependency:copy-dependencies -DincludeScope=runtime

FROM eclipse-temurin:17-jre-alpine
COPY --from=builder /app/target/classes /app/classes
COPY --from=builder /app/target/dependency /app/lib
CMD ["java", "-cp", "/app/classes:/app/lib/*", "MyHandler"]
```

<Note>
Keep the SDK source under `vendor/TaskDaemon-Handlers/java` in the Docker build context. The builder installs it locally before compiling `MyHandler`.
</Note>

## Protocol and execution

The runner reads JSON request lines from stdin and writes one flushed JSON response line per task. Keep application logs on stderr. Successful responses use `status: "success"` and `result`; failures use `status: "error"`, `error`, and optional `retryable` (default: false). Retries require `retryable: true` and remaining retry budget. `attempt` starts at `1` and increases on retries.

Set timeouts in the daemon's handler configuration. Omitting `timeout` inherits `DAEMON_TASK_TIMEOUT`, which defaults to 30 seconds.
