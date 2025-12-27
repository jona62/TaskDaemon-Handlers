# TaskDaemon Java SDK

## Installation

Maven:
```xml
<dependency>
    <groupId>com.taskdaemon</groupId>
    <artifactId>handler</artifactId>
    <version>0.1.0</version>
</dependency>
```

## Usage

```java
import com.taskdaemon.Handler.*;
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
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn package -q

FROM eclipse-temurin:17-jre-alpine
COPY --from=builder /app/target/handler.jar /handler.jar
CMD ["java", "-jar", "/handler.jar"]
```

<Note>
Add the taskdaemon handler dependency to your pom.xml before building.
</Note>
