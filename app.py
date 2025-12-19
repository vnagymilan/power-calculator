import streamlit as st
import numpy as np
from scipy.stats import norm
import plotly.graph_objects as go
from PIL import Image

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="PCD-CT vs. EID-CT Power Calculator",
    layout="centered"
)

# -----------------------------
# Header with logo + single-line title
# -----------------------------
logo = None
try:
    logo = Image.open("musc_logo.jpeg")
except Exception:
    pass

c1, c2 = st.columns([1, 6])
with c1:
    if logo is not None:
        st.image(logo, width=110)
with c2:
    st.markdown(
        "<div style='font-size:34px;font-weight:700;white-space:nowrap;'>"
        "PCD-CT vs. EID-CT Power Calculator"
        "</div>",
        unsafe_allow_html=True,
    )

# -----------------------------
# Intro text
# -----------------------------
st.markdown(
    """
This calculator estimates the **sample size per group** required to detect differences
in quantitative imaging biomarkers between CT systems.

**Independent groups (parallel):**  
Different patients are scanned on different CT systems.  
*Example:* CT-FFR values compared between EID-CT and PCD-CT cohorts.

**Paired (within-patient):**  
The same patients are scanned on both CT systems.  
*Example:* Baseline EID-CT and follow-up PCD-CT plaque progression studies.
"""
)

# -----------------------------
# References
# -----------------------------
references = {
    ("Stenosis severity (%)", "Standard"): "Wolf E V., Gnasso C., Schoepf UJ., et al. Intra-individual comparison of coronary artery stenosis measurements between energy-integrating detector CT and photon-counting detector CT. Imaging. 2023:1–8.",
    ("CT-FFR", "Standard"): "Zsarnoczay E., Pinos D., Schoepf UJ., et al. Intra-individual comparison of coronary CT angiography-based FFR between energy-integrating and photon-counting detector CT systems. Int J Cardiol. 2024;399:131684.",
    ("Stenosis severity (%)", "UHR"): "Vecsey-Nagy M., Tremamunno G., Schoepf UJ., et al. Intraindividual Comparison of Ultrahigh-Spatial-Resolution Photon-Counting Detector CT and Energy-Integrating Detector CT for Coronary Stenosis Measurement. Circ Cardiovasc Imaging. 2024:1–9.",
    ("CT-FFR", "UHR"): "Vecsey-Nagy M., Tremamunno G., Schoepf UJ., et al. Coronary CT angiography-based FFR with ultrahigh-resolution photon-counting detector CT: Intra-individual comparison to energy-integrating detector CT. Eur J Radiol. 2024;181:111797.",
    ("Segment stenosis score", "UHR"): "Tremamunno G., Varga-Szemes A., Schoepf UJ., et al. Semiquantitative metrics of coronary artery disease burden: Intra-individual comparison between ultrahigh-resolution photon-counting detector CT and energy-integrating detector CT. J Cardiovasc Comput Tomogr. 2025.",
    ("Segment involvement score", "UHR"): "Tremamunno G., Varga-Szemes A., Schoepf UJ., et al. Semiquantitative metrics of coronary artery disease burden: Intra-individual comparison between ultrahigh-resolution photon-counting detector CT and energy-integrating detector CT. J Cardiovasc Comput Tomogr. 2025.",
    ("EAT volume (cl)", "UHR"): "Kravchenko D., Vecsey-Nagy M., Tremamunno G., et al. Intra-individual comparison of epicardial adipose tissue characteristics on coronary CT angiography between photon-counting detector and energy-integrating detector CT systems. Eur J Radiol. 2024;181:111728.",
    ("EAT attenuation (HU)", "UHR"): "Kravchenko D., Vecsey-Nagy M., Tremamunno G., et al. Intra-individual comparison of epicardial adipose tissue characteristics on coronary CT angiography between photon-counting detector and energy-integrating detector CT systems. Eur J Radiol. 2024;181:111728.",
    ("PCAT attenuation (HU)", "UHR"): "Tremamunno G., Vecsey-Nagy M., Hagar MT., et al. Intra-individual Differences in Pericoronary Fat Attenuation Index Measurements Between Photon-counting and Energy-integrating Detector Computed Tomography. Acad Radiol. 2025;32:1333–43.",
    ("Total plaque volume (mm³)", "UHR"): "Vecsey-Nagy M., Tremamunno G., Schoepf UJ., et al. Coronary Plaque Quantification with Ultrahigh-Spatial-Resolution Photon-counting Detector CT: Intraindividual Comparison with Energy-integrating Detector CT. Radiology. 2025;314:e241479.",
    ("Calcified plaque volume (mm³)", "UHR"): "Vecsey-Nagy M., Tremamunno G., Schoepf UJ., et al. Coronary Plaque Quantification with Ultrahigh-Spatial-Resolution Photon-counting Detector CT: Intraindividual Comparison with Energy-integrating Detector CT. Radiology. 2025;314:e241479.",
    ("Fibrotic plaque volume (mm³)", "UHR"): "Vecsey-Nagy M., Tremamunno G., Schoepf UJ., et al. Coronary Plaque Quantification with Ultrahigh-Spatial-Resolution Photon-counting Detector CT: Intraindividual Comparison with Energy-integrating Detector CT. Radiology. 2025;314:e241479.",
    ("Low-attenuation plaque volume (mm³)", "UHR"): "Vecsey-Nagy M., Tremamunno G., Schoepf UJ., et al. Coronary Plaque Quantification with Ultrahigh-Spatial-Resolution Photon-counting Detector CT: Intraindividual Comparison with Energy-integrating Detector CT. Radiology. 2025;314:e241479."
}

# -----------------------------
# Biomarker data
# -----------------------------
biomarker_data = {
    "Stenosis severity (%)": {
        "Standard": {"bio_sd": 11.6, "inter_sd": 2.4, "eid_mean": 46.2},
        "UHR": {"bio_sd": 11.6, "inter_sd": 10.2, "eid_mean": 53.1},
    },
    "CT-FFR": {
        "Standard": {"bio_sd": 0.08, "inter_sd": 0.09, "eid_mean": 0.81},
        "UHR": {"bio_sd": 0.08, "inter_sd": 0.11, "eid_mean": 0.70},
    },
    "Segment stenosis score": {
        "UHR": {"bio_sd": 5.93, "inter_sd": 3.18, "eid_mean": 7.8}
    },
    "Segment involvement score": {
        "UHR": {"bio_sd": 4.44, "inter_sd": 1.47, "eid_mean": 7.5}
    },
    "EAT volume (cl)": {
        "UHR": {"bio_sd": 5.67, "inter_sd": 2.27, "eid_mean": 15.1}
    },
    "EAT attenuation (HU)": {
        "UHR": {"bio_sd": 5.20, "inter_sd": 6.53, "eid_mean": -77.9}
    },
    "PCAT attenuation (HU)": {
        "UHR": {"bio_sd": 8.00, "inter_sd": 7.37, "eid_mean": -69.8}
    },
    "Total plaque volume (mm³)": {
        "UHR": {"bio_sd": 515.0, "inter_sd": 239.54, "eid_mean": 1137.0}
    },
    "Calcified plaque volume (mm³)": {
        "UHR": {"bio_sd": 148.6, "inter_sd": 142.02, "eid_mean": 334.8}
    },
    "Fibrotic plaque volume (mm³)": {
        "UHR": {"bio_sd": 380.1, "inter_sd": 206.6, "eid_mean": 723.0}
    },
    "Low-attenuation plaque volume (mm³)": {
        "UHR": {"bio_sd": 11.9, "inter_sd": 84.59, "eid_mean": 82.4}
    },
}

# -----------------------------
# Inputs
# -----------------------------
design = st.radio(
    "Study design",
    ["Independent groups (parallel)", "Paired (within-patient)"],
    horizontal=True,
)

resolution = st.selectbox(
    "Select PCD-CT resolution",
    ["Standard (0.4 mm)", "Ultrahigh-resolution (0.2 mm)"],
)
res_key = "Standard" if resolution.startswith("Standard") else "UHR"

biomarker = st.selectbox(
    "Select biomarker",
    [b for b in biomarker_data if res_key in biomarker_data[b]],
)
bdata = biomarker_data[biomarker][res_key]

col1, col2, col3 = st.columns(3)

with col1:
    alpha = st.number_input("Alpha", 0.001, 0.5, 0.05, 0.01)
with col2:
    power = st.number_input("Power", 0.01, 0.99, 0.8, 0.05)

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

delta_pct = st.number_input("Δ (relative difference, %)", value=5.0)
baseline_mean = abs(float(bdata["eid_mean"]))
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
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;font-size:44px;font-weight:700;'>"
    f"{n_req} patients</div>",
    unsafe_allow_html=True,
)

# -----------------------------
# Plot
# -----------------------------
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(width=3),
        hovertemplate="Δ: %{x:.2f}<br>Sample size: %{customdata:.0f}<extra></extra>",
        customdata=10**y,
        showlegend=False,
    )
)

fig.update_layout(
    xaxis_title=x_label,
    yaxis_title="log₁₀(sample size)",
    hovermode="closest",
    plot_bgcolor="white",
)

fig.update_xaxes(
    showspikes=True,
    spikesnap="cursor",
    spikemode="across",
    spikethickness=2,
)
fig.update_yaxes(showgrid=True)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Reference
# -----------------------------
st.markdown("---")
ref = references.get((biomarker, res_key), "Reference not available.")
st.markdown(f"<sup>*</sup>{ref}", unsafe_allow_html=True)
