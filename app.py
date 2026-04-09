import streamlit as st
import os
import time
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.pipeline.pipeline import DocVQAPipeline
from src.config.config import CONFIG
from src.logging.logger import get_logger

# Page configuration
st.set_page_config(
    page_title="Research DocVQA Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger = get_logger(__name__)

# --- Sidebar ---
st.sidebar.title("Configuration")
perception_mode = st.sidebar.selectbox(
    "Choose Perception Engine",
    ["Tesseract", "PaddleOCR", "VLM", "Hybrid"],
    help="Tesseract: Industry standard OCR\nPaddleOCR: High-accuracy deep learning OCR\nVLM: Pure Visual Question Answering\nHybrid: Combined OCR + Visual Summary"
)

st.sidebar.divider()
st.sidebar.markdown("""
### About this Project
This dashboard is part of a Master's Thesis research comparing different document perception strategies for Visual Question Answering (DocVQA).
""")

# --- Main UI ---
st.title("Research DocVQA System")
st.markdown("""
Compare different OCR and VLM approaches for extracting information from complex documents.
---
""")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Input Document")
    uploaded_file = st.file_uploader("Upload an image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
    
    # Use sample if no file uploaded
    if not uploaded_file:
        sample_path = "data/cache/sample1.png"
        if os.path.exists(sample_path):
            st.info("Using sample document for demonstration.")
            image = Image.open(sample_path)
            st.image(image, caption="Sample Document", use_column_width=True)
        else:
            st.warning("Please upload a document or ensure data/cache/sample1.png exists.")
            image = None
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Document", use_column_width=True)

with col2:
    st.header("Analysis & Q&A")
    question = st.text_input("Ask a question about the document:", placeholder="e.g., What is the total amount due?")
    
    run_button = st.button("Run Pipeline", type="primary", use_container_width=True)

    if run_button and image:
        with st.spinner(f"Running {perception_mode} Pipeline..."):
            pipeline = DocVQAPipeline(perception_type=perception_mode)
            # For interactive demo, ground truth is unknown
            result = pipeline.run(image, question, ground_truth_list=[])
            
            if "Error" in result:
                st.error(f"Pipeline Error: {result['Error']}")
            else:
                st.success("Analysis Complete!")
                
                # Tabs for different result views
                tab1, tab2, tab3 = st.tabs(["Answer", "Performance", "Raw Output"])
                
                with tab1:
                    st.subheader("Final Answer")
                    st.markdown(f"**{result['Prediction']}**")
                
                with tab2:
                    st.subheader("Metrics")
                    m_col1, m_col2, m_col3 = st.columns(3)
                    m_col1.metric("Total Latency", f"{result['Total_Latency']:.2f}s")
                    m_col2.metric("Perception Latency", f"{result['OCR_Latency']:.2f}s")
                    m_col3.metric("Memory Used", f"{result['Memory_Used_MB']:.1f} MB")
                    
                    # Performance breakdown chart
                    perf_data = {
                        "Stage": ["Perception", "Retrieval", "LLM Generation"],
                        "Latency (s)": [result['OCR_Latency'], result['Retrieval_Latency'], result['LLM_Latency']]
                    }
                    df_perf = pd.DataFrame(perf_data)
                    fig, ax = plt.subplots(figsize=(6, 4))
                    sns.barplot(x="Stage", y="Latency (s)", data=df_perf, palette="viridis", ax=ax)
                    st.pyplot(fig)

                with tab3:
                    st.subheader("Pipeline Details")
                    st.json(result)

# --- Comparative Visualization (Placeholder for Benchmarks) ---
st.divider()
st.header("Benchmark Stats")
stats_file = "results/results.csv"
if os.path.exists(stats_file):
    df = pd.read_csv(stats_file)
    if not df.empty:
        st.markdown("Comparative results from recent benchmark runs:")
        # Summary by model
        summary = df.groupby("Model").agg({
            "ANLS": "mean",
            "Total_Latency": "mean"
        }).reset_index()
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Accuracy (ANLS)")
            fig1, ax1 = plt.subplots()
            sns.barplot(x="Model", y="ANLS", data=summary, palette="magma", ax=ax1)
            st.pyplot(fig1)
        with c2:
            st.subheader("Speed (Latency)")
            fig2, ax2 = plt.subplots()
            sns.barplot(x="Model", y="Total_Latency", data=summary, palette="coolwarm", ax=ax2)
            st.pyplot(fig2)
else:
    st.info("No benchmark results found yet. Run main.py to generate comparative data.")

# Footer
st.divider()
st.caption("Developed by Antigravity | Master's Thesis Project © 2026")
