import streamlit as st
import openai
import json
import pdfplumber
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- 1. CYBER-CORE UI ARCHITECTURE ---
st.set_page_config(page_title="CogniAI | Omni-Singularity", page_icon="♾️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;500&family=Space+Grotesk:wght@300;700&display=swap');

    .stApp {
        background: #000000;
        background-image: radial-gradient(circle at 50% 0%, #00331a 0%, #000000 70%);
        color: #00FF41;
        font-family: 'Space Grotesk', sans-serif;
    }

    .omni-panel {
        background: rgba(0, 20, 10, 0.8);
        border: 1px solid #00FF41;
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.1);
    }

    .stButton>button {
        background: transparent !important;
        color: #00FF41 !important;
        border: 1px solid #00FF41 !important;
        border-radius: 5px !important;
        font-family: 'Fira Code', monospace !important;
        transition: 0.3s all;
        width: 100%;
    }

    .stButton>button:hover {
        background: #00FF41 !important;
        color: #000 !important;
        box-shadow: 0 0 30px #00FF41;
    }

    .fira { font-family: 'Fira Code', monospace; color: #00FF41; }
    [data-testid="stHeader"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


# --- 2. PERSISTENCE ENGINE ---
def init_db():
    conn = sqlite3.connect('cogniai_omni.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS stats (id INT PRIMARY KEY, xp INT, lvl INT, rank TEXT)')
    if not conn.execute('SELECT * FROM stats WHERE id=1').fetchone():
        conn.execute('INSERT INTO stats VALUES (1, 0, 1, "INITIATE")')
    conn.commit()
    return conn


# --- 3. HIGH-CAPACITY SYNTHESIS (RECURSIVE CHUNKING) ---
def recursive_synthesis(text, creativity, velocity):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    model = "gpt-4o" if velocity == "Deep Logic" else "gpt-4o-mini"

    # Break text into blocks to ensure NO content is missed (7000 chars each)
    chunks = [text[i:i + 7000] for i in range(0, len(text), 7000)]
    compiled = {"cards": [], "quiz": [], "map": "graph TD\n"}

    prog_bar = st.progress(0)
    for i, chunk in enumerate(chunks):
        st.toast(f"Synchronizing Matrix Block {i + 1}...")
        try:
            res = client.chat.completions.create(
                model=model,
                temperature=creativity,
                response_format={"type": "json_object"},
                messages=[{
                    "role": "system",
                    "content": "You are CogniAI. Generate 15+ detailed flashcards and 5 exam questions for THIS CHUNK. Return JSON."
                }, {"role": "user", "content": chunk}]
            )
            batch = json.loads(res.choices[0].message.content)
            compiled["cards"].extend(batch.get("cards", []))
            compiled["quiz"].extend(batch.get("quiz", []))
            if i == 0: compiled["vision"] = batch.get("vision", "")
        except:
            continue
        prog_bar.progress((i + 1) / len(chunks))

    return compiled


# --- 4. NAVIGATION & STATE ---
db = init_db()
if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'memory' not in st.session_state: st.session_state.memory = None
st.session_state.xp, st.session_state.lvl, st.session_state.rank = db.execute(
    'SELECT xp, lvl, rank FROM stats WHERE id=1').fetchone()

st.markdown("<h1 style='text-align:center; color:#00FF41; letter-spacing:10px;'>COGNIAI</h1>", unsafe_allow_html=True)
nav = st.columns(4)
nav_items = ["HOME", "STUDY LAB", "MATH NEXUS", "VISION"]
for i, item in enumerate(nav_items):
    if nav[i].button(item, use_container_width=True):
        st.session_state.page = item
        st.rerun()


# --- 5. PAGE MODULES ---

def render_home():
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(
            f"<div class='omni-panel'><h2>NEURAL STATUS: {st.session_state.rank}</h2><p>LEVEL: {st.session_state.lvl}</p>",
            unsafe_allow_html=True)
        st.progress(st.session_state.xp / 100)
        st.markdown("</div>", unsafe_allow_html=True)
        st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")
    with c2:
        st.markdown(
            "<div class='omni-panel'><h3>System Logs</h3><p class='fira'>- Context: Active<br>- Recursive Ingest: Ready<br>- Velocity: Swappable</p></div>",
            unsafe_allow_html=True)
        if st.button("☣️ PURGE CACHE"):
            st.session_state.memory = None
            st.rerun()


def render_study_lab():
    l, r = st.columns([1, 2])
    with l:
        st.markdown("<div class='omni-panel'><h3>Ingestion Engine</h3>", unsafe_allow_html=True)
        creativity = st.slider("Neural Entropy", 0.0, 1.0, 0.7)
        velocity = st.radio("Processor Core", ["Deep Logic", "Velocity (Fast)"])

        mode = st.selectbox("Input Source", ["PDF Upload", "Web URL", "Raw Paste"])
        source_data = ""

        if mode == "PDF Upload":
            up = st.file_uploader("Upload Notes", type=['pdf'])
            if up:
                with pdfplumber.open(up) as pdf:
                    source_data = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        elif mode == "Web URL":
            url = st.text_input("Enter URL")
            if url:
                res = requests.get(url)
                source_data = BeautifulSoup(res.text, 'html.parser').get_text()
        elif mode == "Raw Paste":
            source_data = st.text_area("Paste Content", height=200)

        if st.button("EXECUTE SYNC") and source_data:
            st.session_state.memory = recursive_synthesis(source_data, creativity, velocity)
            st.session_state.xp += 35
            if st.session_state.xp >= 100: st.session_state.lvl += 1; st.session_state.xp = 0
            db.execute('UPDATE stats SET xp=?, lvl=? WHERE id=1', (st.session_state.xp, st.session_state.lvl))
            db.commit()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with r:
        if st.session_state.memory:
            st.markdown("<div class='omni-panel'>", unsafe_allow_html=True)
            t1, t2 = st.tabs([f"NODES ({len(st.session_state.memory['cards'])})", "PRACTICE EXAM"])
            with t1:
                for c in st.session_state.memory['cards']:
                    with st.expander(f"SCAN: {c.get('q')}"): st.write(c.get('a'))
            with t2:
                for i, q in enumerate(st.session_state.memory['quiz']):
                    st.write(f"**{i + 1}. {q.get('q')}**")
                    st.radio("Analyze:", q.get('o', []), key=f"q_{i}")
            st.markdown("</div>", unsafe_allow_html=True)


def render_math():
    st.markdown("<div class='omni-panel'><h3>MATH NEXUS</h3>", unsafe_allow_html=True)
    q = st.chat_input("Enter complex equation...")
    if q:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": q}])
        st.markdown(f"<div class='fira'>{res.choices[0].message.content}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_vision():
    st.markdown("<div class='omni-panel'><h3>VISION STUDIO</h3>", unsafe_allow_html=True)
    with st.form("vision"):
        p = st.text_input("Manifest latent vision...")
        if st.form_submit_button("MANIFEST"):
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            img = client.images.generate(model="dall-e-3", prompt=p)
            st.image(img.data[0].url)
    st.markdown("</div>", unsafe_allow_html=True)


# --- ROUTER ---
pages = {"HOME": render_home, "STUDY LAB": render_study_lab, "MATH NEXUS": render_math, "VISION": render_vision}
pages.get(st.session_state.page, render_home)()