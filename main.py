import streamlit as st
import openai
import json
import pdfplumber
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random

# --- 1. THE HYPER-VISUAL ENGINE (3D SPINNER & MATRIX FX) ---
st.set_page_config(page_title="CogniAI | Hyper-Singularity", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;500&family=Space+Grotesk:wght@300;700&display=swap');

    /* Global Matrix Background */
    .stApp {
        background: #000000;
        background-image: radial-gradient(circle at 50% 50%, #002211 0%, #000000 80%);
        color: #00FF41;
        font-family: 'Space Grotesk', sans-serif;
        overflow-x: hidden;
    }

    /* Spinning 3D Photo Cube */
    .cube-container {
        perspective: 1000px;
        width: 300px;
        height: 300px;
        margin: 50px auto;
    }

    .spinning-photo {
        width: 100%;
        height: 100%;
        position: relative;
        transform-style: preserve-3d;
        animation: spin 10s infinite linear;
        border: 2px solid #00FF41;
        box-shadow: 0 0 50px #00FF41;
        border-radius: 20px;
    }

    @keyframes spin {
        from { transform: rotateY(0deg) rotateX(10deg); }
        to { transform: rotateY(360deg) rotateX(10deg); }
    }

    /* Glow Panels */
    .omni-panel {
        background: rgba(0, 15, 5, 0.9);
        border: 1px solid #00FF41;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
        backdrop-filter: blur(10px);
    }

    /* Glitch Text Effect */
    .glitch {
        font-size: 50px;
        font-weight: bold;
        text-transform: uppercase;
        position: relative;
        text-shadow: 0.05em 0 0 #00fffc, -0.03em -0.04em 0 #fc00ff, 0.025em 0.04em 0 #fffc00;
        animation: glitch 725ms infinite;
    }

    @keyframes glitch {
        0% { text-shadow: 0.05em 0 0 #00fffc, -0.03em -0.04em 0 #fc00ff, 0.025em 0.04em 0 #fffc00; }
        15% { text-shadow: 0.05em 0 0 #00fffc, -0.03em -0.04em 0 #fc00ff, 0.025em 0.04em 0 #fffc00; }
        16% { text-shadow: -0.05em -0.025em 0 #00fffc, 0.025em 0.035em 0 #fc00ff, -0.05em -0.05em 0 #fffc00; }
        /* Add more steps for extra glitchiness */
        100% { text-shadow: -0.025em 0 0 #00fffc, -0.025em -0.025em 0 #fc00ff, -0.025em -0.05em 0 #fffc00; }
    }
    </style>
    """, unsafe_allow_html=True)


# --- 2. DB & LOGIC (STABLE) ---
def init_db():
    conn = sqlite3.connect('cogniai_hyper.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS profile (id INT PRIMARY KEY, xp INT, lvl INT)')
    conn.execute('CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY, q TEXT, a TEXT, next_review DATE)')
    if not conn.execute('SELECT * FROM profile WHERE id=1').fetchone():
        conn.execute('INSERT INTO profile VALUES (1, 0, 1)')
    conn.commit()
    return conn


db = init_db()


# --- 3. RECURSIVE DEEP SYNC (THE 12-PAGE BEAST) ---
def deep_sync(text):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    chunks = [text[i:i + 6000] for i in range(0, len(text), 6000)]
    with st.status("🌌 BREACHING DATA HORIZON...", expanded=True) as status:
        for i, chunk in enumerate(chunks):
            res = client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": "Generate 15+ cards. JSON: {'cards':[{'q':'','a':''}]}"},
                          {"role": "user", "content": chunk}]
            )
            data = json.loads(res.choices[0].message.content)
            for c in data['cards']:
                db.execute('INSERT INTO nodes (q, a, next_review) VALUES (?,?,?)',
                           (c['q'], c['a'], datetime.now().date()))
            db.commit()
            st.write(f"Node Block {i + 1} Integrated.")
        status.update(label="SINGULARITY ACHIEVED", state="complete")


# --- 4. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "HOME"
st.markdown("<div style='text-align:center;'><h1 class='glitch'>COGNIAI</h1></div>", unsafe_allow_html=True)

nav = st.columns(4)
menu = ["HOME", "STUDY LAB", "MATH NEXUS", "AI PHOTO GENERATOR"]
for i, x in enumerate(menu):
    if nav[i].button(x): st.session_state.page = x; st.rerun()

# --- 5. MODULES ---

if st.session_state.page == "HOME":
    st.markdown(
        "<div class='omni-panel'><h3>NEURAL CORE: STANDBY</h3><p>Upload 12+ pages to ignite the engine.</p></div>",
        unsafe_allow_html=True)
    st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")

elif st.session_state.page == "STUDY LAB":
    l, r = st.columns([1, 2])
    with l:
        st.markdown("<div class='omni-panel'><h3>INGEST DATA</h3>", unsafe_allow_html=True)
        up = st.file_uploader("Upload PDF")
        if up and st.button("SYNCHRONIZE"):
            with pdfplumber.open(up) as pdf:
                raw = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
                deep_sync(raw)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with r:
        nodes = db.execute('SELECT q, a FROM nodes').fetchall()
        for n in nodes[::-1][:10]:
            with st.expander(f"SCAN: {n[0]}"): st.write(n[1])

elif st.session_state.page == "MATH NEXUS":
    st.markdown("<div class='omni-panel'><h3>SOLVE SYSTEM</h3>", unsafe_allow_html=True)
    q = st.chat_input("Enter problem...")
    if q:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": q}])
        st.write(res.choices[0].message.content)

elif st.session_state.page == "AI PHOTO GENERATOR":
    st.markdown("<div class='omni-panel'><h3>MANIFEST VISUALS</h3>", unsafe_allow_html=True)
    p = st.text_input("Enter prompt...")
    if st.button("GENERATE"):
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        img = client.images.generate(model="dall-e-3", prompt=p)
        url = img.data[0].url

        # THE CRAZY SPINNING PART
        st.markdown(f"""
            <div class="cube-container">
                <div class="spinning-photo">
                    <img src="{url}" style="width:100%; border-radius:20px;">
                </div>
            </div>
        """, unsafe_allow_html=True)