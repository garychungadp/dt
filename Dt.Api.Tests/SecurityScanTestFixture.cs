// INTENTIONALLY VULNERABLE TEST FIXTURE.
// This file exists only to verify that CodeQL detects command injection.
// Remove it immediately after confirming the alert in GitHub.
using System.Diagnostics;

namespace Dt.Api.Tests;

public static class SecurityScanTestFixture
{
    public static void RunUntrustedCommand(string userInput)
    {
        // Deliberately unsafe: user-controlled input reaches a shell.
        Process.Start("/bin/sh", $"-c \"{userInput}\"");
    }
}
