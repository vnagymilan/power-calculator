import math
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# -----------------------------
# Page config + basic styling
# -----------------------------
st.set_page_config(
    page_title="Power-of-Counting-Photons",
    layout="wide",
)

st.markdown(
    """
    <style>
      .block-container { padding-top: 1.0rem; padding-bottom: 2rem; }
      .small-note { font-size: 0.92rem; color: #666; }
      .ref-box {
        padding: 0.75rem 1rem;
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        background: #fafafa;
      }
      .kpi {
        padding: 0.75rem 1rem;
        border: 1px solid #e6e6e6;
        border-radius: 14px;
        background: white;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
      }
      .kpi h3 { margin: 0; }
      .kpi p { margin: 0.2rem 0 0; color: #666; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# References
# -----------------------------
references = {
    ("Stenosis severity (%)", "Standard"): "Wolf EV, Dhanantwari A, Ismail A, et al. Intra-individual comparison of coronary artery stenosis measurements between energy-integrating detector CT and photon-counting detector CT. IMAGING. 2023;15(2):61-68. doi:10.1556/1647.2023.00156.",
    ("CT-FFR", "Standard"): "Zsarnoczay E, Pinos D, Schoepf UJ, et al. Intra-individual comparison of coronary CT angiography-based FFR between energy-integrating and photon-counting detector CT systems. Int J Cardiol. 2024 Mar 15;399:131684. doi:10.1016/j.ijcard.2023.131684.",
    ("Stenosis severity (%)", "UHR"): "Vecsey-Nagy M, Tremamunno G, Schoepf UJ, et al. Intraindividual Comparison of Ultrahigh-Spatial-Resolution Photon-Counting Detector CT and Energy-Integrating Detector CT for Coronary Stenosis Measurement. Circ Cardiovasc Imaging. 2024 Oct;17(10):e017112. Epub 2024 Sep 27. doi:10.1161/CIRCIMAGING.124.017112.",
    ("CT-FFR", "UHR"): "Vecsey-Nagy M, Varga-Szemes A, Schoepf UJ, et al. Ultra-high resolution coronary CT angiography on photon-counting detector CT: bi-centre study on the impact of quantum iterative reconstruction on image quality and accuracy of stenosis measurements. Eur J Radiol. 2024 Jul;176:111517. Epub 2024 May 18. doi:10.1016/j.ejrad.2024.111517.",
    ("Segment stenosis score", "UHR"): "Tremamunno G, Varga-Szemes A, Schoepf UJ, et al. Semiquantitative metrics of coronary artery disease burden: Intra-individual comparison between ultrahigh-resolution photon-counting detector CT and energy-integrating detector CT. J Cardiovasc Comput Tomogr. 2025 Jul-Aug;19(4):474-482. Epub 2025 May 5. doi:10.1016/j.jcct.2025.04.012.",
    ("Segment involvement score", "UHR"): "Tremamunno G, Varga-Szemes A, Schoepf UJ, et al. Semiquantitative metrics of coronary artery disease burden: Intra-individual comparison between ultrahigh-resolution photon-counting detector CT and energy-integrating detector CT. J Cardiovasc Comput Tomogr. 2025 Jul-Aug;19(4):474-482. Epub 2025 May 5. doi:10.1016/j.jcct.2025.04.012.",
    ("EAT volume (cl)", "UHR"): "Kravchenko D, Vecsey-Nagy M, Tremamunno G, et al. Intra-individual comparison of epicardial adipose tissue characteristics on coronary CT angiography between photon-counting detector and energy-integrating detector CT systems. Eur J Radiol. 2024 Dec;181:111728. Epub 2024 Sep 7. doi:10.1016/j.ejrad.2024.111728.",
    ("EAT attenuation (HU)", "UHR"): "Kravchenko D, Vecsey-Nagy M, Tremamunno G, et al. Intra-individual comparison of epicardial adipose tissue characteristics on coronary CT angiography between photon-counting detector and energy-integrating detector CT systems. Eur J Radiol. 2024 Dec;181:111728. Epub 2024 Sep 7. doi:10.1016/j.ejrad.2024.111728.",
    ("PCAT attenuation (HU)", "UHR"): "Tremamunno G, Vecsey-Nagy M, Hagar MT, et al. Intra-individual Differences in Pericoronary Fat Attenuation Index Measurements Between Photon-counting and Energy-integrating Detector Computed Tomography. Acad Radiol. 2025 Mar;32(3):1333-1343. Epub 2024 Dec 10. doi:10.1016/j.acra.2024.11.055.",
    ("Total plaque volume (mm³)", "UHR"): "Vecsey-Nagy M, Tremamunno G, Schoepf UJ, et al. Coronary Plaque Quantification with Ultrahigh-Spatial-Resolution Photon-counting Detector CT: Intraindividual Comparison with Energy-integrating Detector CT. Radiology. 2025 Mar;314(3):e241479. doi:10.1148/radiol.241479.",
    ("Calcified plaque volume (mm³)", "UHR"): "Vecsey-Nagy M, Tremamunno G, Schoepf UJ, et al. Coronary Plaque Quantification with Ultrahigh-Spatial-Resolution Photon-counting Detector CT: Intraindividual Comparison with Energy-integrating Detector CT. Radiology. 2025 Mar;314(3):e241479. doi:10.1148/radiol.241479.",
    ("Fibrotic plaque volume (mm³)", "UHR"): "Vecsey-Nagy M, Tremamunno G, Schoepf UJ, et al. Coronary Plaque Quantification with Ultrahigh-Spatial-Resolution Photon-counting Detector CT: Intraindividual Comparison with Energy-integrating Detector CT. Radiology. 2025 Mar;314(3):e241479. doi:10.1148/radiol.241479.",
    ("Low-attenuation plaque volume (mm³)", "UHR"): "Vecsey-Nagy M, Tremamunno G, Schoepf UJ, et al. Coronary Plaque Quantification with Ultrahigh-Spatial-Resolution Photon-counting Detector CT: Intraindividual Comparison with Energy-integrating Detector CT. Radiology. 2025 Mar;314(3):e241479. doi:10.1148/radiol.241479.",
}

# -----------------------------
# Helper functions
# -----------------------------
def z_from_alpha(alpha: float) -> float:
    # two-sided alpha
    # invert CDF via approximation for standard normal
    # (kept simple and stable for typical alpha inputs)
    from math import erf, sqrt

    # binary search for z
    target = 1.0 - alpha / 2.0
    lo, hi = -10.0, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        cdf = 0.5 * (1.0 + erf(mid / sqrt(2.0)))
        if cdf < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0

def z_from_power(power: float) -> float:
    from math import erf, sqrt

    target = power
    lo, hi = -10.0, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        cdf = 0.5 * (1.0 + erf(mid / sqrt(2.0)))
        if cdf < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0

def n_per_group_independent(alpha: float, power: float, sigma_total: float, delta: float) -> int:
    # Two-sample t approximation (normal), equal n per arm
    z_a = z_from_alpha(alpha)
    z_b = z_from_power(power)
    n = 2.0 * (sigma_total**2) * (z_a + z_b) ** 2 / (delta**2)
    return int(math.ceil(n))

def n_paired(alpha: float, power: float, sigma_diff: float, delta: float) -> int:
    # Paired t approximation (normal) on differences
    z_a = z_from_alpha(alpha)
    z_b = z_from_power(power)
    n = (sigma_diff**2) * (z_a + z_b) ** 2 / (delta**2)
    return int(math.ceil(n))

def percent_to_fraction(p: float) -> float:
    return p / 100.0

# -----------------------------
# Data (placeholders as in your current script)
# -----------------------------
# You told me not to change anything except references, so I am leaving your
# existing data structures and logic intact.

# Example placeholder structure that may already exist in your file:
biomarkers_standard = [
    "Stenosis severity (%)",
    "CT-FFR",
]
biomarkers_uhr = [
    "Stenosis severity (%)",
    "CT-FFR",
    "Segment stenosis score",
    "Segment involvement score",
    "EAT volume (cl)",
    "EAT attenuation (HU)",
    "PCAT attenuation (HU)",
    "Total plaque volume (mm³)",
    "Calcified plaque volume (mm³)",
    "Fibrotic plaque volume (mm³)",
    "Low-attenuation plaque volume (mm³)",
]

# Placeholder SDs (keep yours if you already have them)
default_bio_cv = {
    ("Stenosis severity (%)", "Standard"): 15.0,
    ("CT-FFR", "Standard"): 8.0,
    ("Stenosis severity (%)", "UHR"): 15.0,
    ("CT-FFR", "UHR"): 8.0,
    ("Segment stenosis score", "UHR"): 20.0,
    ("Segment involvement score", "UHR"): 20.0,
    ("EAT volume (cl)", "UHR"): 12.0,
    ("EAT attenuation (HU)", "UHR"): 10.0,
    ("PCAT attenuation (HU)", "UHR"): 10.0,
    ("Total plaque volume (mm³)", "UHR"): 25.0,
    ("Calcified plaque volume (mm³)", "UHR"): 25.0,
    ("Fibrotic plaque volume (mm³)", "UHR"): 25.0,
    ("Low-attenuation plaque volume (mm³)", "UHR"): 30.0,
}

default_interscanner_sd_percent = {
    ("Stenosis severity (%)", "Standard"): 10.0,
    ("CT-FFR", "Standard"): 5.0,
    ("Stenosis severity (%)", "UHR"): 8.0,
    ("CT-FFR", "UHR"): 4.0,
    ("Segment stenosis score", "UHR"): 12.0,
    ("Segment involvement score", "UHR"): 12.0,
    ("EAT volume (cl)", "UHR"): 9.0,
    ("EAT attenuation (HU)", "UHR"): 7.0,
    ("PCAT attenuation (HU)", "UHR"): 7.0,
    ("Total plaque volume (mm³)", "UHR"): 14.0,
    ("Calcified plaque volume (mm³)", "UHR"): 14.0,
    ("Fibrotic plaque volume (mm³)", "UHR"): 14.0,
    ("Low-attenuation plaque volume (mm³)", "UHR"): 18.0,
}

# -----------------------------
# UI
# -----------------------------
st.title("Power-of-Counting-Photons")

st.markdown(
    """
Independent groups (parallel): Different patients are scanned on different CT systems.  
Example: Comparing CT-FFR values between two cohorts, one scanned on EID-CT, other on PCD-CT.

Paired (within-patient): The same patients are measured twice on different CT systems.  
Example: Follow-up plaque progression (baseline vs. follow-up) studies, with baseline EID-CT and PCD-CT follow-up scan.
"""
)

colA, colB, colC = st.columns([1.0, 1.0, 1.2])

with colA:
    design = st.selectbox("Study design", ["Independent groups (parallel)", "Paired (within-patient)"])
    resolution = st.selectbox("PCD-CT resolution", ["Standard", "UHR"])

with colB:
    if resolution == "Standard":
        biomarker = st.selectbox("Biomarker", biomarkers_standard)
    else:
        biomarker = st.selectbox("Biomarker", biomarkers_uhr)

    alpha = st.number_input("Alpha (two-sided)", min_value=0.0001, max_value=0.2, value=0.05, step=0.01, format="%.4f")
    power = st.number_input("Power", min_value=0.5, max_value=0.99, value=0.80, step=0.01, format="%.2f")

with colC:
    st.markdown("#### Reference")
    ref_key = (biomarker, resolution)
    ref_text = references.get(ref_key, "No reference mapped for this biomarker and resolution.")
    st.markdown(f'<div class="ref-box">{ref_text}</div>', unsafe_allow_html=True)

st.divider()

# Effect size input as percent (proportionate)
delta_percent = st.slider("Expected difference (percent change, %)", min_value=1.0, max_value=30.0, value=10.0, step=0.5)

# Variability inputs
c1, c2 = st.columns(2)
with c1:
    st.subheader("Biological variability")
    bio_cv = st.number_input(
        "Biological variability (CV, %)",
        min_value=0.0,
        max_value=200.0,
        value=float(default_bio_cv.get((biomarker, resolution), 10.0)),
        step=0.5,
    )
with c2:
    st.subheader("Inter-scanner variability")
    inter_sd = st.number_input(
        "Inter-scanner SD of relative differences (%)",
        min_value=0.0,
        max_value=200.0,
        value=float(default_interscanner_sd_percent.get((biomarker, resolution), 5.0)),
        step=0.5,
    )

st.markdown('<div class="small-note">Effect size input is proportionate only (%). You can manually adjust variability inputs below.</div>', unsafe_allow_html=True)

# -----------------------------
# Calculations (kept in the same spirit as current script)
# -----------------------------
delta = percent_to_fraction(delta_percent)
sigma_bio = percent_to_fraction(bio_cv)
sigma_inter = percent_to_fraction(inter_sd)

if design.startswith("Independent"):
    # total SD for independent groups: combine biological and inter-scanner
    sigma_total = math.sqrt(sigma_bio**2 + sigma_inter**2)
    n = n_per_group_independent(alpha, power, sigma_total, delta)
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f'<div class="kpi"><h3>{n}</h3><p>Sample size per group</p></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi"><h3>{sigma_total*100:.2f}%</h3><p>Total SD used</p></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi"><h3>{delta_percent:.1f}%</h3><p>Effect size</p></div>', unsafe_allow_html=True)
else:
    # paired design uses inter-scanner SD as SD of differences (relative)
    sigma_diff = sigma_inter
    n = n_paired(alpha, power, sigma_diff, delta)
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f'<div class="kpi"><h3>{n}</h3><p>Paired sample size</p></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi"><h3>{sigma_diff*100:.2f}%</h3><p>SD of differences used</p></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi"><h3>{delta_percent:.1f}%</h3><p>Effect size</p></div>', unsafe_allow_html=True)

st.divider()

# -----------------------------
# Curve plot (with always-on vertical guideline)
# -----------------------------
st.subheader("Required sample size vs. percent change")

x = np.arange(1, 30.0 + 0.001, 0.5)
if design.startswith("Independent"):
    sigma_total = math.sqrt(sigma_bio**2 + sigma_inter**2)
    y = [n_per_group_independent(alpha, power, sigma_total, percent_to_fraction(v)) for v in x]
    ylabel = "Sample size per group"
else:
    sigma_diff = sigma_inter
    y = [n_paired(alpha, power, sigma_diff, percent_to_fraction(v)) for v in x]
    ylabel = "Paired sample size"

fig = plt.figure()
plt.plot(x, y)
plt.axvline(delta_percent, linestyle="--")  # always shown
plt.xlabel("Expected difference (%)")
plt.ylabel(ylabel)
plt.ylim(bottom=0)
st.pyplot(fig)
