import streamlit as st
import requests
import pandas as pd

st.title("Analizator Gier Steam")

appid = st.text_input("Podaj AppID (np. 730 dla CS:GO)")

if appid:
    # Szczegóły
    det = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}").json()
    st.write(det[appid]['data']['name'])

    # Recenzje
    rev = requests.get(f"https://store.steampowered.com/appreviews/{appid}?json=1&num_per_page=100").json()
    df = pd.DataFrame(rev['reviews'])
    st.dataframe(df[['recommendationid', 'author', 'review', 'voted_up']])

    # Analiza: % pozytywnych
    pos = len(df[df['voted_up'] == True]) / len(df) * 100
    st.write(f"Pozytywne: {pos:.2f}%")

    # Gracze online
    players = requests.get(f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}").json()
    st.write(f"Graczy online: {players['response']['player_count']}")
