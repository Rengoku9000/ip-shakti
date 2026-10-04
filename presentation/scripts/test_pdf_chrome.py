import subprocess
import os

html_path = os.path.abspath('test_print.html')
pdf_path = os.path.abspath('test_print.pdf')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write('<!DOCTYPE html><html><head><style>body { font-family: sans-serif; padding: 40px; color: #0b2545; }</style></head><body><h1>SIH 2026 Test</h1><p>Testing Chrome Headless PDF generation for Team OUTLAWS.</p></body></html>')

chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
file_url = "file:///" + html_path.replace("\\", "/")
cmd = [
    chrome,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    file_url
]
res = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", res.returncode)
print("PDF exists:", os.path.exists(pdf_path), "Size:", os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0)
