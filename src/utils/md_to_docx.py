import os
import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER, WD_PARAGRAPH_ALIGNMENT
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.oxml import OxmlElement, ns, parse_xml
from pygments import highlight
from pygments.lexers import get_lexer_by_name, PythonLexer
from pygments.formatters import RawTokenFormatter

def create_element(name):
    return OxmlElement(name)

def create_attribute(element, name, value):
    element.set(ns.qn(name), value)

def add_highlighted_code(doc, code_text, lang='python'):
    """Adds syntax-highlighted code to a DOCX document."""
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.style = 'Normal'
    
    try:
        lexer = get_lexer_by_name(lang)
    except:
        lexer = PythonLexer()
        
    tokens = lexer.get_tokens(code_text)
    
    for ttype, value in tokens:
        run = p.add_run(value)
        run.font.name = 'Courier New'
        run.font.size = Pt(10)
        
        # Simple color mapping based on token type
        t_str = str(ttype)
        if 'Keyword' in t_str: run.font.color.rgb = RGBColor.from_string('0000FF')
        elif 'String' in t_str: run.font.color.rgb = RGBColor.from_string('008000')
        elif 'Comment' in t_str: run.font.color.rgb = RGBColor.from_string('808080')
        elif 'Name.Function' in t_str or 'Name.Class' in t_str: run.font.color.rgb = RGBColor.from_string('A52A2A')

def add_field(run, field_type):
    """Adds a standard Word field (PAGE, NUMPAGES, etc.) safely using raw OXML."""
    fldChar1 = create_element('w:fldChar')
    create_attribute(fldChar1, 'w:fldCharType', 'begin')
    
    instrText = create_element('w:instrText')
    create_attribute(instrText, 'xml:space', 'preserve')
    instrText.text = fld_code = field_type
    
    fldChar2 = create_element('w:fldChar')
    create_attribute(fldChar2, 'w:fldCharType', 'separate')
    
    t = create_element('w:t')
    t.text = "1" # Display 1 initially
    
    fldChar3 = create_element('w:fldChar')
    create_attribute(fldChar3, 'w:fldCharType', 'end')
    
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(t)
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

def add_caption(doc, label_text, raw_caption_text, chapter_num="1", chapter_title=""):
    """Adds a professional academic caption (X.Y) using native Word SEQ fields."""
    clean_caption = re.sub(r'^(Figure|Table|Equation|Formula)\s*\d*[:.]?\s*', '', raw_caption_text, flags=re.IGNORECASE)
    
    p = doc.add_paragraph(style='Caption')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    
    # Label and Chapter Number (e.g., Figure 2.)
    run = p.add_run(f"{label_text} {chapter_num}.")
    run.font.name = 'Arial'
    run.font.size = Pt(11)
    run.bold = True
    
    # Native Sequential Numbering Field (within chapter)
    field_run = p.add_run()
    fldSimple = create_element('w:fldSimple')
    # Use different SEQ identifiers for figures and tables
    seq_id = "EQUATION" if "Equation" in label_text else ("FIGURE" if "Figure" in label_text else "TABLE")
    create_attribute(fldSimple, 'w:instr', f' SEQ {seq_id} \\* ARABIC \\s 1 ')
    field_run._r.append(fldSimple)
    
    # Title
    run2 = p.add_run()
    if clean_caption:
        run2.text += f": {clean_caption}"
    if chapter_title:
        run2.text += f" (Chapter {chapter_num} – {chapter_title})"
    run2.font.name = 'Arial'
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

def add_formatted_text(p, text, doc=None, chapter_num="1", chapter_title=""):
    # Case 1: Standalone Equation Block
    if text.strip().startswith('$$') and text.strip().endswith('$$'):
        latex = text.strip()[2:-2].strip()
        if add_native_equation(p, latex):
            if doc:
                add_caption(doc, "Equation", "", chapter_num=chapter_num, chapter_title=chapter_title)
            return

    # Case 2: Mixed Text and Inline Math ($ symbol)
    parts = re.split(r'(\$.*?\$|\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*)', text)
    for part in parts:
        if not part: continue
        
        if part.startswith('$') and part.endswith('$'):
            latex = part[1:-1].strip()
            if not add_native_equation(p, latex):
                run = p.add_run(latex)
                run.bold = True; run.italic = True
            continue

        run = p.add_run()
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        if part.startswith('***') and part.endswith('***'):
            run.text = part[3:-3]; run.bold = True; run.italic = True
        elif part.startswith('**') and part.endswith('**'):
            run.text = part[2:-2]; run.bold = True
        elif part.startswith('*') and part.endswith('*'):
            run.text = part[1:-1]; run.italic = True
        else:
            run.text = part

def set_academic_styles(doc):
    """Sets Arial 12pt, 1.5 spacing, and justified alignment globally."""
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(12)
    
    paragraph_format = style.paragraph_format
    paragraph_format.line_spacing = 1.5
    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph_format.space_after = Pt(0)
    paragraph_format.space_before = Pt(0)

def set_page_setup(doc):
    """Configures A4, 3.5cm inner margin, 2.0cm others, and Odd/Even paging."""
    section = doc.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    
    # User requested: Inner 3.5cm, others 2.0cm
    section.left_margin = Cm(3.5)
    section.right_margin = Cm(2.0)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    
    # Disable odd/even to ensure a single, consistent footer and prevent duplicates
    doc.settings.odd_and_even_pages_header_footer = False

def add_academic_footer(section):
    """Adds a single centered page number at the bottom of the page."""
    section.footer.is_linked_to_previous = False

    # Center-aligned footer
    footer = section.footer
    if not footer.paragraphs: footer.add_paragraph()
    p = footer.paragraphs[0]
    p.clear()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.font.name = 'Arial'
    run.font.size = Pt(12)
    add_field(run, "PAGE")

def convert_to_professional_docx(md_path, docx_path):
    print(f"Generating Diamond-Standard Document: {md_path} -> {docx_path}")
    doc = Document()
    set_academic_styles(doc)
    set_page_setup(doc)
    add_academic_footer(doc.sections[0])
    
    force_field_update(doc)
    set_toc_styles(doc)

    if not os.path.exists(md_path): return

    with open(md_path, 'r', encoding='utf-8') as f: lines = f.readlines()

    title = next((l.lstrip('#').strip() for l in lines if l.startswith('#')), "Academic Document")
    
    # 1. Title Page (Unnumbered)
    doc.add_heading(title, 0)
    doc.sections[0].footer.is_linked_to_previous = False
    doc.add_page_break()
    
    # 2. Blank Page (Unnumbered)
    doc.add_paragraph(" ")
    doc.add_page_break()

    # 3. Table of Contents Section
    toc_section = doc.add_section(WD_SECTION.NEW_PAGE)
    add_academic_footer(toc_section)
    
    # TOC Header
    p = doc.add_heading("Table of Contents", level=1)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Inject TOC Field
    p_toc = doc.add_paragraph()
    run_toc = p_toc.add_run()
    fldChar1 = create_element('w:fldChar'); create_attribute(fldChar1, 'w:fldCharType', 'begin')
    instrText = create_element('w:instrText'); create_attribute(instrText, 'xml:space', 'preserve')
    instrText.text = ' TOC \\o "1-3" \\h \\z \\u '
    fldChar2 = create_element('w:fldChar'); create_attribute(fldChar2, 'w:fldCharType', 'separate')
    fldChar3 = create_element('w:fldChar'); create_attribute(fldChar3, 'w:fldCharType', 'end')
    run_toc._r.append(fldChar1); run_toc._r.append(instrText); run_toc._r.append(fldChar2); run_toc._r.append(fldChar3)
    # Front matter list of figures / tables is removed from here
    # It will now be generated dynamically whenever their respective ## heading is encountered

    # Main Body Processing
    i = 0
    current_chapter = "1"
    current_chapter_title = ""
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('# ') or line == '---' or line == '***': i += 1; continue
        
        # Chapter start logic (Odd Page)
        if line.startswith('## '):
            level = 2
            # Roman numeral extraction for chapter numbering
            m = re.match(r'## ([IVXLCDM]+)\.', line)
            if m:
                current_chapter = m.group(1)
            else:
                # If no roman numeral, maybe try Arabic if the intro or something
                m_num = re.match(r'## (\d+)\.', line)
                if m_num: current_chapter = m_num.group(1)
            
            # Extract Chapter Name: everything after "## X. "
            title = line.lstrip('#').strip()
            # Determine if chapter should have number
            is_chapter = False
            if title.startswith('Appendix') or (title[0].isdigit() and title[1] == '.'):
                is_chapter = True
                current_chapter_title = re.sub(r'^(\d+\.|Appendix [A-Z]:)\s*', '', title)
                if title.startswith('Appendix'): current_chapter = title.split(':')[0].strip()
                else: current_chapter = title.split('.')[0].strip()
                
            # Formatting and spacing for chapters
            if is_chapter:
                new_section = doc.add_section(WD_SECTION.NEW_PAGE)
                add_academic_footer(new_section)
                p = doc.add_heading(title, 1)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p = doc.add_heading(title, 1)
                if title in ["List of Figures", "List of Tables"]: 
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else: 
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            p.paragraph_format.space_before = Pt(24)
            p.paragraph_format.space_after = Pt(12)
            
            # Dynamic generation of LOF/LOT fields
            if title == "List of Figures":
                p_lof = doc.add_paragraph()
                run_lof = p_lof.add_run()
                fldChar1 = create_element('w:fldChar'); create_attribute(fldChar1, 'w:fldCharType', 'begin')
                instrText = create_element('w:instrText'); create_attribute(instrText, 'xml:space', 'preserve')
                instrText.text = ' TOC \\h \\z \\t "Caption" \\c "FIGURE" '
                fldChar2 = create_element('w:fldChar'); create_attribute(fldChar2, 'w:fldCharType', 'separate')
                fldChar3 = create_element('w:fldChar'); create_attribute(fldChar3, 'w:fldCharType', 'end')
                run_lof._r.append(fldChar1); run_lof._r.append(instrText); run_lof._r.append(fldChar2); run_lof._r.append(fldChar3)
                
            elif title == "List of Tables":
                p_lot = doc.add_paragraph()
                run_lot = p_lot.add_run()
                fldChar1 = create_element('w:fldChar'); create_attribute(fldChar1, 'w:fldCharType', 'begin')
                instrText = create_element('w:instrText'); create_attribute(instrText, 'xml:space', 'preserve')
                instrText.text = ' TOC \\h \\z \\t "Caption" \\c "TABLE" '
                fldChar2 = create_element('w:fldChar'); create_attribute(fldChar2, 'w:fldCharType', 'separate')
                fldChar3 = create_element('w:fldChar'); create_attribute(fldChar3, 'w:fldCharType', 'end')
                run_lot._r.append(fldChar1); run_lot._r.append(instrText); run_lot._r.append(fldChar2); run_lot._r.append(fldChar3)
                
            i += 1
            continue

        if line.startswith('### '):
            doc.add_heading(line.lstrip('#').strip(), level=3)
            i += 1; continue

        if line.startswith('#### '):
            # Map level 4 headers to a bold Normal style to avoid 4444 numbering
            p = doc.add_paragraph(line.lstrip('#').strip(), style='Normal')
            p.runs[0].bold = True
            i += 1; continue

        # Table processing
        if line.startswith('|') or line.startswith('**Table'):
            table_caption = ""
            if line.startswith('**Table'):
                table_caption = line.strip('*').strip()
                i += 1; line = lines[i].strip() if i < len(lines) else ""
            
            # Caption ABOVE table
            if table_caption: add_caption(doc, "Table", table_caption, chapter_num=current_chapter, chapter_title=current_chapter_title)
            
            data = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                l = lines[i].strip()
                if '---' in l: i += 1; continue
                cols = [c.strip() for c in l.split('|') if c.strip()]
                if cols: data.append(cols)
                i += 1
            if data:
                table = doc.add_table(rows=len(data), cols=len(data[0])); table.style = 'Table Grid'
                for r, rd in enumerate(data):
                    for c, val in enumerate(rd): add_formatted_text(table.rows[r].cells[c].paragraphs[0], val, doc=doc, chapter_num=current_chapter, chapter_title=current_chapter_title)
            continue
            
        # Figure processing
        if line.startswith('!['):
            m = re.search(r'!\[(.*?)\]\((.*?)\)', line)
            if m:
                alt, p_path = m.groups()
                full_path = os.path.normpath(os.path.join(os.path.dirname(md_path), p_path))
                if os.path.exists(full_path):
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.paragraph_format.space_before = Pt(0)
                    p_img.paragraph_format.space_after = Pt(0)
                    run_img = p_img.add_run()
                    run_img.add_picture(full_path, width=Inches(6.0))
                    caption_line = lines[i+1].strip().strip('*') if i + 1 < len(lines) and "Figure" in lines[i+1] else alt
                    if i + 1 < len(lines) and "Figure" in lines[i+1]: i += 1
                    # Caption BELOW figure
                    add_caption(doc, "Figure", caption_line, chapter_num=current_chapter, chapter_title=current_chapter_title)
            i += 1; continue
            
        # Code block processing
        if line.startswith('```'):
            lang = line.replace('```', '').strip() or 'python'
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1 # skip ending ```
            
            # Syntax Highlighting
            add_highlighted_code(doc, "".join(code_lines), lang=lang)
            
            # Check for description below
            if i < len(lines) and lines[i].strip().startswith('**Code'):
                code_desc = lines[i].strip().strip('*')
                cp = doc.add_paragraph()
                cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run_desc = cp.add_run(code_desc)
                run_desc.italic = True; run_desc.font.size = Pt(10)
                i += 1
            continue

        if line.startswith('- ') or line.startswith('* '):
            p = doc.add_paragraph(style='List Bullet'); add_formatted_text(p, line[2:].strip(), doc=doc, chapter_num=current_chapter, chapter_title=current_chapter_title); i += 1; continue
            
        p = doc.add_paragraph(); p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; add_formatted_text(p, line, doc=doc, chapter_num=current_chapter, chapter_title=current_chapter_title); i += 1

    doc.save(docx_path)
    print(f"Professional Success: {docx_path}")

if __name__ == "__main__":
    convert_to_professional_docx('Final/thesis/source/thesis.md', 'Final/thesis/Thesis.docx')
    convert_to_professional_docx('Final/paper/source/paper.md', 'Final/paper/paper.docx')
