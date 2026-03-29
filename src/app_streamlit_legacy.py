import streamlit as st
import os
import tempfile
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from segmentation.segmenter import ContractSegmenter
from classification.risk_scorer import RiskScorer
from explanation.explainer import RiskExplainer
from dotenv import load_dotenv

load_dotenv()

# Page Config
st.set_page_config(
    page_title="Legal Risk Suite | PSG Tech",
    page_icon="⚖️",
    layout="wide"
)

# Premium Global Styles
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f0f2f6;
    }

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        margin-bottom: 20px;
    }

    .risk-high {
        border-left: 5px solid #ff4b4b;
        background-color: rgba(255, 75, 75, 0.05);
    }
    .risk-medium {
        border-left: 5px solid #ffa500;
        background-color: rgba(255, 165, 0, 0.05);
    }
    .risk-low {
        border-left: 5px solid #2ecc71;
        background-color: rgba(46, 204, 113, 0.05);
    }

    h1, h2, h3 {
        font-weight: 700 !important;
        color: #1e293b;
    }

    .stMetric {
        background: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    </style>
    """, unsafe_allow_html=True)

# App Header
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://img.freepik.com/free-vector/legal-advice-concept-illustration_114360-1798.jpg", width=120)
with col2:
    st.title("Legal Risk Suite")
    st.markdown("Automated Contract Risk Intelligence | Fine-Tuned LegalBERT v1.0")

st.divider()

# Initialize Modules
@st.cache_resource
def load_modules():
    segmenter = ContractSegmenter()
    scorer = RiskScorer()
    explainer = RiskExplainer()
    return segmenter, scorer, explainer

try:
    segmenter, scorer, explainer = load_modules()
except Exception as e:
    st.error(f"Initialization Error: {e}")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("📂 Document Input")
    uploaded_file = st.file_uploader("Upload Contract (PDF/TXT)", type=["pdf", "txt"])
    use_sample = st.button("✨ Use Sample Agreement")
    
    st.divider()
    st.markdown("### Model Information")
    st.info("**Model**: LegalBERT-base\n\n**Accuracy**: 90.8%\n\n**Dataset**: CUAD v1")

# Main Execution Logic
if uploaded_file is not None or use_sample:
    if use_sample:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tmp_path = os.path.join(base_dir, "tests", "sample_contract.txt")
        is_temp = False
    else:
        suffix = f".{uploaded_file.name.split('.')[-1]}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        is_temp = True

    with st.spinner("Analyzing contract structure and risk posture..."):
        try:
            text = segmenter.extract_text(tmp_path)
            clauses = segmenter.segment_into_clauses(text)
            
            results = []
            for clause in clauses:
                score = scorer.score_clause(clause)
                results.append({
                    "Clause": clause,
                    "Risk Level": score["risk_level"],
                    "Confidence": score['confidence'],
                    "Method": score.get("method", "Inference")
                })
            df = pd.DataFrame(results)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    if is_temp: os.unlink(tmp_path)

    # LAYOUT: Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Risk Dashboard", "🔍 Detailed Analysis", "📄 Source Text"])

    with tab1:
        st.subheader("Contract Risk Profile")
        
        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Clauses", len(df))
        m2.metric("🔴 High Risk", len(df[df["Risk Level"] == "High"]))
        m3.metric("🟠 Medium Risk", len(df[df["Risk Level"] == "Medium"]))
        m4.metric("🟢 Low Risk", len(df[df["Risk Level"] == "Low"]))

        st.divider()
        
        # Analytics Row
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            # Distribution Chart
            fig = px.pie(df, names='Risk Level', 
                         color='Risk Level',
                         color_discrete_map={'High':'#ff4b4b', 'Medium':'#ffa500', 'Low':'#2ecc71'},
                         hole=0.5,
                         title="Risk Distribution Overview")
            fig.update_layout(margin=dict(t=50, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with col_right:
            st.markdown("### AI Summary Insights")
            high_perc = (len(df[df["Risk Level"] == "High"]) / len(df)) * 100
            if high_perc > 20:
                st.warning(f"**High Exposure Alert**: {high_perc:.1f}% of identified clauses are high risk.")
            else:
                st.success("**Standard Posture**: The agreement generally follows a low-risk profile.")
            
            st.info(f"**Average Confidence**: {df['Confidence'].mean():.1%}")

    with tab2:
        st.subheader("Clause-by-Clause Inspection")
        for i, row in df.iterrows():
            risk_color = "high" if row["Risk Level"]=="High" else ("medium" if row["Risk Level"]=="Medium" else "low")
            
            with st.expander(f"Clause {i+1} | {row['Risk Level']} Risk | {row['Confidence']:.1%} Conf"):
                st.markdown(f"""
                <div class="glass-card risk-{risk_color}">
                    <p style="font-size: 1.1em;">{row['Clause']}</p>
                    <small>Detected via: <b>{row['Method']}</b></small>
                </div>
                """, unsafe_allow_html=True)
                
                if row['Risk Level'] != "Low" and os.getenv("GOOGLE_API_KEY"):
                    if st.button(f"Generate Legal Explainer (AI)", key=f"exp_{i}"):
                        with st.spinner("Decoding legal jargon..."):
                            explanation = explainer.generate_explanation(row['Clause'], row['Risk Level'])
                            st.markdown("---")
                            st.markdown(f"**AI Analyst Explanation:**\n\n{explanation}")

    with tab3:
        st.subheader("Extracted Content")
        st.text_area("Full Raw Contract Text", text, height=600)

else:
    # Landing Page
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h2 style="color: #4761ff;">Ready to start your automated review?</h2>
        <p>Please upload a contract document in the sidebar to begin analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 1. Upload\nPDF or TXT documents supported.")
    with col2:
        st.info("### 2. Analyze\nFine-tuned LegalBERT scans for risk.")
    with col3:
        st.info("### 3. Review\nDownload insights and AI explanations.")

# Footer
st.divider()
st.markdown("<p style='text-align: center; color: grey; font-size: 0.8em;'>Built for NRC NLP Course | PSG Tech 2026<br>Experimental AI System - Always consult legal counsel.</p>", unsafe_allow_html=True)
