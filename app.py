import streamlit as st
import numpy as np
from scipy.stats import norm
import plotly.graph_objects as go

# ------------------------
# Page config
# ------------------------
st.set_page_config(page_title="Power calculation letter", layout="wide")

# ------------------------
# Header with logo + single-line title
# ------------------------
col_logo, col_title = st.columns([1, 12])
with col_logo:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/7/7a/Siemens-logo.svg",
        width=70,
    )
with col_title:
    st.markdown(
        "<h2 style='margin:0; padding-top:6px;'>Power calculation letter</h2>",
        unsafe_allow_html=True,
    )

st.markdown(
    """
Independent groups (parallel): Different patients are scanned on different CT systems.  
Example: Comparing CT-FFR values between two cohorts, one scanned on EID-CT, other on PCD-CT.

Paired (within-patient): The same patients are measured twice on different CT systems.  
Example: Follow-up plaque progression (baseline vs. follow-up) studies, with baseline EID-CT and PCD-CT follow-up scan.
"""
)

# ------------------------
# Biomarker database (example structure)
# Replace with your real dict/table as you already had it
# ------------------------
BIOMARKERS = {
    "Standard resolution": {
        "CT-FFR": {
            "eid_mean": 0.80,
            "bio_sd": 0.05,
            "inter_sd": 3.0,
            "ref": "Symons et al. (placeholder long reference)",
        },
    },
    "Ultrahigh-resolution": {
        "CT-FFR": {
            "eid_mean": 0.80,
            "bio_sd": 0.05,
            "inter_sd": 3.0,
            "ref": "Symons et al. (placeholder long reference)",
        },
    },
}

# ------------------------
# Sidebar controls
# ------------------------
st.sidebar.header("Study setup")

resolution = st.sidebar.selectbox("Select resolution", list(BIOMARKERS.keys()))
biomarker = st.sidebar.selectbox(
    "Select biomarker",
    list(BIOMARKERS[resolution].keys()),
)

design = st.sidebar.radio(
    "Study design",
    ["Independent groups (parallel)", "Paired (within-patient)"],
)

alpha = st.sidebar.number_input("Alpha (two-sided)", value=0.05, min_value=0.0001, max_value=0.5, step=0.01, format="%.4f")
power = st.sidebar.number_input("Power", value=0.80, min_value=0.5, max_value=0.99, step=0.01, format="%.2f")

bdata = BIOMARKERS[resolution][biomarker]

z_alpha = norm.ppf(1 - alpha / 2)
z_beta = norm.ppf(power)

# -----------------------------
# Variability inputs
# -----------------------------
if design.startswith("Paired"):
    bio_sd = 0.0
else:
    bio_sd = st.number_input("Biological SD", value=float(bdata["bio_sd"]))

inter_sd = st.number_input("Inter-scanner SD", value=float(bdata["inter_sd"]))

# -----------------------------
# Independent groups
# -----------------------------
if design.startswith("Independent"):
    total_sd = np.sqrt(bio_sd**2 + inter_sd**2)
    st.markdown(f"**Total SD:** {total_sd:.3f}")

    # Effect size input is proportionate only (%)
    delta_pct = st.number_input("Δ (relative difference, %)", value=5.0)
    baseline_mean = abs(float(bdata["eid_mean"]))  # ALWAYS EID-CT
    delta_abs = baseline_mean * (delta_pct / 100.0)

    n = 2 * (((z_alpha + z_beta) * total_sd / delta_abs) ** 2)
    n_req = int(np.ceil(n))

    x = np.linspace(0.1, 50.0, 600)
    delta_curve = abs(bdata["eid_mean"]) * x / 100.0

    y = 2 * (((z_alpha + z_beta) * total_sd / delta_curve) ** 2)
    y = np.log10(np.clip(y, 1, None))

    x_label = "Expected relative difference (%)"

# -----------------------------
# Paired
# -----------------------------
else:
    delta_pct = st.number_input("Δ (required relative change, %)", value=5.0)
    f = (z_alpha + z_beta) ** 2
    n = f * 2 * (inter_sd**2) / (delta_pct**2)
    n_req = int(np.ceil(n))

    x = np.linspace(1.0, 20.0, 600)
    y = np.log10(f * 2 * (inter_sd**2) / (x**2))
    x_label = "Required relative change (%)"

# -----------------------------
# Output
# -----------------------------
st.markdown(f"### Required sample size per group: **{n_req}**")

st.markdown(
    f"""
**Reference (click):**  
<span title="{bdata['ref']}" style="text-decoration: underline; cursor: help;">{biomarker}</span>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Plot
# -----------------------------
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=x,
        y=10 ** y,
        mode="lines",
        name="Sample size",
    )
)

fig.update_layout(
    xaxis_title=x_label,
    yaxis_title="Sample size per group",
    height=450,
    margin=dict(l=10, r=10, t=40, b=10),
)

st.plotly_chart(fig, use_container_width=True)
