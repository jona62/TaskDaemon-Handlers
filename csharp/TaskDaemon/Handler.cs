using System;
using System.Collections.Generic;
using System.Text.Json;

namespace TaskDaemon;

public record Task(string task_id, string task_type, Dictionary<string, object> task_data, int attempt);

public abstract record Result;
public record Success(object result) : Result;
public record Error(string error, bool retryable = false) : Result;

public static class Handler
{
    public static void Run(Func<Task, Result> handler)
    {
        string? line;
        while ((line = Console.ReadLine()) != null)
        {
            Result result;
            try
            {
                var task = JsonSerializer.Deserialize<Task>(line)!;
                result = handler(task);
            }
            catch (Exception e)
            {
                result = new Error(e.Message);
            }

            var response = result switch
            {
                Success s => new { status = "success", result = s.result },
                Error e => (object)new { status = "error", error = e.error, retryable = e.retryable },
                _ => throw new InvalidOperationException()
            };
            Console.WriteLine(JsonSerializer.Serialize(response));
            Console.Out.Flush();
        }
    }
}
