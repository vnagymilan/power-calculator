import streamlit as st
import numpy as np
from scipy.stats import norm

st.set_page_config(page_title="CT Power Calculator", layout="centered")

st.title("📊 CT Power Calculator")
st.markdown("Estimate the required sample size per group based on imaging biomarker variability between CT detector types.")

# ----------------------------
# Data dictionary
# ----------------------------

BIOMARKERS = {
    "Standard resolution": {
        "Stenosis severity (%)": {
            "bio_sd": 11.6,
            "scanner_sd": 2.4,
            "delta": 1.16,
            "citation": "Wolf E V., Gnasso C., Schoepf UJ., et al. *Imaging*. 2023:1–8."
        },
        "CT-FFR": {
            "bio_sd": 0.08,
            "scanner_sd": 0.09,
            "delta": 0.008,
            "citation": "Zsarnoczay E., Pinos D., Schoepf UJ., et al. *Int J Cardiol*. 2024;399:131684."
        }
    },
    "Ultrahigh-resolution": {
        "Stenosis severity (%)": {
            "bio_sd": 11.6,
            "scanner_sd": 10.2,
            "delta": 1.16,
            "citation": "Vecsey-Nagy M., Tremamunno G., Schoepf UJ., et al. *Circ Cardiovasc Imaging*. 2024:1–9."
        },
        "CT-FFR": {
            "bio_sd": 0.08,
            "scanner_sd": 0.11,
            "delta": 0.008,
            "citation": "Vecsey-Nagy M., Tremamunno G., Schoepf UJ., et al. *Eur J Radiol*. 2024;181:111797."
        },
        "Segment stenosis score": {
            "bio_sd": 5.93,
            "scanner_sd": 3.18,
            "delta": 0.593,
            "citation": "Tremamunno G., Varga-Szemes A., Schoepf UJ., et al. *J Cardiovasc Comput Tomogr*. 2025."
        },
        "Segment involvement score": {
            "bio_sd": 2.24,
            "scanner_sd": 1.63,
            "delta": 0.224,
            "citation": "Tremamunno G., Varga-Szemes A., Schoepf UJ., et al. *J Cardiovasc Comput Tomogr*. 2025."
        },
        "EAT Volume (cL)": {
            "bio_sd": 25.3,
            "scanner_sd": 18.4,
            "delta": 2.53,
            "citation": "Kravchenko D., Vecsey-Nagy M., Tremamunno G., et al. *Eur J Radiol*. 2024;181:111728."
        },
        "EAT attenuation (HU)": {
            "bio_sd": 8.3,
            "scanner_sd": 7.3,
            "delta": 0.83,
            "citation": "Kravchenko D., Vecsey-Nagy M., Tremamunno G., et al. *Eur J Radiol*. 2024;181:111728."
        },
        "PCAT attenuation (HU)": {
            "bio_sd": 8.3,
            "scanner_sd": 7.3,
            "delta": 0.83,
            "citation": "Tremamunno G., Vecsey-Nagy M., Hagar MT., et al. *Acad Radiol*. 2025;32:1333–43."
        },
        "Low-attenuation plaque (mm³)": {
            "bio_sd": 27.2,
            "scanner_sd": 27.5,
            "delta": 2.72,
            "citation": "Vecsey-Nagy M., Tremamunno G., Schoepf UJ., et al. *Radiology*. 2025;314:e241479."
        },
        "Fibrotic plaque (mm³)": {
            "bio_sd": 123.6,
            "scanner_sd": 98.2,
            "delta": 12.36,
            "citation": "Vecsey-Nagy M., Tremamunno G., Schoepf UJ., et al. *Radiology*. 2025;314:e241479."
        },
        "Calcified plaque (mm³)": {
            "bio_sd": 38.1,
            "scanner_sd": 25.4,
            "delta": 3.81,
            "citation": "Vecsey-Nagy M., Tremamunno G., Schoepf UJ., et al. *Radiology*. 2025;314:e241479."
        },
        "Total plaque volume (mm³)": {
            "bio_sd": 144.4,
            "scanner_sd": 101.8,
            "delta": 14.44,
            "citation": "Vecsey-Nagy M., Tremamunno G., Schoepf UJ., et al. *Radiology*. 2025;314:e241479."
        }
    }
}

# ----------------------------
# UI: Dropdowns & Inputs
# ----------------------------

resolution = st.selectbox("Select scanner resolution", options=BIOMARKERS.keys())
biomarker = st.selectbox("Select biomarker", options=BIOMARKERS[resolution].keys())

defaults = BIOMARKERS[resolution][biomarker]

col1, col2 = st.columns(2)
with col1:
    bio_sd = st.number_input("Biological SD", value=defaults["bio_sd"], min_value=0.0, format="%.4f")
with col2:
    scanner_sd = st.number_input("Inter-scanner SD", value=defaults["scanner_sd"], min_value=0.0, format="%.4f")

delta = st.number_input("Expected difference (Δ, absolute units)", value=defaults["delta"], min_value=0.0, format="%.4f")

col3, col4 = st.columns(2)
with col3:
    alpha = st.number_input("Alpha (Type I error)", value=0.05, min_value=0.0001, max_value=0.2, step=0.01, format="%.4f")
with col4:
    power = st.number_input("Power (1 - Type II error)", value=0.80, min_value=0.01, max_value=0.99, step=0.01, format="%.2f")

# ----------------------------
# Calculation
# ----------------------------

total_sd = np.sqrt(bio_sd**2 + scanner_sd**2)
z_alpha = norm.ppf(1 - alpha / 2)
z_beta = norm.ppf(power)

if delta > 0:
    n = (2 * (total_sd ** 2) * (z_alpha + z_beta) ** 2) / (delta ** 2)
    st.markdown(f"### 📈 Required sample size per group: **{int(np.ceil(n))}**")
else:
    st.warning("Expected difference (Δ) must be greater than 0.")

# ----------------------------
# Citation
# ----------------------------

st.markdown("---")
st.caption(f"**Reference for inter-scanner SD:** {defaults['citation']}")
