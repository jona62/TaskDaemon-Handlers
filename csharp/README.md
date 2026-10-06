# TaskDaemon C# SDK

## Installation

```bash
dotnet new console --name handler --framework net8.0 --output handler
dotnet add handler/handler.csproj package TaskDaemon.Handler --version 0.1.2
```

[`TaskDaemon.Handler` 0.1.2](https://www.nuget.org/packages/TaskDaemon.Handler/0.1.2) is available on NuGet. It targets .NET 8. Save the example as `handler/Program.cs`.

## Usage

```csharp
using TaskDaemon;

Handler.Run(task => {
    var msg = task.task_data.GetValueOrDefault("message")?.ToString() ?? "";
    return new Success(new { upper = msg.ToUpper() });
});
```

## Dockerfile

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS builder
WORKDIR /app
COPY handler ./handler
RUN dotnet publish handler/handler.csproj -c Release -o out

FROM mcr.microsoft.com/dotnet/runtime:8.0
WORKDIR /app
COPY --from=builder /app/out ./
CMD ["dotnet", "handler.dll"]
```

Build from the directory containing `handler/`.

## Source installation

To use the release source instead, replace the NuGet package reference with a project reference:

```bash
git clone --branch v0.1.2 --depth 1 https://github.com/jona62/TaskDaemon-Handlers.git vendor/TaskDaemon-Handlers
dotnet remove handler/handler.csproj package TaskDaemon.Handler
dotnet add handler/handler.csproj reference vendor/TaskDaemon-Handlers/csharp/TaskDaemon/TaskDaemon.Handler.csproj
```

For this source installation, add the following line to the Docker builder stage before `dotnet publish`, and build from the directory containing both `handler/` and `vendor/`:

```dockerfile
COPY vendor/TaskDaemon-Handlers/csharp/TaskDaemon ./vendor/TaskDaemon-Handlers/csharp/TaskDaemon
```

## Package verification and publication

```bash
dotnet run --project csharp/tests/ProtocolSmoke/ProtocolSmoke.csproj --configuration Release
dotnet pack csharp/TaskDaemon/TaskDaemon.Handler.csproj --configuration Release --output csharp/TaskDaemon/bin/packages
python3 csharp/tests/check_package.py csharp/TaskDaemon/bin/packages/TaskDaemon.Handler.0.1.2.nupkg
```

The package includes the .NET 8 library, MIT license metadata and notice, repository information and a package README. The Python artifact check restores the local package into a temporary consumer with an isolated package cache and runs the protocol smoke test against the installed package. Publishing requires a NuGet.org account and an API key scoped to push new packages and versions for `TaskDaemon.Handler`, or an account-configured trusted publisher. Ownership is established by the publishing account. Keep credentials outside the repository; see Microsoft's [NuGet publishing instructions](https://learn.microsoft.com/en-us/nuget/nuget-org/publish-a-package).

## Protocol and execution

The runner reads JSON request lines from stdin and writes one flushed JSON response line per task. Keep application logs on stderr. Successful responses use `status: "success"` and `result`; failures use `status: "error"`, `error`, and optional `retryable` (default: false). Retries require `retryable: true` and remaining retry budget. `attempt` starts at `1` and increases on retries.

Set timeouts in the daemon's handler configuration. Omitting `timeout` inherits `DAEMON_TASK_TIMEOUT`, which defaults to 30 seconds.
