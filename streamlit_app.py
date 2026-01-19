import streamlit as st
import requests
import pandas as pd

API_KEY = "CBOA1F56A2C833792B2C6AAAFDF9889C7"

st.title("Analizator Gier Steam")

appid = st.text_input("Podaj AppID gry (np. 730 = CS2, 440 = TF2):")

if appid:
    # Podstawowe dane gry
    url_details = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    det = requests.get(url_details).json()
    
    if appid in det and det[appid].get("success"):
        data = det[appid]["data"]
        st.subheader(data.get("name", "Brak nazwy"))
        st.write(f"Developer: {', '.join(data.get('developers', ['-']))}")
        st.write(f"Release date: {data.get('release_date', {}).get('date', '-')}")
        
        # Ocena ogólna + recenzje
        url_reviews = f"https://store.steampowered.com/appreviews/{appid}?json=1&filter=summary"
        rev_summary = requests.get(url_reviews).json()
        qs = rev_summary.get("query_summary", {})
        
        if qs:
            st.write(f"**Ocena:** {qs.get('review_score_desc', '-')}")
            st.write(f"Pozytywne: {qs.get('total_positive', 0):,} ({qs.get('total_positive_percentage', 0)}%)")
            st.write(f"Negatywne: {qs.get('total_negative', 0):,}")
        
        # Tagi
        url_tags = f"https://steamspy.com/api.php?request=appdetails&appid={appid}"
        response = requests.get(url_tags)
        if response.status_code == 200:
            data = response.json()
            tags = data.get("tags", {})
            if tags:
                tag_df = pd.DataFrame([
                    {"Tag": tag, "Głosy": count} 
                    for tag, count in tags.items()
                ]).sort_values("Głosy", ascending=False)
                st.subheader("Najpopularniejsze tagi (SteamSpy)")
                st.dataframe(tag_df.head(12))
            else:
                st.write("Brak tagów w SteamSpy")
        else:
            st.write("SteamSpy niedostępny")
        
        # Gracze online teraz
        url_players = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}&key={API_KEY}"
        players = requests.get(url_players).json()
        count = players["response"].get("player_count", 0)
        st.write(f"**Graczy online teraz:** {count:,}")
    else:
        st.error("Nie znaleziono gry o podanym AppID")
