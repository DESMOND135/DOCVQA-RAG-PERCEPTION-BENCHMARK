import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.lines import Line2D

# Load data
df = pd.read_csv("results/demo_summary.csv")
plots_dir = "results/plots"
os.makedirs(plots_dir, exist_ok=True)

# Set professional academic theme (The "First Example" design style)
sns.set_theme(style="whitegrid", context="talk")
academic_palette = ["#1e3a8a", "#64748b", "#334155", "#94a3b8"]
sns.set_palette(academic_palette)

# Global Font Settings for Final Polish
plt.rcParams.update({
    'font.size': 18,
    'axes.labelsize': 22,
    'axes.titlesize': 30,
    'xtick.labelsize': 18,
    'ytick.labelsize': 18,
    'legend.fontsize': 18,
    'legend.title_fontsize': 20,
    'font.weight': 'bold'
})

def save_max_visibility_plot(fig, filename):
    plt.tight_layout()
    fig.savefig(os.path.join(plots_dir, filename), dpi=300, bbox_inches='tight')
    plt.close(fig)

# 1. Accuracy Comparison (Final Edge Correction)
fig1 = plt.figure(figsize=(16, 12))
df_melted = df.melt(id_vars="Model", value_vars=["ANLS", "F1", "EM"], 
                    var_name="Metric", value_name="Score")
ax1 = sns.barplot(data=df_melted, x="Model", y="Score", hue="Metric")
plt.title("Benchmarking Information Extraction Accuracy", pad=35)
plt.ylabel("Normalized Accuracy Score")
plt.ylim(0, 1.4)
plt.legend(title="Accuracy Metric", loc='upper right', frameon=True, shadow=True)

# MASSIVE ANNOTATION BOX 1 - HYBRID
ax1.annotate('Hybrid model achieves highest accuracy (0.24 ANLS) by\nsynchronizing literal OCR precision with semantic VLM context.', 
             xy=(0, 0.24), xytext=(0.4, 1.05),
             arrowprops=dict(facecolor='#1e3a8a', shrink=0.05, width=6, headwidth=20, headlength=20),
             fontsize=18, fontweight='bold', bbox=dict(facecolor='white', alpha=1.0, edgecolor='#1e3a8a', linewidth=3, boxstyle='round,pad=1.5'))

# MASSIVE ANNOTATION BOX 2 - PADDLEOCR (SHIFTED INWARD TO PREVENT CLIPPING)
ax1.annotate('PaddleOCR fails Correct Match (0%) due to strict string\nformatting and character dataset requirements.', 
             xy=(3, 0.05), xytext=(1.2, 0.6), # Shifted xytext inward from 2.0 to 1.2
             arrowprops=dict(facecolor='#991b1b', shrink=0.05, width=6, headwidth=20, headlength=20),
             fontsize=16, color='#991b1b', fontweight='bold', bbox=dict(facecolor='white', alpha=1.0, edgecolor='#991b1b', linewidth=3, boxstyle='round,pad=1.2'))

save_max_visibility_plot(fig1, "accuracy_comparison.png")

# 2. Efficiency Comparison (Fixed Design)
fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(24, 12))
sns.barplot(data=df, x="Model", y="Total_Latency", ax=ax2a, palette=[academic_palette[0]])
ax2a.set_title("Inference Latency Breakdown")
ax2a.set_ylabel("Seconds per Document")
ax2a.set_ylim(0, 85)
ax2a.legend([Line2D([0], [0], color=academic_palette[0], lw=12)], ['Total Latency'], loc='upper right')

ax2a.annotate('Extreme 52.3s latency caused by sequential\nperception stages on CPU hardware.', 
             xy=(3, 52.3), xytext=(0.1, 75),
             arrowprops=dict(facecolor='#991b1b', shrink=0.05, width=6, headwidth=20, headlength=20),
             fontsize=18, color='#991b1b', fontweight='bold', bbox=dict(facecolor='white', alpha=1.0, edgecolor='#991b1b', linewidth=3, boxstyle='round,pad=1.5'))

sns.barplot(data=df, x="Model", y="Throughput", ax=ax2b, palette=[academic_palette[1]])
ax2b.set_title("System Throughput Capability")
ax2b.set_ylabel("Samples per Second")
ax2b.set_ylim(0, 0.55)
ax2b.legend([Line2D([0], [0], color=academic_palette[1], lw=12)], ['Throughput'], loc='upper right')

ax2b.annotate('VLM achieves 3.4x faster response times (4.2s)\nby sidestepping the complex OCR pipeline.', 
             xy=(1, 0.24), xytext=(1.2, 0.45),
             arrowprops=dict(facecolor='#1e3a8a', shrink=0.05, width=6, headwidth=20, headlength=20),
             fontsize=18, fontweight='bold', bbox=dict(facecolor='white', alpha=1.0, edgecolor='#1e3a8a', linewidth=3, boxstyle='round,pad=1.5'))

plt.suptitle("Operational Efficiency Analysis: The Accuracy-Speed Trade-off", fontsize=36, y=1.05, fontweight='bold')
save_max_visibility_plot(fig2, "efficiency_comparison.png")

# 3. Peak Memory Usage (Fixed Design)
fig3 = plt.figure(figsize=(14, 11))
sns.barplot(data=df, x="Model", y="Memory_Used_MB", palette="mako")
plt.title("Infrastructure Resource Utilization", pad=35)
plt.ylabel("Peak RAM Footprint (MB)")
plt.ylim(0, 7500)
plt.legend([Line2D([0], [0], color="#2d5e7a", lw=12)], ['Memory Usage'], loc='upper right')

ax3 = plt.gca()
ax3.annotate('Tesseract optimized for edge (350 MB)', 
             xy=(2, 350), xytext=(1.5, 2500),
             arrowprops=dict(facecolor='#065f46', shrink=0.05, width=6, headwidth=20, headlength=20),
             fontsize=18, color='#065f46', fontweight='bold', bbox=dict(facecolor='white', alpha=1.0, edgecolor='#065f46', linewidth=3, boxstyle='round,pad=1.5'))

ax3.annotate('Highest memory (4.6 GB) caused by\ndual transformer-based model stacks.', 
             xy=(0, 4600), xytext=(0.2, 6500),
             arrowprops=dict(facecolor='#991b1b', shrink=0.05, width=6, headwidth=20, headlength=20),
             fontsize=18, color='#991b1b', fontweight='bold', bbox=dict(facecolor='white', alpha=1.0, edgecolor='#991b1b', linewidth=3, boxstyle='round,pad=1.5'))

save_max_visibility_plot(fig3, "memory_comparison.png")

# 4. Database Performance (Fixed Design)
fig4 = plt.figure(figsize=(16, 11))
db_df = df[df['Model'] != 'VLM']
df_melted_db = db_df.melt(id_vars="Model", value_vars=["Retrieval_Latency", "Indexing_Time"], 
                             var_name="Operation", value_name="Time (s)")
ax4 = sns.barplot(data=df_melted_db, x="Model", y="Time (s)", hue="Operation", palette="bone")
plt.title("Vector Database Temporal Performance", pad=35)
plt.ylim(0, 0.45)
plt.legend(title="Operation", loc='upper right', frameon=True, shadow=True)

ax4.annotate('Search overhead is negligible (≤0.05s) because\nFAISS indices are optimized for fast retrieval.', 
             xy=(0.1, 0.05), xytext=(0.5, 0.35),
             arrowprops=dict(facecolor='#1e3a8a', shrink=0.05, width=6, headwidth=20, headlength=20),
             fontsize=18, fontweight='bold', bbox=dict(facecolor='white', alpha=1.0, edgecolor='#1e3a8a', linewidth=3, boxstyle='round,pad=1.5'))

save_max_visibility_plot(fig4, "database_efficiency.png")

print("Visuals successfully corrected and finalized with inward-shifted annotations.")
