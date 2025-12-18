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
# Intro text
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
# References
# -----------------------------
long_refs = {
    ("Stenosis severity (%)", "Standard"): "Wolf E V., Gnasso C., Schoepf UJ., et al. Imaging. 2023.",
    ("CT-FFR", "Standard"): "Zsarnoczay E., et al. Int J Cardiol. 2024.",
    ("Stenosis severity (%)", "UHR"): "Vecsey-Nagy M., et al. Circ Cardiovasc Imaging. 2024.",
    ("CT-FFR", "UHR"): "Vecsey-Nagy M., et al. Eur J Radiol. 2024.",
}

# -----------------------------
# SD data (placeholders)
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
    [k for k in biomarker_data if res_key in biomarker_data[k]],
)
bdata = biomarker_data[biomarker][res_key]

colA, colB, colC = st.columns(3)

with colA:
    alpha = st.number_input("Alpha", 0.001, 0.5, 0.05, 0.01)

with colB:
    power = st.number_input("Power", 0.01, 0.99, 0.8, 0.05)

z_alpha = norm.ppf(1 - alpha / 2)
z_beta = norm.ppf(power)

# -----------------------------
# SD inputs
# -----------------------------
if design.startswith("Paired"):
    bio_sd = 0.0
    inter_label = "Inter-scanner SD (%)"
else:
    bio_sd = st.number_input("Biological SD", value=float(bdata["bio_sd"]), format="%.4f")
    inter_label = "Inter-scanner SD"

inter_sd = st.number_input(inter_label, value=float(bdata["inter_sd"]), format="%.4f")

# -----------------------------
# Calculations
# -----------------------------
if design.startswith("Independent"):
    total_sd = np.sqrt(bio_sd**2 + inter_sd**2)

    with colC:
        delta = st.number_input("Δ (Expected difference)", 0.001, 100.0, 1.0)

    n = 2 * (((z_alpha + z_beta) * total_sd / delta) ** 2)
    x = np.linspace(delta / 5, delta * 5, 800)
    y = 2 * (((z_alpha + z_beta) * total_sd / x) ** 2)

    x_title = "Expected difference (Δ)"
    hover = "Δ: %{x:.4f}<br>Sample size: %{customdata:.0f}<extra></extra>"

else:
    with colC:
        delta = st.number_input("Δ (Required proportionate change)", 1.0, 20.0, 5.0)

    f = (z_alpha + z_beta) ** 2
    n = f * (inter_sd ** 2) * 2 / (delta ** 2)
    x = np.linspace(1.0, 20.0, 600)
    y = f * (inter_sd ** 2) * 2 / (x ** 2)

    x_title = "Required proportionate change (Δ)"
    hover = "Δ: %{x:.2f}<br>Sample size: %{customdata:.0f}<extra></extra>"

n_rounded = int(np.ceil(n))

# -----------------------------
# Output
# -----------------------------
st.markdown("---")
st.markdown("<div style='text-align:center;font-size:24px;'>Required sample size per group</div>", unsafe_allow_html=True)
st.markdown(
    f"<div style='text-align:center;font-size:48px;font-weight:bold;'>{n_rounded} patients</div>",
    unsafe_allow_html=True,
)

# -----------------------------
# Plot (dynamic vertical guide line ALWAYS ON)
# -----------------------------
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=x,
        y=np.log10(y),
        mode="lines",
        line=dict(width=3),
        customdata=y,
        hovertemplate=hover,
        showlegend=False,
    )
)

fig.update_layout(
    xaxis_title=x_title,
    yaxis_title="log₁₀(sample size)",
    hovermode="closest",
    plot_bgcolor="white",
    margin=dict(l=40, r=40, t=10, b=40),
)

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
# Contact
# -----------------------------
st.markdown("---")
st.markdown(
    "Questions or suggestions? Contact **[musccvi@musc.edu](mailto:musccvi@musc.edu)**",
    unsafe_allow_html=True,
)
