# TaskDaemon C# SDK

## Installation

```bash
dotnet add package TaskDaemon.Handler
```

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
COPY *.csproj .
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o out

FROM mcr.microsoft.com/dotnet/runtime:8.0
COPY --from=builder /app/out .
CMD ["dotnet", "handler.dll"]
```

<Note>
Run `dotnet add package TaskDaemon.Handler` to add the dependency to your .csproj before building.
</Note>
