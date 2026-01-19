import streamlit as st
import requests
import re

st.title("Gra czy Film Interaktywny – Na Podstawie Filarów")

# Słowa kluczowe dla filarów (angielski, bo API Steam zwraca opisy po ang.)
goals_keywords = ["goal", "objective", "mission", "level", "quest", "achieve", "win", "complete"]
rules_keywords = ["rule", "mechanic", "system", "control", "tutorial", "guide", "strategy", "skill"]
challenge_keywords = ["challenge", "difficulty", "boss", "puzzle", "enemy", "combat", "survive", "hard"]
interaction_keywords = ["interact", "control", "player", "choice", "decision", "build", "explore", "customize"]

def score_filar(text, keywords):
    text = text.lower()
    count = sum(len(re.findall(r'\b' + kw + r'\b', text)) for kw in keywords)
    return min(10, count * 2)  # Prosty scoring: max 10

appid = st.text_input("AppID gry:")

if appid:
    r = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}")
    data = r.json()
    
    if appid in data and data[appid].get("success"):
        game = data[appid]["data"]
        name = game.get("name", "—")
        desc = game.get("detailed_description", "").lower()
        
        st.subheader(name)
        st.markdown("**Pełny opis:**")
        st.markdown(game.get("detailed_description", "Brak"), unsafe_allow_html=True)
        
        if desc:
            g_score = score_filar(desc, goals_keywords)
            r_score = score_filar(desc, rules_keywords)
            c_score = score_filar(desc, challenge_keywords)
            i_score = score_filar(desc, interaction_keywords)
            
            total = (g_score + r_score + c_score + i_score) / 4
            verdict = "GRA" if total > 5 else "FILM INTERAKTYWNY"
            
            st.markdown(f"**AI ocena:** {verdict} ({total:.1f}/10 średnio)")
            st.write(f"Cele: {g_score}/10")
            st.write(f"Zasady: {r_score}/10")
            st.write(f"Wyzwanie: {c_score}/10")
            st.write(f"Interakcja: {i_score}/10")
        else:
            st.info("Brak opisu")
            
    else:
        st.error("Nie znaleziono gry")
