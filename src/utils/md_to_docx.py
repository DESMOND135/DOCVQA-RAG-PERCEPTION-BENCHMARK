import os
import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, ns
from pygments import lexers, util as pygments_util
from pygments.lexers import get_lexer_by_name
from pygments.lexers.python import PythonLexer
from pygments.token import Token

# Jupyter-Style Highlighting
COLOR_MAP = {
    Token.Keyword: RGBColor(0, 0, 255),
    Token.String: RGBColor(163, 21, 21),
    Token.Comment: RGBColor(0, 128, 0),
    Token.Number: RGBColor(9, 134, 115)
}

def create_element(name):
    return OxmlElement(name)

def create_attribute(element, name, value):
    element.set(ns.qn(name), value)

def add_clean_page_number(doc):
    """Simplified: No longer uses OXML to avoid security flags."""
    pass

def add_atomic_toc(doc):
    """Simplified: No longer uses OXML. Users can insert TOC manually in Word."""
    doc.add_heading("Table of Contents", level=1)
    doc.add_paragraph("[Place Cursor Here and go to References > Table of Contents in Word]")
    doc.add_page_break()

def add_title_page(doc, title_text, subtitle="Master's Final Submission"):
    """Creates a formal center-aligned Title Page."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("\n\n\n\n" + title_text)
    run.font.size = Pt(24); run.bold = True
    
    ps = doc.add_paragraph()
    ps.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s_run = ps.add_run("\n" + subtitle + "\nAcademic Year 2025-2026")
    s_run.font.size = Pt(16)
    doc.add_page_break()

def add_formatted_text(p, text):
    parts = re.split(r'(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*)', text)
    for part in parts:
        if not part: continue
        run = p.add_run()
        if part.startswith('***') and part.endswith('***'):
            run.text = part[3:-3]; run.bold = True; run.italic = True
        elif part.startswith('**') and part.endswith('**'):
            run.text = part[2:-2]; run.bold = True
        elif part.startswith('*') and part.endswith('*'):
            run.text = part[1:-1]; run.italic = True
        else:
            run.text = re.sub(r'\$(.*?)\$', r'\1', part)

def add_highlighted_code(doc, code_text, lang='python'):
    try: lexer = get_lexer_by_name(lang)
    except: lexer = PythonLexer()
    p = doc.add_paragraph(); p.style = 'No Spacing'; p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for ttype, value in lexer.get_tokens(code_text):
        run = p.add_run(value); run.font.name = 'Consolas'; run.font.size = Pt(10)
        color = COLOR_MAP.get(ttype, RGBColor(0,0,0))
        if color == RGBColor(0,0,0):
            for ancestor in ttype.split():
                if ancestor in COLOR_MAP: color = COLOR_MAP[ancestor]; break
        run.font.color.rgb = color

def convert_to_gold_docx(md_path, docx_path):
    print(f"Safe Conversion: {md_path} -> {docx_path}")
    doc = Document()
    style = doc.styles['Normal']; style.font.name = 'Times New Roman'; style.font.size = Pt(12)
    
    with open(md_path, 'r', encoding='utf-8') as f: lines = f.readlines()

    # Title and Metadata
    title_line = next((l.lstrip('#').strip() for l in lines if l.startswith('#')), "Document")
    add_title_page(doc, title_line)
    add_atomic_toc(doc)

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line: i += 1; continue
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            doc.add_heading(line.lstrip('#').strip(), level=min(level, 4))
            i += 1; continue
        if line.startswith('|'):
            data = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                l = lines[i].strip()
                if '---' in l: i += 1; continue
                cols = [c.strip() for c in l.split('|') if c.strip() or l.count('|') > 1]
                if cols and not cols[0]: cols = cols[1:]
                if cols and not cols[-1]: cols = cols[:-1]
                data.append(cols); i += 1
            if data:
                table = doc.add_table(rows=len(data), cols=len(data[0])); table.style = 'Table Grid'; table.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r, rd in enumerate(data):
                    for c, val in enumerate(rd): add_formatted_text(table.rows[r].cells[c].paragraphs[0], val)
            continue
        if line.startswith('!['):
            m = re.search(r'!\[(.*?)\]\((.*?)\)', line)
            if m:
                alt, p_path = m.groups(); full = os.path.normpath(os.path.join(os.path.dirname(md_path), p_path))
                if os.path.exists(full):
                    doc.add_picture(full, width=Inches(6))
                    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; add_formatted_text(p, alt) 
            i += 1; continue
        if line.startswith('```'):
            lang = line[3:].strip() or 'python'; code = []; i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'): code.append(lines[i]); i += 1
            i += 1; add_highlighted_code(doc, "".join(code), lang); continue
        
        # Safe bullet point handling
        if line.startswith('- ') or line.startswith('* '):
            p = doc.add_paragraph(style='Normal'); run = p.add_run("• "); add_formatted_text(p, line[2:].strip()); i += 1; continue
            
        p = doc.add_paragraph(); add_formatted_text(p, line); i += 1

    doc.save(docx_path)
    print(f"Safe Success: {docx_path}")

if __name__ == "__main__":
    os.makedirs('Gold_Submission', exist_ok=True)
    convert_to_gold_docx('thesis/thesis.md', 'Gold_Submission/Thesis_Safe.docx')
    convert_to_gold_docx('paper/paper.md', 'Gold_Submission/Paper_Safe.docx')
