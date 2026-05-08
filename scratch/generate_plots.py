import matplotlib.pyplot as plt
import numpy as np
import os

# Data from Table 1
models = ['Hybrid', 'VLM', 'Tesseract', 'PaddleOCR']
anls = [0.24, 0.17, 0.17, 0.13]
f1 = [0.30, 0.20, 0.30, 0.10]
latency = [14.2, 4.2, 11.0, 52.3]
throughput = [0.07, 0.24, 0.09, 0.02]
memory = [4600, 4100, 350, 850]
indexing = [0.12, 0.00, 0.12, 0.12]
retrieval = [0.05, 0.00, 0.05, 0.05]

out_dir = r'c:\Users\Administrator\Downloads\THESIS PROJECT\figures\plots'
os.makedirs(out_dir, exist_ok=True)

# 1. Figure 5.1: Accuracy Benchmark Results (ANLS vs F1)
plt.figure(figsize=(10, 6))
x = np.arange(len(models))
width = 0.35
plt.bar(x - width/2, anls, width, label='ANLS', color='#1e3a8a')
plt.bar(x + width/2, f1, width, label='F1-Score', color='#3b82f6')
plt.ylabel('Score')
plt.title('Accuracy Benchmark: ANLS and F1-Score')
plt.xticks(x, models)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig(os.path.join(out_dir, 'accuracy_comparison.png'), dpi=300)
plt.close()

# 2. Figure 5.2: System Latency and Throughput Inversion
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.bar(x - width/2, latency, width, label='Latency (s)', color='#ef4444')
ax1.set_ylabel('Latency (seconds)', color='#ef4444')
ax1.tick_params(axis='y', labelcolor='#ef4444')

ax2 = ax1.twinx()
ax2.bar(x + width/2, throughput, width, label='Throughput (S/s)', color='#10b981')
ax2.set_ylabel('Throughput (Samples/s)', color='#10b981')
ax2.tick_params(axis='y', labelcolor='#10b981')

plt.title('Latency vs Throughput Inversion')
ax1.set_xticks(x)
ax1.set_xticklabels(models)
plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.savefig(os.path.join(out_dir, 'efficiency_comparison.png'), dpi=300)
plt.close()

# 3. Figure 5.3: Peak Memory Footprint
plt.figure(figsize=(10, 6))
plt.bar(models, memory, color='#8b5cf6')
plt.ylabel('Peak Memory Usage (MB)')
plt.title('Resident Set Size (RSS) Peak Memory Usage')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig(os.path.join(out_dir, 'memory_comparison.png'), dpi=300)
plt.close()

# 4. Figure 5.4: Retrieval vs Indexing Latency
plt.figure(figsize=(10, 6))
plt.bar(x - width/2, indexing, width, label='Indexing Overhead', color='#f59e0b')
plt.bar(x + width/2, retrieval, width, label='Retrieval Latency', color='#6366f1')
plt.ylabel('Time (seconds)')
plt.title('Database Efficiency: Indexing vs Retrieval Latency')
plt.xticks(x, models)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig(os.path.join(out_dir, 'database_efficiency.png'), dpi=300)
plt.close()

# 5. Figure 6.1: Accuracy Tradeoff Analysis (Scatter Plot)
plt.figure(figsize=(10, 6))
colors = ['#1e3a8a', '#ef4444', '#10b981', '#f59e0b']
for i, model in enumerate(models):
    plt.scatter(latency[i], anls[i], s=200, label=model, color=colors[i], edgecolors='black')
    plt.text(latency[i]+1, anls[i], model, fontsize=12, fontweight='bold')

plt.xlabel('Latency (seconds) - Lower is Better')
plt.ylabel('ANLS Score - Higher is Better')
plt.title('Accuracy-Efficiency Frontier: ANLS vs Latency')
plt.grid(linestyle='--', alpha=0.7)
# Annotate the Pareto frontier direction
plt.arrow(50, 0.14, -30, 0.08, head_width=0.005, head_length=2, fc='black', ec='black', alpha=0.5)
plt.text(30, 0.22, 'Optimal Direction', fontsize=10, fontstyle='italic')
plt.savefig(os.path.join(out_dir, 'accuracy_tradeoff.png'), dpi=300)
plt.close()

print("All 5 benchmark plots generated successfully in figures/plots/")
