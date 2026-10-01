var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

var summaries = new[]
{
    "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
};

app.MapGet("/weatherforecast", () =>
{
    var forecast =  Enumerable.Range(1, 5).Select(index =>
        new WeatherForecast
        (
            DateOnly.FromDateTime(DateTime.Now.AddDays(index)),
            Random.Shared.Next(-20, 55),
            summaries[Random.Shared.Next(summaries.Length)]
        ))
        .ToArray();
    return forecast;
})
.WithName("GetWeatherForecast")
.WithOpenApi();

// INTENTIONALLY VULNERABLE SECURITY-SCAN DEMO. Remove after confirming CodeQL.
// 1. CodeQL cs/command-line-injection (CWE-78): 使用 HttpContext.Request 確保污點分析 (Taint Tracking) 正確追蹤
app.MapGet("/security-scan-demo", (HttpContext context) =>
{
    var command = context.Request.Query["command"].ToString();
    var process = System.Diagnostics.Process.Start("/bin/sh", $"-c \"{command}\"");
    return Results.Ok(process?.Id);
});

// 2. CodeQL cs/path-injection (CWE-22): 外部路徑周遊弱點
app.MapGet("/security-scan-path-demo", (HttpContext context) =>
{
    var path = context.Request.Query["path"].ToString();
    var fullPath = Path.Combine("/app/data", path);
    return Results.Text(File.ReadAllText(fullPath));
});

// 3. CodeQL cs/weak-crypto (CWE-327 / CWE-328): 不安全的弱雜湊演算法
app.MapGet("/security-scan-crypto-demo", (HttpContext context) =>
{
    var input = context.Request.Query["input"].ToString();
    using var md5 = System.Security.Cryptography.MD5.Create();
    var hash = md5.ComputeHash(System.Text.Encoding.UTF8.GetBytes(input));
    return Results.Ok(Convert.ToHexString(hash));
});

app.Run();

public partial class Program
{
    // 4. Gitleaks / Secret Scanning 測試金鑰 (符合 AWS Access Key 標準特徵格式)
    public const string DemoAwsAccessKey = "AKIAIOSFODNN7EXAMPLE";
}

public record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);
}
