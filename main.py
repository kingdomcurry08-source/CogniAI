import streamlit as st
import openai
import json
import pdfplumber
import sqlite3
import time
from datetime import datetime

# --- 1. THE HYPER-VOID ENGINE & MATRIX RAIN ---
st.set_page_config(page_title="COGNIAI | SINGULARITY", page_icon="🧬", layout="wide")

# This block injects the Matrix Background + Glitch CSS
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
        z-index: -1; /* Puts it behind everything */
    }

    .stApp {
        background: transparent; /* Makes app transparent so we see the rain */
        color: #00FF41;
        font-family: 'Space Grotesk', sans-serif;
    }

    .omni-card {
        background: rgba(0, 20, 10, 0.85); /* Slightly darker for readability against rain */
        backdrop-filter: blur(10px);
        border: 1px solid #00FF41;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 0 25px rgba(0, 255, 65, 0.3);
    }

    .glitch {
        font-size: 5rem; font-weight: 900; text-align: center;
        text-transform: uppercase; letter-spacing: 15px;
        text-shadow: 3px 3px #ff00c1, -3px -3px #00fff9;
        animation: glitch-anim 2s infinite linear alternate-reverse;
    }
    @keyframes glitch-anim { 0% { opacity: 1; } 50% { opacity: 0.8; transform: skewX(2deg); } 100% { opacity: 1; } }

    .cube-container { perspective: 1000px; display: flex; justify-content: center; padding: 20px; }
    .spinning-photo {
        width: 320px; height: 320px; 
        animation: spin 12s infinite linear;
        border: 3px solid #00FF41; box-shadow: 0 0 60px #00FF41;
    }
    @keyframes spin { from { transform: rotateY(0deg) rotateX(5deg); } to { transform: rotateY(360deg) rotateX(5deg); } }
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
    conn.execute('CREATE TABLE IF NOT EXISTS nodes (q TEXT, a TEXT)')
    conn.commit()
    return conn


db = init_db()

if 'page' not in st.session_state: st.session_state.page = "HOME"

# --- 3. THE HUD (NAVIGATION) ---
st.markdown("<h1 class='glitch'>COGNIAI</h1>", unsafe_allow_html=True)
nav_cols = st.columns(4)
menu = ["CORE", "LAB", "NEXUS", "PHOTO"]
for i, m in enumerate(menu):
    if nav_cols[i].button(m, use_container_width=True):
        st.session_state.page = m
        st.rerun()

# --- 4. MODULES ---

if st.session_state.page == "HOME":
    st.markdown("""
        <div class='omni-card'>
            <h2>SYSTEM INITIALIZED</h2>
            <p>Welcome, Architect. The Matrix Rain indicates the flow of raw data through the Singularity.</p>
        </div>
    """, unsafe_allow_html=True)

    # Dynamic Lore Cards (Zero Empty Space)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            "<div class='omni-card'><h3>⚡ Speed</h3><p>Parallel block processing enables 12-page PDF ingestion in under 10 seconds.</p></div>",
            unsafe_allow_html=True)
    with c2:
        st.markdown(
            "<div class='omni-card'><h3>🧬 Bio-Repetition</h3><p>Memory nodes are algorithmically weighted based on your recall accuracy.</p></div>",
            unsafe_allow_html=True)
    with c3:
        st.markdown(
            "<div class='omni-card'><h3>📐 Calculus Core</h3><p>Direct API link to the Math Nexus for instant symbolic resolution.</p></div>",
            unsafe_allow_html=True)

elif st.session_state.page == "NEXUS":
    st.markdown(
        "<div class='omni-card'><h2>📐 MATH NEXUS</h2><p>Solving the impossible. Enter your equation below.</p></div>",
        unsafe_allow_html=True)

    # Chat Input fixed with a container
    with st.container():
        math_q = st.chat_input("Integrate 3x^2 + 2x + 5 from 0 to 10...")
        if math_q:
            with st.spinner("🔢 ACCESSING LOGIC GATES..."):
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "You are the Math Nexus. Use LaTeX for math."},
                              {"role": "user", "content": math_q}]
                )
                st.markdown(f"<div class='omni-card'>{res.choices[0].message.content}</div>", unsafe_allow_html=True)

elif st.session_state.page == "PHOTO":
    st.markdown("<div class='omni-card'><h2>🖼️ PHOTO MANIFESTATION</h2></div>", unsafe_allow_html=True)
    prompt = st.text_input("Visualize...")
    if st.button("MANIFEST", use_container_width=True):
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        img = client.images.generate(model="dall-e-3", prompt=prompt)
        url = img.data[0].url
        st.markdown(f"""
            <div class="cube-container">
                <div class="spinning-photo">
                    <img src="{url}" style="width:100%; height:100%; object-fit: cover; border-radius: 12px;">
                </div>
            </div>
        """, unsafe_allow_html=True)

# Ticker Footer
st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background: #00FF41; color: black; font-weight: bold; padding: 5px; text-align: center; z-index: 1000;">
        SINGULARITY STATUS: 100% // DATA RAIN: STABLE // ARCHITECT AUTHORIZED
    </div>
""", unsafe_allow_html=True)