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

**Effect size input is proportionate only (%).**
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
    ("Low-attenuation plaque volume (mm³)", "
