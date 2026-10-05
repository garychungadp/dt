import json
import sys
import html
import os

def license_json_to_html(json_path, output_path):
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    # data is a list of library info objects
    # [{"PackageName": "...", "PackageVersion": "...", "LicenseType": "...", "LicenseUrl": "...", ...}]
    if not isinstance(data, list):
        data = []

    total = len(data)
    license_counts = {}
    for item in data:
        lic = item.get('LicenseType') or 'Unknown'
        license_counts[lic] = license_counts.get(lic, 0) + 1

    rows = ""
    for item in data:
        pkg_name = item.get('PackageName', '')
        version = item.get('PackageVersion', '')
        lic_type = item.get('LicenseType') or 'Unknown'
        lic_url = item.get('LicenseUrl', '')
        project = item.get('Projects', '')
        
        url_html = f'<a href="{html.escape(lic_url)}" target="_blank">{html.escape(lic_url)}</a>' if lic_url else 'N/A'
        
        badge_class = "info"
        lic_upper = lic_type.upper()
        if any(w in lic_upper for w in ['GPL', 'AGPL', 'PROPRIETARY', 'FORBIDDEN']):
            badge_class = "danger"
        elif any(w in lic_upper for w in ['MIT', 'APACHE', 'BSD']):
            badge_class = "success"
        elif 'UNKNOWN' in lic_upper:
            badge_class = "warning"

        rows += f"""
        <tr>
            <td><b>{html.escape(pkg_name)}</b></td>
            <td><code>{html.escape(version)}</code></td>
            <td><span class="badge {badge_class}">{html.escape(lic_type)}</span></td>
            <td><small>{html.escape(os.path.basename(project)) if project else '-'}</small></td>
            <td style="white-space: normal;">{url_html}</td>
        </tr>
        """

    summary_cards = f"""
        <div class="card"><div class="label">總套件數</div><div class="num">{total}</div></div>
        <div class="card info"><div class="label">授權類型種類</div><div class="num">{len(license_counts)}</div></div>
    """
    for lic, count in sorted(license_counts.items(), key=lambda x: -x[1])[:3]:
        summary_cards += f'<div class="card success"><div class="label">{html.escape(lic)}</div><div class="num">{count}</div></div>'

    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>NuGet 套件授權檢查報告 (License Report)</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 30px; background-color: #f6f8fa; color: #24292f; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }}
        h1 {{ margin-top: 0; border-bottom: 2px solid #eaecef; padding-bottom: 12px; font-size: 24px; }}
        .summary {{ display: flex; gap: 20px; margin-bottom: 25px; flex-wrap: wrap; }}
        .card {{ flex: 1; min-width: 140px; padding: 15px 20px; border-radius: 6px; background: #f6f8fa; border: 1px solid #d0d7de; text-align: center; }}
        .card .num {{ font-size: 26px; font-weight: bold; margin-top: 5px; }}
        .card.danger .num {{ color: #cf222e; }}
        .card.warning .num {{ color: #9a6700; }}
        .card.success .num {{ color: #1a7f37; }}
        .card.info .num {{ color: #0969da; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px 14px; text-align: left; border-bottom: 1px solid #d0d7de; }}
        th {{ background-color: #f6f8fa; }}
        .badge {{ padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; color: white; display: inline-block; }}
        .badge.danger {{ background-color: #cf222e; }}
        .badge.warning {{ background-color: #bf8700; }}
        .badge.success {{ background-color: #1a7f37; }}
        .badge.info {{ background-color: #0969da; }}
        code {{ background: #f6f8fa; padding: 2px 6px; border-radius: 4px; font-size: 13px; }}
        a {{ color: #0969da; text-decoration: none; word-break: break-all; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📜 NuGet 套件開源授權檢查報告 (License Report)</h1>
        <div class="summary">
            {summary_cards}
        </div>
        <table>
            <thead>
                <tr>
                    <th style="width: 250px;">套件名稱 (Package)</th>
                    <th style="width: 100px;">版本</th>
                    <th style="width: 180px;">授權條款 (License)</th>
                    <th style="width: 180px;">引用專案</th>
                    <th>授權詳細連結 (URL)</th>
                </tr>
            </thead>
            <tbody>
                {rows if rows else '<tr><td colspan="5" style="text-align:center; padding: 30px; color: #57609a;">未檢測到套件授權資訊。</td></tr>'}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Report generated successfully: {output_path} (Total packages: {total})")

if __name__ == '__main__':
    json_input = sys.argv[1] if len(sys.argv) > 1 else 'reports/licenses.json'
    html_output = sys.argv[2] if len(sys.argv) > 2 else 'reports/nuget-license-report.html'
    license_json_to_html(json_input, html_output)
