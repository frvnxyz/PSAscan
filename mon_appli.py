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

# Style CSS forcé pour éviter le texte blanc sur fond blanc
st.markdown("""
    <style>
    .main { background-color: #f5f5f7; }
    
    /* Style des cartes Note et Certif */
    .metric-container {
        background-color: #ffffff !important;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid #e1e1e1;
    }
    
    /* On force la couleur du texte en NOIR */
    .metric-container p {
        color: #666666 !important;
        margin: 0 !important;
        font-size: 0.8em;
    }
    .metric-container h2 {
        color: #1d1d1f !important;
        margin: 0 !important;
        font-weight: bold;
    }
    
    /* Style du bouton eBay */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #007aff !important;
        color: white !important;
        font-weight: bold;
        border: none;
        margin-top: 10px;
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
st.markdown("<h3 style='text-align: center; color: #1d1d1f;'>🔍 Scanner PSA Pro</h3>", unsafe_allow_html=True)

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
        cert_val = certs[-1] if certs else "N/A"
        
        grade_val = "N/A"
        if "10" in full_text: grade_val = "10"
        elif "9" in full_text: grade_val = "9"
        elif "8" in full_text: grade_val = "8"

        details_carte = clean_text_elements(full_text, cert_val)
        construction = f"PSA {grade_val} - {details_carte}"

        st.markdown("---")
        
        # AFFICHAGE DES CARTES (Texte forcé en noir via HTML direct pour plus de sécurité)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class='metric-container'>
                    <p>NOTE</p>
                    <h2 style='color: #007aff !important;'>{grade_val}</h2>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class='metric-container'>
                    <p>CERTIFICAT</p>
                    <h2 style='font-size: 1.1em;'>{cert_val}</h2>
                </div>
            """, unsafe_allow_html=True)

        st.write("") 
        
        # Zone d'édition
        titre_final = st.text_input("📝 Nom de la carte :", value=construction)
        
        if titre_final:
            search_query = titre_final.replace(" ", "+")
            ebay_url = f"https://www.ebay.fr/sch/i.html?_nkw={search_query}&LH_Sold=1&LH_Complete=1"
            st.link_button(f"💰 VOIR LES PRIX VENDUS", ebay_url)

        with st.expander("📄 Voir le texte brut"):
            st.code(full_text)
