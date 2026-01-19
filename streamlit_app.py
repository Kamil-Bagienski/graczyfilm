import streamlit as st
import requests
import pandas as pd

API_KEY = "CBOA1F56A2C833792B2C6AAAFDF9889C7"

st.title("Analizator Gier Steam")

appid = st.text_input("Podaj AppID gry (np. 730 = CS2, 440 = TF2):")

if appid:
    # Dane gry
    url_details = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    det = requests.get(url_details).json()
    
    if appid in det and det[appid].get("success"):
        data = det[appid]["data"]
        
        st.subheader(data.get("name", "Brak nazwy"))
        
        # Krótki opis
        full_desc = data.get("detailed_description", "Brak szczegółowego opisu")
        st.markdown("**Pełny opis:**")
        st.markdown(full_desc, unsafe_allow_html=True)
        
        # Ocena ogólna
        url_reviews = f"https://store.steampowered.com/appreviews/{appid}?json=1&filter=summary"
        rev = requests.get(url_reviews).json()
        qs = rev.get("query_summary", {})
        if qs:
            st.write(f"**Ocena:** {qs.get('review_score_desc', '-')}")
            st.write(f"Pozytywne: {qs.get('total_positive', 0):,} ({qs.get('total_positive_percentage', 0)}%)")
            st.write(f"Negatywne: {qs.get('total_negative', 0):,}")
        
        # Tagi przez SteamSpy
        url_tags = f"https://steamspy.com/api.php?request=appdetails&appid={appid}"
        resp = requests.get(url_tags)
        if resp.status_code == 200:
            tags_data = resp.json()
            tags = tags_data.get("tags", {})
            if tags:
                tag_df = pd.DataFrame([
                    {"Tag": tag, "Głosy": count} 
                    for tag, count in tags.items()
                ]).sort_values("Głosy", ascending=False)
                st.subheader("Najpopularniejsze tagi")
                st.dataframe(tag_df.head(12))
            else:
                st.write("Brak tagów")
        else:
            st.write("SteamSpy niedostępny")
        
        # Gracze online
        url_players = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}&key={API_KEY}"
        players = requests.get(url_players).json()
        count = players["response"].get("player_count", 0)
        st.write(f"**Graczy online teraz:** {count:,}")
        
    else:
        st.error("Nie znaleziono gry")
