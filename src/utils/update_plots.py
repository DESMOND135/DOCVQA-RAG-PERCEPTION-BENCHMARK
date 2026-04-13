import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load data
df = pd.read_csv("results/demo_summary.csv")
plots_dir = "results/plots"
os.makedirs(plots_dir, exist_ok=True)

# Set professional academic theme
sns.set_theme(style="whitegrid", context="talk")
# Use the requested color palette: Deep Blue (#1e3a8a) and Slate Gray (#64748b)
academic_palette = ["#1e3a8a", "#64748b", "#334155", "#94a3b8"]
sns.set_palette(academic_palette)

# Global font settings for high visibility
plt.rcParams.update({
    'font.size': 14,
    'axes.labelsize': 18,
    'axes.titlesize': 22,
    'xtick.labelsize': 15,
    'ytick.labelsize': 15,
    'legend.fontsize': 16,
    'legend.title_fontsize': 18
})

def save_plot(fig, filename):
    plt.tight_layout()
    fig.savefig(os.path.join(plots_dir, filename), dpi=300, bbox_inches='tight')
    plt.close(fig)

# 1. Accuracy Comparison
fig1 = plt.figure(figsize=(12, 8))
df_melted = df.melt(id_vars="Model", value_vars=["ANLS", "F1", "EM"], 
                    var_name="Metric", value_name="Score")
ax1 = sns.barplot(data=df_melted, x="Model", y="Score", hue="Metric")
plt.title("Benchmarking Information Extraction Accuracy", pad=20)
plt.ylabel("Normalized Accuracy Score")
plt.xlabel("Perception Module Strategy")
plt.ylim(0, 1.2) # Extra space for annotations
plt.legend(title="Accuracy Metric", loc='upper right')

# Insights Inside Accuracy Graph
ax1.annotate('Highest Accuracy (ANLS: 0.24)\nBest for Precision Audit', 
             xy=(0, 0.3), xytext=(0.5, 0.8),
             arrowprops=dict(facecolor='black', shrink=0.05, width=2),
             fontsize=14, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8))

ax1.annotate('0% Exact Match failure\ndue to strict formatting', 
             xy=(3, 0.05), xytext=(2.0, 0.15),
             arrowprops=dict(facecolor='red', shrink=0.05, width=2),
             fontsize=14, color='red', bbox=dict(facecolor='white', alpha=0.8))

save_plot(fig1, "accuracy_comparison.png")

# 2. Efficiency Comparison (Latency and Throughput)
fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(20, 10))
sns.barplot(data=df, x="Model", y="Total_Latency", ax=ax2a, palette=[academic_palette[0]])
ax2a.set_title("Inference Latency Breakdown")
ax2a.set_ylabel("Seconds per Document")
ax2a.set_ylim(0, 70)

# Insight on Latency
ax2a.annotate('Extreme CPU Bottleneck\n(52.3 seconds)', 
             xy=(3, 52.3), xytext=(1.5, 60),
             arrowprops=dict(facecolor='red', shrink=0.05, width=2),
             fontsize=14, color='red', bbox=dict(facecolor='white', alpha=0.8))

sns.barplot(data=df, x="Model", y="Throughput", ax=ax2b, palette=[academic_palette[1]])
ax2b.set_title("System Throughput Capability")
ax2b.set_ylabel("Samples per Second")
ax2b.set_ylim(0, 0.4)

# Insight on Throughput
ax2b.annotate('Fastest Real-Time Throughput\n(3.4x faster than Hybrid)', 
             xy=(1, 0.24), xytext=(1.5, 0.35),
             arrowprops=dict(facecolor='black', shrink=0.05, width=2),
             fontsize=14, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8))

plt.suptitle("Operational Efficiency Analysis", fontsize=26, y=1.02)
save_plot(fig2, "efficiency_comparison.png")

# 3. Peak Memory Usage
fig3 = plt.figure(figsize=(10, 8))
sns.barplot(data=df, x="Model", y="Memory_Used_MB", palette="mako")
plt.title("Infrastructure Resource Utilization", pad=20)
plt.ylabel("Peak RAM Footprint (MB)")
plt.ylim(0, 6000)

# Insight on Memory
ax3 = plt.gca()
ax3.annotate('Edge Ready\n(350 MB)', 
             xy=(2, 350), xytext=(2.5, 1500),
             arrowprops=dict(facecolor='green', shrink=0.05, width=2),
             fontsize=14, color='green', fontweight='bold', bbox=dict(facecolor='white', alpha=0.8))

ax3.annotate('Resource Intensive\nDual-Model Stack (4.6 GB)', 
             xy=(0, 4600), xytext=(0.5, 5500),
             arrowprops=dict(facecolor='red', shrink=0.05, width=2),
             fontsize=14, color='red', bbox=dict(facecolor='white', alpha=0.8))

save_plot(fig3, "memory_comparison.png")

# 4. Database Performance
fig4 = plt.figure(figsize=(12, 8))
db_df = df[df['Model'] != 'VLM']
df_melted_db = db_df.melt(id_vars="Model", value_vars=["Retrieval_Latency", "Indexing_Time"], 
                             var_name="Operation", value_name="Time (s)")
ax4 = sns.barplot(data=df_melted_db, x="Model", y="Time (s)", hue="Operation", palette="bone")
plt.title("Vector Database Temporal Performance", pad=20)
plt.ylim(0, 0.25)

# Insight on Database
ax4.annotate('Retrieval is Negligible\n(FAISS is optimized)', 
             xy=(0, 0.05), xytext=(0.5, 0.2),
             arrowprops=dict(facecolor='black', shrink=0.05, width=2),
             fontsize=14, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8))

save_plot(fig4, "database_efficiency.png")

print("Annotated plots successfully updated with in-graph insights.")
