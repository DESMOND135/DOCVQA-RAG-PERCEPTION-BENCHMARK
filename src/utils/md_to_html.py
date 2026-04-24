import os
import markdown
import re

def convert_to_html(md_path, html_path):
    print(f"HTML Conversion: {md_path} -> {html_path}")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    css = """
    <style>
        @page {
            size: A4;
            margin: 2.0cm;
        }
        @page :left {
            margin-left: 2.0cm;
            margin-right: 3.5cm;
        }
        @page :right {
            margin-left: 3.5cm;
            margin-right: 2.0cm;
        }
        body { 
            font-family: Arial, sans-serif; 
            font-size: 12pt;
            line-height: 1.5; 
            margin: 0;
            color: #000; 
            text-align: justify;
        }
        .content {
            padding: 0;
            counter-reset: page 1;
        }
        
        /* Chapters on ODD pages */
        .chapter-start {
             break-before: right;
             page-break-before: right;
        }
        
        h1 { font-size: 18pt; margin-top: 50px; text-align: center; break-before: right; }
        h2 { font-size: 14pt; margin-top: 40px; border-bottom: 2px solid #000; padding-bottom: 10px; break-before: right; }
        h3 { font-size: 12pt; font-weight: bold; margin-top: 30px; }
        
        pre, code { font-family: 'Courier New', Courier, monospace; font-size: 10pt; }
        .code-desc { font-style: italic; font-size: 10pt; text-align: center; margin-top: 5px; }
        
        img { max-width: 100%; height: auto; display: block; margin: 20px auto; }
        .fig-caption { font-size: 11pt; font-weight: bold; text-align: center; margin-top: 5px; }
        
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #000; padding: 8px; text-align: left; }
        th { background: #eee; }
        .table-caption { font-size: 11pt; font-weight: bold; margin-bottom: 5px; }

        .title-page { 
            text-align: center; 
            padding-top: 150px; 
            page-break-after: always;
            break-after: always;
        }
        
        /* Footer Paging Setup (Simulated for Browser/Print) */
        @page {
            @bottom-left {
                content: counter(page);
                font-family: "Times New Roman", Times, serif;
                font-size: 12pt;
            }
            @bottom-right {
                content: counter(page);
                font-family: "Times New Roman", Times, serif;
                font-size: 12pt;
            }
        }
        
        /* CSS for screen viewing simulating the paging */
        .page-num-odd { text-align: right; font-family: "Times New Roman", serif; font-size: 12pt; margin-top: 20px; border-top: 1px solid #ddd; }
        .page-num-even { text-align: left; font-family: "Times New Roman", serif; font-size: 12pt; margin-top: 20px; border-top: 1px solid #ddd; }
    </style>
    """
    
    # Standardize image paths
    md_text = md_text.replace('../../../results/', '../results/')
    md_text = md_text.replace('../../../data/', '../data/')
    
    html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc', 'attr_list'])
    
    # Inject Specific Structural classes for Chapters
    chapter_titles = ["Introduction", "Literature Review", "Methodology", "Evaluation", "Experimental Results", "Conclusion", "References", "Table of Contents"]
    for title_name in chapter_titles:
        html_content = html_content.replace(f'<h2>{title_name}</h2>', f'<h2 class="chapter-start">{title_name}</h2>')
        # Roman numerals chapters
        html_content = re.sub(r'<h2>([IVXLCDM]+\..*?)</h2>', r'<h2 class="chapter-start">\1</h2>', html_content)

    # Table/Code placement fixes (Captions)
    # Markdown tables often have text above/below.
    # We will wrap them in containers if needed, but for now, the CSS handle the spacing.

    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Master's Thesis</title>
    {css}
</head>
<body>
    <div class="title-page">
        <h1 style="break-before: avoid;">Master's Thesis</h1>
        <p>Large Language Model as a Tool for Automatic Extraction of Information from PDF Documents</p>
        <br><br>
        <p>Department of Information Technology</p>
    </div>
    <div class="content">
        {html_content}
    </div>
</body>
</html>
"""
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"HTML Success: {html_path}")

if __name__ == "__main__":
    convert_to_html('deliverables/paper/thesis.md', 'deliverables/paper/Thesis_Viewable.html')
    convert_to_html('deliverables/paper/paper.md', 'deliverables/paper/Paper_Viewable.html')
