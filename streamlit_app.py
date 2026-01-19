import streamlit as st
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

# Przykładowy model ML (trenowany na dummy danych; dostosuj)
vectorizer = TfidfVectorizer()
X_train = vectorizer.fit_transform([
    "Gra z celami, zasadami, wyzwaniami i interakcją.",  # Gra
    "Interaktywny film bez wyzwań, tylko wybory fabularne."  # Film
])
y_train = np.array([1, 0])  # 1=gra, 0=film
model = LogisticRegression().fit(X_train, y_train)

API_KEY = "CBOA1F56A2C833792B2C6AAAFDF9889C7"

st.title("Klasyfikator Gier vs. Filmów Interaktywnych")

appid = st.text_input("AppID gry (np. 730):")

if appid:
    det = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}").json()
    if appid in det and det[appid].get("success"):
        data = det[appid]["data"]
        st.subheader(data.get("name", "Brak nazwy"))
        
        # Opis do analizy AI
        desc = data.get("detailed_description", "")
        st.markdown("**Opis:**")
        st.markdown(desc, unsafe_allow_html=True)
        
        # AI klasyfikacja
        if desc:
            X_test = vectorizer.transform([desc])
            pred = model.predict(X_test)[0]
            prob = model.predict_proba(X_test)[0][1] * 100
            st.write(f"**Klasyfikacja AI:** {'Gra' if pred == 1 else 'Film interaktywny'} ({prob:.2f}% pewności jako gra)")
        
        # Formularz ręczny (filary)
        st.subheader("Ręczna klasyfikacja")
        goals = st.slider("Cele (0-10)", 0, 10, 5)
        rules = st.slider("Zasady (0-10)", 0, 10, 5)
        challenge = st.slider("Wyzwanie (0-10)", 0, 10, 5)
        interaction = st.slider("Interakcja (0-10)", 0, 10, 5)
        
        score = (goals + rules + challenge + interaction) / 40 * 100
        st.write(f"**Wynik:** {score:.2f}% (powyżej 50% = gra)")
        
        # Inne dane (jak wcześniej)
        # ... (dodaj resztę z poprzedniego kodu jeśli chcesz)
    else:
        st.error("Nie znaleziono gry")
