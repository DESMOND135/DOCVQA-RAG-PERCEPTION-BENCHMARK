import os
import re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE

import matplotlib.pyplot as plt
from matplotlib import mathtext

# Professional Academic Palette
BLUE_NAVY = RGBColor(0, 51, 102) # #003366
BLUE_ARXIV = RGBColor(31, 119, 180) # #1f77b4
WHITE = RGBColor(255, 255, 255)
BLACK = RGBColor(0, 0, 0)

def render_latex_to_image(latex, out_path):
    """Renders a LaTeX string into a high-resolution transparent PNG in BLACK."""
    fig = plt.figure(figsize=(10, 2))
    # Academic Standard: Formulas MUST be BLACK
    text = fig.text(
        0.5, 0.5, f"${latex}$",
        ha='center', va='center', fontsize=50, color='#000000'
    )
    fig.savefig(out_path, transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=300)
    plt.close(fig)

def style_title_slide(slide, title_text, subtitle_text):
    fill = slide.background.fill; fill.solid(); fill.fore_color.rgb = BLUE_NAVY
    title_shape = slide.shapes.title; title_shape.text = title_text
    for p in title_shape.text_frame.paragraphs:
        p.alignment = PP_ALIGN.CENTER; p.font.color.rgb = WHITE; p.font.bold = True; p.font.size = Pt(44)
    subtitle = slide.placeholders[1]; subtitle.text = subtitle_text
    for p in subtitle.text_frame.paragraphs:
        p.alignment = PP_ALIGN.CENTER; p.font.color.rgb = WHITE; p.font.size = Pt(24)

def add_slide_decorations(slide, current, total):
    """Adds branding and slide numbers with professional Navy accent."""
    if current > 0:
        # Progress bar at bottom
        bar_width = (current / total) * 13.333
        bar = slide.shapes.add_shape(6, 0, Inches(7.4), Inches(bar_width), Inches(0.1))
        bar.fill.solid(); bar.fill.fore_color.rgb = BLUE_NAVY; bar.line.fill.background()
        
        box = slide.shapes.add_textbox(Inches(12.5), Inches(7.0), Inches(0.8), Inches(0.4))
        p = box.text_frame.paragraphs[0]; p.text = f"{current} / {total}"
        p.font.size = Pt(10); p.font.color.rgb = BLUE_NAVY; p.alignment = PP_ALIGN.RIGHT

def generate_defense_deck(md_path, pptx_path):
    print(f"Generating Presentation Deck: {md_path} -> {pptx_path}")
    prs = Presentation()
    prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)

    with open(md_path, 'r', encoding='utf-8') as f: content = f.read()
    slides_raw = [s for s in content.split('\n---\n') if s.strip()]

    for i, slide_md in enumerate(slides_raw):
        lines = [l.strip() for l in slide_md.split('\n') if l.strip()]
        if not lines: continue
        
        title, bullets, img_path, table_data = "Document Section", [], None, []
        if lines[0].startswith('#'):
            title = lines[0].lstrip('#').strip(); body_lines = lines[1:]
        else:
            body_lines = lines

        if i == 0:
            slide = prs.slides.add_slide(prs.slide_layouts[0])
            style_title_slide(slide, title, "\n".join(body_lines[:2]))
            continue

        slide = prs.slides.add_slide(prs.slide_layouts[1])
        add_slide_decorations(slide, i, len(slides_raw)-1)
        
        # Header - ALWAYS CENTRALIZED
        title_shape = slide.shapes.title; title_shape.text = title
        title_shape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        title_shape.text_frame.paragraphs[0].font.size = Pt(32); title_shape.text_frame.paragraphs[0].font.color.rgb = BLUE_NAVY
        title_shape.text_frame.paragraphs[0].font.bold = True
        
        for line in body_lines:
            if line.startswith('- ') or line.startswith('* '):
                bullets.append(line[2:].strip())
            elif line.startswith('|'):
                if '---' not in line:
                    cols = [c.strip() for c in line.split('|') if c.strip()]
                    if cols: table_data.append(cols)
            elif '$$' in line:
                m = re.search(r'\$\$(.*?)\$\$', line)
                if m:
                    latex = m.group(1).strip()
                    os.makedirs('temp_math', exist_ok=True)
                    math_img = os.path.join('temp_math', f'math_{i}.png')
                    render_latex_to_image(latex, math_img)
                    img_path = math_img
            elif '![' in line:
                m = re.search(r'!\[.*?\]\((.*?)\)', line); 
                if m:
                    p = os.path.normpath(os.path.join(os.path.dirname(md_path), m.group(1)))
                    if os.path.exists(p): img_path = p

        # Content Layout
        content_area = slide.placeholders[1]; content_area.text_frame.clear()
        
        if img_path:
            # DIAGRAMS GET THEIR OWN SPACE (Centralized)
            if "temp_math" in img_path:
                # Equation: Center large
                pic = slide.shapes.add_picture(img_path, Inches(2.0), Inches(2.5), width=Inches(9.3))
                pic.left = int((prs.slide_width - pic.width) / 2)
            else:
                # Diagram: Large center, no bullets if present
                pic = slide.shapes.add_picture(img_path, Inches(1.5), Inches(1.8), width=Inches(10.3))
                pic.left = int((prs.slide_width - pic.width) / 2)
                if pic.height > Inches(5.0): pic.height = Inches(5.0); pic.left = int((prs.slide_width - pic.width) / 2)
            
            # Hide bullets if there's an image on the slide to keep it clean
            if bullets:
                # If there are bullets, put them below or small
                content_area.width = Inches(12.0); content_area.left = Inches(0.6); content_area.top = Inches(6.5)
        elif table_data:
            content_area.width = Inches(12.0); content_area.left = Inches(0.6); content_area.top = Inches(1.5)
            rows, cols = len(table_data), len(table_data[0])
            table = slide.shapes.add_table(rows, cols, Inches(1.0), Inches(2.5), Inches(11.3), Inches(3.0)).table
            for r in range(rows):
                for c in range(cols):
                    cell = table.cell(r, c)
                    cell.text = table_data[r][c]
                    p = cell.text_frame.paragraphs[0]
                    p.font.size = Pt(18); p.font.bold = (r == 0)
                    p.alignment = PP_ALIGN.CENTER
                    if r == 0: cell.fill.solid(); cell.fill.fore_color.rgb = BLUE_NAVY; p.font.color.rgb = WHITE
        else:
            content_area.width = Inches(11.5); content_area.left = Inches(0.9); content_area.top = Inches(1.8)

        # Bullets - Refined
        for b_text in bullets:
            p = content_area.text_frame.add_paragraph()
            p.level = 0; p.space_after = Pt(14)
            p.alignment = PP_ALIGN.CENTER if img_path else PP_ALIGN.LEFT
            
            parts = re.split(r'(\*\*.*?\*\*|\*.*?\*)', b_text)
            for part in parts:
                run = p.add_run()
                if part.startswith('**'): run.text = part[2:-2]; run.font.bold = True
                elif part.startswith('*'): run.text = part[1:-1]; run.font.italic = True
                else: run.text = part
                run.font.size = Pt(22) if img_path else Pt(26)
                run.font.name = 'Calibri'; run.font.color.rgb = BLACK

    prs.save(pptx_path)
    print(f"Presentation Generated: {pptx_path}")

if __name__ == "__main__":
    generate_defense_deck('presentation/presentation.md', 'presentation/presentation.pptx')
