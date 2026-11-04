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
    st.markdown("### ⚙️ Paramètres de Session")
    court_count = st.selectbox("Nombre de terrains disponibles :", [2, 3, 4], index=1)
    total_time_str = st.selectbox("Temps de location total :", ["1h30 (90 min)", "2h00 (120 min)"], index=1)
    total_time = 90 if "90" in total_time_str else 120
    match_time = st.selectbox("Durée d'une partie :", [20, 30], index=1)

with col_players:
    st.markdown(f"### 👥 Liste Padel Addict ({len(st.session_state.players)})")
    new_player = st.text_input("Nom du nouveau joueur :", key="add_player_input")
    if st.button("Ajouter à la liste"):
        if new_player.strip() and new_player.strip() not in st.session_state.players:
            st.session_state.players.append(new_player.strip())
            st.rerun()

    st.markdown("**Sélectionnez les joueurs disponibles aujourd'hui :**")
    selected_players = []
    pl_cols = st.columns(3)
    for idx, player in enumerate(sorted(st.session_state.players)):
        with pl_cols[idx % 3]:
            if st.checkbox(player, value=True, key=f"chk_{player}"):
                selected_players.append(player)

def format_time(minutes):
    h = (minutes // 60) + 14
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

def run_rotation():
    players_needed = court_count * 4
    if len(selected_players) < players_needed:
        st.error(f"❌ Il vous faut au moins {players_needed} joueurs pour remplir {court_count} terrains.")
        return

    total_rounds = total_time // match_time
    rounds = []
    current_time = 0
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

        start_str = format_time(current_time)
        current_time += match_time
        end_str = format_time(current_time)

        rounds.append({
            "round_num": r,
            "time_window": f"{start_str} - {end_str}",
            "courts": courts_data,
            "bench": bench_players
        })
        last_bench = list(bench_players)

    st.session_state.rounds_results = rounds

def generate_pdf(rounds):
    pdf_filename = os.path.expanduser("~/Downloads/Padel_Addict_Planning.pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Padel Addict - Planning des Matchs", ln=True, align="C")
    pdf.ln(10)

    for r in rounds:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(44, 62, 80)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, f"TOUR {r['round_num']} ({r['time_window']})", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 10)
        for c in r['courts']:
            match_txt = f"  Terrain {c['court']}:  {c['t1']} & {c['t1']}   VS   {c['t2']} & {c['t2']}"
            pdf.cell(0, 6, match_txt, ln=True)
        
        if r['bench']:
            pdf.ln(1)
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(125, 102, 8)
            bench_txt = f"  -> Banc (Prioritaires): {', '.join(r['bench'])}"
            pdf.cell(0, 6, bench_txt, ln=True)
            pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    try:
        pdf.output(pdf_filename)
    except:
        pdf_filename = "Padel_Addict_Planning.pdf"
        pdf.output(pdf_filename)
        
    return pdf_filename

st.markdown("---")
col_b1, col_b2, col_b3 = st.columns(3)

with col_b1:
    if st.button("🎲 Générer les Matchs", use_container_width=True, type="primary"):
        run_rotation()

with col_b2:
    if st.button("🔄 Réinitialiser les Tirages", use_container_width=True):
        st.session_state.rounds_results = None
        st.rerun()

if st.session_state.rounds_results:
    pdf_path = generate_pdf(st.session_state.rounds_results)
    with col_b3:
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Télécharger le Planning PDF",
                data=f,
                file_name="Padel_Addict_Planning.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    st.markdown("## 📊 Résultats des Matchs par Tour")
    for r in st.session_state.rounds_results:
        st.markdown(f'<div class="round-header">🔄 TOUR {r["round_num"]} &nbsp;&nbsp;|&nbsp;&nbsp; ⏰ {r["time_window"]} ({match_time} min)</div>', unsafe_allow_html=True)
        court_cols = st.columns(court_count)
        for idx, c in enumerate(r['courts']):
            with court_cols[idx]:
                st.markdown(f"""
                <div class="court-card">
                    <div style="font-weight:bold; color:#007FFF; border-bottom:1px solid #cbd5e1; margin-bottom:5px;">🔲 Terrain {c['court']}</div>
                    <div style="margin: 2px 0;">🔵 <b>{c['t1'][0]}</b> & <b>{c['t1'][1]}</b></div>
                    <div style="color:#E74C3C; font-weight:bold; font-size:0.8rem; margin: 2px 0; text-align:center;">VS</div>
                    <div style="margin: 2px 0;">🟠 <b>{c['t2'][0]}</b> & <b>{c['t2'][1]}</b></div>
                </div>
                """, unsafe_allow_html=True)
        if r['bench']:
            bench_list = ", ".join([f"<b>{p}</b>" for p in r['bench']])
            st.markdown(f"""
            <div class="bench-card">
                🪑 <b>Banc de touche (Prioritaires au prochain tour) :</b> {bench_list}
            </div>
            """, unsafe_allow_html=True)
