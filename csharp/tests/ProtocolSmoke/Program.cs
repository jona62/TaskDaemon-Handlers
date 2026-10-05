using System.Text.Json;
using TaskDaemon;

var input = """
{"task_id":"1","task_type":"echo","task_data":{},"attempt":1}
{"task_id":"2","task_type":"retry","task_data":{},"attempt":2}
{"task_id":"3","task_type":"exception","task_data":{},"attempt":3}
{"task_id":"4","task_type":"echo","task_data":{},"attempt":4}
""";
var output = new FlushWriter();
var originalInput = Console.In;
var originalOutput = Console.Out;
try
{
    Console.SetIn(new StringReader(input));
    Console.SetOut(output);
    Handler.Run(task => task.task_type switch
    {
        "retry" => new TaskDaemon.Error("try again", true),
        "exception" => throw new InvalidOperationException("failed"),
        _ => new Success(new { task_id = task.task_id, attempt = task.attempt })
    });
}
finally
{
    Console.SetIn(originalInput);
    Console.SetOut(originalOutput);
}

var lines = output.ToString().Split('\n', StringSplitOptions.RemoveEmptyEntries);
if (lines.Length != 4 || output.FlushCount < 4)
    throw new InvalidOperationException("Expected four flushed JSON response lines");
for (var index = 0; index < lines.Length; index++)
{
    using var document = JsonDocument.Parse(lines[index]);
    var response = document.RootElement;
    if (index == 0 || index == 3)
    {
        if (response.GetProperty("status").GetString() != "success"
            || response.GetProperty("result").GetProperty("task_id").GetString() != (index + 1).ToString()
            || response.GetProperty("result").GetProperty("attempt").GetInt32() != index + 1)
            throw new InvalidOperationException("Success response did not preserve task identity/attempt");
    }
    else if (response.GetProperty("status").GetString() != "error"
             || response.GetProperty("retryable").GetBoolean() != (index == 1)
             || response.GetProperty("error").GetString() != (index == 1 ? "try again" : "failed"))
    {
        throw new InvalidOperationException("Unexpected error/retryable response");
    }
}
Console.WriteLine("C# stdio protocol smoke passed");

sealed class FlushWriter : StringWriter
{
    public int FlushCount { get; private set; }
    public override void Flush()
    {
        FlushCount++;
        base.Flush();
    }
}
