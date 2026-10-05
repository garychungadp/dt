import json
import sys
import html
import os

def nuget_json_to_html(json_path, output_path):
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    findings = []
    projects = data.get('projects', [])

    for proj in projects:
        proj_path = proj.get('path', 'Unknown Project')
        proj_name = os.path.basename(proj_path)

        for framework in proj.get('frameworks', []):
            fw_name = framework.get('framework', '')

            # Direct packages
            for pkg in framework.get('topLevelPackages', []):
                pkg_id = pkg.get('id', '')
                req_ver = pkg.get('requestedVersion', '')
                res_ver = pkg.get('resolvedVersion', req_ver)
                for v in pkg.get('vulnerabilities', []):
                    findings.append({
                        'project': proj_name,
                        'framework': fw_name,
                        'package': pkg_id,
                        'version': res_ver,
                        'type': 'Direct (直接依賴)',
                        'severity': v.get('severity', 'High'),
                        'advisory_url': v.get('advisoryurl', '')
                    })

            # Transitive packages
            for pkg in framework.get('transitivePackages', []):
                pkg_id = pkg.get('id', '')
                res_ver = pkg.get('resolvedVersion', '')
                for v in pkg.get('vulnerabilities', []):
                    findings.append({
                        'project': proj_name,
                        'framework': fw_name,
                        'package': pkg_id,
                        'version': res_ver,
                        'type': 'Transitive (間接依賴)',
                        'severity': v.get('severity', 'High'),
                        'advisory_url': v.get('advisoryurl', '')
                    })

    total = len(findings)
    critical_count = sum(1 for f in findings if f['severity'].lower() == 'critical')
    high_count = sum(1 for f in findings if f['severity'].lower() == 'high')
    moderate_count = sum(1 for f in findings if f['severity'].lower() in ['moderate', 'medium'])
    low_count = sum(1 for f in findings if f['severity'].lower() == 'low')

    rows = ""
    for f in findings:
        sev = f['severity'].upper()
        badge_class = "danger" if sev in ['CRITICAL', 'HIGH'] else ("warning" if sev in ['MODERATE', 'MEDIUM'] else "info")
        url = f['advisory_url']
        link_html = f'<a href="{html.escape(url)}" target="_blank">{html.escape(url)}</a>' if url else 'N/A'

        rows += f"""
        <tr>
            <td><span class="badge {badge_class}">{html.escape(sev)}</span></td>
            <td><b>{html.escape(f['package'])}</b></td>
            <td><code>{html.escape(f['version'])}</code></td>
            <td>{html.escape(f['type'])}</td>
            <td><code>{html.escape(f['project'])}</code> ({html.escape(f['framework'])})</td>
            <td style="white-space: normal;">{link_html}</td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>NuGet 依賴安全性掃描報告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 30px; background-color: #f6f8fa; color: #24292f; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }}
        h1 {{ margin-top: 0; border-bottom: 2px solid #eaecef; padding-bottom: 12px; font-size: 24px; }}
        .summary {{ display: flex; gap: 20px; margin-bottom: 25px; }}
        .card {{ flex: 1; padding: 15px 20px; border-radius: 6px; background: #f6f8fa; border: 1px solid #d0d7de; text-align: center; }}
        .card .num {{ font-size: 28px; font-weight: bold; margin-top: 5px; }}
        .card.danger .num {{ color: #cf222e; }}
        .card.warning .num {{ color: #9a6700; }}
        .card.info .num {{ color: #0969da; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px 14px; text-align: left; border-bottom: 1px solid #d0d7de; }}
        th {{ background-color: #f6f8fa; }}
        .badge {{ padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; color: white; display: inline-block; }}
        .badge.danger {{ background-color: #cf222e; }}
        .badge.warning {{ background-color: #bf8700; }}
        .badge.info {{ background-color: #0969da; }}
        code {{ background: #f6f8fa; padding: 2px 6px; border-radius: 4px; font-size: 13px; }}
        a {{ color: #0969da; text-decoration: none; word-break: break-all; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 NuGet 依賴套件弱點掃描報告 (Dependency Scan)</h1>
        <div class="summary">
            <div class="card"><div class="label">總弱點數</div><div class="num">{total}</div></div>
            <div class="card danger"><div class="label">嚴重 / 高風險 (Critical/High)</div><div class="num">{critical_count + high_count}</div></div>
            <div class="card warning"><div class="label">中風險 (Moderate)</div><div class="num">{moderate_count}</div></div>
            <div class="card info"><div class="label">低風險 (Low)</div><div class="num">{low_count}</div></div>
        </div>
        <table>
            <thead>
                <tr>
                    <th style="width: 100px;">嚴重度</th>
                    <th style="width: 220px;">套件名稱 (Package)</th>
                    <th style="width: 100px;">版本</th>
                    <th style="width: 150px;">依賴類型</th>
                    <th style="width: 200px;">受影響專案</th>
                    <th>安全諮詢資訊 (Advisory)</th>
                </tr>
            </thead>
            <tbody>
                {rows if rows else '<tr><td colspan="6" style="text-align:center; padding: 30px; color: #57609a;">🎉 太棒了！未發現任何易受攻擊的 NuGet 套件。</td></tr>'}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Report generated successfully: {output_path} (Total findings: {total})")

if __name__ == '__main__':
    json_input = sys.argv[1] if len(sys.argv) > 1 else 'nuget-vulnerabilities.json'
    html_output = sys.argv[2] if len(sys.argv) > 2 else 'reports/nuget-vulnerability-report.html'
    nuget_json_to_html(json_input, html_output)
