import os
import re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE

# Academic Blue Palette
BLUE_DEEP = RGBColor(30, 58, 138)
WHITE = RGBColor(255, 255, 255)

def style_title_slide(slide, title_text, subtitle_text):
    fill = slide.background.fill; fill.solid(); fill.fore_color.rgb = BLUE_DEEP
    title_shape = slide.shapes.title; title_shape.text = title_text
    for p in title_shape.text_frame.paragraphs:
        p.alignment = PP_ALIGN.CENTER; p.font.color.rgb = WHITE; p.font.bold = True; p.font.size = Pt(44)
    subtitle = slide.placeholders[1]; subtitle.text = subtitle_text
    for p in subtitle.text_frame.paragraphs:
        p.alignment = PP_ALIGN.CENTER; p.font.color.rgb = WHITE; p.font.size = Pt(28)

def add_slide_decorations(slide, current, total):
    """Adds branding and slide numbers."""
    # Top Accent
    shape = slide.shapes.add_shape(1, 0, 0, Inches(13.333), Inches(0.1)); shape.fill.solid(); shape.fill.fore_color.rgb = BLUE_DEEP; shape.line.fill.background()
    # Bottom Numbering
    if current > 0:
        box = slide.shapes.add_textbox(Inches(12.5), Inches(7.1), Inches(0.8), Inches(0.4))
        p = box.text_frame.paragraphs[0]; p.text = f"{current} / {total}"; p.font.size = Pt(12); p.font.color.rgb = BLUE_DEEP; p.alignment = PP_ALIGN.RIGHT

def generate_defense_deck(md_path, pptx_path):
    print(f"Generating Defense Deck: {md_path} -> {pptx_path}")
    prs = Presentation()
    prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)

    with open(md_path, 'r', encoding='utf-8') as f: content = f.read()
    slides_raw = [s for s in content.split('\n---\n') if s.strip()]

    for i, slide_md in enumerate(slides_raw):
        lines = [l.strip() for l in slide_md.split('\n') if l.strip()]
        if not lines: continue
        
        title, bullets, img_path = "", [], None
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
        
        # Header - Centered & Bold
        title_shape = slide.shapes.title; title_shape.text = title
        title_shape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        title_shape.text_frame.paragraphs[0].font.size = Pt(36); title_shape.text_frame.paragraphs[0].font.color.rgb = BLUE_DEEP
        
        for line in body_lines:
            if line.startswith('- ') or line.startswith('* '): bullets.append(line[2:].strip())
            elif '![' in line:
                m = re.search(r'!\[.*?\]\((.*?)\)', line); 
                if m:
                    p = os.path.normpath(os.path.join(os.path.dirname(md_path), m.group(1)))
                    if os.path.exists(p): img_path = p

        # Layout Logic: 1-Idea, Minimalist
        body_shape = slide.placeholders[1]; body_shape.text_frame.clear()
        body_shape.text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
        
        if img_path:
            body_shape.width = Inches(6.0); body_shape.left = Inches(0.5); body_shape.top = Inches(1.8)
            slide.shapes.add_picture(img_path, Inches(7.0), Inches(1.8), width=Inches(5.8))
        else:
            body_shape.width = Inches(11.0); body_shape.left = Inches(1.1); body_shape.top = Inches(2.2)

        # Enforce 3-5 Bullets, 24pt Min
        for b in bullets[:5]:
            p = body_shape.text_frame.add_paragraph(); p.text = b; p.level = 0
            p.font.size = Pt(24); p.font.name = 'Arial'; p.space_before = Pt(12); p.alignment = PP_ALIGN.LEFT

    prs.save(pptx_path)
    print(f"Defense Success: {pptx_path}")

if __name__ == "__main__":
    os.makedirs('Final_Academic_Package', exist_ok=True)
    generate_defense_deck('presentation/presentation.md', 'Final_Academic_Package/Presentation_Defense.pptx')
