import streamlit as st
import requests
import re
import csv
from pathlib import Path
from datetime import datetime

# ==================================================
#  TUTAJ WKLEJ SWÓJ KLUCZ API (JEŚLI BĘDZIE POTRZEBA)
# ==================================================
STEAM_API_KEY = "CB0A1F56A2C833792BC26AAFDF9889C7"   # <-- TU WKLEJ KLUCZ (opcjonalne)

# ==================================================
OUT_CSV = "train_data.csv"
LABELS = ["goals", "rules", "challenge", "interaction"]

def clean_html(text: str) -> str:
    text = text or ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def fetch_appdetails(appid: str) -> dict | None:
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=english"
    try:
        r = requests.get(url, timeout=20)
        d = r.json()
    except Exception:
        return None

    if appid not in d or not d[appid].get("success"):
        return None

    return d[appid]["data"]

def get_description(data: dict) -> str:
    return clean_html(
        data.get("detailed_description")
        or data.get("about_the_game")
        or ""
    )

def append_row(row: dict):
    file_exists = Path(OUT_CSV).exists()
    with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def parse_appids(text: str):
    return [x for x in re.split(r"[,\s]+", text.strip()) if x.isdigit()]

# ==================================================
#  UI
# ==================================================
st.set_page_config(layout="wide")
st.title("Steam Dataset Builder")

tab1, tab2 = st.tabs(["Pojedynczy AppID", "Batch AppID"])

# --------------------------------------------------
#  TAB 1 — pojedyncza gra + etykiety
# --------------------------------------------------
with tab1:
    appid = st.text_input("AppID", placeholder="np. 620")

    if st.button("Pobierz"):
        data = fetch_appdetails(appid)
        if not data:
            st.error("Nie udało się pobrać danych.")
        else:
            st.session_state["data"] = data
            st.session_state["appid"] = appid

    data = st.session_state.get("data")
    if data:
        name = data.get("name", "?")
        desc = get_description(data)

        st.subheader(name)
        st.write(desc)

        st.markdown("### Filarowe etykiety (0/1)")
        c1, c2, c3, c4 = st.columns(4)
        goals = c1.checkbox("Goals")
        rules = c2.checkbox("Rules")
        challenge = c3.checkbox("Challenge")
        interaction = c4.checkbox("Interaction")

        verdict = st.selectbox("Werdykt (opcjonalnie)", ["", "GRA", "FILM"])

        if st.button("Zapisz do CSV"):
            row = {
                "timestamp": datetime.utcnow().isoformat(),
                "appid": st.session_state["appid"],
                "name": name,
                "text": desc,
                "goals": int(goals),
                "rules": int(rules),
                "challenge": int(challenge),
                "interaction": int(interaction),
                "verdict": verdict,
            }
            append_row(row)
            st.success("Zapisano do train_data.csv")

# --------------------------------------------------
#  TAB 2 — batch (surowe opisy)
# --------------------------------------------------
with tab2:
    ids_text = st.text_area(
        "Wklej AppID (po przecinku lub w liniach)",
        height=150
    )
    ids = parse_appids(ids_text)

    if st.button("Pobierz batch"):
        saved = 0
        for appid in ids:
            data = fetch_appdetails(appid)
            if not data:
                continue

            desc = get_description(data)
            if not desc:
                continue

            row = {
                "timestamp": datetime.utcnow().isoformat(),
                "appid": appid,
                "name": data.get("name", "?"),
                "text": desc,
                "goals": "",
                "rules": "",
                "challenge": "",
                "interaction": "",
                "verdict": "",
            }
            append_row(row)
            saved += 1

        st.success(f"Zapisano {saved} rekordów do train_data.csv")
