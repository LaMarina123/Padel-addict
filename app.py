import os
import random
import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Padel Addict - Organisateur de Matchs", page_icon="🎾", layout="wide")

st.markdown("""
    <style>
    .round-header { background-color: #2C3E50; color: white; padding: 10px; border-radius: 8px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; }
    .court-card { background-color: #E8F4F8; border-left: 5px solid #007FFF; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .bench-card { background-color: #FEF9E7; border-left: 5px solid #F1C40F; padding: 15px; border-radius: 8px; margin-top: 10px; color: #7D6608; }
    </style>
""", unsafe_allow_html=True)

col_logo, col_title = st.columns([1, 4])
with col_logo:
    logo_path = os.path.expanduser("~/Downloads/logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.info("💡 Placez 'logo.png' dans Téléchargements.")

with col_title:
    st.title("Padel Addict")
    st.subheader("Gestionnaire & Générateur de Matchs Intelligents")

# --- GESTION DU FICHIER DE SAUVEGARDE ---
DB_FILE = "players_list.txt"

def load_players():
    """Charge les joueurs depuis le fichier local ou crée la liste par défaut."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            players = [line.strip() for line in f.readlines() if line.strip()]
            if players:
                return players
    
    # Liste personnalisée de vos 25 joueurs
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
    """Sauvegarde la liste actuelle des joueurs dans le fichier local."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for player in sorted(players_list):
            f.write(f"{player}\n")

# Initialisation des variables session Streamlit
if "players" not in st.session_state:
    st.session_state.players = load_players()

if "rounds_results" not in st.session_state:
    st.session_state.rounds_results = None

col_config, col_players = st.columns(2)

with col_config:
    st.markdown("### ⚙️ Paramètres de Session")
    # Terrains triés par ordre croissant : 2, 3, 4
    court_count = st.selectbox("Nombre de terrains disponibles :", [2, 3, 4], index=0, key="sb_court_count")
    # Temps de location trié par ordre croissant : 1h30 puis 2h00
    total_time_str = st.selectbox("Temps de location total :", ["1h30 (90 min)", "2h00 (120 min)"], index=0, key="sb_total_time")
    total_time = 90 if "90" in total_time_str else 120
    # Durée de partie triée par ordre croissant : 20 puis 30
    match_time = st.selectbox("Durée d'une partie :", [20, 30], index=0, key="sb_match_time")

with col_players:
    st.markdown(f"### 👥 Gestion de la Liste Padel Addict ({len(st.session_state.players)})")
    
    # Ajouter un joueur
    col_add_input, col_add_btn = st.columns([3, 1])
    with col_add_input:
        new_player = st.text_input("Nom du nouveau joueur :", key="add_player_input", label_visibility="collapsed", placeholder="Nom du joueur...")
    with col_add_btn:
        if st.button("➕ Ajouter", use_container_width=True, key="btn_add_player"):
            cleaned_name = new_player.strip()
            if cleaned_name and cleaned_name not in st.session_state.players:
                st.session_state.players.append(cleaned_name)
                save_players(st.session_state.players)
                st.rerun()

    # Supprimer un joueur de la liste globale
    col_del_select, col_del_btn = st.columns([3, 1])
    with col_del_select:
        player_to_delete = st.selectbox("Supprimer un joueur de la base :", ["-- Sélectionner un joueur à retirer --"] + sorted(st.session_state.players), label_visibility="collapsed", key="sb_del_player")
    with col_del_btn:
        if st.button("🗑️ Supprimer", use_container_width=True, type="secondary", key="btn_del_player"):
            if player_to_delete and player_to_delete != "-- Sélectionner un joueur à retirer --":
                st.session_state.players.remove(player_to_delete)
                save_players(st.session_state.players)
                st.rerun()

    st.markdown("---")
    
    # Récupération de l'état actuel pour calculer le nombre de joueurs présents
    current_selected = st.session_state.get("ms_players_today", [])
    
    # Menu Déroulant / Multi-select pour les joueurs du jour avec compteur dynamique
    selected_players = st.multiselect(
        f"🎯 Sélectionnez les joueurs présents aujourd'hui ({len(current_selected)}) :",
        options=sorted(st.session_state.players),
        default=current_selected,  
        placeholder="Choisissez les joueurs...",
        key="ms_players_today"
    )

def run_rotation():
    players_needed = court_count * 4
    if len(selected_players) < players_needed:
        st.error(f"❌ Il vous faut au moins {players_needed} joueurs sélectionnés pour remplir {court_count} terrains (Actuellement : {len(selected_players)}).")
        return

    total_rounds = total_time // match_time
    rounds = []
    bench_count = {p: 0 for p in selected_players}
    
    # Historique strict pour empêcher les doublons : { joueur: set(partenaires_déjà_eus) }
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

        # Assignation des partenaires sans répétition
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
            st.warning(f"⚠️ Impossible de trouver des partenaires 100% uniques pour le Tour {r}. Réinitialisation locale appliquée.")
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
    pdf_filename = "Padel_Addict_Planning.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Padel Addict - Planning des Matchs", ln=True, align="C")
    pdf.ln(10)

    for r in rounds:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(44, 62, 80)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, f"TOUR {r['round_num']} ({r['duration_str']})", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 10)
        for c in r['courts']:
            match_txt = f"  Terrain {c['court']}:  {c['t1'][0]} & {c['t1'][1]}   VS   {c['t2'][0]} & {c['t2'][1]}"
            pdf.cell(0, 6, match_txt, ln=True)
        
        if r['bench']:
            pdf.ln(1)
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(125, 102, 8)
            bench_txt = f"  -> Banc (Prioritaires): {', '.join(r['bench'])}"
            pdf.cell(0, 6, bench_txt, ln=True)
            pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    pdf.output(pdf_filename)
    return pdf_filename

st.markdown("---")
col_b1, col_b2, col_b3 = st.columns(3)

with col_b1:
    if st.button("🎲 Générer les Matchs", use_container_width=True, type="primary", key="btn_generate_matches"):
run_rotation()
with col_b2:
if st.button("🔄 Réinitialiser les Tirages", use_container_width=True, key="btn_reset_draws"):
st.session_state.rounds_results = None
st.rerun()
if st.session_state.rounds_results:
with col_b3:
pdf_file = generate_pdf(st.session_state.rounds_results)
with open(pdf_file, "rb") as f:
st.download_button(
label="📥 Télécharger le Planning (PDF)",
data=f,
file_name="Planning_Padel_Addict.pdf",
mime="application/pdf",
use_container_width=True
)
st.markdown("### 🗓️ Programme des Matchs")
for r in st.session_state.rounds_results:
st.markdown(f"🔄 TOUR {r['round_num']} ({r['duration_str']})", unsafe_allow_html=True)
court_cols = st.columns(court_count)
for i, c in enumerate(r['courts']):
with court_cols[i]:
st.markdown(f"""

🎾 Terrain {c['court']}


👥 Équipe 1 : {c['t1'][0]} & {c['t1'][1]}

VS

👥 Équipe 2 : {c['t2'][0]} & {c['t2'][1]}

""", unsafe_allow_html=True)
if r['bench']:
st.markdown(f"⏳ Sur le banc pour ce tour : {', '.join(r['bench'])}", unsafe_allow_html=True)
