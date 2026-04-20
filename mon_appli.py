import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re

# Configuration pour mobile
st.set_page_config(page_title="PSA Japan Pro", layout="centered")

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

st.title("🎴 Scanner PSA Japon")

mode = st.radio("Source :", ["Appareil Photo", "Importer"], horizontal=True)

img_file = None
if mode == "Appareil Photo":
    # Le paramètre 'facingMode' aide certains téléphones à choisir la bonne caméra
    img_file = st.camera_input("Scanner l'étiquette")
else:
    img_file = st.file_uploader("Choisir une image", type=["jpg", "png"])

if img_file:
    with st.spinner("Analyse..."):
        img = Image.open(img_file)
        img_np = np.array(img)
        results = reader.readtext(img_np, detail=0)
        full_text = " ".join(results)
        
        texte_colle = full_text.replace(" ", "")
        certs = re.findall(r'\d{8,9}', texte_colle)
        cert_val = certs[-1] if certs else ""
        
        grade_val = "N/A"
        if "10" in full_text: grade_val = "10"
        elif "9" in full_text: grade_val = "9"
        elif "8" in full_text: grade_val = "8"

        details_carte = clean_text_elements(full_text, cert_val)
        construction = f"PSA {grade_val} - {details_carte}"
        
        st.divider()
        titre_final = st.text_input("Titre eBay :", value=construction)
        cert_final = st.text_input("Certificat :", value=cert_val)

        if titre_final:
            search_query = titre_final.replace(" ", "+")
            ebay_url = f"https://www.ebay.fr/sch/i.html?_nkw={search_query}&LH_Sold=1&LH_Complete=1"
            st.link_button(f"💰 Voir prix vendus pour : PSA {grade_val}", ebay_url)