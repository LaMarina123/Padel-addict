import os
import random
from datetime import datetime, timedelta
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
        "session_date": "Date de la session :",
        "start_time": "Heure de début :",
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
        "exclude_expander": "🚫 Exclure un ou plusieurs joueurs d'un tour précis (Optionnel)",
        "exclude_round_label": "Tour {} ({}) - Joueurs au repos forcé :",
        "exclude_placeholder": "Aucun joueur exclu",
        "error_min_players": "❌ Il vous faut au moins {} joueurs sélectionnés pour remplir {} terrains (Actuellement : {}).",
        "error_too_many_excluded": "❌ Tour {} : Trop de joueurs exclus ({}). Il ne reste que {} joueurs actifs pour {} places nécessaires.",
        "warning_fallback": "⚠️ Contrainte forte sur le Tour {} : {} paire(s) déjà vue(s) au minimum.",
        "pdf_title": "PADEL ADDICT - {}",
        "pdf_time": "Heure",
        "pdf_court": "Terrain {}",
        "pdf_bench": "Joueurs au repos",
        "pdf_tour": "TOUR",
        "btn_generate": "🎲 Générer les Matchs",
        "btn_reset": "🔄 Réinitialiser les Tirages",
        "btn_download": "📥 Télécharger le Planning (PDF)",
        "pdf_filename": "Planning_Padel_Addict.pdf",
        "schedule_title": "### 🗓️ Programme des Matchs",
        "court_label": "🎾 Terrain",
        "team1_label": "Équipe 1 :",
        "team2_label": "Équipe 2 :",
        "bench_label": "⏳ <b>Sur le banc pour ce tour :</b> ",
        "stats_expander": "📊 Vérifier l'équilibre des temps de repos par joueur",
        "logo_info": "💡 Placez 'logo.png' dans Téléchargements."
    },
    "English": {
        "subtitle": "Smart Match Manager & Generator",
        "config_title": "### ⚙️ Session Settings",
        "lang_select": "Choose language:",
        "session_date": "Session date:",
        "start_time": "Start time:",
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
        "exclude_expander": "🚫 Exclude one or more players from a specific round (Optional)",
        "exclude_round_label": "Round {} ({}) - Forced bench players:",
        "exclude_placeholder": "No excluded player",
        "error_min_players": "❌ You need at least {} selected players to fill {} courts (Currently: {}).",
        "error_too_many_excluded": "❌ Round {}: Too many excluded players ({}). Only {} active players left for {} spots needed.",
        "warning_fallback": "⚠️ Tight constraint on Round {}: minimum {} repeated pair(s) applied.",
        "pdf_title": "PADEL ADDICT - {}",
        "pdf_time": "Time",
        "pdf_court": "Court {}",
        "pdf_bench": "Resting players",
        "pdf_tour": "ROUND",
        "btn_generate": "🎲 Generate Matches",
        "btn_reset": "🔄 Reset Draws",
        "btn_download": "📥 Download Schedule (PDF)",
        "pdf_filename": "Padel_Addict_Schedule.pdf",
        "schedule_title": "### 🗓️ Match Schedule",
        "court_label": "🎾 Court",
        "team1_label": "Team 1:",
        "team2_label": "Team 2:",
        "bench_label": "⏳ <b>On the bench for this round:</b> ",
        "stats_expander": "📊 Check bench balance per player",
        "logo_info": "💡 Place 'logo.png' in Downloads."
    }
}

# --- INITIALISATION DE LA LANGUE ---
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

if "bench_stats" not in st.session_state:
    st.session_state.bench_stats = None

col_config, col_players = st.columns(2)

with col_config:
    t = LANGUAGES[st.session_state.lang]
    st.markdown(t["config_title"])
    
    st.markdown(f"**{t['lang_select']}**")
    col_fr, col_en = st.columns(2)
    with col_fr:
        is_fr_active = st.session_state.lang == "Français"
        if st.button("🇫🇷 Français", use_container_width=True, type="primary" if is_fr_active else "secondary", key="btn_lang_fr"):
            st.session_state.lang = "Français"
            st.rerun()
    with col_en:
        is_en_active = st.session_state.lang == "English"
        if st.button("🇬🇧 English", use_container_width=True, type="primary" if is_en_active else "secondary", key="btn_lang_en"):
            st.session_state.lang = "English"
            st.rerun()
            
    t = LANGUAGES[st.session_state.lang]
    st.markdown("<br>", unsafe_allow_html=True)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        session_date = st.date_input(t["session_date"], value=datetime.today(), format="DD/MM/YYYY", key="di_session_date")
    with col_d2:
        start_time = st.time_input(t["start_time"], value=datetime.strptime("09:00", "%H:%M").time(), step=600, key="ti_start_time")
    
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

    # --- SECTION : EXCLUSIONS PAR TOUR ---
    excluded_by_round = {}
    if selected_players:
        total_rounds_preview = total_time // match_time
        preview_dt = datetime.combine(session_date, start_time)
        with st.expander(t["exclude_expander"], expanded=False):
            for r in range(1, total_rounds_preview + 1):
                r_time_str = preview_dt.strftime("%H:%M")
                preview_dt += timedelta(minutes=match_time)
                
                prev_excl = [p for p in st.session_state.get(f"excl_round_{r}", []) if p in selected_players]
                
                excluded_by_round[r] = st.multiselect(
                    t["exclude_round_label"].format(r, r_time_str),
                    options=sorted(selected_players),
                    default=prev_excl,
                    placeholder=t["exclude_placeholder"],
                    key=f"excl_round_{r}"
                )

def run_rotation():
    t = LANGUAGES[st.session_state.lang]
    players_needed = court_count * 4
    if len(selected_players) < players_needed:
        st.error(t["error_min_players"].format(players_needed, court_count, len(selected_players)))
        return

    total_rounds = total_time // match_time

    # Vérification préalable des exclusions sur chaque tour
    for r in range(1, total_rounds + 1):
        excl_count = len(excluded_by_round.get(r, []))
        active_count = len(selected_players) - excl_count
        if active_count < players_needed:
            st.error(t["error_too_many_excluded"].format(r, excl_count, active_count, players_needed))
            return

    rounds = []
    bench_count = {p: 0 for p in selected_players}
    bench_pair_history = {p: {other: 0 for other in selected_players} for p in selected_players}
    partner_history = {p: set() for p in selected_players}
    last_bench = set()
    current_dt = datetime.combine(session_date, start_time)

    for r in range(1, total_rounds + 1):
        round_time_str = current_dt.strftime("%H:%M")
        current_dt += timedelta(minutes=match_time)

        forced_bench = set(excluded_by_round.get(r, []))
        next_forced_bench = set(excluded_by_round.get(r + 1, []))
        num_bench_needed = len(selected_players) - players_needed
        extra_bench_needed = num_bench_needed - len(forced_bench)

        # Candidats potentiels pour aller sur le banc (hors exclusions forcées)
        candidates = [p for p in selected_players if p not in forced_bench]

        if extra_bench_needed <= 0:
            bench_players = list(forced_bench)
        else:
            # Score de priorité pour aller sur le banc (plus petit = plus prioritaire pour se reposer) :
            # 1. Moins de pauses cumulées jusqu'ici
            # 2. N'était pas sur le banc au tour précédent
            # 3. N'est pas prévu en exclusion forcée au tour suivant
            def bench_priority(p):
                return (
                    bench_count[p],
                    1 if p in last_bench else 0,
                    1 if p in next_forced_bench else 0
                )

            candidates.sort(key=bench_priority)
            cutoff_score = bench_priority(candidates[extra_bench_needed - 1])

            # Joueurs strictement prioritaires pour le banc + groupe à égalité au seuil
            locked_bench = [p for p in candidates if bench_priority(p) < cutoff_score]
            tied_candidates = [p for p in candidates if bench_priority(p) == cutoff_score]
            slots_to_fill = extra_bench_needed - len(locked_bench)

            # Choisir parmi les égalités la combinaison qui mélange au maximum les groupes sur le banc
            best_extra_bench = None
            min_bench_overlap = float("inf")

            for _ in range(500):
                sample_tied = random.sample(tied_candidates, slots_to_fill)
                trial_bench = list(forced_bench) + locked_bench + sample_tied
                overlap = 0
                for i in range(len(trial_bench)):
                    for j in range(i + 1, len(trial_bench)):
                        overlap += bench_pair_history[trial_bench[i]][trial_bench[j]]
                if overlap < min_bench_overlap:
                    min_bench_overlap = overlap
                    best_extra_bench = sample_tied
                    if min_bench_overlap == 0:
                        break

            bench_players = list(forced_bench) + locked_bench + best_extra_bench

        # Mise à jour des compteurs de banc et de paires sur le banc
        for p in bench_players:
            bench_count[p] += 1
        for i in range(len(bench_players)):
            for j in range(i + 1, len(bench_players)):
                p1, p2 = bench_players[i], bench_players[j]
                bench_pair_history[p1][p2] += 1
                bench_pair_history[p2][p1] += 1

        bench_set = set(bench_players)
        round_players = [p for p in selected_players if p not in bench_set]

        # Recherche d'une répartition sur les terrains sans aucun partenaire en double
        best_courts = None
        min_duplicates = float("inf")

        for _ in range(3000):
            random.shuffle(round_players)
            temp_courts = []
            duplicates = 0
            
            for c in range(court_count):
                idx = c * 4
                p1, p2, p3, p4 = round_players[idx:idx+4]
                if p2 in partner_history[p1]:
                    duplicates += 1
                if p4 in partner_history[p3]:
                    duplicates += 1
                temp_courts.append({
                    "court": c + 1,
                    "t1": [p1, p2],
                    "t2": [p3, p4]
                })

            if duplicates < min_duplicates:
                min_duplicates = duplicates
                best_courts = temp_courts
                if min_duplicates == 0:
                    break

        if min_duplicates > 0:
            st.warning(t["warning_fallback"].format(r, min_duplicates))

        # Enregistrement des nouveaux partenaires dans l'historique
        for court in best_courts:
            t1_p1, t1_p2 = court["t1"]
            t2_p1, t2_p2 = court["t2"]
            partner_history[t1_p1].add(t1_p2)
            partner_history[t1_p2].add(t1_p1)
            partner_history[t2_p1].add(t2_p2)
            partner_history[t2_p2].add(t2_p1)

        rounds.append({
            "round_num": r,
            "time_str": round_time_str,
            "duration_str": f"{match_time} min",
            "courts": best_courts,
            "bench": sorted(bench_players)
        })
        last_bench = bench_set

    st.session_state.rounds_results = rounds
    st.session_state.bench_stats = bench_count

def encode_latin1(text):
    return text.encode("latin-1", "replace").decode("latin-1")

def generate_pdf(rounds):
    t = LANGUAGES[st.session_state.lang]
    pdf_filename = t["pdf_filename"]
    
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    
    date_formatted = session_date.strftime("%d/%m/%Y")
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 12, encode_latin1(t["pdf_title"].format(date_formatted)), ln=True, align="C")
    pdf.ln(3)
    
    num_courts = len(rounds[0]["courts"]) if rounds else court_count
    usable_width = 277.0
    w_time = 28.0
    w_bench = 62.0
    w_court = (usable_width - w_time - w_bench) / num_courts
    
    header_h = 11.0
    pdf.set_fill_color(205, 208, 211)
    pdf.set_draw_color(130, 130, 130)
    pdf.set_line_width(0.3)
    pdf.set_font("Helvetica", "B", 10)
    
    pdf.cell(w_time, header_h, encode_latin1(t["pdf_time"]), border=1, align="C", fill=True)
    for c_idx in range(1, num_courts + 1):
        pdf.cell(w_court, header_h, encode_latin1(t["pdf_court"].format(c_idx)), border=1, align="C", fill=True)
    pdf.cell(w_bench, header_h, encode_latin1(t["pdf_bench"]), border=1, align="C", fill=True)
    pdf.ln()
    
    row_h = 21.0
    for idx, r in enumerate(rounds):
        if pdf.get_y() + row_h > 198:
            pdf.add_page()
            pdf.set_fill_color(205, 208, 211)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(w_time, header_h, encode_latin1(t["pdf_time"]), border=1, align="C", fill=True)
            for c_idx in range(1, num_courts + 1):
                pdf.cell(w_court, header_h, encode_latin1(t["pdf_court"].format(c_idx)), border=1, align="C", fill=True)
            pdf.cell(w_bench, header_h, encode_latin1(t["pdf_bench"]), border=1, align="C", fill=True)
            pdf.ln()
            
        is_shaded = (idx % 2 == 1)
        if is_shaded:
            pdf.set_fill_color(242, 243, 245)
        else:
            pdf.set_fill_color(255, 255, 255)
            
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(w_time, row_h, encode_latin1(r.get("time_str", "")), border=1, align="C", fill=True)
        
        for c in r["courts"]:
            x_cell = pdf.get_x()
            pdf.rect(x_cell, y_start, w_court, row_h, style="DF")
            
            t1_str = f"{c['t1'][0]} + {c['t1'][1]}"
            t2_str = f"{c['t2'][0]} + {c['t2'][1]}"
            
            pdf.set_xy(x_cell, y_start + 3.0)
            pdf.set_font("Helvetica", "", 9.5)
            pdf.cell(w_court, 5.0, encode_latin1(t1_str), align="C")
            
            pdf.set_xy(x_cell, y_start + 8.0)
            pdf.set_font("Helvetica", "B", 9.0)
            pdf.cell(w_court, 5.0, "VS", align="C")
            
            pdf.set_xy(x_cell, y_start + 13.0)
            pdf.set_font("Helvetica", "", 9.5)
            pdf.cell(w_court, 5.0, encode_latin1(t2_str), align="C")
            
            pdf.set_xy(x_cell + w_court, y_start)
            
        x_bench = pdf.get_x()
        pdf.rect(x_bench, y_start, w_bench, row_h, style="DF")
        bench_text = ", ".join(r["bench"]) if r["bench"] else "-"
        pdf.set_font("Helvetica", "", 9.5)
        
        lines_est = pdf.multi_cell(w_bench - 4, 5.0, encode_latin1(bench_text), split_only=True)
        total_txt_h = len(lines_est) * 5.0
        y_offset = max(2.0, (row_h - total_txt_h) / 2.0)
        pdf.set_xy(x_bench + 2, y_start + y_offset)
        pdf.multi_cell(w_bench - 4, 5.0, encode_latin1(bench_text), align="C")
        
        pdf.set_xy(x_start, y_start + row_h)

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
        st.session_state.bench_stats = None
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

    if st.session_state.bench_stats:
        with st.expander(t["stats_expander"], expanded=False):
            stats_sorted = sorted(st.session_state.bench_stats.items(), key=lambda x: (-x[1], x[0]))
            cols_stats = st.columns(4)
            for idx, (player_name, count) in enumerate(stats_sorted):
                with cols_stats[idx % 4]:
                    st.write(f"**{player_name}** : {count} pause(s)")

    st.markdown(t["schedule_title"])
    for r in st.session_state.rounds_results:
        st.markdown(f"<div class='round-header'>🔄 {t['pdf_tour']} {r['round_num']} - {r.get('time_str', '')} ({r['duration_str']})</div>", unsafe_allow_html=True)
        
        court_cols = st.columns(court_count)
        for i, c in enumerate(r['courts']):
            with court_cols[i]:
                st.markdown(f"""
                <div class='court-card'>
                    <b>{t['court_label']} {c['court']}</b><br><br>
                    👥 <b>{t['team1_label']}</b> {c['t1'][0]} + {c['t1'][1]}<br>
                    <span style='color:red; font-weight:bold;'>VS</span><br>
                    👥 <b>{t['team2_label']}</b> {c['t2'][0]} + {c['t2'][1]}
                </div>
                """, unsafe_allow_html=True)
        
        if r['bench']:
            st.markdown(f"<div class='bench-card'>{t['bench_label']}{', '.join(r['bench'])}</div>", unsafe_allow_html=True)
