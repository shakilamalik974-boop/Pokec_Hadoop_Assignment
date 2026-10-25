import os
import random
import matplotlib.pyplot as plt

file_path = r"E:\Pokec_Hadoop_Assignment\cluster_completion_values.tsv"
output_dir = r"E:\Pokec_Hadoop_Assignment\output"
os.makedirs(output_dir, exist_ok=True)

data = {0: [], 1: [], 2: []}

with open(file_path, "r", encoding="utf-16") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) >= 2:
            cluster = int(parts[0])
            completion = float(parts[1])
            if cluster in data:
                data[cluster].append(completion)

clusters = [0, 1, 2]
colors = ["#4C78A8", "#F58518", "#54A24B"]

for c in clusters:
    print("Cluster", c, "- users:", len(data[c]))

fig, ax = plt.subplots(figsize=(9, 6))
plot_data = [data[c] for c in clusters]

bp = ax.boxplot(
    plot_data,
    patch_artist=True,
    labels=["Cluster 0", "Cluster 1", "Cluster 2"],
    widths=0.5
)

for patch, color in zip(bp["boxes"], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.75)

random.seed(42)
for i, (values, color) in enumerate(zip(plot_data, colors), start=1):
    jitter = [i + random.uniform(-0.09, 0.09) for _ in values]
    ax.scatter(jitter, values, color=color, edgecolors="black",
               s=35, alpha=0.85, zorder=3)

ax.set_title("Profile Completion by K-Means Cluster")
ax.set_xlabel("K-Means Cluster")
ax.set_ylabel("Completion Percentage")
ax.set_ylim(0, 105)
ax.grid(axis="y", linestyle="--", alpha=0.35)
plt.tight_layout()

output_file = os.path.join(output_dir, "completion_by_cluster_boxplot.png")
plt.savefig(output_file, dpi=300, bbox_inches="tight")
print("Plot saved:", output_file)
plt.show()

