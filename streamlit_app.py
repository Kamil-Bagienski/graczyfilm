import streamlit as st
import requests
import re
import csv
from pathlib import Path
from datetime import datetime
import html
import time

# ==================================================
#  TUTAJ WKLEJ SWÓJ KLUCZ API (JEŚLI BĘDZIE POTRZEBA)
# ==================================================
STEAM_API_KEY = "CB0A1F56A2C833792BC26AAFDF9889C7"   # <-- TU WKLEJ KLUCZ (opcjonalne)

OUT_CSV = "train_data.csv"
LABELS = ["goals", "rules", "challenge", "interaction"]

# ==================================================
#  TEKST: czyszczenie HTML + encje typu &quot;
# ==================================================
def clean_html_text(text: str) -> str:
    text = text or ""
    text = html.unescape(text)                  # &quot; -> "
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)        # usuń tagi
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ==================================================
#  STEAM: pobieranie appdetails (odporne na błędy)
# ==================================================
def fetch_appdetails(appid: str) -> dict | None:
    appid = (appid or "").strip()
    if not appid.isdigit():
        return None

    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=english"

    try:
        r = requests.get(
            url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        r.raise_for_status()
        d = r.json()
    except Exception:
        return None

    if not isinstance(d, dict):
        return None

    entry = d.get(appid)
    if not entry or not entry.get("success"):
        return None

    data = entry.get("data")
    if not isinstance(data, dict):
        return None

    return data

def get_description(data: dict) -> str:
    return clean_html_text(
        data.get("detailed_description")
        or data.get("about_the_game")
        or ""
    )

# ==================================================
#  CSV: zapis przyjazny dla Excela (UTF-8 z BOM + ; + quoting)
# ==================================================
CSV_DELIM = ";"  # Excel PL zwykle oczekuje średnika

CSV_FIELDS = [
    "timestamp", "appid", "name", "text",
    "goals", "rules", "challenge", "interaction",
    "verdict"
]

def append_row(row: dict):
    file_exists = Path(OUT_CSV).exists()

    # utf-8-sig => BOM, żeby Excel nie robił krzaków
    with open(OUT_CSV, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=CSV_FIELDS,
            delimiter=CSV_DELIM,
            quoting=csv.QUOTE_ALL,      # wszystko w cudzysłowie
            quotechar='"',
            escapechar="\\",
            doublequote=True,
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def parse_appids(text: str):
    text = (text or "").strip()
    if not text:
        return []
    return [x for x in re.split(r"[,\s]+", text) if x.isdigit()]

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

    if st.button("Pobierz", key="fetch_one"):
        data = fetch_appdetails(appid)
        if not data:
            st.error("Nie udało się pobrać danych (zły AppID, brak danych lub błąd sieci).")
            st.session_state.pop("data", None)
            st.session_state.pop("appid", None)
        else:
            st.session_state["data"] = data
            st.session_state["appid"] = appid.strip()

    data = st.session_state.get("data")
    if data:
        name = data.get("name", "?")
        desc = get_description(data)

        st.subheader(name)
        st.write(desc if desc else "[brak opisu]")

        st.markdown("### Filarowe etykiety (0/1)")
        c1, c2, c3, c4 = st.columns(4)
        goals = c1.checkbox("Goals", key="goals_one")
        rules = c2.checkbox("Rules", key="rules_one")
        challenge = c3.checkbox("Challenge", key="challenge_one")
        interaction = c4.checkbox("Interaction", key="interaction_one")

        verdict = st.selectbox("Werdykt (opcjonalnie)", ["", "GRA", "FILM"], key="verdict_one")

        if st.button("Zapisz do CSV", key="save_one", disabled=not bool(desc)):
            row = {
                "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
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

    delay = st.slider("Opóźnienie między zapytaniami (sek)", 0.0, 1.0, 0.25, 0.05)

    if st.button("Pobierz batch", key="fetch_batch", disabled=len(ids) == 0):
        saved = 0
        skipped = 0

        with st.status("Pobieranie...", expanded=True) as status:
            for appid in ids:
                data = fetch_appdetails(appid)
                if not data:
                    skipped += 1
                    continue

                desc = get_description(data)
                if not desc:
                    skipped += 1
                    continue

                row = {
                    "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
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

                if delay > 0:
                    time.sleep(delay)

            status.update(label="Zakończono", state="complete", expanded=False)

        st.success(f"Zapisano {saved} rekordów, pominięto {skipped}. Plik: {OUT_CSV}")

# ==================================================
#  (Opcjonalnie) szybkie pobranie CSV w Streamlit Cloud / online
# ==================================================
if Path(OUT_CSV).exists():
    with open(OUT_CSV, "rb") as f:
        st.download_button(
            "Pobierz train_data.csv",
            data=f,
            file_name="train_data.csv",
            mime="text/csv",
        )
