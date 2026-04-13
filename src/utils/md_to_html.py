import os
import markdown
import re

def convert_to_html(md_path, html_path):
    print(f"HTML Conversion: {md_path} -> {html_path}")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    # Simple CSS for academic look
    css = """
    <style>
        body { font-family: 'Times New Roman', Times, serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }
        h1, h2, h3 { color: #1e3a8a; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: Consolas, monospace; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: Consolas, monospace; }
        img { max-width: 100%; height: auto; display: block; margin: 20px auto; border: 1px solid #ddd; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background: #f8fafc; color: #1e3a8a; }
        .title-page { text-align: center; margin-bottom: 100px; padding-top: 100px; }
        .title { font-size: 2.5em; font-weight: bold; margin-bottom: 20px; }
        .subtitle { font-size: 1.5em; color: #666; }
    </style>
    """
    
    # Handle local image paths in HTML
    # MD: ![alt](path) -> HTML: <img src="path" alt="alt">
    # We need to make sure the relative paths in HTML work if the HTML is in Gold_Submission.
    # The MD files are in thesis/ or paper/ folder. External images are usually relative to them.
    
    html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    
    # Basic front matter extraction
    title = "Academic Document"
    match = re.search(r'^#\s+(.*)', md_text, re.MULTILINE)
    if match:
        title = match.group(1)
        
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    {css}
</head>
<body>
    <div class="title-page">
        <div class="title">{title}</div>
        <div class="subtitle">Master's Final Submission<br>Academic Year 2025-2026</div>
    </div>
    {html_content}
</body>
</html>
"""
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"HTML Success: {html_path}")

if __name__ == "__main__":
    os.makedirs('Gold_Submission', exist_ok=True)
    convert_to_html('thesis/thesis.md', 'Gold_Submission/Thesis_Viewable.html')
    convert_to_html('paper/paper.md', 'Gold_Submission/Paper_Viewable.html')
