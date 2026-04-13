import os
import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, ns

def create_element(name):
    return OxmlElement(name)

def create_attribute(element, name, value):
    element.set(ns.qn(name), value)

def add_field(run, field_code):
    """Safely adds a Word field to a run, following the correct XML schema."""
    fldChar1 = create_element('w:fldChar')
    create_attribute(fldChar1, 'w:fldCharType', 'begin')
    run._r.append(fldChar1)
    
    instrText = create_element('w:instrText')
    create_attribute(instrText, 'xml:space', 'preserve')
    instrText.text = field_code
    run._r.append(instrText)
    
    fldChar2 = create_element('w:fldChar')
    create_attribute(fldChar2, 'w:fldCharType', 'separate')
    run._r.append(fldChar2)
    
    fldChar3 = create_element('w:fldChar')
    create_attribute(fldChar3, 'w:fldCharType', 'end')
    run._r.append(fldChar3)

def add_caption(doc, label_text, caption_text):
    """Adds a professional academic caption using native Word SEQ fields for indexing."""
    p = doc.add_paragraph(style='Caption')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Label (e.g., "Figure ")
    run = p.add_run(f"{label_text} ")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.bold = True
    
    # Native Sequential Numbering Field (e.g., SEQ Figure)
    field_run = p.add_run()
    # Simple version for compatibility
    fldSimple = create_element('w:fldSimple')
    create_attribute(fldSimple, 'w:instr', f' SEQ {label_text} \\* ARABIC ')
    field_run._r.append(fldSimple)
    
    # Separator and Caption Title
    run2 = p.add_run(f": {caption_text}")
    run2.font.name = 'Times New Roman'
    run2.font.size = Pt(11)
    run2.bold = True

def add_page_number_footer(doc):
    """Adds a standard 'Page X of Y' footer."""
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        run1 = p.add_run("Page ")
        run1.font.name = 'Times New Roman'
        run1.font.size = Pt(10)

        field_run = p.add_run()
        add_field(field_run, "PAGE")

        run2 = p.add_run(" of ")
        run2.font.name = 'Times New Roman'
        run2.font.size = Pt(10)

        field_run2 = p.add_run()
        add_field(field_run2, "NUMPAGES")

def force_field_update(doc):
    """Adds a setting to force Word to update all fields when the document is opened."""
    element = doc.settings.element
    update_fields = OxmlElement('w:updateFields')
    update_fields.set(ns.qn('w:val'), 'true')
    element.append(update_fields)

def add_automatic_table_of_contents(doc):
    """Inserts an Automatic Table of Contents."""
    doc.add_heading("Table of Contents", level=1)
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    add_field(run, 'TOC \\o "1-3" \\h \\z \\u')
    doc.add_page_break()

def add_automatic_list_of_figures(doc):
    """Inserts an Automatic List of Figures."""
    doc.add_heading("List of Figures", level=1)
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    add_field(run, 'TOC \\c "Figure" \\h \\z \\u')
    doc.add_page_break()

def add_automatic_list_of_tables(doc):
    """Inserts an Automatic List of Tables."""
    doc.add_heading("List of Tables", level=1)
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    add_field(run, 'TOC \\c "Table" \\h \\z \\u')
    doc.add_page_break()

def add_formatted_text(p, text):
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

def convert_to_professional_docx(md_path, docx_path):
    print(f"Generating Diamond-Standard Document: {md_path} -> {docx_path}")
    doc = Document()
    force_field_update(doc)
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)

    if not os.path.exists(md_path): return

    with open(md_path, 'r', encoding='utf-8') as f: lines = f.readlines()

    # Title
    title_line = next((l.lstrip('#').strip() for l in lines if l.startswith('#')), "Academic Document")
    doc.add_heading(title_line, 0)

    add_automatic_table_of_contents(doc)
    add_automatic_list_of_figures(doc)
    add_automatic_list_of_tables(doc)
    add_page_number_footer(doc)

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line: i += 1; continue
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            doc.add_heading(line.lstrip('#').strip(), level=min(level, 3))
            i += 1; continue
            
        if line.startswith('|') or line.startswith('**Table'):
            table_caption = ""
            if line.startswith('**Table'):
                table_caption = line.strip('*').replace('Table:', '').strip()
                i += 1
                if i < len(lines): line = lines[i].strip()
            
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
                
                # Use native Caption style and SEQ Table field
                if table_caption:
                    add_caption(doc, "Table", table_caption)
            continue
            
        if line.startswith('!['):
            m = re.search(r'!\[(.*?)\]\((.*?)\)', line)
            if m:
                alt, p_path = m.groups()
                full_path = os.path.normpath(os.path.join(os.path.dirname(md_path), p_path))
                if os.path.exists(full_path):
                    doc.add_picture(full_path, width=Inches(6))
                    caption_line = ""
                    if i + 1 < len(lines) and ("Figure" in lines[i+1] or "*Figure" in lines[i+1]):
                        caption_line = lines[i+1].strip().strip('*').replace('Figure:', '').strip()
                        i += 1
                    else:
                        caption_line = alt
                    
                    # Use native Caption style and SEQ Figure field
                    add_caption(doc, "Figure", caption_line)
            i += 1; continue
            
        if line.startswith('- ') or line.startswith('* '):
            p = doc.add_paragraph(style='List Bullet')
            add_formatted_text(p, line[2:].strip())
            i += 1; continue
            
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_formatted_text(p, line)
        i += 1

    doc.save(docx_path)
    print(f"Professional Success: {docx_path}")

if __name__ == "__main__":
    os.makedirs('Gold_Submission', exist_ok=True)
    convert_to_professional_docx('thesis/thesis.md', 'Gold_Submission/Thesis_Gold.docx')
    convert_to_professional_docx('paper/paper.md', 'Gold_Submission/Paper_Gold.docx')
