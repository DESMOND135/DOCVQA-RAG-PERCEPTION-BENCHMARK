import fitz
import json

doc = fitz.open("Thesis_correction.pdf")
output = []
for page in doc:
    for annot in page.annots():
        info = annot.info
        rect = annot.rect
        
        # Get text in the rectangle
        text_in_rect = page.get_text("text", clip=rect).strip()
        # If no text in rect, maybe expand a bit
        if not text_in_rect:
            rect.x0 = max(0, rect.x0 - 20)
            rect.y0 = max(0, rect.y0 - 20)
            rect.x1 = min(page.rect.x1, rect.x1 + 20)
            rect.y1 = min(page.rect.y1, rect.y1 + 20)
            text_in_rect = page.get_text("text", clip=rect).strip()
            
        content = info.get('content')
        if content:
            output.append({
                "page": page.number,
                "comment": content,
                "context": text_in_rect
            })

with open("annotations.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
