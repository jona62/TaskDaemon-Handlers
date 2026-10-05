# TaskDaemon Java SDK

## Installation

The Maven Central coordinates are `io.github.jona62:handler:0.1.2`. Until registry publication is verified, install the SDK into your local Maven repository:

```bash
git clone https://github.com/jona62/TaskDaemon-Handlers.git vendor/TaskDaemon-Handlers
mvn -f vendor/TaskDaemon-Handlers/java/pom.xml install
```

Then add this dependency to your application's `pom.xml`:
```xml
<dependency>
    <groupId>io.github.jona62</groupId>
    <artifactId>handler</artifactId>
    <version>0.1.2</version>
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

## Package verification and publication

`mvn -B -f java/pom.xml clean verify` runs the protocol regression test and creates the binary, sources and Javadoc JARs under `java/target/`.

The `central` Maven profile signs these artifacts and configures the current Sonatype Central Portal publisher. Publishing requires a verified `io.github.jona62` namespace, a Portal token pair in `CENTRAL_USERNAME` and `CENTRAL_PASSWORD`, and an exported signing key in `MAVEN_GPG_KEY`. The `java/central-settings.xml` file references the token environment variables without storing their values. A protected key also requires `MAVEN_GPG_PASSPHRASE`; `MAVEN_GPG_KEY_FINGERPRINT` selects a key from a multi-key export. The signing public key must be available to Central. The Java package and imports remain `com.taskdaemon`.

After those prerequisites are configured, the release command is:

```bash
mvn -B -s java/central-settings.xml -f java/pom.xml -Pcentral -Dcentral.autoPublish=true -DwaitUntil=published deploy
```

Keep credentials outside the repository. See the official [Central requirements](https://central.sonatype.org/publish/requirements/), [Portal authentication](https://central.sonatype.org/publish/generate-portal-token/) and [Maven publisher](https://central.sonatype.org/publish/publish-portal-maven/) instructions.

## Protocol and execution

The runner reads JSON request lines from stdin and writes one flushed JSON response line per task. Keep application logs on stderr. Successful responses use `status: "success"` and `result`; failures use `status: "error"`, `error`, and optional `retryable` (default: false). Retries require `retryable: true` and remaining retry budget. `attempt` starts at `1` and increases on retries.

Set timeouts in the daemon's handler configuration. Omitting `timeout` inherits `DAEMON_TASK_TIMEOUT`, which defaults to 30 seconds.
