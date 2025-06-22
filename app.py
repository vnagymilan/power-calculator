import streamlit as st
import numpy as np
from scipy.stats import norm

st.set_page_config(page_title="PCD-CT vs. EID-CT Power Calculator", layout="centered")

st.title("Sample Size Calculator for PCD-CT vs. EID-CT")

st.markdown("""
This calculator estimates the **sample size per group** needed to detect a difference (Δ) in imaging biomarkers between CT systems.  
Please enter **absolute values** (e.g., entering 1.5 for CT-FFR is invalid).  
You can manually adjust standard deviation values below.
""")

# Mapping of biomarker -> {resolution -> {SDs + reference}}
biomarker_data = {
    "Stenosis severity (%)": {
        "Standard": {
            "bio_sd": 11.6, "inter_sd": 2.4,
            "ref": "Wolf EV et al. Imaging. 2023:1–8."
        },
        "UHR": {
            "bio_sd": 11.6, "inter_sd": 10.2,
            "ref": "Vecsey-Nagy M et al. Circ Cardiovasc Imaging. 2024:1–9."
        }
    },
    "CT-FFR": {
        "Standard": {
            "bio_sd": 0.08, "inter_sd": 0.09,
            "ref": "Zsarnoczay E et al. Int J Cardiol. 2024;399:131684."
        },
        "UHR": {
            "bio_sd": 0.08, "inter_sd": 0.11,
            "ref": "Vecsey-Nagy M et al. Eur J Radiol. 2024;181:111797."
        }
    },
    "Segment stenosis score": {
        "UHR": {
            "bio_sd": 5.93, "inter_sd": 3.18,
            "ref": "Tremamunno G et al. J Cardiovasc Comput Tomogr. 2025."
        }
    },
    "Segment involvement score": {
        "UHR": {
            "bio_sd": 3.87, "inter_sd": 2.63,
            "ref": "Tremamunno G et al. J Cardiovasc Comput Tomogr. 2025."
        }
    },
    "EAT volume (cl)": {
        "UHR": {
            "bio_sd": 13.15, "inter_sd": 5.65,
            "ref": "Kravchenko D et al. Eur J Radiol. 2024;181:111728."
        }
    },
    "EAT attenuation (HU)": {
        "UHR": {
            "bio_sd": 7.27, "inter_sd": 2.61,
            "ref": "Kravchenko D et al. Eur J Radiol. 2024;181:111728."
        }
    },
    "PCAT attenuation (HU)": {
        "UHR": {
            "bio_sd": 6.80, "inter_sd": 3.28,
            "ref": "Tremamunno G et al. Acad Radiol. 2025;32:1333–43."
        }
    },
    "Total plaque volume (mm³)": {
        "UHR": {
            "bio_sd": 45.58, "inter_sd": 19.75,
            "ref": "Vecsey-Nagy M et al. Radiology. 2025;314:e241479."
        }
    },
    "Calcified plaque volume (mm³)": {
        "UHR": {
            "bio_sd": 16.36, "inter_sd": 11.83,
            "ref": "Vecsey-Nagy M et al. Radiology. 2025;314:e241479."
        }
    },
    "Fibrotic plaque volume (mm³)": {
        "UHR": {
            "bio_sd": 30.53, "inter_sd": 16.35,
            "ref": "Vecsey-Nagy M et al. Radiology. 2025;314:e241479."
        }
    },
    "Low-attenuation plaque volume (mm³)": {
        "UHR": {
            "bio_sd": 22.94, "inter_sd": 13.58,
            "ref": "Vecsey-Nagy M et al. Radiology. 2025;314:e241479."
        }
    },
}

# Resolution selection
resolution = st.selectbox("Select PCD-CT resolution", ["Standard (0.4 mm)", "Ultrahigh-resolution (0.2 mm)"])
res_key = "Standard" if resolution.startswith("Standard") else "UHR"

# Biomarker options based on resolution
valid_biomarkers = [k for k, v in biomarker_data.items() if res_key in v]
biomarker = st.selectbox("Select biomarker", valid_biomarkers)
bdata = biomarker_data[biomarker][res_key]

# Input section
st.subheader("Study parameters")
col1, col2, col3 = st.columns(3)
with col1:
    alpha = st.number_input("Alpha (type I error)", min_value=0.001, max_value=0.5, value=0.05, step=0.01)
with col2:
    power = st.number_input("Power (1 - β)", min_value=0.01, max_value=0.99, value=0.8, step=0.05)
with col3:
    delta = st.number_input("Expected difference (Δ)", min_value=0.001, value=1.0, step=0.1)

# Custom SD inputs
st.subheader("Standard deviations (modifiable)")
bio_sd = st.number_input("Biological SD", value=bdata["bio_sd"], format="%.4f")
inter_sd = st.number_input("Inter-scanner SD*", value=bdata["inter_sd"], format="%.4f")
total_sd = np.sqrt(bio_sd**2 + inter_sd**2)

# Sample size calculation
z_alpha = norm.ppf(1 - alpha / 2)
z_beta = norm.ppf(power)
n = 2 * ((z_alpha + z_beta) * total_sd / delta) ** 2
n_rounded = int(np.ceil(n))

# Output
st.markdown("---")
st.subheader("Output")
st.write(f"**Total SD:** {total_sd:.3f}")
st.write(f"**Required sample size per group:** {n_rounded}")

# Reference + Contact
st.markdown("---")
st.markdown(f"""
<sup>*</sup>{bdata["ref"]}  
Questions or suggestions? Contact **[musccvi@musc.edu](mailto:musccvi@musc.edu)**
""", unsafe_allow_html=True)
