import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

os.makedirs('results/diagrams_minimal', exist_ok=True)

# ----------------------------------------------------
# 1. Generate Layout Detection Architecture
# ----------------------------------------------------
fig, ax = plt.subplots(figsize=(6, 8))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Document Background
doc = patches.Rectangle((10, 10), 80, 80, linewidth=2, edgecolor='black', facecolor='#fbfbfb')
ax.add_patch(doc)

# Header
header = patches.Rectangle((20, 75), 60, 10, linewidth=2, edgecolor='#3b82f6', facecolor='#dbeafe', linestyle='--')
ax.add_patch(header)
ax.text(50, 80, 'Header Text', ha='center', va='center', fontsize=12, fontweight='bold', color='black')

# Paragraph 1
para1 = patches.Rectangle((20, 55), 60, 15, linewidth=2, edgecolor='#10b981', facecolor='#d1fae5', linestyle='--')
ax.add_patch(para1)
ax.text(50, 62.5, 'Paragraph Text Block', ha='center', va='center', fontsize=10, color='black')

# Table Matrix
table = patches.Rectangle((20, 20), 60, 30, linewidth=2, edgecolor='#ef4444', facecolor='#fee2e2', linestyle='--')
ax.add_patch(table)
ax.text(50, 35, 'Dense Tabular Data Matrix', ha='center', va='center', fontsize=10, fontweight='bold', color='black')
# Table inner grid to show structure
ax.plot([40, 40], [20, 50], color='#ef4444', linewidth=1)
ax.plot([60, 60], [20, 50], color='#ef4444', linewidth=1)
ax.plot([20, 80], [40, 40], color='#ef4444', linewidth=1)
ax.plot([20, 80], [30, 30], color='#ef4444', linewidth=1)

# Annotations (The "Analysis")
ax.annotate('Header Region', xy=(80, 80), xytext=(85, 80), arrowprops=dict(facecolor='black', arrowstyle='->'))
ax.annotate('Text Region', xy=(80, 62.5), xytext=(85, 62.5), arrowprops=dict(facecolor='black', arrowstyle='->'))
ax.annotate('Table Layout', xy=(80, 35), xytext=(85, 35), arrowprops=dict(facecolor='black', arrowstyle='->'))

plt.title('PaddleOCR Layout Detection Logic', fontsize=14, pad=20)
plt.savefig('results/diagrams_minimal/layout_detection.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------
# 2. Skew Correction Diagram
# ----------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4))
ax.set_xlim(0, 100)
ax.set_ylim(0, 50)
ax.axis('off')

# Skewed box
skewed_box = patches.Polygon([[10, 20], [40, 30], [38, 38], [8, 28]], closed=True, 
                             linewidth=2, edgecolor='#3b82f6', facecolor='#eff6ff', linestyle='--')
ax.add_patch(skewed_box)
ax.text(24, 29, 'SKEWED TEXT', rotation=18, ha='center', va='center', fontsize=12, fontweight='bold', color='black')

# Transform Arrow
ax.annotate('', xy=(65, 25), xytext=(45, 25), arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8))
ax.text(55, 30, 'Direction\nClassifier', ha='center', va='center', fontsize=10)

# Corrected box
straight_box = patches.Rectangle((70, 20), 25, 10, linewidth=2, edgecolor='#10b981', facecolor='#ecfdf5', linestyle='-')
ax.add_patch(straight_box)
ax.text(82.5, 25, 'CORRECTED', ha='center', va='center', fontsize=12, fontweight='bold', color='black')

plt.title('PaddleOCR Skew and Orientation Normalization', fontsize=14, pad=10)
plt.savefig('results/diagrams_minimal/paddle_skew.png', dpi=300, bbox_inches='tight')
plt.close()

print("Layout visualization images generated successfully in results/diagrams_minimal/")
