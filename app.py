import streamlit as st
import numpy as np
from scipy.stats import norm
from PIL import Image

# Page setup
st.set_page_config(page_title="PCD-CT vs. EID-CT Power Calculator", layout="centered")

# Load MUSC logo
logo_path = "Image 22.6.2025 at 10.58.jpeg"  # make sure this file is in the same directory or adjust path
logo = Image.open(logo_path)

# Title and logo
col1, col2 = st.columns([1, 4])
with col1:
    st.image(logo, width=100)
with col2:
    st.markdown("""
        <div style='padding-top: 15px; font-size: 26px; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>
            PCD-CT vs. EID-CT Sample Size Calculator
        </div>
    """, unsafe_allow_html=True)

# Introduction
st.markdown("""
This calculator estimates the **sample size per group** needed to detect a difference (Δ) in imaging biomarkers between CT systems.  
Please enter **absolute values** (e.g., entering 1.5 for CT-FFR is invalid).  
You can manually adjust standard deviation values below.

- **Biological SD** represents variation across different patients.  
- **Inter-scanner SD** reflects intra-individual variation when the same patient is scanned on both PCD-CT and EID-CT.
""")

# Long-format references
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
    ("Low-attenuation plaque volume (mm³)", "UHR"): "Vecsey-Nagy M., Tremamunno G., Schoepf UJ., et al. Coronary Plaque Quantification with Ultrahigh-Spatial-Resolution Photon-counting Detector CT: Intraindividual Comparison with Energy-integrating Detector CT. Radiology. 2025;314:e241479."
}

# SD data
biomarker_data = {
    "Stenosis severity (%)": {
        "Standard": {"bio_sd": 11.6, "inter_sd": 2.4},
        "UHR": {"bio_sd": 11.6, "inter_sd": 10.2}
    },
    "CT-FFR": {
        "Standard": {"bio_sd": 0.08, "inter_sd": 0.09},
        "UHR": {"bio_sd": 0.08, "inter_sd": 0.11}
    },
    "Segment stenosis score": {"UHR": {"bio_sd": 5.93, "inter_sd": 3.18}},
    "Segment involvement score": {"UHR": {"bio_sd": 4.44, "inter_sd": 1.47}},
    "EAT volume (cl)": {"UHR": {"bio_sd": 5.67, "inter_sd": 2.27}},
    "EAT attenuation (HU)": {"UHR": {"bio_sd": 5.20, "inter_sd": 6.53}},
    "PCAT attenuation (HU)": {"UHR": {"bio_sd": 8.00, "inter_sd": 7.37}},
    "Total plaque volume (mm³)": {"UHR": {"bio_sd": 515.00, "inter_sd": 239.54}},
    "Calcified plaque volume (mm³)": {"UHR": {"bio_sd": 148.60, "inter_sd": 142.02}},
    "Fibrotic plaque volume (mm³)": {"UHR": {"bio_sd": 380.10, "inter_sd": 206.60}},
    "Low-attenuation plaque volume (mm³)": {"UHR": {"bio_sd": 11.90, "inter_sd": 84.59}}
}

# Inputs
resolution = st.selectbox("Select PCD-CT resolution", ["Standard (0.4 mm)", "Ultrahigh-resolution (0.2 mm)"])
res_key = "Standard" if resolution.startswith("Standard") else "UHR"

valid_biomarkers = [k for k in biomarker_data if res_key in biomarker_data[k]]
biomarker = st.selectbox("Select biomarker", valid_biomarkers)
bdata = biomarker_data[biomarker][res_key]
ref = long_refs.get((biomarker, res_key), "Reference not available.")


col1, col2, col3 = st.columns(3)

with col1:
    alpha = st.number_input("Alpha", min_value=0.001, max_value=0.5, value=0.05, step=0.01)

with col2:
    power = st.number_input("Power", min_value=0.01, max_value=0.99, value=0.8, step=0.05)

# Δ range dictionary
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
    "Low-attenuation plaque volume (mm³)": (1.0, 10000.0)
}

# Use delta range dynamically
delta_min, delta_max = delta_limits.get(biomarker, (0.001, 100.0))

with col3:
    delta = st.number_input(
        "Δ (Expected difference)",
        min_value=delta_min,
        max_value=delta_max,
        value=delta_min,
        step=0.1
    )



bio_sd = st.number_input("Biological SD", value=bdata["bio_sd"], format="%.4f")
inter_sd = st.number_input("Inter-scanner SD*", value=bdata["inter_sd"], format="%.4f")
total_sd = np.sqrt(bio_sd**2 + inter_sd**2)
st.markdown(f"**Total SD:** {total_sd:.3f}")

# Sample size
z_alpha = norm.ppf(1 - alpha / 2)
z_beta = norm.ppf(power)
n = 2 * ((z_alpha + z_beta) * total_sd / delta) ** 2
n_rounded = int(np.ceil(n))

# Output
st.markdown("---")
st.markdown(f"<div style='text-align: center; font-size: 24px;'>Required sample size per group</div>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align: center; font-size: 48px; font-weight: bold;'>{n_rounded} patients</div>", unsafe_allow_html=True)

import matplotlib.pyplot as plt

# Optional sample size curve
if st.button("Show sample size curve"):
    # Generate Δ values
    delta_range = np.linspace(delta_min, delta_max, 100)

    # Sample size formula
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)
    sample_sizes = 2 * ((z_alpha + z_beta) * total_sd / delta_range) ** 2

    # Clamp minimum sample size to avoid log10(sample_sizes < 1)
    sample_sizes = np.clip(sample_sizes, 1, None)

    # Plotting log10 of sample size
    fig, ax = plt.subplots()
    ax.plot(delta_range, np.log10(sample_sizes), linewidth=2)
    ax.set_xlabel("Expected difference (Δ)")
    ax.set_ylabel("log₁₀(sample size)")
    ax.set_title(f"Sample Size Curve for {biomarker}")
    ax.set_ylim(bottom=0.0)  # Show y-axis starting at log₁₀(1) = 0
    ax.grid(True)

    st.pyplot(fig)


# Reference and contact
st.markdown("---")
st.markdown(f"""
<sup>*</sup>{ref}  

Questions or suggestions? Contact **[musccvi@musc.edu](mailto:musccvi@musc.edu)**
""", unsafe_allow_html=True)

