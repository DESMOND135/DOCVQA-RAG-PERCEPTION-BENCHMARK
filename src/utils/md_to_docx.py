import os
import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_static_toc(doc, lines):
    """
    Generates a 100% Static (Plain Text) Table of Contents.
    Contains no field codes, ensuring the file opens on any system.
    """
    doc.add_heading("Table of Contents", level=1)
    toc_p = doc.add_paragraph()
    
    for line in lines:
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            if level <= 3:
                title = line.lstrip('#').strip()
                indent = "    " * (level - 1)
                run = toc_p.add_run(f"{indent}{title}\n")
                run.font.name = 'Times New Roman'
                run.font.size = Pt(11)
                if level == 1: run.bold = True
    
    doc.add_page_break()

def add_formatted_text(p, text):
    # Standard formatting for bold/italic
    parts = re.split(r'(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*)', text)
    for part in parts:
        if not part: continue
        run = p.add_run()
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        if part.startswith('***') and part.endswith('***'):
            run.text = part[3:-3]; run.bold = True; run.italic = True
        elif part.startswith('**') and part.endswith('**'):
            run.text = part[2:-2]; run.bold = True
        elif part.startswith('*') and part.endswith('*'):
            run.text = part[1:-1]; run.italic = True
        else:
            clean_text = re.sub(r'\$(.*?)\$', r'\1', part)
            run.text = clean_text

def convert_to_final_safe_docx(md_path, docx_path):
    print(f"Generating Zero-Risk Academic Document: {md_path} -> {docx_path}")
    doc = Document()
    
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)

    with open(md_path, 'r', encoding='utf-8') as f: lines = f.readlines()

    # Title
    title_line = next((l.lstrip('#').strip() for l in lines if l.startswith('#')), "Academic Document")
    doc.add_heading(title_line, 0)

    # Static TOC
    add_static_toc(doc, lines)

    # Content
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line: i += 1; continue
        
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            doc.add_heading(line.lstrip('#').strip(), level=min(level, 3))
            i += 1; continue
            
        if line.startswith('|'):
            data = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                l = lines[i].strip()
                if '---' in l: i += 1; continue
                cols = [c.strip() for c in l.split('|') if c.strip()]
                if cols: data.append(cols)
                i += 1
            if data:
                table = doc.add_table(rows=len(data), cols=len(data[0]))
                table.style = 'Table Grid'
                for r, rd in enumerate(data):
                    for c, val in enumerate(rd):
                        add_formatted_text(table.rows[r].cells[c].paragraphs[0], val)
            continue
            
        if line.startswith('!['):
            m = re.search(r'!\[(.*?)\]\((.*?)\)', line)
            if m:
                alt, p_path = m.groups()
                full_path = os.path.normpath(os.path.join(os.path.dirname(md_path), p_path))
                if os.path.exists(full_path):
                    doc.add_picture(full_path, width=Inches(6))
                    # Bold Figure Label (Mandatory)
                    caption_line = ""
                    if i + 1 < len(lines) and ("Figure" in lines[i+1] or "*Figure" in lines[i+1]):
                        caption_line = lines[i+1].strip().strip('*')
                        i += 1
                    else:
                        caption_line = f"Figure: {alt}"
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = p.add_run(caption_line)
                    run.bold = True; run.font.size = Pt(11)
            i += 1; continue
            
        if line.startswith('- ') or line.startswith('* '):
            p = doc.add_paragraph(style='List Bullet')
            add_formatted_text(p, line[2:].strip())
            i += 1; continue
            
        p = doc.add_paragraph()
        add_formatted_text(p, line)
        i += 1

    doc.save(docx_path)
    print(f"Success: {docx_path}")

if __name__ == "__main__":
    os.makedirs('Gold_Submission', exist_ok=True)
    # Generate the Final "Safe" versions the user requested
    convert_to_final_safe_docx('thesis/thesis.md', 'Gold_Submission/Thesis_Safe.docx')
    convert_to_final_safe_docx('paper/paper.md', 'Gold_Submission/Paper_Safe.docx')
