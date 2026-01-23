import streamlit as st
import openai
import json
import pdfplumber
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# --- 1. SYSTEM CORE & PERSISTENCE ---
st.set_page_config(page_title="CogniAI | God-Tier", page_icon="♾️", layout="wide")


def init_db():
    conn = sqlite3.connect('cogniai_omega.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS profile (id INT PRIMARY KEY, xp INT, lvl INT, rank TEXT)')
    conn.execute('''CREATE TABLE IF NOT EXISTS memory_nodes
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY,
                        q
                        TEXT,
                        a
                        TEXT,
                        easiness
                        REAL,
                        interval
                        INT,
                        next_review
                        DATE
                    )''')
    if not conn.execute('SELECT * FROM profile WHERE id=1').fetchone():
        conn.execute('INSERT INTO profile VALUES (1, 0, 1, "NEOPHYTE")')
    conn.commit()
    return conn


db = init_db()

# --- 2. THE ULTIMATE UI (GOD MODE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;700&family=Fira+Code&display=swap');

    .stApp {
        background: #020202 !important;
        background-image: radial-gradient(circle at 20% 30%, rgba(0, 255, 65, 0.05) 0%, transparent 40%),
                          radial-gradient(circle at 80% 70%, rgba(0, 255, 65, 0.05) 0%, transparent 40%) !important;
        color: #00FF41 !important;
        font-family: 'Space Grotesk', sans-serif;
    }

    .omni-panel {
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #00FF41;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.2);
    }

    .stButton>button {
        background: transparent !important;
        color: #00FF41 !important;
        border: 1px solid #00FF41 !important;
        transition: 0.3s;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .stButton>button:hover {
        background: #00FF41 !important;
        color: black !important;
        box-shadow: 0 0 40px #00FF41;
    }
    </style>
    """, unsafe_allow_html=True)


# --- 3. RECURSIVE CHUNKING ENGINE (THE 12-PAGE FIX) ---
def deep_sync(text, creativity, velocity):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    model = "gpt-4o" if velocity == "Deep Logic" else "gpt-4o-mini"

    # Split into 6000 character chunks to avoid missing data
    chunks = [text[i:i + 6000] for i in range(0, len(text), 6000)]

    for i, chunk in enumerate(chunks):
        st.toast(f"Synchronizing Matrix Block {i + 1}...")
        response = client.chat.completions.create(
            model=model,
            temperature=creativity,
            response_format={"type": "json_object"},
            messages=[{"role": "system",
                       "content": "You are CogniAI. Generate 15+ flashcards and a detailed summary for this block. Return JSON: {'cards': [{'q':'','a':''}], 'summary': ''}"},
                      {"role": "user", "content": chunk}]
        )
        data = json.loads(response.choices[0].message.content)

        for card in data['cards']:
            db.execute('INSERT INTO memory_nodes (q, a, easiness, interval, next_review) VALUES (?,?,?,?,?)',
                       (card['q'], card['a'], 2.5, 0, datetime.now().date()))
        db.commit()


# --- 4. NAVIGATION & STATE ---
if 'page' not in st.session_state: st.session_state.page = "HOME"
xp, lvl, rank = db.execute('SELECT xp, lvl, rank FROM profile WHERE id=1').fetchone()

st.markdown("<h1 style='text-align:center; color:#00FF41; letter-spacing:15px;'>COGNIAI</h1>", unsafe_allow_html=True)
cols = st.columns(4)
nav = ["HOME", "STUDY LAB", "MATH NEXUS", "AI PHOTO GENERATOR"]
for i, item in enumerate(nav):
    if cols[i].button(item): st.session_state.page = item; st.rerun()


# --- 5. MODULES ---

def render_home():
    st.markdown(f"<div class='omni-panel'><h2>RANK: {rank} | LEVEL {lvl}</h2></div>", unsafe_allow_html=True)
    st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")


def render_lab():
    l, r = st.columns([1, 2])
    with l:
        st.markdown("<div class='omni-panel'><h3>DATA INGEST</h3>", unsafe_allow_html=True)
        creativity = st.slider("Neural Entropy", 0.0, 1.0, 0.7)
        velocity = st.select_slider("Velocity", options=["Deep Logic", "Fast Velocity"])
        src = st.selectbox("Source", ["PDF", "Web URL", "Text Paste"])

        raw_data = ""
        if src == "PDF":
            up = st.file_uploader("Upload Notes")
            if up:
                with pdfplumber.open(up) as pdf: raw_data = "\n".join(
                    [p.extract_text() for p in pdf.pages if p.extract_text()])
        elif src == "Web URL":
            url = st.text_input("URL")
            if url: raw_data = BeautifulSoup(requests.get(url).text, 'html.parser').get_text()
        else:
            raw_data = st.text_area("Paste", height=300)

        if st.button("SYNCHRONIZE") and raw_data:
            deep_sync(raw_data, creativity, velocity)
            st.success("Matrix Updated.")
        st.markdown("</div>", unsafe_allow_html=True)

    with r:
        due = db.execute('SELECT id, q, a FROM memory_nodes WHERE next_review <= ?',
                         (datetime.now().date(),)).fetchall()
        st.markdown(f"<div class='omni-panel'><h3>RECALL NODES: {len(due)}</h3>", unsafe_allow_html=True)
        for node in due[:10]:  # Show 10 at a time
            with st.expander(f"SCAN: {node[1]}"):
                st.write(node[2])
        st.markdown("</div>", unsafe_allow_html=True)


def render_math():
    st.markdown("<div class='omni-panel'><h3>MATH NEXUS</h3>", unsafe_allow_html=True)
    q = st.chat_input("Enter problem...")
    if q:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": q}])
        st.write(res.choices[0].message.content)
    st.markdown("</div>", unsafe_allow_html=True)


def render_photo():
    st.markdown("<div class='omni-panel'><h3>AI PHOTO GENERATOR</h3>", unsafe_allow_html=True)
    p = st.text_input("Manifest Vision...")
    if st.button("MANIFEST"):
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        img = client.images.generate(model="dall-e-3", prompt=p)
        st.image(img.data[0].url)
    st.markdown("</div>", unsafe_allow_html=True)


# --- ROUTER ---
router = {"HOME": render_home, "STUDY LAB": render_lab, "MATH NEXUS": render_math, "AI PHOTO GENERATOR": render_photo}
router.get(st.session_state.page, render_home)()