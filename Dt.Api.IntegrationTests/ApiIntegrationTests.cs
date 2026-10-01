using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Mvc.Testing;

namespace Dt.Api.IntegrationTests;

public class ApiIntegrationTests : IClassFixture<WebApplicationFactory<global::Program>>
{
    private readonly HttpClient client;

    public ApiIntegrationTests(WebApplicationFactory<global::Program> factory)
    {
        client = factory.CreateClient();
    }

    [Fact]
    public async Task WeatherForecast_ReturnsFiveForecasts()
    {
        var response = await client.GetAsync("/weatherforecast");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var forecasts = await response.Content.ReadFromJsonAsync<WeatherForecast[]>();
        Assert.NotNull(forecasts);
        Assert.Equal(5, forecasts!.Length);
    }
}

public record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary);
