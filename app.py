import streamlit as st
import numpy as np
from scipy.stats import norm

st.set_page_config(page_title="PCD-CT vs. EID-CT Power Calculator", layout="centered")

st.title("Sample Size Calculator for PCD-CT vs. EID-CT")
st.markdown("""
This tool estimates the required sample size per group to detect differences in imaging biomarkers across CT technologies.  
**Please enter absolute values** (e.g., a Δ of 1.5 is invalid for CT-FFR).  

Select the appropriate scanner resolution and biomarker to auto-populate standard deviations from prior studies.  
""")

# ---------- Dropdown for Resolution ----------
resolution = st.selectbox("Select resolution", [
    "Standard resolution (0.4 mm)",
    "Ultrahigh-resolution (0.2 mm)"
])

# ---------- Biomarkers per Resolution ----------
biomarkers_04 = {
    "Stenosis severity (QCA-correlated, %)": ("3.7", "2.3", "Szilveszter et al, JACC CVI 2024"),
    "Non-calcified plaque volume (mm³)": ("20.1", "15.2", "Vecsey-Nagy et al, Radiology 2024"),
    "CT-FFR (value)": ("0.048", "0.034", "Szilveszter et al, EHJ CVI 2023")
}

biomarkers_02 = {
    "Plaque max attenuation (HU)": ("25.2", "11.4", "Vecsey-Nagy et al, Under Review"),
    "Calcium blooming (mm)": ("0.16", "0.10", "Vecsey-Nagy et al, EHJ CVI 2024"),
    "Lumen area (mm²)": ("1.85", "1.00", "Szilveszter et al, SCCT 2024")
}

# ---------- Show Biomarker Dropdown Based on Resolution ----------
if resolution.startswith("Standard"):
    selected_biomarker = st.selectbox("Select biomarker", list(biomarkers_04.keys()))
    bio_sd, inter_sd, citation = biomarkers_04[selected_biomarker]
else:
    selected_biomarker = st.selectbox("Select biomarker", list(biomarkers_02.keys()))
    bio_sd, inter_sd, citation = biomarkers_02[selected_biomarker]

# ---------- Convert SDs ----------
bio_sd = float(bio_sd)
inter_sd = float(inter_sd)
total_sd = np.sqrt(bio_sd**2 + inter_sd**2)

# ---------- Input Parameters ----------
st.subheader("Study parameters")

col1, col2, col3 = st.columns(3)
with col1:
    alpha = st.number_input("Alpha (type I error)", value=0.05, step=0.01, format="%.2f")
with col2:
    power = st.number_input("Power (1 - β)", value=0.8, step=0.05, format="%.2f")
with col3:
    delta = st.number_input("Expected difference (Δ)", value=1.0, step=0.1)

# ---------- Compute Sample Size ----------
z_alpha = norm.ppf(1 - alpha / 2)
z_beta = norm.ppf(power)
n = 2 * ((z_alpha + z_beta) * total_sd / delta) ** 2
n_rounded = int(np.ceil(n))

# ---------- Output ----------
st.subheader("Required sample size per group")
st.write(f"**{n_rounded} patients per group** are required.")

# ---------- Display SDs and Footnote ----------
st.markdown("---")
st.markdown(f"""
**Biological SD:** {bio_sd}  
**Inter-scanner SD:** {inter_sd}  
**Total SD:** {total_sd:.3f}  

<sub>SD values derived from: {citation}</sub>
""", unsafe_allow_html=True)
