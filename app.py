import streamlit as st
import numpy as np
from scipy.stats import norm
from PIL import Image
import plotly.graph_objects as go

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="PCD-CT vs. EID-CT Power Calculator", layout="centered")

# -----------------------------
# Header: logo next to ONE-LINE title
# -----------------------------
logo = None
try:
    logo_path = "musc_logo.jpeg"  # ensure this file is in the repo root
    logo = Image.open(logo_path)
except Exception:
    logo = None

hcol1, hcol2 = st.columns([1, 6])
with hcol1:
    if logo is not None:
        st.image(logo, width=110)

with hcol2:
    st.markdown(
        """
        <div style="
            font-size: 34px;
            font-weight: 700;
            line-height: 1.1;
            white-space: nowrap;
        ">
            PCD-CT vs. EID-CT Power Calculator
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# Intro text (your wording)
# -----------------------------
st.markdown(
    """
This calculator estimates the **sample size per group** needed to detect a difference in imaging biomarkers between CT systems.

**Independent groups (parallel):**  
Different patients are scanned on different CT systems.  
*Example:* Comparing **CT-FFR** values between two cohorts, one scanned on **EID-CT** and the other on **PCD-CT**.

**Paired (within-patient):**  
The same patients are measured twice on different CT systems.  
*Example:* **Follow-up plaque progression** studies with **baseline EID-CT** and a **PCD-CT follow-up** scan.

You can manually adjust variability inputs below.
"""
)

# -----------------------------
# References (FULL)
# -----------------------------
long_refs = {
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
    ("Low-attenuation plaque volume (mm³)", "UHR"): "Vecsey-Nagy M., Tremamunno G., Schoepf UJ., et al. Coronary Plaque Quantification with Ultrahigh-Spatial-Resolution Photon-counting Detector CT: Intraindividual Comparison with Energy-integrating Detector CT. Radiology. 2025;314:e241479.",
}

# -----------------------------
# SD data (FULL biomarker list)
# NOTE: inter_sd placeholders below should be replaced with your percentage inter-scanner SD table.
# -----------------------------
biomarker_data = {
    "Stenosis severity (%)": {
        "Standard": {"bio_sd": 11.6, "inter_sd": 2.4},
        "UHR": {"bio_sd": 11.6, "inter_sd": 10.2},
    },
    "CT-FFR": {
        "Standard": {"bio_sd": 0.08, "inter_sd": 0.09},
        "UHR": {"bio_sd": 0.08, "inter_sd": 0.11},
    },
    "Segment stenosis score": {"UHR": {"bio_sd": 5.93, "inter_sd": 3.18}},
    "Segment involvement score": {"UHR": {"bio_sd": 4.44, "inter_sd": 1.47}},
    "EAT volume (cl)": {"UHR": {"bio_sd": 5.67, "inter_sd": 2.27}},
    "EAT attenuation (HU)": {"UHR": {"bio_sd": 5.20, "inter_sd": 6.53}},
    "PCAT attenuation (HU)": {"UHR": {"bio_sd": 8.00, "inter_sd": 7.37}},
    "Total plaque volume (mm³)": {"UHR": {"bio_sd": 515.00, "inter_sd": 239.54}},
    "Calcified plaque volume (mm³)": {"UHR": {"bio_sd": 148.60, "inter_sd": 142.02}},
    "Fibrotic plaque volume (mm³)": {"UHR": {"bio_sd": 380.10, "inter_sd": 206.60}},
    "Low-attenuation plaque volume (mm³)": {"UHR": {"bio_sd": 11.90, "inter_sd": 84.59}},
}

# -----------------------------
# Inputs (study design first)
# -----------------------------
design = st.radio(
    "Study design",
    ["Independent groups (parallel)", "Paired (within-patient)"],
    index=0,
    horizontal=True,
)

resolution = st.selectbox(
    "Select PCD-CT resolution",
    ["Standard (0.4 mm)", "Ultrahigh-resolution (0.2 mm)"],
)
res_key = "Standard" if resolution.startswith("Standard") else "UHR"

valid_biomarkers = [k for k in biomarker_data if res_key in biomarker_data[k]]
biomarker = st.selectbox("Select biomarker", valid_biomarkers)
bdata = biomarker_data[biomarker][res_key]
ref = long_refs.get((biomarker, res_key), "Reference not available.")

colA, colB, colC = st.columns(3)

with colA:
    alpha = st.number_input("Alpha", min_value=0.001, max_value=0.5, value=0.05, step=0.01)

with colB:
    power = st.number_input("Power", min_value=0.01, max_value=0.99, value=0.8, step=0.05)

# Z values
z_alpha = norm.ppf(1 - alpha / 2)
z_beta = norm.ppf(power)

# Δ limits for independent absolute Δ
delta_limits = {
    "Stenosis severity (%)": (1.0, 100.0),
    "CT-FFR": (0.001, 1.0),
    "Segment stenosis score": (1.0, 48.0),
    "Segment involvement score": (1.0, 16.0),
    "EAT volume (cl)": (1.0, 100.0),
    "EAT attenuation (HU)": (1.0, 30.0),
    "PCAT attenuation (HU)": (1.0, 30.0),
    "Total plaque volume (mm³)": (1.0, 10000.0),
    "Calcified plaque volume (mm³)": (1.0, 10000.0),
    "Fibrotic plaque volume (mm³)": (1.0, 10000.0),
    "Low-attenuation plaque volume (mm³)": (1.0, 10000.0),
}

# -----------------------------
# SD inputs
# -----------------------------
if design.startswith("Paired"):
    # hide Biological SD entirely
    bio_sd = 0.0
    inter_label = "Inter-scanner SD (%)"
else:
    bio_sd = st.number_input("Biological SD", value=float(bdata["bio_sd"]), format="%.4f")
    inter_label = "Inter-scanner SD"

inter_sd = st.number_input(inter_label, value=float(bdata["inter_sd"]), format="%.4f")

# -----------------------------
# Calculations + curves
# -----------------------------
if design.startswith("Independent"):
    total_sd = float(np.sqrt(bio_sd**2 + inter_sd**2))
    st.markdown(f"**Total SD:** {total_sd:.3f}")

    delta_min, delta_max = delta_limits.get(biomarker, (0.001, 100.0))

    with colC:
        step = 0.005 if biomarker == "CT-FFR" else 0.1
        fmt = "%.4f" if biomarker == "CT-FFR" else "%.2f"
        delta = st.number_input(
            "Δ (Expected difference in %)",
            min_value=float(delta_min),
            max_value=float(delta_max),
            value=float(delta_min),
            step=float(step),
            format=fmt,
        )

    n = 2 * (((z_alpha + z_beta) * total_sd / delta) ** 2)
    n_rounded = int(np.ceil(n))

    x_vals = np.linspace(delta_min, delta_max, 1000)
    sample_sizes = 2 * (((z_alpha + z_beta) * total_sd / x_vals) ** 2)
    sample_sizes = np.clip(sample_sizes, 1, None)
    y_vals = np.log10(sample_sizes)

    x_title = "Expected proportionate difference (%)"
    hover = "Δ: %{x:.4f}<br>Sample size: %{customdata:.0f}<extra></extra>"

else:
    with colC:
        delta_pct = st.number_input(
            "Δ (Expected change in %)",
            min_value=1.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            format="%.2f",
        )

    f = (z_alpha + z_beta) ** 2
    n = f * (inter_sd ** 2) * 2 / (delta_pct ** 2)
    n_rounded = int(np.ceil(n))

    x_vals = np.linspace(1.0, 20.0, 600)
    sample_sizes = f * (inter_sd ** 2) * 2 / (x_vals ** 2)
    sample_sizes = np.clip(sample_sizes, 1, None)
    y_vals = np.log10(sample_sizes)

    x_title = "Expected proportionate change (%)"
    # no extra percent sign in hover
    hover = "Δ: %{x:.2f}<br>Sample size: %{customdata:.0f}<extra></extra>"

# -----------------------------
# Output
# -----------------------------
st.markdown("---")
st.markdown("<div style='text-align: center; font-size: 24px;'>Required sample size per group</div>", unsafe_allow_html=True)
st.markdown(
    f"<div style='text-align: center; font-size: 48px; font-weight: bold;'>{n_rounded} patients</div>",
    unsafe_allow_html=True,
)

# -----------------------------
# Plot (dynamic cursor-following vertical guide line ALWAYS ON)
# -----------------------------
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=x_vals,
        y=y_vals,
        mode="lines",
        line=dict(width=3),
        hovertemplate=hover,
        customdata=sample_sizes,
        showlegend=False,
    )
)

fig.update_layout(
    xaxis_title=x_title,
    yaxis_title="log₁₀(sample size)",
    hovermode="closest",  # keeps tooltip clean (no extra header number)
    hoverlabel=dict(bgcolor="white", bordercolor="black", font_size=13),
    plot_bgcolor="white",
    margin=dict(l=40, r=40, t=10, b=40),
)

# Cursor-following vertical guide line (spikes) - ALWAYS ON
fig.update_xaxes(
    showgrid=False,
    showspikes=True,
    spikesnap="cursor",
    spikemode="across",
    spikethickness=2,
    spikedash="dash",
)
fig.update_yaxes(showgrid=True, zeroline=False)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Reference + contact
# -----------------------------
st.markdown("---")
st.markdown(
    f"""
<sup>*</sup>{ref}  

Questions or suggestions? Contact **[musccvi@musc.edu](mailto:musccvi@musc.edu)**
""",
    unsafe_allow_html=True,
)
