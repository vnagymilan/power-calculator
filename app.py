import streamlit as st
import numpy as np
from scipy.stats import norm

st.set_page_config(page_title="Power Calculator", page_icon="📊")

st.title("Power Calculator for CT Metric Comparison")

st.markdown(
    """
This calculator estimates the **required sample size per group** for comparing two groups using imaging-derived biomarkers.
All inputs are expected as **absolute values** in the unit of the selected metric (e.g., 0.03 for CT-FFR, 1 HU for PCAT, 3% for stenosis).
"""
)

# Input fields
bio_sd = st.number_input("Biological Standard Deviation", value=11.6, min_value=0.0, format="%.4f")
scanner_sd = st.number_input("Inter-scanner Standard Deviation", value=2.4, min_value=0.0, format="%.4f")
delta = st.number_input("Expected Difference (Δ), in absolute units", value=1.0, min_value=0.0, format="%.4f")
alpha = st.number_input("Alpha (Type I Error Rate)", value=0.05, min_value=0.0001, max_value=0.2, step=0.01, format="%.4f")
power = st.number_input("Power (1 - Type II Error Rate)", value=0.80, min_value=0.01, max_value=0.99, step=0.01, format="%.2f")

# Z-scores from standard normal distribution
z_alpha = norm.ppf(1 - alpha / 2)
z_beta = norm.ppf(power)

# Total variability
total_sd = np.sqrt(bio_sd**2 + scanner_sd**2)

# Sample size formula
if delta > 0:
    n = (2 * (total_sd ** 2) * (z_alpha + z_beta) ** 2) / (delta ** 2)
    st.success(f"📊 Required sample size per group: **{int(np.ceil**
