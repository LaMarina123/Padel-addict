import os
import random
import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Padel Addict - Match Organizer", page_icon="🎾", layout="wide")

LANG_DICT = {
    "FR": {
        "title": "Padel Addict",
        "subtitle": "Gestionnaire & Générateur de Matchs Intelligents",
        "logo_tip": "💡 Placez 'logo.png' dans Téléchargements.",
        "config_title": "### ⚙️ Paramètres de Session",
        "court_lbl": "Nombre de terrains disponibles :",
        "time_lbl": "Temps de location total :",
        "match_lbl": "Durée d'une partie :",
        "player_title": "### 👥 Gestion de la Liste Padel Addict",
        "placeholder_add": "Nom du joueur...",
        "btn_add": "➕ Ajouter",
        "select_del": "-- Sélectionner un joueur à retirer --",
        "btn_del": "🗑️ Supprimer",
        "multiselect_lbl": "🎯 Sélectionnez les joueurs présents aujourd'hui :",
        "placeholder_select": "Choisissez les joueurs...",
        "selected_count": "Joueurs sélectionnés pour aujourd'hui :",
        "error_min_players": "❌ Il vous faut au moins {} joueurs sélectionnés pour remplir {} terrains (Actuellement : {}).",
        "btn_generate": "🎲 Générer les Matchs",
        "btn_reset": "🔄 Réinitialiser les Tirages",
        "btn_pdf": "📄 Télécharger le Planning PDF",
        "results_title": "## 📊 Résultats des Matchs par Tour",
        "tour": "TOUR",
        "duration": "Durée :",
        "court": "Terrain",
        "bench": "🪑 <b>Banc de touche (Prioritaires au prochain tour) :</b>",
        "pdf_title": "Padel Addict - Planning des Matchs",
        "pdf_bench": "  -> Banc (Prioritaires): "
    },
    "EN": {
        "title": "Padel Addict",
        "subtitle": "Smart Match Organizer & Generator",
        "logo_tip": "💡 Place 'logo.png' in Downloads.",
        "config_title": "### ⚙️ Session Settings",
        "court_lbl": "Number of available courts:",
        "time_lbl": "Total booking time:",
        "match_lbl": "Match duration:",
        "player_title": "### 👥 Padel Addict Roster Management",
        "placeholder_add": "Player name...",
        "btn_add": "➕ Add",
        "select_del": "-- Select a player to remove --",
        "btn_del": "🗑️ Delete",
        "multiselect_lbl": "🎯 Select today's available players:",
        "placeholder_select": "Choose players...",
        "selected_count": "Players selected for today:",
        "error_min_players": "❌ You need at least {} selected players to fill {} courts (Currently: {}).",
        "btn_generate": "🎲 Generate Matches",
        "btn_reset": "🔄 Reset Draws",
        "btn_pdf": "📄 Download PDF Schedule",
        "results_title": "## 📊 Match Results per Round",
        "tour": "ROUND",
        "duration": "Duration:",
        "court": "Court",
        "bench": "🪑 <b>Bench (Priority for next round):</b>",
        "pdf_title": "Padel Addict - Match Schedule",
        "pdf_bench": "  -> Bench (Priority): "
    }
}

st.markdown("""
    <style>
    .round-header { background-color: #2C3E50; color: white; padding: 10px; border-radius: 8px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; }
    .court-card { background-color: #E8F4F8; border-left: 5px solid #007FFF; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .bench-card { background-color: #FEF9E7; border-left: 5px solid #F1C40F; padding: 15px; border-radius: 8px; margin-top: 10px; color: #7D6608; }
    </style>
""", unsafe_allow_html=True)

if "lang" not in st.session_state:
    st.session_state.lang = "FR"

col_logo, col_title, col_lang = st.columns([1.5, 4, 1.5])

with col_lang:
    st.markdown("<div style='text-align: right; padding-top: 10px;'><b>🌐 Language</b></div>", unsafe_allow_html=True)
    lang_choice = st.selectbox("Lang", ["🇫🇷 Français", "🇬🇧 English"], label_visibility="collapsed", index=0 if st.session_state.lang == "FR" else 1)
    new_lang = "FR" if "Français" in lang_choice else "EN"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

T = LANG_DICT[st.session_state.lang]

with col_logo:
    logo_path = os.path.expanduser("~/Downloads/logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.info(T["logo_tip"])

with col_title:
    st.title(T["title"])
    st.subheader(T["subtitle"])

if "players" not in st.session_state:
    st.session_state.players = [
        "Thomas", "Lucas", "Nicolas", "Alexandre", "Julien", 
        "Guillaume", "Maxime", "Romain", "Antoine", "Florian", 
        "Cédric", "Jérôme", "Vincent", "Mathieu", "Pierre", "Benoît"
    ]
if "rounds_results" not in st.session_state:
    st.session_state.rounds_results = None

col_config, col_players = st.columns(2)

with col_config:
    st.markdown(T["config_title"])
    court_count = st.selectbox(T["court_lbl"], [2, 3, 4], index=1)
    total_time_str = st.selectbox(T["time_lbl"], ["1h30 (90 min)", "2h00 (120 min)"], index=1)
    total_time = 90 if "90" in total_time_str else 120
    match_time = st.selectbox(T["match_lbl"], [20, 30], index=1)

with col_players:
    st.markdown(f"{T['player_title']} ({len(st.session_state.players)})")
    
    col_add_input, col_add_btn = st.columns([3, 1])
    with col_add_input:
        new_player = st.text_input("Add Player", key="add_player_input", label_visibility="collapsed", placeholder=T["placeholder_add"])
    with col_add_btn:
        if st.button(T["btn_add"], use_container_width=True):
            if new_player.strip() and new_player.strip() not in st.session_state.players:
                st.session_state.players.append(new_player.strip())
                st.rerun()

    col_del_select, col_del_btn = st.columns([3, 1])
    with col_del_select:
        player_to_delete = st.selectbox("Delete Player", [T["select_del"]] + sorted(st.session_state.players), label_visibility="collapsed")
    with col_del_btn:
        if st.button(T["btn_del"], use_container_width=True, type="secondary"):
            if player_to_delete and player_to_delete != T["select_del"]:
                st.session_state.players.remove(player_to_delete)
                st.rerun()

    st.markdown("---")
    
    selected_players = st.multiselect(
        T["multiselect_lbl"],
        options=sorted(st.session_state.players),
        default=[],
        placeholder=T["placeholder_select"]
    )
    
    st.markdown(f"**{T['selected_count']} `{len(selected_players)}`**")

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
        pdf.cell(0, 8, f"{T['tour']} {r['round_num']} ({r['duration_str']})", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 10)
        for c in r['courts']:
            match_txt = f"  {T['court']} {c['court']}:  {', '.join(c['t1'])}   VS   {', '.join(c['t2'])}"
            pdf.cell(0, 6, match_txt, ln=True)
        
        if r['bench']:
            pdf.ln(1)
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(125, 102, 8)
            bench_txt = f"{T['pdf_bench']}{', '.join(r['bench'])}"
            pdf.cell(0, 6, bench_txt, ln=True)
            pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    pdf.output(pdf_filename)
    return pdf_filename

st.markdown("---")
col_b1, col_b2, col_b3 = st.columns(3)

with col_b1:
    if st.button(T["btn_generate"], use_container_width=True, type="primary"):
        run_rotation()

with col_b2:
    if st.button(T["btn_reset"], use_container_width=True):
        st.session_state.rounds_results = None
        st.rerun()

if st.session_state.rounds_results:
    pdf_path = generate_pdf(st.session_state.rounds_results)
    with col_b3:
        with open(pdf_path, "rb") as f:
            st.download_button(
                label=T["btn_pdf"],
                data=f,
                file_name="Padel_Addict_Planning.pdf",
                mime="application/pdf",use_container_width=True
)
st.markdown(T["results_title"])
for r in st.session_state.rounds_results:
st.markdown(f'🔄 {T["tour"]} {r["round_num"]}   |   ⏰ {T["duration"]} {r["duration_str"]}', unsafe_allow_html=True)
court_cols = st.columns(court_count)
for idx, c in enumerate(r['courts']):
with court_cols[idx]:
st.markdown(f"""

🔲 {T['court']} {c['court']}
🔵 {', '.join(c['t1'])}
VS
🟠 {', '.join(c['t2'])}

""", unsafe_allow_html=True)
if r['bench']:
bench_list = ", ".join([f"{p}" for p in r['bench']])
st.markdown(f"""

{T['bench']} {bench_list}

""", unsafe_allow_html=True)
