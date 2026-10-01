namespace Dt.Api.Tests;

public class WeatherForecastTests
{
    [Fact]
    public void TemperatureF_IsCalculatedFromTemperatureC()
    {
        var forecast = new global::WeatherForecast(DateOnly.FromDateTime(DateTime.UtcNow), 0, "Cold");

        Assert.Equal(32, forecast.TemperatureF);
    }
}
