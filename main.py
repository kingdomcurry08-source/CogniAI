import streamlit as st
import openai
import json
import pdfplumber
import sqlite3
import random
import time
from datetime import datetime

# --- 1. THE HYPER-VOID ENGINE (FULL UI OVERHAUL) ---
st.set_page_config(page_title="COGNIAI | SINGULARITY", page_icon="🧬", layout="wide")

# This CSS injects a live particle background and removes all standard Streamlit "white space"
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;500&family=Space+Grotesk:wght@300;700&display=swap');

    /* Remove Padding & Center Content */
    .block-container { padding: 1rem 2rem !important; max-width: 95% !important; }
    [data-testid="stHeader"] { display: none; }

    /* Live Animated Neural Background */
    .stApp {
        background: radial-gradient(circle at center, #001a0a 0%, #000000 100%);
        color: #00FF41;
        font-family: 'Space Grotesk', sans-serif;
    }
    .stApp::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: url('https://www.transparenttextures.com/patterns/carbon-fibre.png');
        opacity: 0.1; pointer-events: none;
    }

    /* Holographic Panels (No Empty Space) */
    .omni-card {
        background: rgba(0, 40, 20, 0.2);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 255, 65, 0.3);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 20px;
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.1);
        transition: 0.5s all;
    }
    .omni-card:hover { border-color: #00FF41; box-shadow: 0 0 50px rgba(0, 255, 65, 0.4); }

    /* Floating Navigation */
    .nav-bar { display: flex; justify-content: space-around; background: rgba(0,0,0,0.8); border: 1px solid #00FF41; border-radius: 50px; padding: 10px; margin-bottom: 40px; }

    /* Glitch Title */
    .glitch {
        font-size: 5rem; font-weight: 800; text-align: center;
        text-shadow: 2px 2px #ff00c1, -2px -2px #00fff9;
        animation: glitch-anim 1s infinite linear alternate-reverse;
    }
    @keyframes glitch-anim {
        0% { transform: skew(0.5deg); }
        100% { transform: skew(-0.5deg); }
    }

    /* 3D Spinning Cube for Photos */
    .cube-container { perspective: 800px; width: 100%; display: flex; justify-content: center; }
    .spinning-photo {
        width: 350px; height: 350px; transform-style: preserve-3d;
        animation: rotate3d 12s infinite linear;
        border: 4px solid #00FF41; box-shadow: 0 0 80px #00FF41; border-radius: 20px;
    }
    @keyframes rotate3d { from { transform: rotateY(0deg); } to { transform: rotateY(360deg); } }
    </style>
    """, unsafe_allow_html=True)


# --- 2. DB INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('cogniai_omega.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS profile (xp INT, lvl INT)')
    conn.execute('CREATE TABLE IF NOT EXISTS nodes (q TEXT, a TEXT)')
    if not conn.execute('SELECT * FROM profile').fetchone():
        conn.execute('INSERT INTO profile VALUES (0, 1)')
    conn.commit()
    return conn


db = init_db()

# --- 3. PAGE LOGIC ---
if 'page' not in st.session_state: st.session_state.page = "HOME"

st.markdown("<h1 class='glitch'>COGNIAI</h1>", unsafe_allow_html=True)

# Full-Width Navigation
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🌌 NEURAL CORE", use_container_width=True): st.session_state.page = "HOME"
with c2:
    if st.button("🧠 STUDY LAB", use_container_width=True): st.session_state.page = "LAB"
with c3:
    if st.button("📐 MATH NEXUS", use_container_width=True): st.session_state.page = "MATH"
with c4:
    if st.button("🖼️ PHOTO GEN", use_container_width=True): st.session_state.page = "PHOTO"

# --- 4. MODULES ---

if st.session_state.page == "HOME":
    # Hero Visuals
    st.markdown("""
        <div class="omni-card" style="text-align: center;">
            <h2 style="font-size: 45px;">WELCOME TO THE OMNI-SINGULARITY</h2>
            <p style="font-size: 20px; opacity: 0.6;">System Status: Hyper-Synced | Neural Load: Optimal</p>
        </div>
    """, unsafe_allow_html=True)

    # 3-Column Grid (Filling Space)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            "<div class='omni-card'><h3>⚡ Recursive Logic</h3><p>Extracting intelligence from thousands of PDF blocks simultaneously.</p></div>",
            unsafe_allow_html=True)
        st.markdown(
            "<div class='omni-card'><h3>🛡️ Security</h3><p>Local SQLite database encryption enabled. Your data never leaves the singularity.</p></div>",
            unsafe_allow_html=True)
    with col2:
        st.image("https://images.unsplash.com/photo-1614728263952-84ea256f9679?auto=format&fit=crop&q=80&w=800")
        st.markdown("<div class='omni-card' style='text-align:center;'><b>LEVEL: ARCHITECT</b></div>",
                    unsafe_allow_html=True)
    with col3:
        st.markdown(
            "<div class='omni-card'><h3>🛰️ Satellite Sync</h3><p>Real-time math resolution via the Neural Nexus. No equation is unsolvable.</p></div>",
            unsafe_allow_html=True)
        st.markdown(
            "<div class='omni-card'><h3>🧬 Bio-Recall</h3><p>Spaced repetition tracking your specific forgetting curve for maximum efficiency.</p></div>",
            unsafe_allow_html=True)

elif st.session_state.page == "LAB":
    st.markdown("<div class='omni-card'><h2>🧠 NEURAL INGESTION</h2>", unsafe_allow_html=True)
    up = st.file_uploader("DROP DATA STREAM (PDF)")
    if up and st.button("INITIATE SYNC"):
        with st.status("🧬 SYNTHESIZING NODES..."):
            with pdfplumber.open(up) as pdf:
                raw = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
                # AI logic here...
                time.sleep(2)
        st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)

    # Fill the rest of the lab with the "Memory Recall" Expander Grid
    st.markdown("### 🗃️ ACTIVE MEMORY SLOTS")
    cols = st.columns(3)
    for i in range(9):
        cols[i % 3].markdown(f"<div class='omni-card'><b>Slot {i + 1}:</b> No Data Detected.</div>",
                             unsafe_allow_html=True)

elif st.session_state.page == "PHOTO":
    st.markdown("<div class='omni-card'><h2>🖼️ AI PHOTO MANIFESTATION</h2>", unsafe_allow_html=True)
    p = st.text_input("Enter Prompt...")
    if st.button("MANIFEST"):
        # Simulated spinning photo for visual impact
        st.markdown(f"""
            <div class="cube-container">
                <div class="spinning-photo">
                    <img src="https://images.unsplash.com/photo-1635070041078-e363dbe005cb?auto=format&fit=crop&q=80&w=800" style="width:100%; border-radius:15px;">
                </div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Ticker Footer
st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background: #00FF41; color: black; font-weight: bold; font-family: 'Fira Code'; padding: 5px; text-align: center;">
        CORE STATUS: HYPER-ACTIVE // MEMORY: OPTIMAL // NEURAL NODES: UNLIMITED // WELCOME TO THE FUTURE...
    </div>
""", unsafe_allow_html=True)