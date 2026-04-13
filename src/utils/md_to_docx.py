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

def add_page_number_footer(doc):
    """Adds a standard 'Page X of Y' footer."""
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        run = p.add_run("Page ")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)

        # Page Field
        fldChar1 = create_element('w:fldChar')
        create_attribute(fldChar1, 'w:fldCharType', 'begin')
        p._p.append(fldChar1)
        
        instrText = create_element('w:instrText')
        instrText.text = "PAGE"
        p._p.append(instrText)
        
        fldChar2 = create_element('w:fldChar')
        create_attribute(fldChar2, 'w:fldCharType', 'end')
        p._p.append(fldChar2)

        run = p.add_run(" of ")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)

        # NumPages Field
        fldChar3 = create_element('w:fldChar')
        create_attribute(fldChar1, 'w:fldCharType', 'begin') # reused var name for simplicity
        p._p.append(fldChar3)
        
        instrText2 = create_element('w:instrText')
        instrText2.text = "NUMPAGES"
        p._p.append(instrText2)
        
        fldChar4 = create_element('w:fldChar')
        create_attribute(fldChar4, 'w:fldCharType', 'end')
        p._p.append(fldChar4)

def add_automatic_table_of_contents(doc):
    """Inserts an Automatic Table of Contents with dotted leaders."""
    doc.add_heading("Table of Contents", level=1)
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    
    fldChar1 = create_element('w:fldChar')
    create_attribute(fldChar1, 'w:fldCharType', 'begin')
    run._r.append(fldChar1)
    
    instrText = create_element('w:instrText')
    create_attribute(instrText, 'xml:space', 'preserve')
    # \o "1-3" - include headers 1 to 3
    # \h - use hyperlinks
    # \z - hide tab leader and page number in web layout
    # \u - use the applied logical sequence
    instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
    run._r.append(instrText)
    
    fldChar2 = create_element('w:fldChar')
    create_attribute(fldChar2, 'w:fldCharType', 'separate')
    run._r.append(fldChar2)
    
    # Optional placeholder that tells the user to update
    run.add_text("Right-click here and select 'Update Field' to generate the Table of Contents")
    
    fldChar3 = create_element('w:fldChar')
    create_attribute(fldChar3, 'w:fldCharType', 'end')
    run._r.append(fldChar3)
    doc.add_page_break()

def add_automatic_list_of_figures(doc):
    """Inserts an Automatic List of Figures."""
    doc.add_heading("List of Figures", level=1)
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    
    fldChar1 = create_element('w:fldChar')
    create_attribute(fldChar1, 'w:fldCharType', 'begin')
    run._r.append(fldChar1)
    
    instrText = create_element('w:instrText')
    create_attribute(instrText, 'xml:space', 'preserve')
    instrText.text = 'TOC \\c "Figure" \\h \\z \\u'
    run._r.append(instrText)
    
    fldChar2 = create_element('w:fldChar')
    create_attribute(fldChar2, 'w:fldCharType', 'separate')
    run._r.append(fldChar2)
    
    run.add_text("Right-click here and select 'Update Field' to generate the List of Figures")
    
    fldChar3 = create_element('w:fldChar')
    create_attribute(fldChar3, 'w:fldCharType', 'end')
    run._r.append(fldChar3)
    doc.add_page_break()

def add_automatic_list_of_tables(doc):
    """Inserts an Automatic List of Tables."""
    doc.add_heading("List of Tables", level=1)
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    
    fldChar1 = create_element('w:fldChar')
    create_attribute(fldChar1, 'w:fldCharType', 'begin')
    run._r.append(fldChar1)
    
    instrText = create_element('w:instrText')
    create_attribute(instrText, 'xml:space', 'preserve')
    instrText.text = 'TOC \\c "Table" \\h \\z \\u'
    run._r.append(instrText)
    
    fldChar2 = create_element('w:fldChar')
    create_attribute(fldChar2, 'w:fldCharType', 'separate')
    run._r.append(fldChar2)
    
    run.add_text("Right-click here and select 'Update Field' to generate the List of Tables")
    
    fldChar3 = create_element('w:fldChar')
    create_attribute(fldChar3, 'w:fldCharType', 'end')
    run._r.append(fldChar3)
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
    
    # Global Style Setup
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)

    with open(md_path, 'r', encoding='utf-8') as f: lines = f.readlines()

    # Title
    title_line = next((l.lstrip('#').strip() for l in lines if l.startswith('#')), "Academic Document")
    doc.add_heading(title_line, 0)

    # Automated Lists
    add_automatic_table_of_contents(doc)
    add_automatic_list_of_figures(doc)
    add_automatic_list_of_tables(doc)

    # Footer
    add_page_number_footer(doc)

    # Content
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line: i += 1; continue
        
        # Headings (indexed correctly for TOC)
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            doc.add_heading(line.lstrip('#').strip(), level=min(level, 3))
            i += 1; continue
            
        # Tables 
        if line.startswith('|') or line.startswith('**Table'):
            table_caption = ""
            if line.startswith('**Table'):
                table_caption = line.strip('*')
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
                
                # Add Table Caption (indexed for LOT)
                if table_caption:
                    p = doc.add_paragraph()
                    p.style = 'Caption'
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = p.add_run(table_caption)
                    run.bold = True; run.font.size = Pt(11)
            continue
            
        # Figures (Images)
        if line.startswith('!['):
            m = re.search(r'!\[(.*?)\]\((.*?)\)', line)
            if m:
                alt, p_path = m.groups()
                full_path = os.path.normpath(os.path.join(os.path.dirname(md_path), p_path))
                if os.path.exists(full_path):
                    doc.add_picture(full_path, width=Inches(6))
                    # Add Figure Caption (indexed for LOF)
                    caption_line = ""
                    if i + 1 < len(lines) and ("Figure" in lines[i+1] or "*Figure" in lines[i+1]):
                        caption_line = lines[i+1].strip().strip('*')
                        i += 1
                    else:
                        caption_line = f"Figure: {alt}"
                    
                    p = doc.add_paragraph()
                    p.style = 'Caption' # Style used by Word for TOC indexing
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = p.add_run(caption_line)
                    run.bold = True; run.font.size = Pt(11)
            i += 1; continue
            
        # Lists
        if line.startswith('- ') or line.startswith('* '):
            p = doc.add_paragraph(style='List Bullet')
            add_formatted_text(p, line[2:].strip())
            i += 1; continue
            
        # Normal Paragraphs
        p = doc.add_paragraph()
        add_formatted_text(p, line)
        i += 1

    doc.save(docx_path)
    print(f"Professional Success: {docx_path}")

if __name__ == "__main__":
    os.makedirs('Gold_Submission', exist_ok=True)
    # Output to final clean names
    convert_to_professional_docx('thesis/thesis.md', 'Gold_Submission/Thesis.docx')
    convert_to_professional_docx('paper/paper.md', 'Gold_Submission/Paper.docx')
