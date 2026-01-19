import streamlit as st
import requests
import re

st.title("Gra czy Film Interaktywny")

goals_k     = r'\b(goal|objective|mission|quest|task|target|win|complete|achieve|end|finish|unlock|progress|level up)\b'
rules_k     = r'\b(rule|mechanic|system|control|tutorial|strategy|skill|ability|upgrade|craft|build|inventory|resource)\b'
challenge_k = r'\b(challenge|difficulty|hard|boss|enemy|combat|fight|die|survive|puzzle|obstacle|fail|retry|death)\b'
inter_k     = r'\b(interact|control|player|choice|decision|action|move|explore|customize|create|play|engage|affect)\b'

def count_score(text, pattern):
    return len(re.findall(pattern, text.lower()))

appid = st.text_input("AppID:")

if appid:
    r = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}")
    if appid in (d := r.json()) and d[appid].get("success"):
        game = d[appid]["data"]
        name = game.get("name", "?")
        desc = (game.get("detailed_description") or "").lower()
        
        st.subheader(name)
        st.markdown(desc, unsafe_allow_html=True)
        
        if desc:
            g = count_score(desc, goals_k)
            r = count_score(desc, rules_k)
            c = count_score(desc, challenge_k)
            i = count_score(desc, inter_k)
            
            total = g + r + c + i
            avg   = total / 4
            score = min(10, avg * 0.8)   # skalowanie empiryczne
            
            verdict = "GRA" if score > 4.5 else "FILM / SPACERÓWKA"
            
            st.markdown(f"**Wynik: {verdict}  –  {score:.1f}/10**")
            st.write(f"Cele: {g} pkt")
            st.write(f"Zasady: {r} pkt")
            st.write(f"Wyzwanie: {c} pkt")
            st.write(f"Interakcja: {i} pkt")
        else:
            st.info("Brak opisu")
    else:
        st.error("Gra nie znaleziona")
