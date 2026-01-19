import streamlit as st
import requests
from transformers import pipeline

st.title("Gra czy Film Interaktywny – Lepsze AI")

# Ładujemy model (pobierze się automatycznie przy pierwszym uruchomieniu)
@st.cache_resource
def load_classifier():
    return pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

classifier = load_classifier()

appid = st.text_input("AppID gry:")

if appid:
    r = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}")
    data = r.json()
    
    if appid in data and data[appid].get("success"):
        game = data[appid]["data"]
        name = game.get("name", "—")
        desc = game.get("detailed_description", "")
        
        st.subheader(name)
        st.markdown("**Pełny opis:**")
        st.markdown(desc, unsafe_allow_html=True)
        
        if desc:
            result = classifier(desc[:512])[0]  # ograniczenie długości
            label = result["label"]
            score = result["score"] * 100
            
            if label == "POSITIVE":
                verdict = "GRA"
                confidence = score
            else:
                verdict = "FILM INTERAKTYWNY / SPACERÓWKA"
                confidence = 100 - score
                
            st.markdown(f"**AI ocena:** {verdict}  –  {confidence:.1f}%")
        else:
            st.info("Brak opisu do analizy")
            
    else:
        st.error("Nie znaleziono gry")
