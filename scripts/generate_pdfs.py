import os
import subprocess
import markdown

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>__TITLE__</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<style>
  @page {
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1f2937;
    line-height: 1.6;
    font-size: 11pt;
    padding: 0 10px;
  }
  h1, h2, h3, h4 {
    color: #111827;
    font-weight: 700;
    page-break-after: avoid;
  }
  h1 {
    font-size: 20pt;
    border-bottom: 2px solid #2563eb;
    padding-bottom: 8px;
    margin-top: 0;
  }
  h2 {
    font-size: 15pt;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 5px;
    margin-top: 24px;
    color: #1e40af;
  }
  h3 {
    font-size: 12.5pt;
    margin-top: 18px;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
  }
  th, td {
    border: 1px solid #d1d5db;
    padding: 7px 10px;
    text-align: left;
  }
  th {
    background-color: #f3f4f6;
    font-weight: 600;
  }
  tr:nth-child(even) {
    background-color: #f9fafb;
  }
  pre {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 10px;
    font-size: 8.5pt;
    overflow-x: auto;
    font-family: Consolas, Monaco, "Courier New", monospace;
    page-break-inside: avoid;
  }
  code {
    background-color: #f1f5f9;
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 9.5pt;
    font-family: Consolas, Monaco, "Courier New", monospace;
  }
  blockquote {
    border-left: 4px solid #3b82f6;
    margin: 14px 0;
    padding: 6px 14px;
    background-color: #eff6ff;
    color: #1e3a8a;
  }
  hr {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 20px 0;
  }
  ul, ol {
    padding-left: 20px;
  }
  li {
    margin-bottom: 4px;
  }
</style>
</head>
<body>
__BODY__
</body>
</html>
"""

def convert_md_to_pdf(md_filename, pdf_filename):
    print(f"Converting {md_filename} -> {pdf_filename}...")
    with open(md_filename, "r", encoding="utf-8") as f:
        md_text = f.read()

    html_content = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "nl2br"]
    )
    
    html_page = HTML_TEMPLATE.replace("__TITLE__", md_filename.replace(".md", "")).replace("__BODY__", html_content)
    
    temp_html = md_filename.replace(".md", ".temp.html")
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_page)

    abs_html_path = os.path.abspath(temp_html)
    abs_pdf_path = os.path.abspath(pdf_filename)

    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ]
    
    browser_exe = None
    for p in edge_paths:
        if os.path.exists(p):
            browser_exe = p
            break
            
    if not browser_exe:
        raise RuntimeError("No Chromium/Edge browser found for printing to PDF!")

    cmd = [
        browser_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={abs_pdf_path}",
        f"file:///{abs_html_path}"
    ]

    subprocess.run(cmd, check=True)
    
    if os.path.exists(temp_html):
        os.remove(temp_html)
        
    if os.path.exists(abs_pdf_path):
        size_kb = os.path.getsize(abs_pdf_path) / 1024
        print(f"SUCCESS: Generated {pdf_filename} ({size_kb:.1f} KB)")
    else:
        print(f"FAILED to generate {pdf_filename}")

if __name__ == "__main__":
    convert_md_to_pdf("Round_1_Submission_EV_Infra_Map_India_Urja_X.md", "Round_1_Submission_EV_Infra_Map_India_Urja_X.pdf")
    convert_md_to_pdf("Urja_X_MVP_Specification.md", "Urja_X_MVP_Specification.pdf")
