import os
import csv
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, silhouette_score

warnings.filterwarnings("ignore")
os.makedirs("output", exist_ok=True)

# Dataset has no header; columns are identified by their positions.
rows = []
with open("data/pokec_100.txt", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        if len(row) == 60:
            rows.append(row)

df = pd.DataFrame(rows)
df.columns = ["col_" + str(i + 1) for i in range(60)]

df["completion_percentage"] = pd.to_numeric(df["col_3"], errors="coerce")
df["gender"] = df["col_4"].replace("null", np.nan)
df["region"] = df["col_5"].replace("null", np.nan)
df["last_login"] = pd.to_datetime(df["col_6"], errors="coerce")
df["registration"] = pd.to_datetime(df["col_7"], errors="coerce")
df["age"] = pd.to_numeric(df["col_8"], errors="coerce")
df.loc[df["age"] <= 0, "age"] = np.nan

df["days_since_registration"] = (
    df["last_login"] - df["registration"]
).dt.total_seconds() / 86400

df["days_since_registration"] = df["days_since_registration"].where(
    df["days_since_registration"] >= 0
)

# Multilabel text features: use simple indicators for hobbies and languages.
df["hobbies"] = df["col_12"].replace("null", "")
df["spoken_languages"] = df["col_11"].replace("null", "")

df["hobby_count"] = df["hobbies"].apply(
    lambda x: len([v for v in x.split(",") if v.strip()])
)
df["language_count"] = df["spoken_languages"].apply(
    lambda x: len([v for v in x.split(",") if v.strip()])
)

df["favourite_color"] = df["col_21"].replace("null", np.nan)

# Exclude identifiers and the target from predictors.
features = [
    "age", "gender", "region", "days_since_registration",
    "hobby_count", "language_count", "favourite_color"
]

data = df[features + ["completion_percentage"]].copy()
data = data.replace(["null", "", "None"], np.nan)
data = data.dropna(subset=["completion_percentage"])
data = data[
    data["completion_percentage"].between(0, 100)
].copy()

if len(data) < 10:
    raise ValueError("Too few valid records for train/test analysis.")

numeric_features = [
    "age", "days_since_registration", "hobby_count", "language_count"
]
categorical_features = [
    "gender", "region", "favourite_color"
]

# Use one shared split for fair model comparison.
X = data[features]
y = data["completion_percentage"]

# X_train, X_test, y_train, y_test = train_test_split(
#     X, y, test_size=0.20, random_state=42
# )
# Split 1: 70% training, 30% temporary data
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, random_state=42
)

# Split 2: divide remaining 30% equally into validation and test
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, random_state=42
)

print("\nDATA SPLIT")
print("Training records:", len(X_train))
print("Validation records:", len(X_val))
print("Testing records:", len(X_test))

def make_preprocessor():
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler())
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore"))
    ])
    return ColumnTransformer([
        ("numeric", numeric, numeric_features),
        ("categorical", categorical, categorical_features)
    ])

models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(
        n_estimators=100, random_state=42, min_samples_leaf=2
    )
}

# results = []
# for name, model in models.items():
#     pipeline = Pipeline([
#         ("preprocess", make_preprocessor()),
#         ("model", model)
#     ])
#     pipeline.fit(X_train, y_train)
#     pred = pipeline.predict(X_test)

#     results.append({
#         "Model": name,
#         "MAE": mean_absolute_error(y_test, pred),
#         "RMSE": np.sqrt(mean_squared_error(y_test, pred)),
#         "R2": r2_score(y_test, pred)
#     })

# results_df = pd.DataFrame(results)
# results_df.to_csv("output/model_results.csv", index=False)
# print("\nMODEL EVALUATION (small sample; test set = 20%)")
# print(results_df.to_string(index=False))

results = []

for name, model in models.items():
    pipeline = Pipeline([
        ("preprocess", make_preprocessor()),
        ("model", model)
    ])

    # Train the model using training data
    pipeline.fit(X_train, y_train)

    # Evaluate on validation data for model comparison
    val_pred = pipeline.predict(X_val)

    results.append({
        "Model": name,
        "Validation_MAE": mean_absolute_error(y_val, val_pred),
        "Validation_RMSE": np.sqrt(mean_squared_error(y_val, val_pred)),
        "Validation_R2": r2_score(y_val, val_pred)
    })

# Select the model with the lowest validation MAE
results_df = pd.DataFrame(results)
results_df.to_csv("output/model_results.csv", index=False)

print("\nVALIDATION RESULTS")
print(results_df.to_string(index=False))

best_model_name = results_df.loc[
    results_df["Validation_MAE"].idxmin(), "Model"
]

print("\nSelected model:", best_model_name)

# Evaluate the selected model once on the held-out test set
best_model = models[best_model_name]

final_pipeline = Pipeline([
    ("preprocess", make_preprocessor()),
    ("model", best_model)
])

final_pipeline.fit(X_train, y_train)
test_pred = final_pipeline.predict(X_test)

print("\nFINAL TEST RESULTS")
print("Test MAE:", round(mean_absolute_error(y_test, test_pred), 3))
print("Test RMSE:", round(np.sqrt(mean_squared_error(y_test, test_pred)), 3))
print("Test R2:", round(r2_score(y_test, test_pred), 3))

# Age and gender descriptive analysis.
print("\nVALID PROFILE ROWS:", len(df))
print("VALID AGE VALUES:", df["age"].notna().sum())
print("\nAVERAGE COMPLETION BY GENDER")
print(df.groupby("gender", dropna=True)["completion_percentage"].mean())

print("\nAVERAGE COMPLETION BY AGE GROUP")
df["age_group"] = pd.cut(
    df["age"],
    bins=[0, 19, 24, 29, 120],
    labels=["Under 20", "20-24", "25-29", "30+"]
)
print(df.groupby("age_group", observed=False)["completion_percentage"].agg(
    ["mean", "count"]
))

# # Correlation heatmap.
# corr = df[
#     ["completion_percentage", "age", "days_since_registration",
#      "hobby_count", "language_count"]
# ].corr(numeric_only=True)

# plt.figure(figsize=(8, 6))
# sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1)
# plt.title("Pokec Sample: Numerical Feature Correlations")
# plt.tight_layout()
# plt.savefig("output/correlation_heatmap.png", dpi=200)
# plt.close()

# # Required boxplot: completion by favourite color.
# plot_df = df.dropna(subset=["favourite_color", "completion_percentage"]).copy()
# top_colors = plot_df["favourite_color"].value_counts().head(8).index
# plot_df = plot_df[plot_df["favourite_color"].isin(top_colors)]

# if not plot_df.empty:
#     plt.figure(figsize=(10, 6))
#     sns.boxplot(data=plot_df, x="favourite_color", y="completion_percentage")
#     plt.xticks(rotation=35, ha="right")
#     plt.title("Completion Percentage by Favourite Color")
#     plt.tight_layout()
#     plt.savefig("output/completion_by_color.png", dpi=200)
#     plt.close()

# # K-Means clustering on scaled numerical features.
# cluster_cols = [
#     "age", "days_since_registration", "hobby_count",
#     "language_count", "completion_percentage"
# ]
# cluster_data = df[cluster_cols].copy()
# cluster_data = cluster_data.replace([np.inf, -np.inf], np.nan)
# cluster_data = cluster_data.dropna()

# if len(cluster_data) >= 10:
#     scaled = StandardScaler().fit_transform(cluster_data)
#     k = min(3, len(cluster_data) - 1)
#     labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(scaled)
#     cluster_data["cluster"] = labels

#     print("\nCLUSTER SUMMARY")
#     print(cluster_data.groupby("cluster").agg(
#         users=("completion_percentage", "size"),
#         average_completion=("completion_percentage", "mean"),
#         average_age=("age", "mean"),
#         average_registration_days=("days_since_registration", "mean")
#     ))

#     if len(set(labels)) > 1 and len(set(labels)) < len(labels):
#         print("Silhouette score:", round(silhouette_score(scaled, labels), 3))

#     cluster_data.to_csv("output/cluster_assignments.csv", index=False)

#     plt.figure(figsize=(8, 5))
#     sns.boxplot(data=cluster_data, x="cluster", y="completion_percentage")
#     plt.title("Completion Percentage by K-Means Cluster")
#     plt.tight_layout()
#     plt.savefig("output/completion_by_cluster.png", dpi=200)
#     plt.close()

# print("\nAnalysis complete. Check the output folder for CSV files and plots.")
# Professional chart styling
sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.titlepad"] = 14

# 1. Professional correlation heatmap
corr = df[
    ["completion_percentage", "age", "days_since_registration",
     "hobby_count", "language_count"]
].corr(numeric_only=True)

fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="vlag",
    vmin=-1,
    vmax=1,
    center=0,
    square=True,
    linewidths=1,
    linecolor="white",
    annot_kws={"size": 11, "weight": "bold"},
    cbar_kws={"shrink": 0.8, "label": "Correlation coefficient"},
    ax=ax
)
ax.set_title("Pokec Sample: Numerical Feature Correlations", fontsize=14)
ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha="right")
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
fig.tight_layout()
fig.savefig("output/correlation_heatmap.png", bbox_inches="tight")
plt.close(fig)

# 2. Professional boxplot: completion by favourite color
plot_df = df.dropna(
    subset=["favourite_color", "completion_percentage"]
).copy()

top_colors = plot_df["favourite_color"].value_counts().head(8).index
plot_df = plot_df[plot_df["favourite_color"].isin(top_colors)]

if not plot_df.empty:
    color_order = plot_df["favourite_color"].value_counts().index.tolist()
    palette = sns.color_palette("Set2", n_colors=len(color_order))

    fig, ax = plt.subplots(figsize=(11, 6.5))
    sns.boxplot(
        data=plot_df,
        x="favourite_color",
        y="completion_percentage",
        order=color_order,
        hue="favourite_color",
        hue_order=color_order,
        palette=palette,
        legend=False,
        width=0.62,
        linewidth=1.4,
        fliersize=3,
        ax=ax
    )
    ax.set_title("Profile Completion by Favourite Color", fontsize=14)
    ax.set_xlabel("Favourite color", fontsize=11, labelpad=8)
    ax.set_ylabel("Profile completion (%)", fontsize=11, labelpad=8)
    ax.set_ylim(0, 100)
    ax.tick_params(axis="x", rotation=30)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.grid(axis="x", visible=False)
    sns.despine(ax=ax, left=False, bottom=True)
    fig.tight_layout()
    fig.savefig("output/completion_by_color.png", bbox_inches="tight")
    plt.close(fig)

# 3. Professional boxplot: completion by K-Means cluster
cluster_cols = [
    "age", "days_since_registration", "hobby_count",
    "language_count", "completion_percentage"
]
cluster_data = df[cluster_cols].copy()
cluster_data = cluster_data.replace([np.inf, -np.inf], np.nan)
cluster_data = cluster_data.dropna()

if len(cluster_data) >= 10:
    scaled = StandardScaler().fit_transform(cluster_data)
    k = min(3, len(cluster_data) - 1)
    labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(scaled)
    cluster_data["cluster"] = labels

    print("\nCLUSTER SUMMARY")
    print(cluster_data.groupby("cluster").agg(
        users=("completion_percentage", "size"),
        average_completion=("completion_percentage", "mean"),
        average_age=("age", "mean"),
        average_registration_days=("days_since_registration", "mean")
    ))

    if len(set(labels)) > 1 and len(set(labels)) < len(labels):
        print("Silhouette score:", round(silhouette_score(scaled, labels), 3))

    cluster_data.to_csv("output/cluster_assignments.csv", index=False)

    # Professional multicolor K-Means cluster plot
    fig, ax = plt.subplots(figsize=(11, 7))

    cluster_order = sorted(cluster_data["cluster"].unique())
    cluster_palette = {
        0: "#2E86DE",  # Blue
        1: "#FF851B",  # Orange
        2: "#28A745"   # Green
    }

    # Colored boxplots
    sns.boxplot(
        data=cluster_data,
        x="cluster",
        y="completion_percentage",
        order=cluster_order,
        hue="cluster",
        hue_order=cluster_order,
        palette=cluster_palette,
        legend=False,
        width=0.52,
        linewidth=1.5,
        fliersize=0,
        saturation=0.65,
        ax=ax
    )

    # Different colored dots for each cluster
    sns.stripplot(
        data=cluster_data,
        x="cluster",
        y="completion_percentage",
        order=cluster_order,
        hue="cluster",
        hue_order=cluster_order,
        palette=cluster_palette,
        dodge=False,
        jitter=0.10,
        size=6,
        alpha=0.75,
        edgecolor="white",
        linewidth=0.3,
        legend=False,
        ax=ax
    )

    # Title, labels and styling
    ax.set_title(
        "Profile Completion by K-Means Cluster",
        fontsize=17,
        fontweight="bold",
        pad=18
    )
    ax.set_xlabel("K-Means cluster", fontsize=13, labelpad=10)
    ax.set_ylabel("Profile completion (%)", fontsize=13, labelpad=10)
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 20))
    ax.tick_params(axis="both", labelsize=11)

    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.grid(axis="x", visible=False)
    sns.despine(ax=ax)

    # Legend with matching dot colors
    from matplotlib.lines import Line2D

    legend_handles = [
        Line2D(
            [0], [0],
            marker="o",
            color="w",
            label=f"Cluster {c}",
            markerfacecolor=cluster_palette[c],
            markersize=9
        )
        for c in cluster_order
    ]

    ax.legend(
        handles=legend_handles,
        title="Cluster",
        loc="upper left",
        bbox_to_anchor=(1.01, 1),
        frameon=True
    )

    fig.tight_layout()
    fig.savefig(
        "output/completion_by_cluster.png",
        dpi=300,
        bbox_inches="tight",
        facecolor="white"
    )
    plt.close(fig)