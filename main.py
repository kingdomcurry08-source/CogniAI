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

# --- 1. THE HYPER-VISUAL ENGINE (GOD-TIER UI) ---
st.set_page_config(page_title="CogniAI | Existence", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;500&family=Space+Grotesk:wght@300;700&display=swap');

    .stApp {
        background: #000000;
        background-image: radial-gradient(circle at 50% 50%, #002211 0%, #000000 80%);
        color: #00FF41;
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Landing Page Styling */
    .hero-section {
        text-align: center;
        padding: 100px 20px;
        background: rgba(0, 255, 65, 0.02);
        border-radius: 30px;
        margin-bottom: 50px;
    }

    .feature-card {
        background: rgba(0, 15, 5, 0.9);
        border: 1px solid #00FF41;
        padding: 30px;
        border-radius: 15px;
        margin: 20px 0;
        transition: 0.3s;
    }
    .feature-card:hover { transform: translateY(-10px); box-shadow: 0 0 30px #00FF41; }

    /* 3D Spinning Photo Cube */
    .cube-container { perspective: 1000px; width: 300px; height: 300px; margin: 50px auto; }
    .spinning-photo {
        width: 100%; height: 100%; position: relative;
        transform-style: preserve-3d; animation: spin 10s infinite linear;
        border: 2px solid #00FF41; box-shadow: 0 0 50px #00FF41; border-radius: 20px;
    }
    @keyframes spin { from { transform: rotateY(0deg); } to { transform: rotateY(360deg); } }

    .glitch {
        font-size: 60px; font-weight: bold; text-transform: uppercase;
        text-shadow: 0.05em 0 0 #00fffc, -0.03em -0.04em 0 #fc00ff;
        animation: glitch 1s infinite;
    }
    @keyframes glitch {
        0% { transform: translate(0); }
        20% { transform: translate(-2px, 2px); }
        40% { transform: translate(-2px, -2px); }
        60% { transform: translate(2px, 2px); }
        80% { transform: translate(2px, -2px); }
        100% { transform: translate(0); }
    }
    </style>
    """, unsafe_allow_html=True)


# --- 2. DATA ARCHITECTURE ---
def init_db():
    conn = sqlite3.connect('cogniai_v13.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS profile (id INT PRIMARY KEY, xp INT, lvl INT)')
    conn.execute('CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY, q TEXT, a TEXT)')
    if not conn.execute('SELECT * FROM profile WHERE id=1').fetchone():
        conn.execute('INSERT INTO profile VALUES (1, 0, 1)')
    conn.commit()
    return conn


db = init_db()


# --- 3. RECURSIVE DEEP SYNC ---
def deep_sync(text):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    chunks = [text[i:i + 6000] for i in range(0, len(text), 6000)]
    with st.status("🧬 INITIATING NEURAL HARVEST...", expanded=True) as status:
        for i, chunk in enumerate(chunks):
            res = client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": "Extract 15+ cards. JSON: {'cards':[{'q':'','a':''}]}"},
                          {"role": "user", "content": chunk}]
            )
            data = json.loads(res.choices[0].message.content)
            for c in data['cards']:
                db.execute('INSERT INTO nodes (q, a) VALUES (?,?)', (c['q'], c['a']))
            db.commit()
            st.write(f"Harvested Block {i + 1}/{len(chunks)}")
        status.update(label="SINGULARITY COMPLETE", state="complete")


# --- 4. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "HOME"
st.markdown("<div style='text-align:center;'><h1 class='glitch'>COGNIAI</h1></div>", unsafe_allow_html=True)

nav = st.columns(4)
menu = ["HOME", "STUDY LAB", "MATH NEXUS", "AI PHOTO GENERATOR"]
for i, x in enumerate(menu):
    if nav[i].button(x, use_container_width=True):
        st.session_state.page = x
        st.rerun()

# --- 5. MODULES ---

if st.session_state.page == "HOME":
    # Cinematic Hero Section
    st.markdown("""
        <div class="hero-section">
            <h2 style='font-size: 40px;'>The Future of Intelligence.</h2>
            <p style='font-size: 20px; opacity: 0.7;'>Scroll to explore the Singularity.</p>
        </div>
    """, unsafe_allow_html=True)

    # Feature 1: Deep Memory
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
            <div class="feature-card">
                <h3>🧠 Recursive Neural Ingest</h3>
                <p>CogniAI doesn't just read; it synthesizes. Upload 12, 50, or 100 pages. 
                The system breaks data into 'Neural Blocks', ensuring zero information loss 
                and maximum recall accuracy.</p>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.image("https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=800")

    # Feature 2: Visual Mastery
    c3, c4 = st.columns(2)
    with c3:
        st.image("https://images.unsplash.com/photo-1620712943543-bcc4628c7185?auto=format&fit=crop&q=80&w=800")
    with c4:
        st.markdown("""
            <div class="feature-card">
                <h3>🖼️ AI Photo Generator</h3>
                <p>Convert abstract concepts into 3D spinning visual manifestations. 
                Using DALL-E 3 technology, CogniAI visualizes history, biology, and 
                physics in a high-fidelity 3D workspace.</p>
            </div>
        """, unsafe_allow_html=True)

    # Feature 3: Math Nexus
    st.markdown("""
        <div class="feature-card" style='text-align:center;'>
            <h3>📐 The Math Nexus</h3>
            <p>From calculus to quantum mechanics, the Nexus resolves complex equations 
            with step-by-step logic, turning the impossible into the understandable.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br><h2 style='text-align:center;'>Ready to begin?</h2>", unsafe_allow_html=True)
    if st.button("ENTER STUDY LAB", use_container_width=True):
        st.session_state.page = "STUDY LAB"
        st.rerun()

elif st.session_state.page == "STUDY LAB":
    l, r = st.columns([1, 2])
    with l:
        st.markdown("<div class='omni-panel'><h3>DATA INGEST</h3>", unsafe_allow_html=True)
        up = st.file_uploader("Upload 12+ Page PDF")
        if up and st.button("INITIATE SYNC"):
            with pdfplumber.open(up) as pdf:
                raw = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
                deep_sync(raw)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with r:
        nodes = db.execute('SELECT q, a FROM nodes').fetchall()
        st.subheader(f"Total Neural Nodes: {len(nodes)}")
        for n in nodes[::-1][:15]:
            with st.expander(f"SCAN: {n[0]}"): st.write(n[1])

elif st.session_state.page == "MATH NEXUS":
    st.markdown("<div class='omni-panel'><h3>SOLVE SYSTEM</h3>", unsafe_allow_html=True)
    q = st.chat_input("Input equation...")
    if q:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": q}])
        st.write(res.choices[0].message.content)

elif st.session_state.page == "AI PHOTO GENERATOR":
    st.markdown("<div class='omni-panel'><h3>MANIFEST VISUALS</h3>", unsafe_allow_html=True)
    p = st.text_input("Describe the vision...")
    if st.button("GENERATE"):
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        img = client.images.generate(model="dall-e-3", prompt=p)
        url = img.data[0].url
        st.markdown(
            f'<div class="cube-container"><div class="spinning-photo"><img src="{url}" style="width:100%; border-radius:20px;"></div></div>',
            unsafe_allow_html=True)