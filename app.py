import streamlit as st
import time

# ==========================================
# STYLIZACJA GRAFICZNA (REXROTH CTRLX DASHBOARD)
# ==========================================
st.set_page_config(page_title="Bosch Rexroth ctrlX - AgroDrill Flota", layout="wide")

st.markdown("""
    <style>
    .main-container { background-color: #f8fafc; padding: 20px; border-radius: 15px; border: 2px solid #005691; }
    .status-panel { background-color: #1e293b; padding: 20px; border-radius: 10px; border-bottom: 4px solid #ed0007; color: white; }
    .telemetry-text { font-family: 'Courier New', monospace; font-size: 13px; color: #38bdf8; line-height: 1.6; }
    .bosch-header { color: #005691; font-weight: 800; font-size: 30px; margin-bottom: 0; }
    .bosch-red { color: #ed0007; }
    
    /* Nowe style dla animacji 3 etapów maszyny */
    .machine-area { background-color: #f1f5f9; border-radius: 10px; padding: 15px; border: 1px dashed #cbd5e1; text-align: center; }
    .ground-line { background-color: #451a03; height: 15px; border-radius: 5px; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="bosch-header">⚙️ BOSCH <span class="bosch-red">Rexroth</span> ctrlX AgroDrill v9.0</p>', unsafe_allow_html=True)
st.markdown('<p style="color: #64748b; margin-top: 5px;">Panel Monitorowania Floty GPO — Przepływ End-to-End & Analiza AI</p>', unsafe_allow_html=True)
st.write("---")

# ==========================================
# SYSTEM PAMIĘCI I ENERGII
# ==========================================
if "bat_main" not in st.session_state: st.session_state.bat_main = 30
if "bat_solar" not in st.session_state: st.session_state.bat_solar = 85
if "swap_done" not in st.session_state: st.session_state.swap_done = False

# Panel Boczny
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Bosch-logo.svg/1024px-Bosch-logo.svg.png", width=150)
tryb_sieci = st.sidebar.toggle("🌐 Połączenie IT (Chmura GPO)", value=True)

if st.sidebar.button("🔄 Resetuj System i Energię"):
    st.session_state.bat_main = 30
    st.session_state.bat_solar = 85
    st.session_state.swap_done = False
    st.rerun()

# ==========================================
# UKŁAD STRONY (3 KOLUMNY)
# ==========================================
col_left, col_mid, col_right = st.columns([1, 2, 1])

# --- KOLUMNA LEWA: USTAWIENIA I METRYKI (Z TWÓCH GRAFIK) ---
with col_left:
    st.markdown('<div class="status-panel">', unsafe_allow_html=True)
    st.subheader("📍 Dane Wejściowe")
    strefa = st.selectbox("Strefa operacyjna:", ["Polska (Multidoniczki A1)", "Hiszpania (Multidoniczki B4)"])
    typ_sadzonki = st.selectbox("Typ uprawy:", ["Młoda Jabłoń", "Drzewo Oliwne", "Krzew Borówki"])
    
    st.write("---")
    st.subheader("🔌 System Zasilania")
    st.write(f"Akumulator Główny: **{st.session_state.bat_main}%**")
    st.progress(st.session_state.bat_main)
    st.write(f"Rezerwa Solar-Pack: **{st.session_state.bat_solar}%**")
    st.progress(st.session_state.bat_solar)
    
    st.write("---")
    st.subheader("📊 Sensory Chwytaka (Metryki)")
    # Suwak symulujący przeciążenie (Prąd uzwojenia)
    prad = st.slider("Prąd uzwojenia silnika (I)", 1.0, 15.0, 3.8, step=0.2, help="Norma krytyczna: > 10.0 A (Kamień)")
    encoder = st.radio("Status Enkodera ramienia:", ["Płynny przyrost pozycji", "BRAK PRZYROSTU (Zablokowanie)"])
    st.markdown('</div>', unsafe_allow_html=True)

# --- KOLUMNA ŚRODKOWA: WIDOK OPERACYJNY MASZYNY ---
with col_mid:
    st.subheader("🖥️ Cyfrowy Bliźniak Maszyny (Stan Pracy)")
    
    container_1 = st.empty()
    container_2 = st.empty()
    container_3 = st.empty()
    progress_bar = st.progress(0)
    status_msg = st.empty()
    
    # Początkowy podgląd maszynowy
    container_1.markdown('<div class="machine-area">📦 <b>Etap 1:</b> Oczekiwanie na pobranie z multidoniczki...</div>', unsafe_allow_html=True)
    container_2.markdown('<div class="machine-area">🔄 <b>Etap 2:</b> Karuzela dozująca pusta</div>', unsafe_allow_html=True)
    container_3.markdown('<div class="machine-area">🚜 <b>Etap 3:</b> Lemechy obsypujące w pozycji spoczynkowej</div><div class="ground-line"></div>', unsafe_allow_html=True)
    
    uruchom = st.button("🚀 URUCHOM AUTOMATYCZNY PROCES SADZENIA", type="primary", use_container_width=True)

    if uruchom:
        # SCENARIUSZ SWAPU BATERII
        if st.session_state.bat_main <= 15 and not st.session_state.swap_done:
            status_msg.warning("⚡ [ctrlX PLC] Niski poziom baterii głównej! Uruchamianie procedury automatycznego przerzucenia ogniw Smart Swap...")
            time.sleep(1.5)
            st.session_state.bat_main, st.session_state.bat_solar = st.session_state.bat_solar, st.session_state.bat_main
            st.session_state.swap_done = True
            st.toast("🔄 Akumulatory zamienione!")
            st.rerun()
            
        elif st.session_state.bat_main <= 15 and st.session_state.swap_done:
            status_msg.error("❌ [KRYTYCZNY BRAK ENERGII] Obie baterie wyczerpane. Flota zatrzymana.")
            
        # SCENARIUSZ AWARII (ZABLOKOWANIE CHWYTAKA NA KAMIENIU - NA PODSTAWIE STRONY 1)
        elif prad > 10.0 or encoder == "BRAK PRZYROSTU (Zablokowanie)":
            container_1.markdown('<div class="machine-area" style="background-color: #fee2e2; border-color: #ef4444;">💥 <b>[BŁĄD 1] Maszyna (OT):</b> Chwytak zablokował się na kamieniu w multidoniczce! Prąd drastycznie rośnie!</div>', unsafe_allow_html=True)
            time.sleep(1.0)
            
            status_msg.error("🚨 [KROK 2: ctrlX PLC] Wykryto krytyczny prąd uzwojenia i timeout pozycji! NATYCHMIASTOWE ODCIĘCIE PRĄDU w milisekundy. Ochrona CAPEX aktywna (brak deformacji ramienia). Inicjacja makra cofania.")
            
            if not tryb_sieci:
                st.sidebar.error("📴 OFFLINE FALLBACK: Brak chmury! Lokalny sterownik ctrlX samoczynnie wywozi robota na skraj pola i włącza fizyczny kogut.")
            else:
                st.sidebar.info("📡 IT Edge & AI Cloud: Dane telemetryczne wysłane do systemu zarządzania flotą GPO. Wygenerowano alert mechaniczny Permanent Jam.")
        
        # SCENARIUSZ PRAWIDŁOWY (Z TRZECH ETAPÓW NA ZDJĘCIU)
        else:
            # Etap 1
            container_1.markdown('<div class="machine-area" style="background-color: #e0f2fe;">🤖 🛰️ <b>Etap 1 w toku:</b> Chwytak precyzyjny pobiera bryłkę korzeniową sadzonki...</div>', unsafe_allow_html=True)
            status_msg.info("Trwa realizacja Etapu 1...")
            progress_bar.progress(33)
            time.sleep(0.8)
            container_1.markdown('<div class="machine-area" style="background-color: #dcfce7;">✅ <b>Etap 1 zakończony:</b> Sadzonka pobrana prawidłowo.</div>', unsafe_allow_html=True)
            
            # Etap 2
            container_2.markdown('<div class="machine-area" style="background-color: #e0f2fe;">🔄 🦖 <b>Etap 2 w toku:</b> Ramię robota przenosi sadzonkę. Zawór spustowy karuzeli otwiera sekcję dozującą...</div>', unsafe_allow_html=True)
            status_msg.info("Trwa realizacja Etapu 2...")
            progress_bar.progress(66)
            time.sleep(0.8)
            container_2.markdown('<div class="machine-area" style="background-color: #dcfce7;">✅ <b>Etap 2 zakończony:</b> Karuzela dozująca obrócona pomyślnie.</div>', unsafe_allow_html=True)
            
            # Etap 3
            container_3.markdown('<div class="machine-area" style="background-color: #e0f2fe;">🚜 🌱 <b>Etap 3 w toku:</b> Zrzut przez pionowy aparat. Elastyczne pady sadzące osadzają roślinę. Lemechy obsypują ziemię, a koła dogniatają bryłkę!</div><div class="ground-line"></div>', unsafe_allow_html=True)
            status_msg.info("Trwa realizacja Etapu 3...")
            progress_bar.progress(100)
            time.sleep(0.8)
            container_3.markdown('<div class="machine-area" style="background-color: #dcfce7;">✅ <b>Etap 3 zakończony:</b> Sadzonka zintegrowana z gruntem. Zespół obsypująco-dogniatający wraca do bazy.</div><div class="ground-line"></div>', unsafe_allow_html=True)
            
            # Aktualizacja baterii
            st.session_state.bat_main -= 5
            if "Polska" in strefa: st.session_state.bat_solar = min(100, st.session_state.bat_solar + 1)
            else: st.session_state.bat_solar = min(100, st.session_state.bat_solar + 3)
            
            status_msg.success(f"🌱 Sukces! System zakończył pełny cykl End-to-End. Posadzono: {typ_sadzonki}.")
            st.balloons()
            time.sleep(1.0)
            st.rerun()

# --- KOLUMNA PRAWA: KONSOLA LOGIKI REXROTH ---
with col_right:
    st.markdown('<div class="status-panel">', unsafe_allow_html=True)
    st.subheader("📊 Konsola ctrlX IT-Edge")
    
    status_systemu = "ZABLOKOWANY (KAMIEN)" if (prad > 10.0 or encoder == "BRAK PRZYROSTU (Zablokowanie)") else "READY"
    status_sieci = "CONNECTED (GPO CLOUD)" if tryb_sieci else "OFFLINE (LOCAL FALLBACK)"
    
    st.markdown(f"""
    <p class="telemetry-text">
    &gt; STEROWNIK: Bosch Rexroth ctrlX<br>
    &gt; LINK IT: {status_sieci}<br>
    -------------------------<br>
    &gt; METRYKI OT INTERFEJSU:<br>
    - Pobór prądu silnika: {prad} A<br>
    - Encoder feedback: OK<br>
    - Timeout flag: False<br>
    -------------------------<br>
    &gt; ENERGIA FLOTY:<br>
    - Główny moduł: {st.session_state.bat_main}%<br>
    - Solar backup: {st.session_state.bat_solar}%<br>
    - Przełącznik swapu: {'AKTYWNY' if st.session_state.swap_done else 'NIEAKTYWNY'}<br>
    -------------------------<br>
    &gt; GLOBALNY STATUS: {status_systemu}
    </p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
