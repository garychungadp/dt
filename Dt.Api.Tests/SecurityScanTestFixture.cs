// INTENTIONALLY VULNERABLE TEST FIXTURE.
// This file exists only to verify that GitHub Security Scanning (CodeQL / Secret Scanning) detects risks.
// Remove it immediately after confirming the alerts in GitHub.
using System.Diagnostics;
using System.IO;
using System.Security.Cryptography;
using System.Text;

namespace Dt.Api.Tests;

public static class SecurityScanTestFixture
{
    // 1. GitHub CodeQL: 命令注入 (Command Injection / CWE-78, cs/command-line-injection)
    public static void RunUntrustedCommand(string userInput)
    {
        // Deliberately unsafe: user-controlled input reaches a shell.
        Process.Start("/bin/sh", $"-c \"{userInput}\"");
    }

    // 2. GitHub CodeQL: 路徑周遊 (Path Injection / CWE-22, cs/path-injection)
    public static string ReadArbitraryFile(string userFilename)
    {
        var basePath = "/app/data";
        var fullPath = Path.Combine(basePath, userFilename);
        return File.ReadAllText(fullPath);
    }

    // 3. GitHub CodeQL: 使用弱加密/雜湊演算法 (Weak Cryptography / CWE-327, CWE-328, cs/weak-crypto)
    public static byte[] HashPasswordWithWeakAlgorithm(string password)
    {
        using var md5 = MD5.Create();
        return md5.ComputeHash(Encoding.UTF8.GetBytes(password));
    }

    // 4. GitHub CodeQL: 硬編碼機密 (Hardcoded Credentials / CWE-798, cs/hardcoded-credentials)
    public const string HardcodedPassword = "Password1234!@#SuperSecret";
}
