import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Pokec Hadoop Analytics",
    page_icon="📊",
    layout="wide"
)

BASE = Path(__file__).parent
OUTPUT = BASE / "output"

st.title("📊 Pokec Social Network Analytics")
st.caption("Hadoop HDFS | MapReduce | Machine Learning")

st.markdown("""
This dashboard presents the analysis of the Pokec social network
dataset using MapReduce processing and machine learning.
""")

st.divider()

# Dataset overview
st.header("1. Dataset Analysis")

col1, col2, col3 = st.columns(3)

col1.metric("Dataset Records", "100")
col2.metric("Valid Age Records", "77")
col3.metric("Average Completion", "44.58%")

st.divider()

# Model results
st.header("2. Machine Learning Results")

model_file = OUTPUT / "model_results.csv"

if model_file.exists():
    df = pd.read_csv(model_file)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Model results file not found.")

st.divider()

# Clustering
st.header("3. K-Means Clustering")

cluster_file = OUTPUT / "cluster_assignments.csv"

if cluster_file.exists():
    clusters = pd.read_csv(cluster_file)
    st.dataframe(clusters.head(20), use_container_width=True)

# Visualizations
st.header("4. Data Visualizations")

plots = [
    ("Completion by Cluster", "completion_by_cluster_boxplot.png"),
    ("Completion by Favourite Color", "completion_by_color.png"),
    ("Correlation Heatmap", "correlation_heatmap.png"),
]

for title, filename in plots:
    path = OUTPUT / filename
    if path.exists():
        st.subheader(title)
        st.image(str(path), use_container_width=True)

st.divider()

st.header("5. MapReduce Processing")

st.write("""
The project uses Hadoop Streaming and MapReduce for:
- Feature analysis
- Missing value and outlier analysis
- Categorical encoding
- Hobbies and spoken languages analysis
- Registration days calculation
- Data normalization
- K-Means clustering
""")

st.success("Pokec analytics dashboard loaded successfully.")

st.caption("MS Computer Science | Advanced Operating Systems Assignment")