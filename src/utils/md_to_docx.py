import os
import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement, ns, parse_xml

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

def set_toc_styles(doc):
    """Sets professional academic tab stops (right-aligned dotted leaders) for the TOC."""
    # 6.5 inches is standard for right margin on US Letter (8.5 - 1 - 1)
    right_margin_pos = Inches(6.5)
    
    for style_name in ['TOC 1', 'TOC 2', 'TOC 3']:
        if style_name in doc.styles:
            style = doc.styles[style_name]
            tab_stops = style.paragraph_format.tab_stops
            tab_stops.add_tab_stop(right_margin_pos, WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

def add_caption(doc, label_text, raw_caption_text):
    """Adds a professional academic caption using native Word SEQ fields for indexing."""
    # Cleanup: Remove duplicate labels from the source markdown (e.g. "Figure 1: ")
    # This prevents "Figure 1: Figure 1: ..."
    clean_caption = re.sub(r'^(Figure|Table)\s*\d*[:.]?\s*', '', raw_caption_text, flags=re.IGNORECASE)
    
    p = doc.add_paragraph(style='Caption')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Label
    run = p.add_run(f"{label_text} ")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.bold = True
    
    # Native Sequential Numbering Field
    field_run = p.add_run()
    fldSimple = create_element('w:fldSimple')
    create_attribute(fldSimple, 'w:instr', f' SEQ {label_text} \\* ARABIC ')
    field_run._r.append(fldSimple)
    
    # Separator and Title
    run2 = p.add_run(f". {clean_caption}")
    run2.font.name = 'Times New Roman'
    run2.font.size = Pt(11)
    run2.bold = True

def add_page_number_footer(doc):
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        add_field(p.add_run("Page "), "PAGE")
        add_field(p.add_run(" of "), "NUMPAGES")

def force_field_update(doc):
    element = doc.settings.element
    update_fields = OxmlElement('w:updateFields')
    update_fields.set(ns.qn('w:val'), 'true')
    element.append(update_fields)

def get_omml_for_latex(latex):
    """
    Returns the OMML (Office Math Markup Language) XML for specific project formulas.
    Strictly follows the Word schema to prevent document corruption.
    """
    m = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"'
    
    # Standard components
    sum_n = '<m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>'
    sum_limits = '<m:sub><m:r><m:t>i=1</m:t></m:r></m:sub><m:sup><m:r><m:t>N</m:t></m:r></m:sup>'
    
    if "ANLS" in latex:
        return f'''<m:oMath {m}>
            <m:r><m:t>ANLS = </m:t></m:r>
            <m:f><m:num><m:r><m:t>1</m:t></m:r></m:num><m:den><m:r><m:t>N</m:t></m:r></m:den></m:f>
            {sum_n}{sum_limits}<m:e>
            <m:r><m:t> max </m:t></m:r>
            <m:sSub><m:e><m:r><m:t>g ∈ G</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
            <m:r><m:t> SC(g, P</m:t></m:r><m:sSub><m:e><m:r><m:t>i</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>)</m:t></m:r></m:e></m:nary>
        </m:oMath>'''

    if "EM =" in latex:
        return f'''<m:oMath {m}>
            <m:r><m:t>EM = </m:t></m:r>
            <m:f><m:num><m:r><m:t>1</m:t></m:r></m:num><m:den><m:r><m:t>N</m:t></m:r></m:den></m:f>
            {sum_n}{sum_limits}<m:e>
            <m:r><m:t> \mathbb{{I}}(P</m:t></m:r><m:sSub><m:e><m:r><m:t>i</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
            <m:r><m:t> ∈ G</m:t></m:r><m:sSub><m:e><m:r><m:t>i</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>)</m:t></m:r></m:e></m:nary>
        </m:oMath>'''

    # 3. F1 Formula
    if "F_1" in latex or "F1 =" in latex:
        return f'''<m:oMath {m}>
            <m:sSub><m:e><m:r><m:t>F</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub><m:r><m:t> = 2 ⋅ </m:t></m:r>
            <m:f><m:num><m:r><m:t>Precision ⋅ Recall</m:t></m:r></m:num><m:den><m:r><m:t>Precision + Recall</m:t></m:r></m:den></m:f>
        </m:oMath>'''

    # 4. Cosine Similarity (Textbook Version)
    if "Similarity" in latex or "sim(" in latex:
        return f'''<m:oMath {m}>
            <m:r><m:t>Similarity(A, B) = </m:t></m:r>
            <m:f><m:num><m:r><m:t>A ⋅ B</m:t></m:r></m:num><m:den><m:r><m:t>‖A‖ ‖B‖</m:t></m:r></m:den></m:f>
        </m:oMath>'''

    # 6. Math Fragments for Variable Definitions (A, B, dot, norm)
    # Note: Prioritize complex fragments (cdot, \|) over simple ones (mathbf{A},mathbf{B})
    if "cdot" in latex:
        return f'<m:oMath {m}><m:r><m:rPr><m:bold/></m:rPr><m:t>A</m:t></m:r><m:r><m:t> · </m:t></m:r><m:r><m:rPr><m:bold/></m:rPr><m:t>B</m:t></m:r></m:oMath>'
    if "\|" in latex:
        symbol = "A" if "A" in latex else "B"
        return f'<m:oMath {m}><m:r><m:t>‖</m:t></m:r><m:r><m:rPr><m:bold/></m:rPr><m:t>{symbol}</m:t></m:r><m:r><m:t>‖</m:t></m:r></m:oMath>'
    if "mathbf{A}" in latex:
        return f'<m:oMath {m}><m:r><m:rPr><m:bold/></m:rPr><m:t>A</m:t></m:r></m:oMath>'
    if "mathbf{B}" in latex:
        return f'<m:oMath {m}><m:r><m:rPr><m:bold/></m:rPr><m:t>B</m:t></m:r></m:oMath>'

    return None

def add_native_equation(paragraph, latex):
    """Injects native Equation (OMML) XML."""
    xml = get_omml_for_latex(latex)
    if xml:
        el = parse_xml(xml)
        paragraph._p.append(el)
        return True
    return False

def add_formatted_text(p, text):
    # Case 1: Standalone Equation Block
    if text.strip().startswith('$$') and text.strip().endswith('$$'):
        latex = text.strip()[2:-2].strip()
        if add_native_equation(p, latex):
            return

    # Case 2: Mixed Text and Inline Math ($ symbol)
    # This ensures "bold vectors" and "norms" in the "Where" section look like math, not typed text.
    parts = re.split(r'(\$.*?\$|\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*)', text)
    for part in parts:
        if not part: continue
        
        # Inline Math Processor
        if part.startswith('$') and part.endswith('$'):
            latex = part[1:-1].strip()
            if not add_native_equation(p, latex):
                # Fallback to bolded/italicized if OMML fails
                run = p.add_run(latex)
                run.bold = True; run.italic = True
            continue

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
            run.text = part

def convert_to_professional_docx(md_path, docx_path):
    print(f"Generating Diamond-Standard Document: {md_path} -> {docx_path}")
    doc = Document()
    force_field_update(doc)
    set_toc_styles(doc)

    if not os.path.exists(md_path): return

    with open(md_path, 'r', encoding='utf-8') as f: lines = f.readlines()

    # Pass 1: Extract Title, Executive Summary, Abstract, and Acknowledgments
    title = next((l.lstrip('#').strip() for l in lines if l.startswith('#')), "Academic Document")
    exec_summary = []
    abstract_content = []
    ack_content = []
    
    current_section = None
    body_lines = []
    
    for line in lines:
        if "## Executive Summary" in line:
            current_section = "exec_summary"
            continue
        if "## Abstract" in line or "### Abstract" in line:
            current_section = "abstract"
            continue
        if "## Acknowledgments" in line:
            current_section = "acknowledgments"
            continue
        if current_section and line.startswith('---'):
            current_section = None
            continue
        
        if current_section == "exec_summary":
            exec_summary.append(line.strip())
        elif current_section == "abstract":
            abstract_content.append(line.strip())
        elif current_section == "acknowledgments":
            ack_content.append(line.strip())
        else:
            body_lines.append(line)

    # 1. Title Page (Excluded from TOC)
    doc.add_heading(title, 0)
    doc.add_page_break()

    # 2. Executive Summary (Manual formatting to avoid TOC)
    if exec_summary:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("Executive Summary")
        run.bold = True; run.font.size = Pt(14)
        
        for p_text in exec_summary:
            if not p_text.strip(): continue
            sp = doc.add_paragraph()
            # Handle headers inside the summary
            if p_text.startswith('###'):
                run = sp.add_run(p_text.lstrip('#').strip())
                run.bold = True
            elif p_text.startswith('*'):
                sp.style = 'List Bullet'
                add_formatted_text(sp, p_text.lstrip('*').strip())
            else:
                sp.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                add_formatted_text(sp, p_text)
        doc.add_page_break()

    # 3. Abstract (Manual formatting to avoid TOC)
    if abstract_content:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("Abstract")
        run.bold = True; run.font.size = Pt(14)
        
        for p_text in abstract_content:
            if not p_text.strip(): continue
            ap = doc.add_paragraph()
            ap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_formatted_text(ap, p_text)
        doc.add_page_break()

    # 3. Acknowledgments (Manual formatting to avoid TOC)
    if ack_content:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("Acknowledgments")
        run.bold = True; run.font.size = Pt(14)
        
        for p_text in ack_content:
            if not p_text.strip(): continue
            acp = doc.add_paragraph()
            acp.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_formatted_text(acp, p_text)
        doc.add_page_break()

    # 4. Tables/Figures/TOC
    doc.add_heading("List of Figures", level=1); add_field(doc.add_paragraph().add_run(), 'TOC \\c "Figure" \\h \\z \\u')
    doc.add_page_break()
    doc.add_heading("List of Tables", level=1); add_field(doc.add_paragraph().add_run(), 'TOC \\c "Table" \\h \\z \\u')
    doc.add_page_break()
    doc.add_heading("Table of Contents", level=1); add_field(doc.add_paragraph().add_run(), 'TOC \\o "1-3" \\h \\z \\u')
    doc.add_page_break()

    add_page_number_footer(doc)

    # Main Body
    i = 0
    while i < len(body_lines):
        line = body_lines[i].strip()
        if not line: i += 1; continue
        
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            # Skip the main title in body if it was already on title page
            if level == 1 and title in line: i += 1; continue
            doc.add_heading(line.lstrip('#').strip(), level=min(level, 3))
            i += 1; continue
            
        if line.startswith('|') or line.startswith('**Table'):
            table_caption = ""
            if line.startswith('**Table'):
                table_caption = line.strip('*').strip()
                i += 1; line = body_lines[i].strip() if i < len(body_lines) else ""
            
            data = []
            while i < len(body_lines) and body_lines[i].strip().startswith('|'):
                l = body_lines[i].strip()
                if '---' in l: i += 1; continue
                cols = [c.strip() for c in l.split('|') if c.strip()]
                if cols: data.append(cols)
                i += 1
            if data:
                table = doc.add_table(rows=len(data), cols=len(data[0])); table.style = 'Table Grid'
                for r, rd in enumerate(data):
                    for c, val in enumerate(rd): add_formatted_text(table.rows[r].cells[c].paragraphs[0], val)
                if table_caption: add_caption(doc, "Table", table_caption)
            continue
            
        if line.startswith('!['):
            m = re.search(r'!\[(.*?)\]\((.*?)\)', line)
            if m:
                alt, p_path = m.groups()
                full_path = os.path.normpath(os.path.join(os.path.dirname(md_path), p_path))
                if os.path.exists(full_path):
                    # Set width to 6.5 inches for full-page professional density
                    doc.add_picture(full_path, width=Inches(6.5))
                    caption_line = body_lines[i+1].strip().strip('*') if i + 1 < len(body_lines) and "Figure" in body_lines[i+1] else alt
                    if i + 1 < len(body_lines) and "Figure" in body_lines[i+1]: i += 1
                    add_caption(doc, "Figure", caption_line)
            i += 1; continue
            
        if line.startswith('- ') or line.startswith('* '):
            p = doc.add_paragraph(style='List Bullet'); add_formatted_text(p, line[2:].strip()); i += 1; continue
            
        p = doc.add_paragraph(); p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; add_formatted_text(p, line); i += 1

    doc.save(docx_path)
    print(f"Professional Success: {docx_path}")

if __name__ == "__main__":
    convert_to_professional_docx('Deliverable/thesis/source/thesis.md', 'Deliverable/thesis/thesis.docx')
    convert_to_professional_docx('Deliverable/paper/source/paper.md', 'Deliverable/paper/paper.docx')
