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
plt.ylim(0, 1.0)
plt.legend(title="Accuracy Metric", loc='upper left', bbox_to_anchor=(1, 1))
save_plot(fig1, "accuracy_comparison.png")

# 2. Efficiency Comparison (Latency and Throughput)
fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(18, 9))
sns.barplot(data=df, x="Model", y="Total_Latency", ax=ax2a, palette=[academic_palette[0]])
ax2a.set_title("Inference Latency Breakdown")
ax2a.set_ylabel("Seconds per Document")
ax2a.set_xlabel("Perception Strategy")

sns.barplot(data=df, x="Model", y="Throughput", ax=ax2b, palette=[academic_palette[1]])
ax2b.set_title("System Throughput Capability")
ax2b.set_ylabel("Samples per Second")
ax2b.set_xlabel("Perception Strategy")

plt.suptitle("Operational Efficiency Analysis", fontsize=26, y=1.02)
# Add manual legends for colors
from matplotlib.lines import Line2D
custom_lines = [Line2D([0], [0], color=academic_palette[0], lw=8),
                Line2D([0], [0], color=academic_palette[1], lw=8)]
ax2b.legend(custom_lines, ['Latency Metric', 'Throughput Metric'], loc='upper left', bbox_to_anchor=(1, 1))

save_plot(fig2, "efficiency_comparison.png")

# 3. Peak Memory Usage
fig3 = plt.figure(figsize=(10, 8))
sns.barplot(data=df, x="Model", y="Memory_Used_MB", palette="mako")
plt.title("Infrastructure Resource Utilization", pad=20)
plt.ylabel("Peak RAM Footprint (MB)")
plt.xlabel("Perception Strategy")
# Add legend explaining bars
plt.legend([Line2D([0], [0], color="#2d5e7a", lw=8)], ['Peak Memory (RSS)'], loc='upper left', bbox_to_anchor=(1, 1))
save_plot(fig3, "memory_comparison.png")

# 4. Database Performance
fig4 = plt.figure(figsize=(12, 8))
# Filter out VLM if it has 0 values to avoid clutter
db_df = df[df['Model'] != 'VLM']
df_melted_db = db_df.melt(id_vars="Model", value_vars=["Retrieval_Latency", "Indexing_Time"], 
                             var_name="Operation", value_name="Time (s)")
sns.barplot(data=df_melted_db, x="Model", y="Time (s)", hue="Operation", palette="bone")
plt.title("Vector Database Temporal Performance", pad=20)
plt.ylabel("Inference Time (s)")
plt.xlabel("Strategy Using FAISS Indexing")
plt.legend(title="Indexing Phase", loc='upper left', bbox_to_anchor=(1, 1))
save_plot(fig4, "database_efficiency.png")

print("Plots successfully updated with improved academic formatting.")
