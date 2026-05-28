import streamlit as st
import time

# ==========================================
# STYLIZACJA GRAFICZNA (BOSCH DASHBOARD)
# ==========================================
st.set_page_config(page_title="Bosch AgroDrill - Multi-Battery v8.4", layout="wide")

st.markdown("""
    <style>
    .main-container { background-color: #f8fafc; padding: 20px; border-radius: 15px; border: 2px solid #005691; }
    .status-panel { background-color: #2d3748; padding: 20px; border-radius: 10px; border-bottom: 4px solid #ed0007; color: white; }
    .telemetry-text { font-family: 'Courier New', monospace; font-size: 14px; color: #63b3ed; line-height: 1.8; }
    .bosch-header { color: #005691; font-weight: 800; font-size: 32px; margin-bottom: 0; }
    .bosch-red { color: #ed0007; }
    
    .ground-area { background-color: #451a03; border-radius: 0 0 15px 15px; height: 120px; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; }
    .sky-area { background-color: #bae6fd; height: 80px; border-radius: 15px 15px 0 0; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 5px; color: #1e293b; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="bosch-header">⚙️ BOSCH <span class="bosch-red">AgroDrill</span> Guard v8.4</p>', unsafe_allow_html=True)
st.markdown('<p style="color: #64748b; margin-top: 5px;">Zrównoważone zarządzanie energią — System Dwubateryjny Solar-Pack</p>', unsafe_allow_html=True)
st.write("---")

# ==========================================
# INICJALIZACJA SYSTEMU ZASILANIA W PAMIĘCI
# ==========================================
if "bateria_glowna" not in st.session_state:
    st.session_state.bateria_glowna = 85
if "bateria_zapasowa" not in st.session_state:
    st.session_state.bateria_zapasowa = 42

CHMURA_ROSLIN = {
    "Polska (Umiarkowana)": {"Róża Premium": 40, "Młoda Jabłoń": 60, "Borówka Amerykańska": 35},
    "Hiszpania (Śródziemnomorska)": {"Drzewo Oliwne": 70, "Lawenda Wąskolistna": 25, "Drzewko Cytrusowe": 50},
    "Egipt (Pustynna / Sucha)": {"Palma Daktylowa": 90, "Aloes Zwyczajny": 20, "Agawa Niebieska": 45},
    "Japonia (Azjatycka / Wilgotna)": {"Drzewko Bonsai": 30, "Bambus Ozdobny": 55, "Krzew Herbaty": 40}
}

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Bosch-logo.svg/1024px-Bosch-logo.svg.png", width=150)
status = st.sidebar.toggle("🌐 Tryb Online (Cloud)", value=True)

# Przycisk do resetu zasilania
if st.sidebar.button("🔌 Podłącz ładowarkę serwisową"):
    st.session_state.bateria_glowna = 100
    st.session_state.bateria_zapasowa = 50
    st.rerun()

# ==========================================
# UKŁAD STRONY (3 KOLUMNY)
# ==========================================
col_left, col_mid, col_right = st.columns([1, 2, 1])

# --- KOLUMNA LEWA: STEROWANIE I ENERGIA ---
with col_left:
    st.markdown('<div class="status-panel">', unsafe_allow_html=True)
    st.subheader("⚙️ Konfiguracja GPS")
    region = st.selectbox("Wykryta Strefa Klimatyczna:", list(CHMURA_ROSLIN.keys()))
    plant = st.selectbox("Profil Agronomiczny Rośliny:", list(CHMURA_ROSLIN[region].keys()))
    target_depth = CHMURA_ROSLIN[region][plant]
    
    st.write("---")
    st.subheader("🔋 Eko-Zasilanie Bosch")
    
    st.write(f"**Akumulator Główny:** {st.session_state.bateria_glowna}%")
    st.progress(st.session_state.bateria_glowna)
    
    st.write(f"**Bateria Zapasowa (Solar):** {st.session_state.bateria_zapasowa}%")
    st.progress(st.session_state.bateria_zapasowa)
    
    # Logika nasłonecznienia zależna od strefy
    if "Egipt" in region:
        solar_status = "☀️ INTENSYWNE (Ładowanie +4% / cykl)"
        solar_gain = 4
    elif "Hiszpania" in region:
        solar_status = "🌤️ DOBRE (Ładowanie +2% / cykl)"
        solar_gain = 2
    else:
        solar_status = "☁️ UMIARKOWANE (Ładowanie +1% / cykl)"
        solar_gain = 1
        
    st.caption(f"Status PV: {solar_status}")
    
    st.write("---")
    st.subheader("⛏️ Sensory Wiertła")
    vib_val = st.slider("Wibracje wrzeciona (mm/s)", 1.0, 8.0, 2.4, step=0.1)
    st.markdown('</div>', unsafe_allow_html=True)

# --- KOLUMNA ŚRODKOWA: WIDOK TERENOWY ---
with col_mid:
    st.subheader("🖥️ Cyfrowy Bliźniak (Widok Terenowy)")
    st.write(f"Plan: Wykop **{target_depth} cm** | System: **{'Cloud AI' if status else 'Edge AI (Offline)'}**")
    
    container = st.empty()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    container.markdown("""
        <div class="sky-area">🕷️ (Oczekiwanie)</div>
        <div class="ground-area"><p style="color: #632a08;">░░░░ GLEBA NIENARUSZONA ░░░░</p></div>
    """, unsafe_allow_html=True)
    
    start_btn = st.button("🚀 URUCHOM CYKL ROBOCZY", type="primary", use_container_width=True)

    if start_btn:
        if st.session_state.bateria_glowna <= 15:
            status_text.error(f"❌ KRYTYCZNY BŁĄD SYSTEMU: Za niski poziom energii akumulatora głównego ({st.session_state.bateria_glowna}%). Praca wstrzymana.")
            st.info("💡 *Wskazówka dla prezentera:* Użyj przycisku awaryjnego na panelu bocznym, aby podłączyć ładowarkę.")
            
        elif vib_val > 5.5:
            container.markdown(f"""
                <div class="sky-area" style="background-color: #fca5a5;">⚠️ ALARM REAKCJI AI</div>
                <div class="ground-area" style="background-color: #7f1d1d;"><p style="color: white; font-weight: bold;">💥 ZABLOKOWANO NA KAMIENIU!</p></div>
            """, unsafe_allow_html=True)
            status_text.error(f"🚨 ALERT OCHRONY NARZĘDZI AI: Wykryto kamień! Zatrzymano wiercenie.")
            
        else:
            # --- FAZA 1: KROCZENIE ---
            for i in range(0, 31, 10):
                spacer = "&nbsp;" * (i * 2)
                leg_icon = "🕷️" if i % 20 == 0 else "👣"
                container.markdown(f"""
                    <div class="sky-area">{spacer} {leg_icon} 🤖</div>
                    <div class="ground-area"><p style="color: #cbd5e1;">░░░░ POZYCJONOWANIE W TOKU ░░░░</p></div>
                """, unsafe_allow_html=True)
                time.sleep(0.2)

            # --- FAZA 2: WIERCE ---
            for depth in range(0, target_depth + 1, 10):
                hole = "🕳️" * (depth // 10) if depth >= 10 else "•"
                container.markdown(f"""
                    <div class="sky-area">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 🕷️ Wiercenie...<br> ⚙️</div>
                    <div class="ground-area"><p style="font-size: 25px;">{hole} ⛏️</p></div>
                """, unsafe_allow_html=True)
                progress_bar.progress(int((depth / target_depth) * 100))
                time.sleep(0.2)

            # --- FAZA 3: SADZENIE ---
            for grow in range(1, 4):
                plant_emoji = "🌱" if grow == 1 else "🌿" if grow == 2 else "🌳"
                container.markdown(f"""
                    <div class="sky-area">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 🕷️ (Zakończono pomyślnie!)</div>
                    <div class="ground-area"><p style="font-size: 40px;">{plant_emoji}</p></div>
                """, unsafe_allow_html=True)
                time.sleep(0.3)

            # --- ZMIANA STANÓW BATERII PO ZADANIU ---
            st.session_state.bateria_glowna -= 5  
            st.session_state.bateria_zapasowa = min(100, st.session_state.bateria_zapasowa + solar_gain) 
            
            status_text.success(f"✅ Cykl zakończony! Zużyto 5% energii głównej. Panele solarne doładowały baterię zapasową o +{solar_gain}%.")
            st.balloons()
            time.sleep(1.0)
            st.rerun()
            
    else:
        if st.session_state.bateria_glowna <= 15: 
            status_text.warning("🪫 Status: Krytyczny poziom energii roboczej.")
        elif vib_val > 5.5: 
            status_text.error("⚠️ Status: Wykryto kamień.")
        else: 
            status_text.write("🤖 Status: Gotowy do rozpoczęcia cyklu.")

# --- KOLUMNA PRAWA: KONSOLA TELEMETRII ---
with col_right:
    st.markdown('<div class="status-panel">', unsafe_allow_html=True)
    st.subheader("📊 Konsola Telemetrii")
    
    if st.session_state.bateria_glowna <= 15:
        system_status = "STREFA_AWARYJNA (LOW_BAT)"
    elif vib_val > 5.5:
        system_status = "STREFA_AWARYJNA (OBSTACLE)"
    else:
        system_status = "BEZPIECZNY (READY)"

    st.markdown(f"""
    <p class="telemetry-text">
    &gt; URZĄDZENIE: AGRODRILL v8.4<br>
    &gt; CHMURA: {'CONNECTED' if status else 'OFFLINE'}<br>
    -------------------------<br>
    &gt; AKUMULATOR GŁÓWNY: {st.session_state.bateria_glowna}%<br>
    &gt; SOLAR BACKUP: {st.session_state.bateria_zapasowa}%<br>
    &gt; OGNIWA PV: {solar_status.split()[0]}<br>
    -------------------------<br>
    &gt; GŁĘBOKOŚĆ CELU: {target_depth} cm<br>
    &gt; TEST WIBRACJI: {vib_val} mm/s<br>
    -------------------------<br>
    &gt; STATUS: {system_status}
    </p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
