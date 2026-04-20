import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re

# --- CONFIGURATION MOBILE ---
st.set_page_config(
    page_title="PSA Scan Pro", 
    page_icon="🔍",
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# Style CSS pour que ça ressemble à une vraie App iPhone
st.markdown("""
    <style>
    .main { background-color: #f5f5f7; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #007aff;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .metric-container {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

def clean_text_elements(full_text, cert):
    query = full_text.replace(cert, "")
    garbage = ["MINT", "GEM MT", "PRISTINE", "NM-MT"]
    for word in garbage:
        query = query.replace(word, "")
    query = re.sub(r'[^a-zA-Z0-9\s#\-]', ' ', query)
    words = query.split()
    final_words = [w for w in words if len(w) >= 2]
    return " ".join(final_words).upper()

# --- HEADER APP ---
st.markdown("<h2 style='text-align: center; color: #1d1d1f;'>🔍 Scanner PSA</h2>", unsafe_allow_html=True)

# Tabs pour un look plus "iOS"
tab1, tab2 = st.tabs(["📸 Caméra", "📂 Album"])

with tab1:
    img_file_cam = st.camera_input("Scanner l'étiquette")
with tab2:
    img_file_up = st.file_uploader("Choisir une photo", type=["jpg", "png"])

img_file = img_file_cam if img_file_cam else img_file_up

if img_file:
    with st.spinner("Analyse..."):
        img = Image.open(img_file)
        img_np = np.array(img)
        results = reader.readtext(img_np, detail=0)
        full_text = " ".join(results)
        
        # Extraction Data
        texte_colle = full_text.replace(" ", "")
        certs = re.findall(r'\d{8,9}', texte_colle)
        cert_val = certs[-1] if certs else ""
        
        grade_val = "N/A"
        if "10" in full_text: grade_val = "10"
        elif "9" in full_text: grade_val = "9"
        elif "8" in full_text: grade_val = "8"

        details_carte = clean_text_elements(full_text, cert_val)
        construction = f"PSA {grade_val} - {details_carte}"

        # --- AFFICHAGE STYLE IPHONE ---
        st.markdown("---")
        
        # Affichage des métriques dans des jolies cartes
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='metric-container'><p style='color:gray;margin:0;'>NOTE</p><h2 style='margin:0;color:#007aff;'>{grade_val}</h2></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-container'><p style='color:gray;margin:0;'>CERTIF</p><h2 style='margin:0;font-size:1.2em;padding-top:8px;'>{cert_val}</h2></div>", unsafe_allow_html=True)

        st.write("") # Espace
        
        # Titre éditable
        titre_final = st.text_input("📝 Nom détecté :", value=construction)
        
        # Bouton eBay géant
        if titre_final:
            search_query = titre_final.replace(" ", "+")
            ebay_url = f"https://www.ebay.fr/sch/i.html?_nkw={search_query}&LH_Sold=1&LH_Complete=1"
            st.link_button(f"💰 VOIR PRIX VENDUS", ebay_url)

        with st.expander("📄 Voir le texte brut"):
            st.code(full_text)
