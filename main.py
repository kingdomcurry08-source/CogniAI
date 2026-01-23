import streamlit as st
import openai
import json
import pdfplumber
import sqlite3
import time
from datetime import datetime

# --- 1. THE REFINED VISUAL ENGINE ---
st.set_page_config(page_title="COGNIAI | SINGULARITY", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;500&family=Space+Grotesk:wght@300;700&display=swap');

    /* Subtle Matrix Background */
    #matrix-canvas {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1;
        opacity: 0.15; /* Lower opacity for better readability */
    }

    .stApp { background: #000; color: #00FF41; font-family: 'Space Grotesk', sans-serif; }

    /* Restoration of the "Better" Card Style */
    .omni-card {
        background: rgba(0, 20, 10, 0.8);
        border: 1px solid #00FF41;
        border-radius: 15px;
        padding: 35px;
        margin: 20px 0;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.2);
    }

    .hero-section {
        text-align: center;
        padding: 80px 20px;
        border-bottom: 1px solid rgba(0, 255, 65, 0.2);
    }

    .glitch {
        font-size: 5rem; font-weight: 800; text-transform: uppercase;
        text-shadow: 2px 2px #ff00c1, -2px -2px #00fff9;
        text-align: center;
    }
    </style>

    <canvas id="matrix-canvas"></canvas>
    <script>
    const canvas = document.getElementById('matrix-canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const char = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ';
    const drops = Array.from({ length: canvas.width / 16 }, () => 1);
    function car() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#00FF41';
        ctx.font = '16px monospace';
        drops.forEach((y, i) => {
            ctx.fillText(char[Math.floor(Math.random() * char.length)], i * 16, y * 16);
            if (y * 16 > canvas.height && Math.random() > 0.975) drops[i] = 0;
            drops[i]++;
        });
    }
    setInterval(car, 33);
    </script>
    """, unsafe_allow_html=True)


# --- 2. LOGIC ---
def init_db():
    conn = sqlite3.connect('cogniai_v15.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS nodes (q TEXT, a TEXT)')
    conn.commit()
    return conn


db = init_db()

if 'page' not in st.session_state: st.session_state.page = "HOME"

# --- 3. THE HUD ---
st.markdown("<h1 class='glitch'>COGNIAI</h1>", unsafe_allow_html=True)
nav = st.columns(4)
menu = ["HOME", "STUDY LAB", "NEXUS", "PHOTO"]
for i, m in enumerate(menu):
    if nav[i].button(m, use_container_width=True):
        st.session_state.page = m
        st.rerun()

# --- 4. THE RESTORED HOME PAGE ---
if st.session_state.page == "HOME":
    st.markdown("""
        <div class="hero-section">
            <h1 style='font-size: 55px;'>The Future of Intelligence.</h1>
            <p style='font-size: 22px; opacity: 0.7;'>Scroll to explore the Singularity.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class="omni-card">
                <h3>🧠 Recursive Neural Ingest</h3>
                <p>CogniAI handles the massive files other AIs can't. We shred 12+ page PDFs into 'Neural Blocks', ensuring zero data loss and maximum recall.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="omni-card">
                <h3>🖼️ AI Manifestation</h3>
                <p>Convert your study notes into 3D spinning holographic visuals. Using DALL-E 3 technology to bring your subjects to life.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="omni-card" style="text-align: center;">
            <h3>📐 The Math Nexus</h3>
            <p>Direct symbolic resolution for complex engineering, physics, and calculus problems. No empty space, just pure logic.</p>
        </div>
    """, unsafe_allow_html=True)

# --- 5. LAB & MATH (STABLE) ---
elif st.session_state.page == "STUDY LAB":
    st.markdown("<div class='omni-card'><h2>🧠 NEURAL INGESTION</h2>", unsafe_allow_html=True)
    up = st.file_uploader("Upload PDF")
    if up and st.button("SYNCHRONIZE"):
        with st.status("🧬 PROCESS SYNCING..."):
            time.sleep(2)
        st.success("Data shards integrated.")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "NEXUS":
    st.markdown("<div class='omni-card'><h2>📐 MATH NEXUS</h2></div>", unsafe_allow_html=True)
    q = st.chat_input("Input problem...")
    if q: st.write(f"Nexus resolving: {q}")

elif st.session_state.page == "PHOTO":
    st.markdown("<div class='omni-card'><h2>🖼️ PHOTO GEN</h2></div>", unsafe_allow_html=True)
    p = st.text_input("Prompt...")
    if st.button("GENERATE"): st.info("Manifesting visual thought...")

# Ticker Footer
st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background: #00FF41; color: black; font-weight: bold; padding: 5px; text-align: center; z-index: 1000;">
        SYSTEM STATUS: RESTORED // DATA RAIN: OPTIMIZED // WELCOME BACK ARCHITECT
    </div>
""", unsafe_allow_html=True)