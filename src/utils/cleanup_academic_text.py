import re
import os

def cleanup_text(text):
    # Rule 4: No multiple spaces
    text = re.sub(r' +', ' ', text)
    # Rule 4: No space before punctuation
    text = re.sub(r' ([,.:;?!)\]}>”’])', r'\1', text)
    # Rule 4: No space after opening brackets or quotes
    text = re.sub(r'([\[{(«“‘]) ', r'\1', text)
    # Rule 11: Quotations nested quotes << >> into « »
    text = text.replace('<<', '«').replace('>>', '»')
    
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        # Rule 4: Do not start paragraphs with space
        clean_line = line.lstrip(' ')
        # Rule 4: No space at end of paragraph
        clean_line = clean_line.rstrip(' ')
        
        # Rule 5: No full stop at end of headings
        if clean_line.startswith('#'):
            clean_line = clean_line.rstrip('.')
            
        new_lines.append(clean_line)
    
    text = '\n'.join(new_lines)
    return text

def process_file(path):
    if not os.path.exists(path): 
        print(f"Skipping: {path} (Not found)")
        return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = cleanup_text(content)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    process_file('Final/thesis/source/thesis.md')
    process_file('Final/paper/source/paper.md')
    print("Academic text cleanup complete.")
