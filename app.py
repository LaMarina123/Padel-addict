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
LANG_DICT = {
    "FR": {
        "subtitle": "Gestionnaire & Générateur de Matchs Intelligents",
        "logo_tip": "💡 Placez 'logo.png' dans Téléchargements.",
        "config_title": "⚙️ Paramètres de Session",
        "courts_label": "Nombre de terrains disponibles :",
        "total_time_label": "Temps de location total :",
        "match_time_label": "Durée d'une partie :",
        "t_90": "1h30 (90 min)",
        "t_120": "2h00 (120 min)",
        "mgmt_title": "👥 Gestion de la Liste Padel Addict",
        "add_placeholder": "Nom du joueur...",
        "add_btn": "➕ Ajouter",
        "del_placeholder": "-- Sélectionner un joueur à retirer --",
        "del_btn": "🗑️ Supprimer",
        "select_players_label": "🎯 Sélectionnez les joueurs présents aujourd'hui",
        "select_placeholder": "Choisissez les joueurs...",
        "error_min_players": "❌ Il vous faut au moins {} joueurs sélectionnés pour remplir {} terrains (Actuellement : {}).",
        "btn_generate": "🎲 Générer les Matchs",
        "btn_reset": "🔄 Réinitialiser les Tirages",
        "btn_download": "📥 Télécharger le Planning",
        "pdf_title": "Padel Addict - Planning des Matchs",
        "pdf_tour": "TOUR",
        "pdf_court": "Terrain",
        "pdf_bench": "-> Banc (Prioritaires):"
    },
    "EN": {
        "subtitle": "Smart Match Manager & Generator",
        "logo_tip": "💡 Place 'logo.png' in Downloads.",
        "config_title": "⚙️ Session Settings",
        "courts_label": "Available courts:",
        "total_time_label": "Total booking time:",
        "match_time_label": "Match duration:",
        "t_90": "1h30 (90 mins)",
        "t_120": "2h00 (120 mins)",
        "mgmt_title": "👥 Padel Addict Roster Management",
        "add_placeholder": "Player name...",
        "add_btn": "➕ Add Player",
        "del_placeholder": "-- Select a player to remove --",
        "del_btn": "🗑️ Delete",
        "select_players_label": "🎯 Select today's present players",
        "select_placeholder": "Choose players...",
        "error_min_players": "❌ You need at least {} selected players to fill {} courts (Currently: {}).",
        "btn_generate": "🎲 Generate Matches",
        "btn_reset": "🔄 Reset Draws",
        "btn_download": "📥 Download Schedule",
        "pdf_title": "Padel Addict - Match Schedule",
        "pdf_tour": "ROUND",
        "pdf_court": "Court",
        "pdf_bench": "-> Bench (Priority):"
    }
}

col_logo, col_title = st.columns([1, 4])
with col_logo:
    logo_path = os.path.expanduser("~/Downloads/logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.info(LANG_DICT["FR"]["logo_tip"] if "lang" not in st.session_state else LANG_DICT[st.session_state.lang]["logo_tip"])

# --- GESTION DU FICHIER DE SAUVEGARDE ---
DB_FILE = "players_list.txt"

def load_players():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            players = [line.strip() for line in f.readlines() if line.strip()]
            if players:
                return players
    
    default_players = [
        "Thomas", "Lucas", "Nicolas", "Alexandre", "Julien", 
        "Guillaume", "Maxime", "Romain", "Antoine", "Florian", 
        "Cédric", "Jérôme", "Vincent", "Mathieu", "Pierre", "Benoît"
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

# --- SÉLECTEUR DE LANGUE ---
if "lang" not in st.session_state:
    st.session_state.lang = "FR"

with col_title:
    col_t, col_l = st.columns([4, 1])
    with col_t:
        st.title("Padel Addict")
    with col_l:
        st.session_state.lang = st.selectbox("🌐 Language", ["FR", "EN"], index=0 if st.session_state.lang == "FR" else 1)
    
    st.subheader(LANG_DICT[st.session_state.lang]["subtitle"])

# Raccourci vers les traductions actives
T = LANG_DICT[st.session_state.lang]

col_config, col_players = st.columns(2)

with col_config:
    st.markdown(f"### {T['config_title']}")
    court_count = st.selectbox(T["courts_label"], [2, 3, 4], index=1, key="sb_court_count")
    total_time_str = st.selectbox(T["total_time_label"], [T["t_90"], T["t_120"]], index=1, key="sb_total_time")
    total_time = 90 if "90" in total_time_str else 120
    match_time = st.selectbox(T["match_time_label"], [20, 30], index=1, key="sb_match_time")

with col_players:
    st.markdown(f"### {T['mgmt_title']} ({len(st.session_state.players)})")
    
    # Ajouter un joueur
    col_add_input, col_add_btn = st.columns([3, 1])
    with col_add_input:
        new_player = st.text_input("Nom", key="add_player_input", label_visibility="collapsed", placeholder=T["add_placeholder"])
    with col_add_btn:
        if st.button(T["add_btn"], use_container_width=True, key="btn_add_player"):
            cleaned_name = new_player.strip()
            if cleaned_name and cleaned_name not in st.session_state.players:
                st.session_state.players.append(cleaned_name)
                save_players(st.session_state.players)
                st.rerun()

    # Supprimer un joueur de la liste globale
    col_del_select, col_del_btn = st.columns([3, 1])
    with col_del_select:
        player_to_delete = st.selectbox("Supprimer", [T["del_placeholder"]] + sorted(st.session_state.players), label_visibility="collapsed", key="sb_del_player")
    with col_del_btn:
        if st.button(T["del_btn"], use_container_width=True, type="secondary", key="btn_del_player"):
            if player_to_delete and player_to_delete != T["del_placeholder"]:
                st.session_state.players.remove(player_to_delete)
                save_players(st.session_state.players)
                st.rerun()

    st.markdown("---")
    
    # Récupération dynamique du nombre de joueurs présents
    current_selected = st.session_state.get("ms_players_today", [])
    
    # Menu Déroulant avec compteur dynamique multilingue
    selected_players = st.multiselect(
        f"{T['select_players_label']} ({len(current_selected)}) :",
        options=sorted(st.session_state.players),
        default=[],  
        placeholder=T["select_placeholder"],
        key="ms_players_today"
    )

def run_rotation():
    players_needed = court_count * 4
    if len(selected_players) < players_needed:
        st.error(T["error_min_players"].format(players_needed, court_count, len(selected_players)))
        return

    total_rounds = total_time // match_time
    rounds = []
    bench_count = {p: 0 for p in selected_players}
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

        random.shuffle(round_players)
        courts_data = []
        for c in range(1, court_count + 1):
            t1_p1 = round_players.pop(0)
            t1_p2 = round_players.pop(0)
            t2_p1 = round_players.pop(0)
            t2_p2 = round_players.pop(0)

            courts_data.append({
                "court": c,
                "t1": [t1_p1, t1_p2],
                "t2": [t2_p1, t2_p2]
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
    pdf_filename = "Padel_Addict_Planning.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, T["pdf_title"], ln=True, align="C")
    pdf.ln(10)

    for r in rounds:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(44, 62, 80)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, f"{T['pdf_tour']} {r['round_num']} ({r['duration_str']})", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 10)
        for c in r['courts']:
            match_txt = f"  {T['pdf_court']} {c['court']}:  {c['t1'][0]} & {c['t1'][1]}   VS   {c['t2'][0]} & {c['t2'][1]}"
            pdf.cell(0, 6, match_txt, ln=True)
        
        if r['bench']:
            pdf.ln(1)
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(125, 102, 8)
            bench_txt = f"  {T['pdf_bench']} {', '.join(r['bench'])}"
            pdf.cell(0, 6, bench_txt, ln=True)pdf.set_text_color(0, 0, 0)
pdf.ln(5)
pdf.output(pdf_filename)
return pdf_filename
st.markdown("---")
col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
if st.button(T["btn_generate"], use_container_width=True, type="primary", key="btn_generate_matches"):
run_rotation()
with col_b2:
if st.button(T["btn_reset"], use_container_width=True, key="btn_reset_draws"):
st.session_state.rounds_results = None
st.rerun()
if st.session_state.rounds_results:
pdf_path = generate_pdf(st.session_state.rounds_results)
with col_b3:
with open(pdf_path, "rb") as f:
st.download_button(
label=T["btn_download"],
data=f,
file_name="Padel_Addict_Planning.pdf",
mime="application/pdf",
use_container_width=True
)
