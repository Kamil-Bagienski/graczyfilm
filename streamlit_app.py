import streamlit as st
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

# Prosty model AI
vectorizer = TfidfVectorizer()
X_train = vectorizer.fit_transform([
    "Gra z celami, zasadami, wyzwaniami i interakcją gracza.",
    "Interaktywny film bez wyzwań, tylko wybory fabularne.",
    "Przygodówka z zagadkami i mechanikami rozgrywki.",
    "Spacerówka z pięknymi widokami i historią bez zasad."
])
y_train = np.array([1, 0, 1, 0])
model = LogisticRegression().fit(X_train, y_train)

API_KEY = "CBOA1F56A2C833792B2C6AAAFDF9889C7"

st.title("Gra czy Film Interaktywny")

appid = st.text_input("AppID gry:")

if appid:
    det = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}").json()
    
    if appid in det and det[appid].get("success"):
        data = det[appid]["data"]
        name = data.get("name", "Brak nazwy")
        
        st.subheader(name)
        
        # Krótki opis
        st.markdown("**Krótki opis:**")
        st.write(data.get("short_description", "—"))
        
        # Pełny opis
        st.markdown("**Pełny opis:**")
        st.markdown(data.get("detailed_description", "Brak opisu"), unsafe_allow_html=True)
        
        # AI klasyfikacja
        desc = data.get("detailed_description", "")
        if desc:
            X_test = vectorizer.transform([desc])
            pred = model.predict(X_test)[0]
            prob = model.predict_proba(X_test)[0][1] * 100
            wynik = "GRA" if pred == 1 else "FILM INTERAKTYWNY"
            st.markdown(f"**AI mówi:** {wynik} ({prob:.1f}%)")
        
        # Ręczna ocena
        st.subheader("Ręczna ocena (0–10)")
        g = st.slider("Cele", 0, 10, 5)
        z = st.slider("Zasady", 0, 10, 5)
        w = st.slider("Wyzwanie", 0, 10, 5)
        i = st.slider("Interakcja", 0, 10, 5)
        
        score = (g + z + w + i) / 40 * 100
        st.write(f"Wynik: **{score:.1f}%**")
        
    else:
        st.error("Nie znaleziono gry")
