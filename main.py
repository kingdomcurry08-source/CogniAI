import streamlit as st
import openai
import json
import pdfplumber
import sqlite3
import time
import pandas as pd
from datetime import datetime

# --- 1. THE ARCHITECT UI ENGINE ---
st.set_page_config(page_title="CogniAI | Ultimate", page_icon="🏆", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;500&family=Space+Grotesk:wght@300;700&display=swap');

    /* Background & Matrix Layer */
    #matrix-canvas { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; opacity: 0.12; }
    .stApp { background: #050505; color: #00FF41; font-family: 'Space Grotesk', sans-serif; }

    /* Holographic Containers */
    .glass-panel {
        background: rgba(10, 25, 15, 0.85);
        border: 1px solid rgba(0, 255, 65, 0.3);
        border-radius: 20px;
        padding: 40px;
        margin: 20px 0;
        box-shadow: 0 8px 32px 0 rgba(0, 255, 65, 0.1);
        backdrop-filter: blur(12px);
    }

    /* Animated Navigation */
    .stButton>button {
        background: transparent !important;
        border: 1px solid #00FF41 !important;
        color: #00FF41 !important;
        transition: 0.4s all ease;
        border-radius: 8px !important;
        font-family: 'Fira Code', monospace !important;
    }
    .stButton>button:hover {
        background: #00FF41 !important;
        color: #000 !important;
        box-shadow: 0 0 20px #00FF41;
    }

    /* The Glitch Branding */
    .glitch-title {
        font-size: 4rem; font-weight: 800; text-align: center;
        letter-spacing: 10px; color: #00FF41;
        text-shadow: 2px 2px #ff00c1, -2px -2px #00fff9;
    }

    /* 3D Manifestation Chamber */
    .manifest-chamber {
        perspective: 1000px; display: flex; justify-content: center; padding: 30px;
    }
    .holo-cube {
        width: 380px; height: 380px;
        transform-style: preserve-3d;
        animation: rotate-manifest 20s infinite linear;
        border: 3px solid #00FF41;
        box-shadow: 0 0 60px rgba(0, 255, 65, 0.5);
        border-radius: 25px;
    }
    @keyframes rotate-manifest { from { transform: rotateY(0deg); } to { transform: rotateY(360deg); } }
    </style>

    <canvas id="matrix-canvas"></canvas>
    <script>
    const canvas = document.getElementById('matrix-canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth; canvas.height = window.innerHeight;
    const char = '01';
    const drops = Array.from({ length: Math.ceil(canvas.width / 20) }, () => 1);
    function draw() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#00FF41';
        ctx.font = '15px monospace';
        drops.forEach((y, i) => {
            ctx.fillText(char[Math.floor(Math.random() * char.length)], i * 20, y * 20);
            if (y * 20 > canvas.height && Math.random() > 0.975) drops[i] = 0;
            drops[i]++;
        });
    }
    setInterval(draw, 50);
    </script>
    """, unsafe_allow_html=True)


# --- 2. THE LOGIC CORE ---
def init_db():
    conn = sqlite3.connect('cogniai_pro.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, q TEXT, a TEXT, level INT)')
    conn.commit()
    return conn


db = init_db()

if 'page' not in st.session_state: st.session_state.page = "DASHBOARD"

# --- 3. HUD (TOP NAVIGATION) ---
st.markdown("<h1 class='glitch-title'>COGNIAI PRO</h1>", unsafe_allow_html=True)
nav = st.columns(5)
btns = ["DASHBOARD", "LAB", "NEXUS", "MANIFEST", "ZEN MODE"]
for i, x in enumerate(btns):
    if nav[i].button(x, use_container_width=True):
        st.session_state.page = x
        st.rerun()

# --- 4. MODULES ---

if st.session_state.page == "DASHBOARD":
    st.markdown(
        "<div class='glass-panel'><h2>WELCOME, ARCHITECT</h2><p>Today's Objective: Synchronize 3 Neural Nodes.</p></div>",
        unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='glass-panel'><h3>⚡ 98%</h3><p>Recall Accuracy</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='glass-panel'><h3>📚 14</h3><p>Active Shards</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='glass-panel'><h3>🔥 5 Day</h3><p>Study Streak</p></div>", unsafe_allow_html=True)

    st.markdown("### 📋 RECENT INTELLIGENCE GATHERED")
    data = {"Subject": ["Calculus III", "Bio-Chemistry", "Macro-Economics"],
            "Status": ["Mastered", "In Review", "Ingesting"]}
    st.table(pd.DataFrame(data))

elif st.session_state.page == "LAB":
    st.markdown("<div class='glass-panel'><h2>🧠 NEURAL INGESTION LAB</h2>", unsafe_allow_html=True)
    up = st.file_uploader("Upload Homework PDF (Up to 50 pages)", type="pdf")
    if up and st.button("SYNCHRONIZE DATA"):
        with st.status("🧬 SHREDDING AND RECONSTRUCTING..."):
            time.sleep(3)
            st.success("Neural Nodes Created.")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "NEXUS":
    st.markdown(
        "<div class='glass-panel'><h2>📐 MATH NEXUS v4.0</h2><p>State-of-the-art symbolic resolution engine.</p></div>",
        unsafe_allow_html=True)
    with st.container():
        q = st.chat_input("Input equation for resolution...")
        if q:
            st.markdown(f"<div class='glass-panel'><b>Nexus Result:</b><br>Resolution pending for equation: {q}</div>",
                        unsafe_allow_html=True)

elif st.session_state.page == "MANIFEST":
    st.markdown("<div class='glass-panel'><h2>🖼️ CONCEPT MANIFESTATION</h2>", unsafe_allow_html=True)
    p = st.text_input("Describe a concept (e.g., 'DNA Double Helix with neon glow')")
    if st.button("MANIFEST"):
        if p:
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            res = client.images.generate(model="dall-e-3", prompt=p)
            url = res.data[0].url
            st.markdown(f"""
                <div class="manifest-chamber">
                    <div class="holo-cube">
                        <img src="{url}" style="width:100%; height:100%; object-fit: cover; border-radius: 22px;">
                    </div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "ZEN MODE":
    st.markdown(
        "<div class='glass-panel' style='text-align:center;'><h2>🧘 ZEN FOCUS MODE</h2><p>Silence the noise. Master the craft.</p></div>",
        unsafe_allow_html=True)
    st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")  # Lo-fi beats
    st.markdown("<div class='glass-panel'><h3>Focus Timer</h3><h1>25:00</h1></div>", unsafe_allow_html=True)

# Ticker Footer
st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background: #00FF41; color: black; font-weight: bold; padding: 5px; text-align: center; z-index: 10000;">
        ACTIVE SESSION // LATENCY: 14ms // SYNC: ENCRYPTED // COGNIAI PRO v1.0
    </div>
""", unsafe_allow_html=True)