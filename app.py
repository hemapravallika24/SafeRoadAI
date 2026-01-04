# app.py — SafeRoad AI (FINAL)
# Auto-scroll FIXED using streamlit.components
# Cloud + Local compatible

import os
import io
from pathlib import Path
import re
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from PyPDF2 import PdfReader
import google.generativeai as genai

# ----- PAGE CONFIG -----
st.set_page_config(
    page_title="Road Safety Intervention — SafeRoad AI",
    page_icon="🚦",
    layout="wide"
)

# ----- PREMIUM CSS -----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: "Poppins", sans-serif; }
.stApp {
    background: linear-gradient(135deg, #f3e7ff 0%, #e3f0ff 50%, #fff8f3 100%);
}
.card {
    background: white;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 18px;
    box-shadow: 0 8px 28px rgba(0,0,0,0.05);
}
.interv {
    border-radius: 14px;
    padding: 16px;
    background: #fff;
    margin-bottom: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}
.pill {
    padding: 6px 10px;
    border-radius: 999px;
    background: #e6f2ff;
    font-size: 13px;
    font-weight: 600;
    margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)

# ----- API CONFIG -----
API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)
MODEL_NAME = "models/gemini-2.5-flash"

# ----- LOAD DATA -----
INTERVENTIONS_CSV = "data/irc_interventions.csv"

def load_interventions(csv_path):
    p = Path(csv_path)
    if p.exists():
        df = pd.read_csv(p)
        if "keywords" not in df.columns:
            df["keywords"] = ""
        return df
    return pd.DataFrame(columns=["title", "description", "keywords"])

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text.strip()

def extract_road_issues(text):
    pattern = r"(?i)\b(pothole|curve|lighting|sign|barrier|accident|intersection|school)\b"
    return list(set(re.findall(pattern, text)))

def find_matching_interventions(issues, df):
    matches = []
    for _, row in df.iterrows():
        kws = str(row.get("keywords", "")).lower()
        desc = str(row.get("description", "")).lower()
        title = str(row.get("title", "")).lower()
        for issue in issues:
            if issue.lower() in kws or issue.lower() in desc or issue.lower() in title:
                matches.append(row)
                break
    return pd.DataFrame(matches)

def generate_ai_summary(issue_text, matches):
    prompt = f"""
Summarize the road safety issue and suggest top interventions.

Issue:
{issue_text[:600]}

Interventions:
{matches.head(5).to_string(index=False)}
"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"AI Summary unavailable ({e})"

interventions_df = load_interventions(INTERVENTIONS_CSV)

# ----- HERO -----
st.markdown("""
<div class="card">
<h1>🚦 SafeRoad AI</h1>
<p>AI-powered road safety intervention decision support system</p>
</div>
""", unsafe_allow_html=True)

# ----- INPUT -----
mode = st.radio("Choose input method:", ["📝 Manual Description", "📄 Upload PDF"])

user_input = ""
uploaded_pdf = None

if mode == "📝 Manual Description":
    user_input = st.text_area(
        "Describe the road safety issue:",
        placeholder="Example: High-speed curve with poor signage",
        height=160
    )
    analyze_clicked = st.button("Analyze Issue")

else:
    uploaded_pdf = st.file_uploader("Upload road audit PDF", type=["pdf"])
    analyze_clicked = uploaded_pdf is not None

# ----- RESULTS -----
if analyze_clicked:

    st.markdown("<div id='ai-results'></div>", unsafe_allow_html=True)

    with st.spinner("🔍 Analyzing road safety issue using AI…"):
        if mode == "📝 Manual Description":
            issues = extract_road_issues(user_input)
            matches = find_matching_interventions(issues, interventions_df)
            summary = generate_ai_summary(user_input, matches)
        else:
            pdf_text = extract_text_from_pdf(uploaded_pdf)
            issues = extract_road_issues(pdf_text)
            matches = find_matching_interventions(issues, interventions_df)
            summary = generate_ai_summary(pdf_text, matches)

    st.success("✅ Analysis complete! Scroll down to view results")

    st.markdown("<div class='card'><h3>Detected Issues</h3>" +
                ", ".join(issues) + "</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'><h3>Recommended Interventions</h3>", unsafe_allow_html=True)
    if not matches.empty:
        for _, row in matches.iterrows():
            st.markdown(f"""
            <div class="interv">
                <b>{row['title']}</b><br>
                {row['description']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No matching interventions found.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'><h3>🧠 AI Summary</h3></div>", unsafe_allow_html=True)
    st.write(summary)

    # ✅ REAL AUTO-SCROLL (WORKS ON STREAMLIT CLOUD)
    components.html("""
    <script>
        const el = window.parent.document.getElementById("ai-results");
        if (el) { el.scrollIntoView({ behavior: "smooth" }); }
    </script>
    """, height=0)

# ----- FOOTER -----
st.markdown("<hr>")
st.markdown("🚦 **SafeRoad AI © 2025 | Team Ignite**")
