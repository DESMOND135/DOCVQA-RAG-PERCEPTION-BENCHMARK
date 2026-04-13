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
    Token.Keyword: RGBColor(30, 58, 138),
    Token.String: RGBColor(163, 21, 21),
    Token.Comment: RGBColor(0, 128, 0),
    Token.Number: RGBColor(9, 134, 115)
}

def create_element(name):
    return OxmlElement(name)

def create_attribute(element, name, value):
    element.set(ns.qn(name), value)

def add_page_number_footer(doc):
    """
    Adds a professional 'Page X of Y' footer to all sections.
    This uses standard OOXML field codes for maximum compatibility.
    """
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add 'Page ' text
        run = p.add_run("Page ")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)

        # Insert Page Number Field
        fldChar1 = create_element('w:fldChar')
        create_attribute(fldChar1, 'w:fldCharType', 'begin')
        p._p.append(fldChar1)
        
        instrText = create_element('w:instrText')
        instrText.text = "PAGE"
        p._p.append(instrText)
        
        fldChar2 = create_element('w:fldChar')
        create_attribute(fldChar2, 'w:fldCharType', 'end')
        p._p.append(fldChar2)

        # Add ' of ' text
        run = p.add_run(" of ")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)

        # Insert Total Pages Field
        fldChar3 = create_element('w:fldChar')
        create_attribute(fldChar3, 'w:fldCharType', 'begin')
        p._p.append(fldChar3)
        
        instrText2 = create_element('w:instrText')
        instrText2.text = "NUMPAGES"
        p._p.append(instrText2)
        
        fldChar4 = create_element('w:fldChar')
        create_attribute(fldChar4, 'w:fldCharType', 'end')
        p._p.append(fldChar4)

def add_table_of_contents(doc):
    """
    Inserts a standard Table of Contents field.
    Word will prompt to update this on first open.
    """
    doc.add_heading("Table of Contents", level=1)
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    
    fldChar1 = create_element('w:fldChar')
    create_attribute(fldChar1, 'w:fldCharType', 'begin')
    run._r.append(fldChar1)
    
    instrText = create_element('w:instrText')
    create_attribute(instrText, 'xml:space', 'preserve')
    instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
    run._r.append(instrText)
    
    fldChar2 = create_element('w:fldChar')
    create_attribute(fldChar2, 'w:fldCharType', 'separate')
    run._r.append(fldChar2)
    
    # Placeholder text that gets replaced by Word
    run.add_text("Right-click here and select 'Update Field' to generate TOC")
    
    fldChar3 = create_element('w:fldChar')
    create_attribute(fldChar3, 'w:fldCharType', 'end')
    run._r.append(fldChar3)
    
    doc.add_page_break()

def add_title_page(doc, title_text, subtitle="Master's Final Submission"):
    """Creates a formal center-aligned Title Page."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("\n\n\n\n\n" + title_text)
    run.font.size = Pt(26); run.bold = True; run.font.name = 'Times New Roman'
    
    ps = doc.add_paragraph()
    ps.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s_run = ps.add_run("\n" + subtitle + "\nAcademic Year 2025-2026\n\nCzestochowa University of Technology")
    s_run.font.size = Pt(16); s_run.font.name = 'Times New Roman'
    doc.add_page_break()

def add_formatted_text(p, text):
    # Regex to catch Bold, Italic, Bold-Italic
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
            # Strip simple math $ residues
            clean_text = re.sub(r'\$(.*?)\$', r'\1', part)
            run.text = clean_text

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
    print(f"Generating Diamond-Standard Document: {md_path} -> {docx_path}")
    doc = Document()
    
    # Global Style Setup
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    doc.settings.odd_and_even_pages_header_footer = False

    with open(md_path, 'r', encoding='utf-8') as f: lines = f.readlines()

    # 1. Title Page
    title_line = next((l.lstrip('#').strip() for l in lines if l.startswith('#')), "Academic Document")
    add_title_page(doc, title_line)

    # 2. Table of Contents
    add_table_of_contents(doc)

    # 3. Footer Pagination
    add_page_number_footer(doc)

    # 4. Content Parsing
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line: i += 1; continue
        
        # Headings
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            h = doc.add_heading(line.lstrip('#').strip(), level=min(level, 3))
            i += 1; continue
            
        # Tables
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
                table = doc.add_table(rows=len(data), cols=len(data[0]))
                table.style = 'Table Grid'; table.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r, rd in enumerate(data):
                    for c, val in enumerate(rd): 
                        add_formatted_text(table.rows[r].cells[c].paragraphs[0], val)
            continue
            
        # Figures (Images)
        if line.startswith('!['):
            m = re.search(r'!\[(.*?)\]\((.*?)\)', line)
            if m:
                alt, p_path = m.groups()
                full_path = os.path.normpath(os.path.join(os.path.dirname(md_path), p_path))
                if os.path.exists(full_path):
                    # Add Image
                    doc.add_picture(full_path, width=Inches(6))
                    # Add Caption (Bold & Centered)
                    caption_line = ""
                    if i + 1 < len(lines) and (lines[i+1].strip().startswith('*Figure') or lines[i+1].strip().startswith('Figure')):
                        caption_line = lines[i+1].strip().strip('*')
                        i += 1
                    else:
                        caption_line = f"Figure: {alt}"
                    
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = p.add_run(caption_line)
                    run.bold = True; run.font.size = Pt(11); run.font.name = 'Times New Roman'
            i += 1; continue
            
        # Code Blocks
        if line.startswith('```'):
            lang = line[3:].strip() or 'python'; code = []; i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code.append(lines[i]); i += 1
            i += 1; add_highlighted_code(doc, "".join(code), lang); continue
        
        # Lists
        if line.startswith('- ') or line.startswith('* '):
            p = doc.add_paragraph(style='List Bullet')
            add_formatted_text(p, line[2:].strip())
            i += 1; continue
            
        # Normal Paragraphs
        p = doc.add_paragraph()
        add_formatted_text(p, line)
        i += 1

    metadata = doc.core_properties
    metadata.author = "Antigravity Academic Tool"
    metadata.title = title_line

    doc.save(docx_path)
    print(f"Success: {docx_path}")

if __name__ == "__main__":
    os.makedirs('Gold_Submission', exist_ok=True)
    convert_to_gold_docx('thesis/thesis.md', 'Gold_Submission/Thesis.docx')
    convert_to_gold_docx('paper/paper.md', 'Gold_Submission/Paper.docx')
