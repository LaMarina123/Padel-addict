import os
import random
import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Padel Addict", page_icon="🎾", layout="wide")

st.markdown("""
    <style>
    .round-header { background-color: #2C3E50; color: white; padding: 10px; border-radius: 8px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; }
    .court-card { background-color: #E8F4F8; border-left: 5px solid #007FFF; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .bench-card { background-color: #FEF9E7; border-left: 5px solid #F1C40F; padding: 15px; border-radius: 8px; margin-top: 10px; color: #7D6608; }
    </style>
""", unsafe_allow_html=True)

# --- DICTIONNAIRE DE TRADUCTION ---
LANGUAGES = {
    "Français": {
        "subtitle": "Gestionnaire & Générateur de Matchs Intelligents",
        "config_title": "### ⚙️ Paramètres de Session",
        "lang_select": "Choisir la langue :",
        "courts_available": "Nombre de terrains disponibles :",
        "rental_time": "Temps de location total :",
        "match_duration": "Durée d'une partie :",
        "player_management": "### 👥 Gestion de la Liste Padel Addict",
        "add_placeholder": "Nom du joueur...",
        "add_btn": "➕ Ajouter",
        "del_placeholder": "-- Sélectionner un joueur à retirer --",
        "del_btn": "🗑️ Supprimer",
        "select_today": "🎯 Sélectionnez les joueurs présents aujourd'hui ({}) :",
        "select_placeholder": "Choisissez les joueurs...",
        "error_min_players": "❌ Il vous faut au moins {} joueurs sélectionnés pour remplir {} terrains (Actuellement : {}).",
        "warning_fallback": "⚠️ Impossible de trouver des partenaires 100% uniques pour le Tour {}. Réinitialisation locale appliquée.",
        "pdf_title": "Padel Addict - Planning des Matchs",
        "pdf_tour": "TOUR",
        "pdf_court": "Terrain",
        "pdf_bench": "  -> Banc (Prioritaires): ",
        "btn_generate": "🎲 Générer les Matchs",
        "btn_reset": "🔄 Réinitialiser les Tirages",
        "btn_download": "📥 Télécharger le Planning (PDF)",
        "pdf_filename": "Planning_Padel_Addict.pdf",
        "schedule_title": "### 🗓️ Programme des Matchs",
        "court_label": "🎾 Terrain",
        "team1_label": "Équipe 1 :",
        "team2_label": "Équipe 2 :",
        "bench_label": "⏳ <b>Sur le banc pour ce tour :</b> ",
        "logo_info": "💡 Placez 'logo.png' dans Téléchargements."
    },
    "English": {
        "subtitle": "Smart Match Manager & Generator",
        "config_title": "### ⚙️ Session Settings",
        "lang_select": "Choose language:",
        "courts_available": "Number of available courts:",
        "rental_time": "Total rental time:",
        "match_duration": "Match duration:",
        "player_management": "### 👥 Padel Addict Player List Management",
        "add_placeholder": "Player name...",
        "add_btn": "➕ Add",
        "del_placeholder": "-- Select a player to remove --",
        "del_btn": "🗑️ Delete",
        "select_today": "🎯 Select players present today ({}):",
        "select_placeholder": "Choose players...",
        "error_min_players": "❌ You need at least {} selected players to fill {} courts (Currently: {}).",
        "warning_fallback": "⚠️ Unable to find 100% unique partners for Round {}. Local reset applied.",
        "pdf_title": "Padel Addict - Match Schedule",
        "pdf_tour": "ROUND",
        "pdf_court": "Court",
        "pdf_bench": "  -> Bench (Priority): ",
        "btn_generate": "🎲 Generate Matches",
        "btn_reset": "🔄 Reset Draws",
        "btn_download": "📥 Download Schedule (PDF)",
        "pdf_filename": "Padel_Addict_Schedule.pdf",
        "schedule_title": "### 🗓️ Match Schedule",
        "court_label": "🎾 Court",
        "team1_label": "Team 1:",
        "team2_label": "Team 2:",
        "bench_label": "⏳ <b>On the bench for this round:</b> ",
        "logo_info": "💡 Place 'logo.png' in Downloads."
    }
}

# --- SELECTION DE LA LANGUE ---
if "lang" not in st.session_state:
    st.session_state.lang = "Français"

col_logo, col_title = st.columns([1, 4])
with col_logo:
    logo_path = os.path.expanduser("~/Downloads/logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.info(LANGUAGES[st.session_state.lang]["logo_info"])

with col_title:
    st.title("Padel Addict")
    st.subheader(LANGUAGES[st.session_state.lang]["subtitle"])

# --- GESTION DU FICHIER DE SAUVEGARDE ---
DB_FILE = "players_list.txt"

def load_players():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            players = [line.strip() for line in f.readlines() if line.strip()]
            if players:
                return players
    
    default_players = [
        "Gerald", "Marie-Noelle", "Rachide", "Massimo", "Claude",
        "Geoff", "Joanna", "Bernard", "Chris", "Fausta",
        "Elaine", "Carol", "Dave", "Peter", "Nathalie",
        "Jane", "Peter Teylor", "Sam", "TriinP", "Mario",
        "René", "Brian", "Eline", "Bo", "Richard"
    ]
    save_players(default_players)
    return default_players

def save_players(players_list):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for player in sorted(players_list):
            f.write(f"{player}\n")

if "players" not in st.session_state:
    st.session_state.players = load_players()

if "rounds_results" not in st.session_state:
    st.session_state.rounds_results = None

col_config, col_players = st.columns(2)

with col_config:
    t = LANGUAGES[st.session_state.lang]
    st.markdown(t["config_title"])
    
    st.session_state.lang = st.selectbox(t["lang_select"], ["Français", "English"], index=0 if st.session_state.lang == "Français" else 1)
    t = LANGUAGES[st.session_state.lang]
    
    court_count = st.selectbox(t["courts_available"], [2, 3, 4], index=0, key="sb_court_count")
    total_time_str = st.selectbox(t["rental_time"], ["1h30 (90 min)", "2h00 (120 min)"], index=0, key="sb_total_time")
    total_time = 90 if "90" in total_time_str else 120
    match_time = st.selectbox(t["match_duration"], [20, 30], index=0, key="sb_match_time")

with col_players:
    t = LANGUAGES[st.session_state.lang]
    st.markdown(f"{t['player_management']} ({len(st.session_state.players)})")
    
    col_add_input, col_add_btn = st.columns([3, 1])
    with col_add_input:
        new_player = st.text_input(t["add_placeholder"], key="add_player_input", label_visibility="collapsed", placeholder=t["add_placeholder"])
    with col_add_btn:
        if st.button(t["add_btn"], use_container_width=True, key="btn_add_player"):
            cleaned_name = new_player.strip()
            if cleaned_name and cleaned_name not in st.session_state.players:
                st.session_state.players.append(cleaned_name)
                save_players(st.session_state.players)
                st.rerun()

    col_del_select, col_del_btn = st.columns([3, 1])
    with col_del_select:
        player_to_delete = st.selectbox(t["del_placeholder"], [t["del_placeholder"]] + sorted(st.session_state.players), label_visibility="collapsed", key="sb_del_player")
    with col_del_btn:
        if st.button(t["del_btn"], use_container_width=True, type="secondary", key="btn_del_player"):
            if player_to_delete and player_to_delete != t["del_placeholder"]:
                st.session_state.players.remove(player_to_delete)
                save_players(st.session_state.players)
                st.rerun()

    st.markdown("---")
    current_selected = st.session_state.get("ms_players_today", [])
    
    selected_players = st.multiselect(
        t["select_today"].format(len(current_selected)),
        options=sorted(st.session_state.players),
        default=current_selected,  
        placeholder=t["select_placeholder"],
        key="ms_players_today"
    )

def run_rotation():
    t = LANGUAGES[st.session_state.lang]
    players_needed = court_count * 4
    if len(selected_players) < players_needed:
        st.error(t["error_min_players"].format(players_needed, court_count, len(selected_players)))
        return

    total_rounds = total_time // match_time
    rounds = []
    bench_count = {p: 0 for p in selected_players}
    partner_history = {p: set() for p in selected_players}
    last_bench = []

    for r in range(1, total_rounds + 1):
        pool = list(selected_players)
        round_players = []

        if last_bench:
            for p in last_bench:
                if p in pool and len(round_players) < players_needed:
                    round_players.append(p)
                    pool.remove(p)

        pool.sort(key=lambda x: bench_count[x], reverse=True)
        while len(round_players) < players_needed and pool:
            round_players.append(pool.pop(0))

        bench_players = [p for p in selected_players if p not in round_players]
        for p in bench_players:
            bench_count[p] += 1

        success = False
        for _ in range(1000):  
            random.shuffle(round_players)
            temp_courts = []
            valid_distribution = True
            available_players = list(round_players)

            for c in range(1, court_count + 1):
                p1 = available_players.pop(0)
                p2 = next((p for p in available_players if p not in partner_history[p1]), None)
                if not p2:
                    valid_distribution = False
                    break
                available_players.remove(p2)

                p3 = available_players.pop(0)
                p4 = next((p for p in available_players if p not in partner_history[p3]), None)
                if not p4:
                    valid_distribution = False
                    break
                available_players.remove(p4)

                temp_courts.append({
                    "court": c,
                    "t1": [p1, p2],
                    "t2": [p3, p4]
                })

            if valid_distribution:
                for court in temp_courts:
                    t1_p1, t1_p2 = court["t1"]
                    t2_p1, t2_p2 = court["t2"]
                    partner_history[t1_p1].add(t1_p2)
                    partner_history[t1_p2].add(t1_p1)
                    partner_history[t2_p1].add(t2_p2)
                    partner_history[t2_p2].add(t2_p1)
                
                courts_data = temp_courts
                success = True
                break

        if not success:
            st.warning(t["warning_fallback"].format(r))
            random.shuffle(round_players)
            courts_data = []
            for c in range(1, court_count + 1):
                courts_data.append({
                    "court": c,
                    "t1": [round_players.pop(0), round_players.pop(0)],
                    "t2": [round_players.pop(0), round_players.pop(0)]
                })

        rounds.append({
            "round_num": r,
            "duration_str": f"{match_time} min",
            "courts": courts_data,
            "bench": bench_players
        })
        last_bench = list(bench_players)

    st.session_state.rounds_results = rounds

def generate_pdf(rounds):
    t = LANGUAGES[st.session_state.lang]
    pdf_filename = t["pdf_filename"]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, t["pdf_title"], ln=True, align="C")
    pdf.ln(10)

    for r in rounds:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(44, 62, 80)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, f"{t['pdf_tour']} {r['round_num']} ({r['duration_str']})", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 10)
        for c in r['courts']:
            match_txt = f"  {t['pdf_court']} {c['court']}:  {c['t1'][0]} & {c['t1'][1]}   VS   {c['t2'][0]} & {c['t2'][1]}"
            pdf.cell(0, 6, match_txt, ln=True)
        
        if r['bench']:
            pdf.ln(1)
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(125, 102, 8)
            bench_txt = f"{t['pdf_bench']}{', '.join(r['bench'])}"
            pdf.cell(0, 6, bench_txt, ln=True)
            pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    pdf.output(pdf_filename)
    return pdf_filename

st.markdown("---")
t = LANGUAGES[st.session_state.lang]
col_b1, col_b2, col_b3 = st.columns(3)

with col_b1:
    if st.button(t["btn_generate"], use_container_width=True, type="primary", key="btn_generate_matches"):
        run_rotation()

with col_b2:
    if st.button(t["btn_reset"], use_container_width=True, key="btn_reset_draws"):
        st.session_state.rounds_results = None
        st.rerun()

if st.session_state.rounds_results:
    with col_b3:
        pdf_file = generate_pdf(st.session_state.rounds_results)
        with open(pdf_file, "rb") as f:
            st.download_button(
                label=t["btn_download"],
                data=f,
                file_name=t["pdf_filename"],
                mime="application/pdf",
                use_container_width=True
            )

    st.markdown(t["schedule_title"])
    for r in st.session_state.rounds_results:
        st.markdown(f"<div class='round-header'>🔄 {t['pdf_tour']} {r['round_num']} ({r['duration_str']})</div>", unsafe_allow_html=True)
        
        court_cols = st.columns(court_count)
        for i, c in enumerate(r['courts']):
            with court_cols[i]:
                st.markdown(f"""
                <div class='court-card'>
                    <b>{t['court_label']} {c['court']}</b><br><br>
                    👥 <b>{t['team1_label']}</b> {c['t1'][0]} & {c['t1'][1]}<br>
                    <span style='color:red; font-weight:bold;'>VS</span><br>
                    👥 <b>{t['team2_label']}</b> {c['t2'][0]} & {c['t2'][1]}
                </div>
                """, unsafe_allow_html=True)
        
        if r['bench']:
            st.markdown(f"<div class='bench-card'>{t['bench_label']}{', '.join(r['bench'])}</div>", unsafe_allow_html=True)
