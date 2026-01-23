import streamlit as st
import openai
import json
import pdfplumber
import sqlite3
import time
from datetime import datetime

# --- 1. THE HYPER-VOID ENGINE & MATRIX RAIN ---
st.set_page_config(page_title="COGNIAI | SINGULARITY", page_icon="🧬", layout="wide")

# This block injects the Matrix Background + Glitch CSS with LAYER FIXES
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;500&family=Space+Grotesk:wght@300;700&display=swap');

    /* Background Canvas Setup */
    #matrix-canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1; /* Keep this at the very back */
    }

    /* THE FIX: Force the main app container to the front */
    .main .block-container {
        z-index: 99;
        position: relative;
    }

    .stApp {
        background: transparent;
        color: #00FF41;
        font-family: 'Space Grotesk', sans-serif;
    }

    .omni-card {
        background: rgba(0, 10, 5, 0.95); /* Darker for better contrast */
        backdrop-filter: blur(10px);
        border: 2px solid #00FF41;
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 0 35px rgba(0, 255, 65, 0.4);
        position: relative;
        z-index: 100; /* Content Layer */
    }

    .glitch {
        font-size: 5rem; font-weight: 900; text-align: center;
        text-transform: uppercase; letter-spacing: 15px;
        text-shadow: 3px 3px #ff00c1, -3px -3px #00fff9;
    }

    /* Fixed Button Visibility */
    .stButton>button {
        background: rgba(0, 255, 65, 0.1) !important;
        border: 1px solid #00FF41 !important;
        color: #00FF41 !important;
        font-weight: bold !important;
    }
    </style>

    <canvas id="matrix-canvas"></canvas>

    <script>
    const canvas = document.getElementById('matrix-canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ';
    const fontSize = 16;
    const columns = canvas.width / fontSize;
    const drops = Array.from({ length: columns }, () => 1);
    function draw() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#00FF41';
        ctx.font = fontSize + 'px monospace';
        for (let i = 0; i < drops.length; i++) {
            const text = characters.charAt(Math.floor(Math.random() * characters.length));
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }
    setInterval(draw, 33);
    </script>
    """, unsafe_allow_html=True)


# --- 2. LOGIC GATES ---
def init_db():
    conn = sqlite3.connect('cogniai_omega.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY AUTOINCREMENT, q TEXT, a TEXT)')
    conn.commit()
    return conn


db = init_db()

if 'page' not in st.session_state: st.session_state.page = "CORE"

# --- 3. THE HUD (NAVIGATION) ---
st.markdown("<h1 class='glitch'>COGNIAI</h1>", unsafe_allow_html=True)
nav_cols = st.columns(4)
menu = ["CORE", "LAB", "NEXUS", "PHOTO"]
for i, m in enumerate(menu):
    if nav_cols[i].button(m, use_container_width=True):
        st.session_state.page = m
        st.rerun()

# --- 4. MODULES ---

if st.session_state.page == "CORE":
    st.markdown("""
        <div class='omni-card'>
            <h2>⚡ SYSTEM CORE ONLINE</h2>
            <p>Ready for data ingestion. Navigate to the LAB to process your 12-page intelligence files.</p>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "LAB":
    st.markdown("<div class='omni-card'><h2>🧠 NEURAL INGESTION LAB</h2>", unsafe_allow_html=True)

    up = st.file_uploader("DROP INTELLIGENCE DATA (PDF)", type="pdf")

    if up:
        st.info("File Detected. Ready for synchronization.")
        if st.button("🚀 INITIATE DEEP SYNC", use_container_width=True):
            with st.status("🧬 SYNTHESIZING NEURAL NODES...", expanded=True) as status:
                with pdfplumber.open(up) as pdf:
                    raw_text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
                    st.write(f"Reading {len(pdf.pages)} pages...")
                    # Add AI logic here in your final version
                    time.sleep(2)
                status.update(label="SINGULARITY ACHIEVED", state="complete")
            st.success("Data integrated into local memory.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Display Nodes
    st.markdown("### 🗃️ ACTIVE MEMORY NODES")
    nodes = db.execute('SELECT q, a FROM nodes').fetchall()
    if nodes:
        for n in nodes[::-1][:10]:
            with st.expander(f"SCAN: {n[0]}"):
                st.write(n[1])
    else:
        st.markdown("<div class='omni-card'>Empty Archive. Awaiting Input.</div>", unsafe_allow_html=True)

elif st.session_state.page == "NEXUS":
    st.markdown("<div class='omni-card'><h2>📐 MATH NEXUS</h2></div>", unsafe_allow_html=True)
    with st.container():
        math_q = st.chat_input("Enter equation...")
        if math_q:
            st.markdown(f"<div class='omni-card'>Resolving: {math_q}...</div>", unsafe_allow_html=True)

elif st.session_state.page == "PHOTO":
    st.markdown("<div class='omni-card'><h2>🖼️ PHOTO MANIFESTATION</h2></div>", unsafe_allow_html=True)
    prompt = st.text_input("Describe the vision...")
    if st.button("MANIFEST"):
        st.info("Manifesting...")

# Ticker Footer
st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background: #00FF41; color: black; font-weight: bold; padding: 5px; text-align: center; z-index: 1000;">
        SINGULARITY STATUS: 100% // DATA RAIN: STABLE // ARCHITECT AUTHORIZED
    </div>
""", unsafe_allow_html=True)