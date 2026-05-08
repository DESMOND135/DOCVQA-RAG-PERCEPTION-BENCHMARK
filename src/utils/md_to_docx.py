import os
import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER, WD_PARAGRAPH_ALIGNMENT
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement, ns, parse_xml
from pygments import highlight
from pygments.lexers import get_lexer_by_name, PythonLexer
from pygments.formatters import RawTokenFormatter

def create_element(name):
    return OxmlElement(name)

def create_attribute(element, name, value):
    element.set(ns.qn(name), value)

def add_field(run, field_type):
    """
    Adds a Word field (PAGE, DATE, TOC) to a run.
    """
    fldChar1 = create_element('w:fldChar')
    create_attribute(fldChar1, 'w:fldCharType', 'begin')
    
    instrText = create_element('w:instrText')
    create_attribute(instrText, 'xml:space', 'preserve')
    instrText.text = field_type
    
    fldChar2 = create_element('w:fldChar')
    create_attribute(fldChar2, 'w:fldCharType', 'separate')
    
    t = create_element('w:t')
    t.text = "1" # Placeholder
    
    fldChar3 = create_element('w:fldChar')
    create_attribute(fldChar3, 'w:fldCharType', 'end')
    
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(t)
    run._r.append(fldChar3)

def force_field_update(doc):
    element = doc.settings.element
    update_fields = OxmlElement('w:updateFields')
    update_fields.set(ns.qn('w:val'), 'true')
    element.append(update_fields)

def set_toc_styles(doc):
    for i in range(1, 4):
        style_name = f'TOC {i}'
        if style_name in doc.styles:
            style = doc.styles[style_name]
            style.font.name = 'Arial'
            style.font.size = Pt(12)
            style.paragraph_format.line_spacing = 1.15
            style.paragraph_format.space_after = Pt(2)

def get_omml_for_latex(latex):
    try:
        from latex2mathml.converter import convert
        mathml = convert(latex)
        from lxml import etree
        xslt = etree.fromstring("""
            <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                            xmlns:m="http://www.w3.org/1998/Math/MathML"
                            xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
                <xsl:output method="xml" encoding="UTF-8"/>
                <xsl:template match="/">
                    <xsl:copy-of select="."/>
                </xsl:template>
            </xsl:stylesheet>
        """)
        return mathml # This is a placeholder; real OMML conversion is complex
    except:
        return None

def add_native_equation(paragraph, latex):
    return False # Simplified for stability

def add_caption(doc, label_text, raw_caption_text, chapter_num="1"):
    """Adds a professional academic caption (X.Y) with manual numbering for total reliability."""
    clean_caption = re.sub(r'^(Figure|Table|Equation|Formula)\s*[\dA-Z.]*[:.]?\s*', '', raw_caption_text, flags=re.IGNORECASE)
    
    if not hasattr(doc, '_caption_counts'): doc._caption_counts = {}
    key = (label_text, chapter_num)
    doc._caption_counts[key] = doc._caption_counts.get(key, 0) + 1
    num = doc._caption_counts[key]
    
    p = doc.add_paragraph(style='Caption')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(24)
    
    label_run = p.add_run(f"{label_text} {chapter_num}.{num}")
    label_run.bold = True
    
    if clean_caption:
        p.add_run(f": {clean_caption}").bold = True
    
    if "Equation" in label_text:
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; p.clear()
        p.add_run(f"( {chapter_num}.").font.size = Pt(12)
        r_seq = p.add_run()
        f1 = create_element('w:fldChar'); create_attribute(f1, 'w:fldCharType', 'begin')
        i1 = create_element('w:instrText'); i1.text = ' SEQ EQUATION \\* ARABIC \\s 1 '
        f2 = create_element('w:fldChar'); create_attribute(f2, 'w:fldCharType', 'separate')
        t2 = create_element('w:t'); t2.text = "1"; f3 = create_element('w:fldChar'); create_attribute(f3, 'w:fldCharType', 'end')
        r_seq._r.append(f1); r_seq._r.append(i1); r_seq._r.append(f2); r_seq._r.append(t2); r_seq._r.append(f3)
        p.add_run(" )").font.size = Pt(12); p.paragraph_format.space_after = Pt(12)

def add_formatted_text(p, text, doc=None, chapter_num="1"):
    if text.strip().startswith('$$') and text.strip().endswith('$$'):
        if doc: add_caption(doc, "Equation", "", chapter_num=chapter_num)
        return
    parts = re.split(r'(\$.*?\$|\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*)', text)
    for part in parts:
        if not part: continue
        run = p.add_run()
        run.font.name = 'Arial'; run.font.size = Pt(12)
        if part.startswith('$') and part.endswith('$'): run.text = part[1:-1]; run.italic = True; run.bold = True
        elif part.startswith('***') and part.endswith('***'): run.text = part[3:-3]; run.bold = True; run.italic = True
        elif part.startswith('**') and part.endswith('**'): run.text = part[2:-2]; run.bold = True
        elif part.startswith('*') and part.endswith('*'): run.text = part[1:-1]; run.italic = True
        else: run.text = part

def set_academic_styles(doc):
    style = doc.styles['Normal']
    font = style.font; font.name = 'Arial'; font.size = Pt(12)
    pf = style.paragraph_format; pf.line_spacing = 1.5; pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.space_after = Pt(0); pf.space_before = Pt(0)

def set_heading_styles(doc):
    # Rule 1: No heading should appear alone at the bottom
    for level in range(0, 5):
        s_name = f'Heading {level}' if level > 0 else 'Title'
        if s_name in doc.styles:
            s = doc.styles[s_name]; s.paragraph_format.keep_with_next = True; s.paragraph_format.keep_together = True
            s.paragraph_format.space_before = Pt(12); s.paragraph_format.space_after = Pt(6)
            if level == 1: s.font.size = Pt(16); s.font.bold = True
            elif level == 2: s.font.size = Pt(14); s.font.bold = True
            elif level == 3: s.font.size = Pt(12); s.font.bold = True

def define_caption_style(doc):
    if 'Caption' not in doc.styles:
        s = doc.styles.add_style('Caption', WD_STYLE_TYPE.PARAGRAPH)
        s.base_style = doc.styles['Normal']; s.font.name = 'Arial'; s.font.size = Pt(11); s.font.italic = True
        s.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

def set_page_setup(doc):
    section = doc.sections[0]
    section.page_height = Cm(29.7); section.page_width = Cm(21.0)
    section.left_margin = Cm(3.5); section.right_margin = Cm(2.0); section.top_margin = Cm(2.0); section.bottom_margin = Cm(2.0)
    doc.settings.odd_and_even_pages_header_footer = True

def add_academic_footer(section, has_numbering=True):
    section.footer.is_linked_to_previous = False
    if not has_numbering:
        section.footer.paragraphs[0].clear(); section.even_page_footer.paragraphs[0].clear(); return
    for i, p in enumerate([section.footer.paragraphs[0], section.even_page_footer.paragraphs[0]]):
        p.clear(); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if i == 0 else WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(); run.font.name = 'Times New Roman'; run.font.size = Pt(12)
        add_field(run, "PAGE")

def set_column_layout(section, num_columns=2):
    """Sets the number of columns for a section."""
    sectPr = section._sectPr
    cols = sectPr.xpath('./w:cols')
    if not cols:
        cols = OxmlElement('w:cols')
        sectPr.append(cols)
    else:
        cols = cols[0]
    cols.set(ns.qn('w:num'), str(num_columns))
    cols.set(ns.qn('w:space'), '720') # 0.5 inch space between columns

def convert_to_professional_docx(md_path, docx_path):
    print(f"Applying Global Corrections to: {docx_path}")
    is_paper = "paper" in docx_path.lower()
    doc = Document()
    define_caption_style(doc)
    set_academic_styles(doc)
    set_heading_styles(doc)
    set_page_setup(doc)
    
    if not is_paper:
        add_academic_footer(doc.sections[0], has_numbering=False)
        force_field_update(doc)
        set_toc_styles(doc)
    
    if not os.path.exists(md_path): return
    with open(md_path, 'r', encoding='utf-8') as f: lines = f.readlines()
    
    current_chapter = "1"
    
    # Paper Specific Header Logic
    if is_paper:
        # Title
        title_line = next((l.lstrip('#').strip() for l in lines if l.startswith('# ')), "Document")
        tp = doc.add_heading(title_line, 0)
        tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Authors & Affiliations
        author_info = []
        abstract_lines = []
        in_abstract = False
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('**Author:**') or line.startswith('**Affiliation:**') or line.startswith('**Preprint:**'):
                author_info.append(line)
                i += 1
                continue
            if line.startswith('**Abstract**'):
                in_abstract = True
                i += 1
                continue
            if in_abstract:
                if line.startswith('##'):
                    in_abstract = False
                    break
                if line: abstract_lines.append(line)
            i += 1
            if not in_abstract and i > 20: break # Safety break
            
        # Add Authors
        if author_info:
            ap = doc.add_paragraph()
            ap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for info in author_info:
                run = ap.add_run(info.replace('**', '') + "\n")
                run.font.size = Pt(11)
        
        # Add Abstract
        if abstract_lines:
            ab_head = doc.add_paragraph()
            ab_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = ab_head.add_run("Abstract")
            run.bold = True
            run.font.size = Pt(12)
            
            ab_body = doc.add_paragraph(" ".join(abstract_lines))
            ab_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            ab_body.paragraph_format.left_indent = Inches(0.5)
            ab_body.paragraph_format.right_indent = Inches(0.5)
            ab_body.paragraph_format.line_spacing = 1.0
            for run in ab_body.runs: run.font.size = Pt(10); run.italic = True
            
        # Switch to 2 columns for the rest
        new_section = doc.add_section(WD_SECTION.CONTINUOUS)
        set_column_layout(new_section, 2)
        # Reset margins for paper columns
        new_section.left_margin = Cm(2.0)
        new_section.right_margin = Cm(2.0)
        
        # Start processing from after abstract
        i = 0
        while i < len(lines) and not lines[i].startswith('## 1. Introduction'): i += 1
    else:
        # Thesis Header Logic
        title_line = next((l.lstrip('#').strip() for l in lines if l.startswith('#')), "Document")
        subtitle_line = next((l.strip('*').strip() for l in lines if l.strip().startswith('**')), "")
        tp = doc.add_heading(title_line, 0); tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if subtitle_line:
            sp = doc.add_paragraph(subtitle_line, style='Subtitle'); sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in sp.runs: r.font.size = Pt(14); r.bold = True
        doc.add_page_break(); doc.add_section(WD_SECTION.NEW_PAGE); add_academic_footer(doc.sections[-1], has_numbering=False)
        i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line or line == '---' or line == '***': i += 1; continue
        if line.startswith('## '):
            title = line.lstrip('#').strip()
            # Always update chapter number if it starts with digit
            m = re.match(r'^(\d+)\.', title)
            if m: current_chapter = m.group(1)
            elif "Appendix" in title: current_chapter = title.split(':')[0].replace("Appendix", "").strip()
            
            if not is_paper:
                is_odd = any(t in title for t in ["Introduction", "Conclusion", "References", "Bibliography", "Abstract", "Table of Contents", "List of"]) or (title[0].isdigit() and "." in title[:3])
                if is_odd:
                    doc.add_section(WD_SECTION.ODD_PAGE); add_academic_footer(doc.sections[-1], has_numbering=True)
            doc.add_heading(title, 1); i += 1; continue
        if line.startswith('### '): doc.add_heading(line.lstrip('#').strip(), level=2); i += 1; continue
        if line.startswith('#### '): p = doc.add_paragraph(); p.add_run(line.lstrip('#').strip()).bold = True; i += 1; continue
        if line.startswith('|') or (line.startswith('**Table') and i+1 < len(lines) and '|' in lines[i+1]):
            caption = ""; 
            if line.startswith('**Table'): caption = line.strip('*').strip(); i += 1
            if caption: add_caption(doc, "Table", caption, current_chapter)
            data = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                if '---' not in lines[i]: data.append([c.strip() for c in lines[i].strip().split('|') if c.strip()])
                i += 1
            if data:
                tbl = doc.add_table(rows=len(data), cols=len(data[0])); tbl.style = 'Table Grid'
                tbl.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
                for r, row_data in enumerate(data):
                    tbl.rows[r]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
                    for c, val in enumerate(row_data):
                        cp = tbl.rows[r].cells[c].paragraphs[0]
                        add_formatted_text(cp, val, doc, current_chapter)
                        if r < len(data) - 1: cp.paragraph_format.keep_with_next = True
            continue
        if line.startswith('!['):
            alt = re.findall(r'!\[(.*?)\]', line)[0]
            m = re.search(r'\((.*?)\)', line)
            if m:
                raw_path = m.group(1)
                # Resolve path relative to the markdown file
                path = os.path.normpath(os.path.join(os.path.dirname(md_path), raw_path))
                if os.path.exists(path):
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.paragraph_format.keep_with_next = True
                    run = p_img.add_run()
                    # Scale image for columns if it's a paper
                    width_cm = 15 if not is_paper else 8
                    run.add_picture(path, width=Cm(width_cm))
                    cap = alt
                    if i+1 < len(lines) and "Figure" in lines[i+1]:
                        cap = lines[i+1].strip().strip('*')
                        i += 1
                    add_caption(doc, "Figure", cap, current_chapter)
            i += 1; continue
        if line.startswith('```'):
            i += 1; code = ""
            while i < len(lines) and not lines[i].strip().startswith('```'): code += lines[i]; i += 1
            p_c = doc.add_paragraph(); r_c = p_c.add_run(code.strip()); r_c.font.name = 'Courier New'; r_c.font.size = Pt(10)
            if i+2 < len(lines) and lines[i+1].strip() == "" and "Code" in lines[i+2]:
                p_d = doc.add_paragraph(lines[i+2].strip().strip('*')); p_d.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_d.runs[0].italic = True; i += 2
            i += 1; continue
        if line.startswith('- ') or line.startswith('* '):
            p = doc.add_paragraph(style='List Bullet'); add_formatted_text(p, line[2:], doc, current_chapter); i += 1; continue
        if re.match(r'^\d+\. ', line):
            p = doc.add_paragraph(style='List Number'); add_formatted_text(p, line[line.find(' ')+1:], doc, current_chapter); i += 1; continue
        p = doc.add_paragraph(); add_formatted_text(p, line, doc, current_chapter); i += 1
    doc.save(docx_path); print(f"Success: {docx_path}")

if __name__ == "__main__":
    convert_to_professional_docx('thesis/thesis.md', 'thesis/Thesis.docx')
    convert_to_professional_docx('paper/paper.md', 'paper/paper.docx')
