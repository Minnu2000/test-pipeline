#!/usr/bin/env python3
import os
import sys
import hashlib
from datetime import datetime
from urllib.parse import quote

# Configuration
BASE_DIR = "releases"
LOGO_PATH = "https://criticalshift.io/_astro/critical_shift.CJ2LLfLD_1Iu40z.webp"
CSS_PATH = "/style.css"  # Hardcoded as requested

CSS_CONTENT = """/* style.css */
body {
    font-family: Arial, sans-serif;
    padding: 40px;
    background-color: #e5e7eb;
    color: black;
}
.header {
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    margin-bottom: 10px;
}
.header img {
    position: absolute;
    left: 0;
    width: 80px;
    height: auto;
}
.header h2 {
    margin: 0;
    color: black;
    text-align: center;
}
h3 {
    color: black;
    margin-top: 20px;
    text-align: left;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    border-radius: 12px;
    overflow: hidden;
    background: #fff;
}
th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #eee;
    color: black;
}
th {
    background-color: #4f46e5;
    color: #fff;
}
tr:hover {
    background-color: #f9f9f9;
}
a {
    color: black;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
.icon {
    margin-right: 8px;
    font-size: 1rem;
}
.icon.folder {
    color: #f59e0b;
}
.icon.file {
    color: #3b82f6;
}
code {
    font-size: 0.85rem;
    color: #222;
    background: #f0f0f0;
    padding: 2px 5px;
    border-radius: 3px;
    font-family: monospace;
    word-break: break-all;
}
"""

def human_size(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024**2:
        return f"{size // 1024} KB"
    elif size < 1024**3:
        return f"{size // (1024**2)} MB"
    else:
        return f"{size // (1024**3)} GB"

def generate_breadcrumb(dir_path):
    rel = os.path.relpath(dir_path, BASE_DIR)
    breadcrumb = f'<a href="/{BASE_DIR}/">releases</a>'
    
    if rel == ".":
        return breadcrumb
        
    parts = rel.split(os.sep)
    current = ""
    for part in parts:
        current = os.path.join(current, part)
        breadcrumb += f' / <a href="/{BASE_DIR}/{current.replace(os.sep, "/")}/">{part}</a>'
    return breadcrumb


def get_header(dir_path, mode, CSS_PATH, logo_path=LOGO_PATH, show_sha=False):
    breadcrumb = generate_breadcrumb(dir_path)
    sha_header = "<th>SHA256</th>" if show_sha else ""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="icon" href="https://criticalshift.io/favicon.ico" type="image/x-icon">
    <title>CriticalShift</title>
    <link rel="stylesheet" href="{CSS_PATH}">
</head>
<body>
<div class="header">
    <img src="{logo_path}" alt="Logo">
    <h3>Directory listing for <span style="color:black;">{breadcrumb}</span></h3>
</div>
<h3>Files and Folders</h3>
<table>
<tr>
<th>Name</th><th>Size</th><th>Date</th>{sha_header}
</tr>
"""

def generate_index(dir_path, CSS_PATH):
    mode = "shield" if "kform-shield-v" in dir_path else "default"
    
    # Check if there are any real files to display for SHA column logic
    has_files = False
    try:
        has_files = any(entry.is_file() and entry.name != "index.html" for entry in os.scandir(dir_path))
    except FileNotFoundError:
        return

    index_file = os.path.join(dir_path, "index.html")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(get_header(dir_path, mode, CSS_PATH, show_sha=(mode=="shield" and has_files)))

        # List contents
        entries = sorted(os.scandir(dir_path), key=lambda e: (not e.is_dir(), e.name))
        
        for entry in entries:
            if entry.name == "index.html":
                continue
                
            date = datetime.fromtimestamp(entry.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            url = quote(entry.name)
            
            if entry.is_dir():
                f.write(f"<tr><td><span class='icon folder'>📁</span><a href='{url}/'>{entry.name}/</a></td>")
                f.write(f"<td>-</td><td>{date}</td>")
                if mode == "shield" and has_files:
                    f.write("<td>-</td>")
                f.write("</tr>\n")
            else:
                size = human_size(entry.stat().st_size)
                f.write(f"<tr><td><span class='icon file'>📄</span><a href='{url}'>{entry.name}</a></td>")
                f.write(f"<td>{size}</td><td>{date}</td>")
                
                if mode == "shield":
                    with open(entry.path, "rb") as fobj:
                        hash_val = hashlib.sha256(fobj.read()).hexdigest()
                    f.write(f"<td><code>{hash_val}</code></td>")
                f.write("</tr>\n")

        f.write("</table></body></html>")
    print(f"✅ Indexed: {dir_path}")

if __name__ == "__main__":
    # Ensure releases directory exists or not
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    # 1. Write CSS file to the root (one level above releases)
    local_css_file = os.path.join(os.getcwd(), "style.css")
    with open(local_css_file, "w", encoding="utf-8") as css_file:
        css_file.write(CSS_CONTENT)
    print(f"🎨 CSS written to {local_css_file}")

    # 2. Generate HTML pages linking to /style.css
    for root, dirs, files in os.walk(BASE_DIR):
        generate_index(root, CSS_PATH)