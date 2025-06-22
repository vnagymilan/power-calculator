import streamlit as st
import numpy as np
from scipy.stats import norm

# Data from Excel
standard_dict = {
    "Stenosis severity (%)": {"biological_sd": 11.6, "interscanner_sd": 2.4, "total_sd": 11.85},
    "CT-FFR": {"biological_sd": 0.08, "interscanner_sd": 0.09, "total_sd": 0.12},
}

uhr_dict = {
    "Stenosis severity (%)": {"biological_sd": 11.6, "interscanner_sd": 10.2, "total_sd": 15.47},
    "CT-FFR": {"biological_sd": 0.08, "interscanner_sd": 0.11, "total_sd": 0.14},
    "Segment stenosis score": {"biological_sd": 5.93, "interscanner_sd": 3.18, "total_sd": 6.73},
    "Minimal lumen area (mm²)": {"biological_sd": 1.89, "interscanner_sd": 1.32, "total_sd": 2.30},
    "Minimal lumen diameter (mm)": {"biological_sd": 0.25, "interscanner_sd": 0.18, "total_sd": 0.31},
    "Plaque burden (%)": {"biological_sd": 10.87, "interscanner_sd": 6.97, "total_sd": 12.97},
    "Low-density NCP volume (mm³)": {"biological_sd": 22.94, "interscanner_sd": 13.58, "total_sd": 26.68},
    "Total plaque volume (mm³)": {"biological_sd": 45.58, "interscanner_sd": 19.75, "total_sd": 49.81},
    "Max plaque attenuation (HU)": {"biological_sd": 38.47, "interscanner_sd": 18.55, "total_sd": 42.65},
    "Calcium blooming (mm)": {"biological_sd": 0.17, "interscanner_sd": 0.13, "total_sd": 0.21},
    "Lumen area (mm²)": {"biological_sd": 1.85, "interscanner_sd": 1.00, "total_sd": 2.10},
}

# UI Layout
st.set_page_config(page_title="PCD-CT vs. EID-CT Power Calculator", layout="centered")
st.title("Sample Size Calculator for PCD-CT vs. EID-CT")
st.markdown("""
This calculator estimates the required **sample size per group** to detect an expected difference (Δ) between imaging biomarkers acquired on different CT technologies.  
**All values must be entered as absolute values** (e.g., a Δ of 1.5 is invalid for CT-FFR).  

Select a resolution and biomarker to load standard deviation values from published and in-review intra-individual studies.
""")

# Resolution Selection
resolution = st.selectbox("CT resolution", ["Standard resolution (0.4 mm)", "Ultrahigh-resolution (0.2 mm)"])

# Biomarker selection
if resolution.startswith("Standard"):
    biomarker = st.selectbox("Select biomarker", list(standard_dict.keys()))
    data = standard_dict[biomarker]
else:
    biomarker = st.selectbox("Select biomarker", list(uhr_dict.keys()))
    data = uhr_dict[biomarker]

# Input fields
st.subheader("Study parameters")
col1, col2, col3 = st.columns(3)
with col1:
    alpha = st.number_input("Alpha (type I error)", min_value=0.001, max_value=0.5, value=0.05, step=0.01)
with col2:
    power = st.number_input("Power (1 - β)", min_value=0.01, max_value=0.99, value=0.8, step=0.05)
with col3:
    delta = st.number_input("Expected difference (Δ)", min_value=0.001, value=1.0, step=0.1)

# Sample size calculation
z_alpha = norm.ppf(1 - alpha / 2)
z_beta = norm.ppf(power)
total_sd = data["total_sd"]
n = 2 * ((z_alpha + z_beta) * total_sd / delta) ** 2
n_rounded = int(np.ceil(n))

# Output
st.subheader("Required sample size per group")
st.write(f"**{n_rounded} patients per group** are required to detect a difference of Δ = {delta} with {int(power*100)}% power and α = {alpha}.")

# Display SDs
st.markdown("---")
st.markdown(f"""
**Biological SD:** {data['biological_sd']}  
**Inter-scanner SD**<sup>*</sup>: {data['interscanner_sd']}  
**Total SD:** {total_sd:.3f}  
""", unsafe_allow_html=True)

# Footnotes and contact
st.markdown("---")
st.markdown("""
<sup>*</sup>Inter-scanner SD values were derived from intra-individual comparisons between matched PCD-CT and EID-CT reconstructions.  
For questions or suggestions, contact **[musccvi@musc.edu](mailto:musccvi@musc.edu)**.
""", unsafe_allow_html=True)
