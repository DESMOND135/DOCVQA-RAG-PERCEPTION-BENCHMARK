from PIL import Image
import os

img_path = r'c:\Users\Administrator\Downloads\THESIS PROJECT\figures\diagrams\paddleocr_academic.png'
out_path = r'c:\Users\Administrator\Downloads\THESIS PROJECT\figures\diagrams\paddleocr_academic_clean.png'

if os.path.exists(img_path):
    img = Image.open(img_path)
    width, height = img.size
    # Crop the bottom 10% or specifically the bottom caption area
    # Based on the visual, the caption is at the very bottom. 
    # Let's crop to 90% of height.
    cropped_img = img.crop((0, 0, width, int(height * 0.92)))
    cropped_img.save(out_path)
    print(f"Image cropped and saved to {out_path}")
else:
    print("Image not found.")
