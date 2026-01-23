import streamlit as st
import openai
import json
import pdfplumber
import sqlite3
import time
from datetime import datetime

# --- 1. THE HYPER-VOID ENGINE & VISUAL STABILIZATION ---
st.set_page_config(page_title="COGNIAI | SINGULARITY", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;500&family=Space+Grotesk:wght@300;700&display=swap');

    /* Background Layer: Matrix Rain */
    #matrix-canvas {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1;
        opacity: 0.18;
    }

    /* Content Layering */
    .stApp { background: #000; color: #00FF41; font-family: 'Space Grotesk', sans-serif; }

    .omni-card {
        background: rgba(0, 15, 5, 0.92);
        border: 1px solid #00FF41;
        border-radius: 15px;
        padding: 35px;
        margin: 20px 0;
        box-shadow: 0 0 25px rgba(0, 255, 65, 0.3);
        position: relative;
        z-index: 10;
    }

    /* Hero Branding */
    .hero-section {
        text-align: center;
        padding: 60px 20px;
        border-bottom: 1px solid rgba(0, 255, 65, 0.2);
    }

    .glitch {
        font-size: 5.5rem; font-weight: 800; text-transform: uppercase;
        text-shadow: 3px 3px #ff00c1, -3px -3px #00fff9;
        letter-spacing: 12px;
        text-align: center;
    }

    /* 3D MANIFESTATION CHAMBER */
    .photo-chamber {
        display: flex; justify-content: center; align-items: center;
        perspective: 1200px; padding: 40px 0;
        z-index: 1000;
    }

    .spinning-cube {
        width: 380px; height: 380px;
        transform-style: preserve-3d;
        animation: rotate-cube 18s infinite linear;
        border: 4px solid #00FF41;
        box-shadow: 0 0 70px rgba(0, 255, 65, 0.6);
        border-radius: 20px;
    }

    @keyframes rotate-cube {
        from { transform: rotateY(0deg) rotateX(5deg); }
        to { transform: rotateY(360deg) rotateX(5deg); }
    }
    </style>

    <canvas id="matrix-canvas"></canvas>
    <script>
    const canvas = document.getElementById('matrix-canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const char = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ';
    const drops = Array.from({ length: Math.ceil(canvas.width / 16) }, () => 1);
    function rain() {
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
    setInterval(rain, 33);
    </script>
    """, unsafe_allow_html=True)


# --- 2. DB INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('cogniai_v15.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY AUTOINCREMENT, q TEXT, a TEXT)')
    conn.commit()
    return conn


db = init_db()

# --- 3. NAVIGATION HUD ---
if 'page' not in st.session_state: st.session_state.page = "HOME"

st.markdown("<h1 class='glitch'>COGNIAI</h1>", unsafe_allow_html=True)
nav = st.columns(4)
menu = ["HOME", "LAB", "NEXUS", "PHOTO"]
for i, m in enumerate(menu):
    if nav[i].button(m, use_container_width=True):
        st.session_state.page = m
        st.rerun()

# --- 4. MODULES ---

if st.session_state.page == "HOME":
    st.markdown("""
        <div class="hero-section">
            <h1 style='font-size: 50px; color: #00FF41;'>The Future of Intelligence.</h1>
            <p style='font-size: 22px; opacity: 0.8;'>Recursive neural processing for the modern architect.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class="omni-card">
                <h3>🧠 Recursive Neural Ingest</h3>
                <p>Engineered for massive datasets. Shred 12+ page PDFs into 'Neural Blocks' for zero-loss memory retention.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="omni-card">
                <h3>🖼️ AI Manifestation</h3>
                <p>Witness your data in 3D. Convert complex subjects into spinning holographic manifestations.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="omni-card" style="text-align: center;">
            <h3>📐 The Math Nexus</h3>
            <p>Direct symbolic logic resolution. No equation is too complex for the Singularity Core.</p>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "LAB":
    st.markdown("<div class='omni-card'><h2>🧠 NEURAL INGESTION LAB</h2>", unsafe_allow_html=True)
    up = st.file_uploader("Upload Intelligence PDF", type="pdf")
    if up and st.button("INITIATE DEEP SYNC", use_container_width=True):
        with st.status("🧬 PROCESS SYNCING..."):
            with pdfplumber.open(up) as pdf:
                # Add your 12-page recursive logic here
                time.sleep(2)
            st.success("Singularity Synced.")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "NEXUS":
    st.markdown("<div class='omni-card'><h2>📐 MATH NEXUS</h2></div>", unsafe_allow_html=True)
    with st.container():
        q = st.chat_input("Enter symbolic problem...")
        if q:
            st.markdown(f"<div class='omni-card'>Resolving logic gates for: {q}</div>", unsafe_allow_html=True)

elif st.session_state.page == "PHOTO":
    st.markdown("<div class='omni-card'><h2>🖼️ PHOTO MANIFESTATION</h2>", unsafe_allow_html=True)
    p = st.text_input("Enter visual prompt...")
    if st.button("EXECUTE", use_container_width=True):
        if p:
            with st.spinner("🌌 RENDERING..."):
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                res = client.images.generate(model="dall-e-3", prompt=p)
                url = res.data[0].url
                st.markdown(f"""
                    <div class="photo-chamber">
                        <div class="spinning-cube">
                            <img src="{url}" style="width:100%; height:100%; object-fit: cover; border-radius: 16px;">
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Ticker Footer
st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background: #00FF41; color: black; font-weight: bold; padding: 5px; text-align: center; z-index: 10000;">
        SINGULARITY STATUS: ACTIVE // ARCHITECT AUTHORIZED // NO EMPTY BYTES DETECTED
    </div>
""", unsafe_allow_html=True)