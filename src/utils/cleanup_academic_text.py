import re
import os

def cleanup_text(text):
    # Rule 2: No multiple spaces
    text = re.sub(r' +', ' ', text)
    # Rule 2: No space before punctuation
    text = re.sub(r' ([,.:;?!)\]}>”’])', r'\1', text)
    # Rule 2: No space after opening brackets or open quotes
    text = re.sub(r'([\[{(„‘]) ', r'\1', text)
    # Rule 2: No space at end of paragraph
    text = re.sub(r' \n', r'\n', text)
    # Rule 2: Titles should not end with period
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('#'):
            line = line.rstrip('.')
        new_lines.append(line)
    text = '\n'.join(new_lines)
    return text

def process_file(path):
    if not os.path.exists(path): return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = cleanup_text(content)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    process_file('Deliverable/thesis/source/thesis.md')
    process_file('Deliverable/paper/source/paper.md')
    print("Academic text cleanup complete.")
