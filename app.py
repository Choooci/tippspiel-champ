# bundesliga_tippspiel.py

import streamlit as st
import pandas as pd
import requests
from pathlib import Path
from PIL import Image
import base64
from io import BytesIO

# --- Passwortschutz ---
PASSWORT = "040822"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- Saison-Infos ---
season_dict = {
    1: '2022-23',
    2: '2023-24',
    3: '2024-25',
    4: '2025-26'
}

# --- OpenLigaDB URLs nach Saison ---
season_api_urls = {
    1: "https://www.openligadb.de/api/getbltable/bl1/2022",
    2: "https://www.openligadb.de/api/getbltable/bl1/2023",
    3: "https://www.openligadb.de/api/getbltable/bl1/2024",
    4: "https://www.openligadb.de/api/getbltable/bl1/2025",
}

# --- Tipp-Listen ---
paul1 = ["Schalke", "Bremen", "Hoffenheim", "Mainz"]
tuschi1 = ["Hertha", "Augsburg", "Union", "Gladbach"]
choci1 = ["Bochum", "Stuttgart", "Köln", "Freiburg"]
paul2 = ["Bochum", "Hoffenheim", "Köln", "Frankfurt"]
tuschi2 = ["Darmstadt", "Bremen", "Stuttgart", "Gladbach"]
choci2 = ["Heidenheim", "Augsburg", "Mainz", "Wolfsburg"]
dan3 = ["Heidenheim", "Bremen", "Augsburg", "Dortmund"]
paul3 = ["Kiel", "Mainz", "Wolfsburg", "Frankfurt"]
tuschi3 = ["Union", "Pauli", "Freiburg", "Stuttgart"]
choci3 = ["Bochum", "Hoffenheim", "Gladbach", "Leipzig"]
dan4 = ["Köln", "Bremen", "Augsburg", "Dortmund"]
paul4 = ["Hamburg", "Union", "Leipzig", "Leverkusen"]
tuschi4 = ["Heidenheim", "Gladbach", "Pauli", "Freiburg"]
choci4 = ["Hoffenheim", "Mainz", "Wolfsburg", "Stuttgart"]

tipps_dict = {
    1: {"Paul": paul1, "Tuschi": tuschi1, "Choci": choci1},
    2: {"Paul": paul2, "Tuschi": tuschi2, "Choci": choci2},
    3: {"Dan": dan3, "Paul": paul3, "Tuschi": tuschi3, "Choci": choci3},
    4: {"Dan": dan4, "Paul": paul4, "Tuschi": tuschi4, "Choci": choci4},
}

# --- Top-6 Tipps ---
top6_tipps = {
    1: {
        "Paul": ["Bayern", "Dortmund", "Leipzig", "Leverkusen", "Gladbach", "Wolfsburg"],
        "Tuschi": ["Bayern", "Leipzig", "Dortmund", "Frankfurt", "Leverkusen", "Hoffenheim"],
        "Choci": ["-", "Leverkusen", "Dortmund", "RB Scheiße", "Wolfsburg", "Frankfurt"],
    },
    2: {
        "Paul": ["Leverkusen", "Bayern", "Dosenkacke", "DasTeammitMatsHummels", "Union", "Gladbach"],
        "Tuschi": ["Harry Kane", "Vizekusen", "Dortmund", "Leipzig", "Union", "Frankfurt"],
        "Choci": ["Kevin Volland", "FC Bauern", "Vizekusen", "Doofmund", "Dosenverein", "Frankfurt"],
    },
    3: {
        "Dan": ["nicht getippt wir dullis", "-", "-", "-", "-", "-"],
        "Paul": ["nicht getippt wir dullis", "-", "-", "-", "-", "-"],
        "Tuschi": ["nicht getippt wir dullis", "-", "-", "-", "-", "-"],
        "Choci": ["nicht getippt wir dullis", "-", "-", "-", "-", "-"],
    },
    4: {
        "Dan": ["Bayern", "Frankfurt", "Dortmund", "Stuttgart", "Lverkusen", "Leipzig"],
        "Paul": ["Bayern", "Frankfurt", "Stuhlgang", "Dortmund", "Freiburg", "Leverkusen"],
        "Tuschi": ["Bayern", "Dortmund", "Frankfurt", "Scheißig", "Stuttgart", "Leverkusen", "Augsburg"],
        "Choci": ["Im Herzen von Europa liegt die Eintracht am Main", "FC Bauern", "Freiburg", "Leverbusen", "Dortmund", "Stuttgart"],
    }
}

# --- Teams Informationen ---
teams_info = {
    "Köln": {"name": "1. FC Köln", "logo": "Logos/Koeln.png"},
    "Bremen": {"name": "Werder Bremen", "logo": "Logos/Bremen.png"},
    "Augsburg": {"name": "FC Augsburg", "logo": "Logos/Augsburg.png"},
    "Dortmund": {"name": "Borussia Dortmund", "logo": "Logos/Dortmund.png"},
    "Hamburg": {"name": "Hamburger SV", "logo": "Logos/Hamburg.png"},
    "Union": {"name": "1. FC Union Berlin", "logo": "Logos/Union.png"},
    "Leipzig": {"name": "RB Leipzig", "logo": "Logos/Leipzig.png"},
    "Leverkusen": {"name": "Bayer 04 Leverkusen", "logo": "Logos/Leverkusen.png"},
    "Heidenheim": {"name": "1. FC Heidenheim 1846", "logo": "Logos/Heidenheim.png"},
    "Gladbach": {"name": "Borussia Mönchengladbach", "logo": "Logos/Gladbach.png"},
    "Pauli": {"name": "FC St. Pauli", "logo": "Logos/Pauli.png"},
    "Freiburg": {"name": "SC Freiburg", "logo": "Logos/Freiburg.png"},
    "Hoffenheim": {"name": "TSG Hoffenheim", "logo": "Logos/Hoffenheim.png"},
    "Mainz": {"name": "1. FSV Mainz 05", "logo": "Logos/Mainz.png"},
    "Wolfsburg": {"name": "VfL Wolfsburg", "logo": "Logos/Wolfsburg.png"},
    "Stuttgart": {"name": "VfB Stuttgart", "logo": "Logos/Stuttgart.png"},
    "Frankfurt": {"name": "Eintracht Frankfurt", "logo": "Logos/Frankfurt.png"},
    "Darmstadt": {"name": "SV Darmstadt 98", "logo": "Logos/Darmstadt.png"},
    "Bochum": {"name": "VfL Bochum", "logo": "Logos/Bochum.png"},
    "Kiel": {"name": "Holstein Kiel", "logo": "Logos/Kiel.png"},
    "Hertha": {"name": "Hertha BSC", "logo": "Logos/Hertha.png"},
    "Schalke": {"name": "FC Schalke 04", "logo": "Logos/Schalke.png"},
    "Bayern": {"name": "FC Bauern München", "logo": "Logos/Bayern.png"},
}

# --- Haupt-App ---
def show_app():
    st.set_page_config(page_title="⚽ Bundesliga Tippspiel Champs", layout="centered")
    st.title("⚽ Bundesliga Tippspiel Champs")

    # --- Shortcut-Menü ---
    st.sidebar.markdown("### ⚡ Quick Links")
    st.sidebar.markdown("""
    - [🏆 Rangliste](#rangliste)
    - [📋 Einzelteams](#einzelteams)
    - [💸 Einsatz-Regeln](#einsatzregeln)
    - [⭐ Top-6 Tipps](#top6tipps)
    - [🏆 Bundesliga Top-6](#bundesligatop6)
    - [🏅 Bestenliste](#bestenliste)
    - [📊 Statistik](#statistik)
    """, unsafe_allow_html=True)

    # --- Saisonwahl: Startwert = aktuelle Saison (4) ---
    if "season_index" not in st.session_state:
        st.session_state.season_index = 4

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ vorherige Saison"):
            st.session_state.season_index = max(1, st.session_state.season_index - 1)
    with col3:
        if st.button("➡️ nächste Saison"):
            st.session_state.season_index = min(len(season_dict), st.session_state.season_index + 1)

    season_key = st.session_state.season_index
    season = season_dict[season_key]

    st.write(f"**Aktuelle Saison:** Bundesliga {season}")
    st.write(f"**Saison im Tippspiel:** {season_key}")

    # --- Tabelle laden über API ---
    url = season_api_urls[season_key]
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame([{
            "Team": team["teamName"],
            "Kurzname": team.get("shortName", ""),
            "Punkte": team["points"],
            "Sp.": team["matches"],
            "Siege": team["won"],
            "Unentschieden": team["draw"],
            "Niederlagen": team["lost"],
            "Tordifferenz": team["goalDiff"]
        } for team in data])
    else:
        st.error(f"Die Tabelle konnte nicht geladen werden. Status Code: {response.status_code}")
        return

    # --- Punkteberechnung ---
    def berechne_punkte_und_spiele(liste):
        gesamtpunkte, gesamtspiele = 0, 0
        punkte_teams = []
        for team in liste:
            team_data = df.loc[df['Team'].str.contains(team, case=False), ['Team', 'Punkte', 'Sp.']]
            if not team_data.empty:
                punkte = int(team_data['Punkte'].iloc[0])
                gesamtpunkte += punkte
                gesamtspiele += int(team_data['Sp.'].iloc[0])
                punkte_teams.append((team, punkte))
            else:
                punkte_teams.append((team, 0))
        return gesamtpunkte, gesamtspiele, punkte_teams

    listen = tipps_dict[season_key]
    ergebnisse = {name: berechne_punkte_und_spiele(liste) for name, liste in listen.items()}

    # Hier kannst du wie im ersten Code die restlichen Bereiche (Rangliste, Einzelteams, Top-6, Bestenliste, Statistik, usw.) übernehmen.

    # --- Abstand und Linie ---
    st.markdown("<hr><br>", unsafe_allow_html=True)

    # --- Rangliste ---
    punkte_df = pd.DataFrame(
        [(name, daten[0], daten[1]) for name, daten in ergebnisse.items()],
        columns=['Name', 'Punkte', 'Sp.']
    )
    punkte_df = punkte_df.sort_values('Punkte', ascending=True).reset_index(drop=True)
    punkte_df['Platzierung'] = range(1, len(punkte_df)+1)
    punkte_df = punkte_df[['Platzierung','Name','Punkte','Sp.']].copy()
    punkte_df = punkte_df.rename(columns={'Sp.': 'Spiele'})


    # Hintergrundfarben + Emojis
    def highlight_top4(row):
        platz = row['Platzierung']
        if platz == 1:
            return ['background-color:#fff9e6; font-weight:bold; text-align:center']*len(row)
        elif platz == 2:
            return ['background-color:#f2f2f2; font-weight:bold; text-align:center']*len(row)
        elif platz == 3:
            return ['background-color:#f7e6d9; font-weight:bold; text-align:center']*len(row)
        elif platz == 4:
            return ['background-color:#e6f0ff; font-weight:bold; text-align:center']*len(row)
        else:
            return ['']*len(row)

    def platz_emoji(platz):
        if platz == 1: return f"🥇 {platz}"
        elif platz == 2: return f"🥈 {platz}"
        elif platz == 3: return f"🥉 {platz}"
        elif platz == 4: return f"🪵 {platz}"
        else: return str(platz)


    # --- Rangliste (HTML Tabelle, ohne Kästchen, nur abwechselnde Hintergrundfarben) ---
    st.markdown('<a id="rangliste"></a>', unsafe_allow_html=True)
    st.markdown("""
    <h3 style='border-left:5px solid #ff4d4d; padding-left:10px;'>🏆 Rangliste</h3>
    """, unsafe_allow_html=True)

    def render_rangliste(df):
        html = "<table style='border-collapse:collapse; width:100%;'>"
        # Tabellenkopf
        html += "<tr style='background-color:#ffffff; text-align:center; font-weight:bold;'>"
        html += "<th>Platz</th><th>Name</th><th>Punkte</th><th>Spiele</th></tr>"


        for i, row in df.iterrows():
            bg_color = "#ffffff" if i % 2 == 0 else "#f9f9f9"
            platz = row['Platzierung']
            # Emojis für Top4
            if platz == 1: platz_text = f"🥇 {platz}"
            elif platz == 2: platz_text = f"🥈 {platz}"
            elif platz == 3: platz_text = f"🥉 {platz}"
            elif platz == 4: platz_text = f"🪵 {platz}"
            else: platz_text = str(platz)
            
            html += f"<tr style='background-color:{bg_color}; text-align:center;'>"
            html += f"<td>{platz_text}</td><td style='text-align:left; padding-left:10px;'>{row['Name']}</td>"
            html += f"<td>{row['Punkte']}</td><td>{row['Spiele']}</td>"
            html += "</tr>"
        
        html += "</table>"
        return html

    st.markdown(render_rangliste(punkte_df), unsafe_allow_html=True)



    # --- Abstand und Linie ---
    st.markdown("<hr><br>", unsafe_allow_html=True)

    # --- Einzelteams ---
    st.markdown('<a id="einzelteams"></a>', unsafe_allow_html=True)
    farben = {'Paul':'#e6f7ff','Tuschi':'#fff0e6','Choci':'#f9f0ff','Dan':'#e6ffe6'}
    st.markdown("""
    <div style="
        background-color:#f5f5f5;
        padding:15px;
        border-radius:10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom:15px;
    ">
        <h3>📋 Punkte der Einzelteams</h3>
    </div>
    """, unsafe_allow_html=True)
    zeilen_hoehe = 40
    logo_hoehe = 25
    logo_breite_max = 70

    for name, daten in ergebnisse.items():
        st.markdown(f"**{name}**")
        st.markdown(f'<div style="background-color:{farben.get(name,"white")}; padding:5px; border-radius:5px;">', unsafe_allow_html=True)
        for team, punkte in daten[2]:
            info = teams_info.get(team, {"name": team, "logo": ""})
            team_name = info["name"]
            logo_path = info["logo"]
            if logo_path and Path(logo_path).exists():
                img = Image.open(logo_path)
                w,h = img.size
                neu_w = int((logo_hoehe/h)*w)
                img = img.resize((neu_w, logo_hoehe))
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode()
                logo_html = f"<img src='data:image/png;base64,{img_b64}' height='{logo_hoehe}px' style='display:block; margin:auto;'>"
            else:
                logo_html = ""
            st.markdown(
                f"""
                <div style='display:flex; align-items:center; height:{zeilen_hoehe}px; padding:2px 0'>
                    <div style='width:{logo_breite_max}px; display:flex; justify-content:center;'>{logo_html}</div>
                    <div style='flex:4; padding-left:10px'>{team_name}</div>
                    <div style='flex:1; text-align:right'>{punkte} Punkte</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Abstand und Linie ---
    st.markdown("<hr><br>", unsafe_allow_html=True)

    # --- Einsatz-Text ---
    st.markdown('<a id="einsatzregeln"></a>', unsafe_allow_html=True)
    st.markdown("""
    ### 💸 Einsatz-Regeln
    - **4. Platz** → 3 Runden zahlen  
    - **3. Platz** → 2 Runden zahlen  
    - **2. Platz** → 1 Runde zahlen  

    ⚠️ Bei **Punktgleichheit** zahlen die den Abend!  
    🎰 Bei **3 oder 4 Punktgleichen** geht's ins **Casino**!
    """)





        


    # --- Top-6 Darstellung wie „Punkte der Einzelteams“ ---
    st.markdown('<a id="top6tipps"></a>', unsafe_allow_html=True)
    st.markdown("<hr><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="
        background-color:#f5f5f5;
        padding:15px;
        border-radius:10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom:15px;
    ">
        <h3>⭐ Top-6 Tipps der Bundesliga</h3>
    </div>
    """, unsafe_allow_html=True)

    # Personen aus der aktuellen Saison
    personen = list(tipps_dict[season_key].keys())

    for name in personen:
        st.markdown(f"**{name}**")
        st.markdown(f'<div style="background-color:{farben.get(name,"white")}; padding:5px; border-radius:5px;">', unsafe_allow_html=True)
        
        # Nur die Top-6 Tipps dieser Saison
        teams = top6_tipps.get(season_key, {}).get(name, [])
        
        for team in teams:
            info = teams_info.get(team, {"name": team, "logo": ""})
            team_name = info["name"]
            logo_path = info["logo"]

            if logo_path and Path(logo_path).exists():
                img = Image.open(logo_path)
                w,h = img.size
                neu_w = int((logo_hoehe/h)*w)
                img = img.resize((neu_w, logo_hoehe))
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode()
                logo_html = f"<img src='data:image/png;base64,{img_b64}' height='{logo_hoehe}px' style='display:block; margin:auto;'>"
            else:
                logo_html = ""

            st.markdown(
                f"""
                <div style='display:flex; align-items:center; height:{zeilen_hoehe}px; padding:2px 0'>
                    <div style='width:{logo_breite_max}px; display:flex; justify-content:center;'>{logo_html}</div>
                    <div style='flex:4; padding-left:10px'>{team_name}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)




    # --- Bundesliga Top-6 Tabelle schöner anzeigen wie Einzelteams ---
    st.markdown('<a id="bundesligatop6"></a>', unsafe_allow_html=True)
    st.markdown("<hr><br>", unsafe_allow_html=True)
    st.subheader(f"🏆 Bundesliga Top-6 Saison - {season}")

    zeilen_hoehe = 40
    logo_hoehe = 25
    logo_breite_max = 70

    try:
        url = season_api_urls[season_key]
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame([{
                "Team": team["teamName"],
                "Kurzname": team.get("shortName", ""),
                "Punkte": team["points"],
                "Sp.": team["matches"],
                "Siege": team["won"],
                "Unentschieden": team["draw"],
                "Niederlagen": team["lost"],
                "Tordifferenz": team["goalDiff"]
            } for team in data])

            # Nur die Top-6 Teams auswählen
            top6_df = df.head(6).copy()

            # Spalten anpassen: nur Team und Punkte
            if 'Team' in top6_df.columns and 'Punkte' in top6_df.columns:
                top6_df = top6_df[['Team','Punkte']]
            elif 'Mannschaft' in top6_df.columns and 'Punkte' in top6_df.columns:
                top6_df = top6_df[['Mannschaft','Punkte']]
                top6_df.rename(columns={'Mannschaft':'Team'}, inplace=True)

            for i, row in top6_df.iterrows():
                team_key = row['Team'].split()[0]  # erster Teil des Namens als Schlüssel
                info = teams_info.get(team_key, {"name": row['Team'], "logo": ""})
                team_name = info["name"]
                logo_path = info["logo"]

                if logo_path and Path(logo_path).exists():
                    img = Image.open(logo_path)
                    w,h = img.size
                    neu_w = int((logo_hoehe/h)*w)
                    img = img.resize((neu_w, logo_hoehe))
                    buffered = BytesIO()
                    img.save(buffered, format="PNG")
                    img_b64 = base64.b64encode(buffered.getvalue()).decode()
                    logo_html = f"<img src='data:image/png;base64,{img_b64}' height='{logo_hoehe}px' style='display:block; margin:auto;'>"
                else:
                    logo_html = ""

                st.markdown(
                    f"""
                    <div style='display:flex; align-items:center; height:{zeilen_hoehe}px; padding:2px 0; border-bottom:1px solid #f0f0f0;'>
                        <div style='width:{logo_breite_max}px; display:flex; justify-content:center;'>{logo_html}</div>
                        <div style='flex:4; padding-left:10px'>{team_name}</div>
                        <div style='flex:1; text-align:right'>{row['Punkte']} Punkte</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    except Exception as e:
        st.error(f"Die Top-6 Tabelle konnte nicht geladen werden: {e}")





    # --- Abstand und Linie ---
    st.markdown("<hr><br>", unsafe_allow_html=True)

    # --- Bestenliste ---
    st.markdown("""
    <div style="
        border: 2px solid #ccc;
        padding:15px;
        border-radius:10px;
        margin-bottom:15px;
    ">
        <h3>🏅 Bestenliste</h3>
    </div>
    """, unsafe_allow_html=True)


    def erstelle_bestenliste(saison_keys, titel, platz4_holz=False):
    gesamtpunkte = {}
        for key in saison_keys:
            listen = tipps_dict[key]
            url = season_api_urls[key]
            response = requests.get(url)
            if response.status_code != 200:
                st.error(f"Bestenliste: Tabelle für Saison {season_dict[key]} konnte nicht geladen werden.")
                continue
            data = response.json()
            df_saison = pd.DataFrame([{"Team": team["teamName"], "Punkte": team["points"]} for team in data])
            for name, teams in listen.items():
                if name not in gesamtpunkte:
                    gesamtpunkte[name] = 0
                for team in teams:
                    team_data = df_saison.loc[df_saison['Team'].str.contains(team, case=False), 'Punkte']
                    if not team_data.empty:
                        gesamtpunkte[name] += int(team_data.iloc[0])

    # Ergebnisse sortieren
    bestenliste_df = pd.DataFrame(gesamtpunkte.items(), columns=["Name", "Gesamtpunkte"])
    bestenliste_df = bestenliste_df.sort_values(by="Gesamtpunkte", ascending=False).reset_index(drop=True)

    # Emojis Top4
    best_df_display = bestenliste_df.copy()
    best_df_display['Platzierung'] = range(1, len(best_df_display)+1)
    def emoji_top4(p):
        if p==1: return f"🥇 {p}"
        elif p==2: return f"🥈 {p}"
        elif p==3: return f"🥉 {p}"
        elif p==4 and platz4_holz: return f"🪵 {p}"
        else: return str(p)
        best_df_display['Platzierung'] = best_df_display['Platzierung'].apply(emoji_top4)

    def highlight_top4_bl(row):
        platz = int(''.join(filter(str.isdigit,str(row['Platzierung']))))
        if platz==1: return ['background-color:#fff9e6; font-weight:bold; text-align:center']*len(row)
        elif platz==2: return ['background-color:#f2f2f2; font-weight:bold; text-align:center']*len(row)
        elif platz==3: return ['background-color:#f7e6d9; font-weight:bold; text-align:center']*len(row)
        elif platz==4 and platz4_holz: return ['background-color:#e6f0ff; font-weight:bold; text-align:center']*len(row)
        else: return ['']*len(row)

    st.subheader(titel)
    st.dataframe(best_df_display.style.apply(highlight_top4_bl, axis=1), use_container_width=True, hide_index=True)


    # Bestenliste 3 Personen: Saison 2022-23 & 2023-24
    erstelle_bestenliste([1,2], "Beste 3 Personen (Saison 2022-23 & 2023-24")

    # Bestenliste 4 Personen: Saison 2024-25 und später
    spaetere_saisons = [k for k in season_dict if k >=3]
    erstelle_bestenliste(spaetere_saisons, "Beste 4 Personen (Saison ab 2024-25)", platz4_holz=True)


    # --- Abstand und Linie ---
    st.markdown("<hr><br>", unsafe_allow_html=True)

    # --- Statistik: Wie oft welcher Verein gewählt ---
    st.markdown('<a id="statistik"></a>', unsafe_allow_html=True)
    st.markdown("""
    <div style="
        border: 2px solid #ccc;
        padding:15px;
        border-radius:10px;
        margin-bottom:15px;
    ">
        <h3>📊 Statistik: Anzahl Tipps pro Verein</h3>
    </div>
    """, unsafe_allow_html=True)

    # Alle Personen, über alle Saisons
    alle_personen = set()
    for key in tipps_dict:
        alle_personen.update(tipps_dict[key].keys())

    # Statistik erstellen
    statistik_dict = {name:{} for name in alle_personen}

    for key in tipps_dict:
        listen = tipps_dict[key]
        for name, teams in listen.items():
            for team in teams:
                statistik_dict[name][team] = statistik_dict[name].get(team, 0) + 1

    # Farben wie bei Einzelteams
    farben = {'Paul':'#e6f7ff','Tuschi':'#fff0e6','Choci':'#f9f0ff','Dan':'#e6ffe6'}

    # Layout wie bei Einzelteams
    zeilen_hoehe = 35
    logo_hoehe = 25
    logo_breite_max = 70

    for name, teams_count in statistik_dict.items():
        st.markdown(f"**{name}**")
        st.markdown(f'<div style="background-color:{farben.get(name,"white")}; padding:5px; border-radius:5px;">', unsafe_allow_html=True)
        
        # Sortiere nach Häufigkeit absteigend
        sorted_teams = sorted(teams_count.items(), key=lambda x: x[1], reverse=True)
        
        for team, anzahl in sorted_teams:
            info = teams_info.get(team, {"name": team, "logo": ""})
            team_name = info["name"]
            logo_path = info["logo"]

            # Logo als Base64 einbetten
            if logo_path and Path(logo_path).exists():
                img = Image.open(logo_path)
                w,h = img.size
                neu_w = int((logo_hoehe/h)*w)
                img = img.resize((neu_w, logo_hoehe))
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode()
                logo_html = f"<img src='data:image/png;base64,{img_b64}' height='{logo_hoehe}px' style='display:block; margin:auto;'>"
            else:
                logo_html = ""

            st.markdown(
                f"""
                <div style='display:flex; align-items:center; height:{zeilen_hoehe}px; padding:2px 0'>
                    <div style='width:{logo_breite_max}px; display:flex; justify-content:center;'>{logo_html}</div>
                    <div style='flex:4; padding-left:10px'>{team_name}</div>
                    <div style='flex:1; text-align:right'>{anzahl}x</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)



    # --- Credits ---
    st.markdown("""
    <hr>
    <p style='text-align:center; font-size:12px; color:gray;'>
    ⚠️ Dieses Tippspiel wurde mit 💙 selbst erstellt und ist einmalig.  
    Bitte KickTipp, Check24 & Co.: Keine Kopien! 😎  
    Made by uns – für uns! ⚽🎉
    </p>
    """, unsafe_allow_html=True)






# --- Passwortabfrage ---
if not st.session_state.authenticated:
    eingabe = st.text_input("🔑 Passwort eingeben:", type="password")
    if st.button("Login"):
        if eingabe == PASSWORT:
            st.session_state.authenticated = True
            st.success("✅ Zugriff gewährt!")
            st.info("✅ Passwort korrekt – hier wird jetzt der komplette Tippspiel-Inhalt angezeigt.")
            show_app()
        else:
            st.error("❌ Falsches Passwort")
else:
    show_app()

