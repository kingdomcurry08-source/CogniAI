import streamlit as st
import openai
import json
import pdfplumber
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import random

# --- 1. INTERFACE & ANIMATION ---
st.set_page_config(page_title="CogniAI | Omni-Singularity", page_icon="♾️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;500&family=Space+Grotesk:wght@300;700&display=swap');

    .stApp {
        background: #000000;
        background-image: radial-gradient(circle at 50% 0%, #002211 0%, #000000 70%);
        color: #00FF41;
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Neural Pulse Animation for Cards */
    @keyframes pulse { 0% { border-color: #00FF41; } 50% { border-color: #004411; } 100% { border-color: #00FF41; } }

    .omni-panel {
        background: rgba(0, 15, 5, 0.85);
        border: 1px solid #00FF41;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        animation: pulse 4s infinite ease-in-out;
    }

    .stButton>button {
        background: transparent !important;
        color: #00FF41 !important;
        border: 1px solid #00FF41 !important;
        border-radius: 4px !important;
        font-family: 'Fira Code', monospace !important;
        transition: 0.3s all;
        width: 100%;
    }

    .stButton>button:hover {
        background: #00FF41 !important;
        color: #000 !important;
        box-shadow: 0 0 25px #00FF41;
    }

    .fira { font-family: 'Fira Code', monospace; color: #00FF41; }
    [data-testid="stHeader"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


# --- 2. PERSISTENCE LAYER (SM-2 & STATS) ---
def init_db():
    conn = sqlite3.connect('cogniai_v12.db', check_same_thread=False)
    # Master User Table
    conn.execute('CREATE TABLE IF NOT EXISTS profile (id INT PRIMARY KEY, xp INT, lvl INT, rank TEXT)')
    # Spaced Repetition Nodes
    conn.execute('''CREATE TABLE IF NOT EXISTS nodes
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
        conn.execute('INSERT INTO profile VALUES (1, 0, 1, "INITIATE")')
    conn.commit()
    return conn


db = init_db()


# --- 3. CORE LOGIC: SM-2 ALGORITHM ---
def update_node(node_id, quality):
    row = db.execute('SELECT easiness, interval FROM nodes WHERE id=?', (node_id,)).fetchone()
    e, i = row
    if quality >= 3:
        i = 1 if i == 0 else (6 if i == 1 else round(i * e))
        e = e + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    else:
        i = 1;
        e = 1.3
    e = max(1.3, e)
    next_date = (datetime.now() + timedelta(days=i)).date()
    db.execute('UPDATE nodes SET easiness=?, interval=?, next_review=? WHERE id=?', (e, i, next_date, node_id))
    db.commit()


# --- 4. RECURSIVE HEAVY-DUTY SYNTHESIS ---
def recursive_sync(text):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    chunks = [text[i:i + 6000] for i in range(0, len(text), 6000)]

    with st.status("🧠 Processing Neural Blocks...", expanded=True) as status:
        for i, chunk in enumerate(chunks):
            st.write(f"Decoding Block {i + 1}...")
            res = client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "Extract 15+ complex flashcards. JSON: {'cards':[{'q':'','a':''}]}"},
                    {"role": "user", "content": chunk}]
            )
            data = json.loads(res.choices[0].message.content)
            for c in data['cards']:
                db.execute('INSERT INTO nodes (q, a, easiness, interval, next_review) VALUES (?,?,?,?,?)',
                           (c['q'], c['a'], 2.5, 0, datetime.now().date()))
            db.commit()
        status.update(label="Sync Complete!", state="complete")


# --- 5. THE TERMINAL HUD ---
if 'page' not in st.session_state: st.session_state.page = "HOME"
xp, lvl, rank = db.execute('SELECT xp, lvl, rank FROM profile WHERE id=1').fetchone()

with st.sidebar:
    st.markdown(f"<div class='omni-panel'><h2 class='fira'>{rank}</h2><p>LVL {lvl} | XP {xp}/100</p></div>",
                unsafe_allow_html=True)
    st.progress(xp / 100)
    if st.button("☣️ PURGE MEMORY"):
        db.execute('DELETE FROM nodes');
        db.commit();
        st.rerun()

st.markdown("<h1 style='text-align:center; color:#00FF41; letter-spacing:10px;'>COGNIAI</h1>", unsafe_allow_html=True)
nav = st.columns(5)
btns = ["HOME", "STUDY LAB", "PRACTICE EXAM", "MATH NEXUS", "AI PHOTO GENERATOR"]
for i, x in enumerate(btns):
    if nav[i].button(x): st.session_state.page = x; st.rerun()

# --- 6. PAGE ROUTING ---

if st.session_state.page == "HOME":
    st.markdown(
        "<div class='omni-panel'><h3>SYSTEM: ONLINE</h3><p>Awaiting neural input. Access Study Lab to begin.</p></div>",
        unsafe_allow_html=True)
    st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")

elif st.session_state.page == "STUDY LAB":
    l, r = st.columns([1, 2])
    with l:
        st.markdown("<div class='omni-panel'><h3>INGESTION</h3>", unsafe_allow_html=True)
        src = st.selectbox("Source", ["PDF", "URL", "Text"])
        data = ""
        if src == "PDF":
            up = st.file_uploader("Upload Notes")
            if up:
                with pdfplumber.open(up) as pdf: data = "\n".join(
                    [p.extract_text() for p in pdf.pages if p.extract_text()])
        elif src == "URL":
            u = st.text_input("Link")
            if u: data = BeautifulSoup(requests.get(u).text, 'html.parser').get_text()
        else:
            data = st.text_area("Paste", height=300)

        if st.button("SYNCHRONIZE"):
            recursive_sync(data)
            db.execute('UPDATE profile SET xp = xp + 30 WHERE id=1');
            db.commit()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with r:
        st.markdown("<div class='omni-panel'><h3>RECALL NODES</h3>", unsafe_allow_html=True)
        nodes = db.execute('SELECT q, a FROM nodes').fetchall()
        for n in nodes[::-1][:15]:
            with st.expander(f"SCAN: {n[0]}"): st.write(n[1])
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "PRACTICE EXAM":
    due = db.execute('SELECT id, q, a FROM nodes WHERE next_review <= ?', (datetime.now().date(),)).fetchall()
    if due:
        card = random.choice(due)
        st.markdown(f"<div class='omni-panel'><h2>{card[1]}</h2></div>", unsafe_allow_html=True)
        if st.button("REVEAL"):
            st.success(card[2])
            cols = st.columns(5)
            for i in range(5):
                if cols[i].button(f"Level {i + 1}"):
                    update_node(card[0], i + 1)
                    db.execute('UPDATE profile SET xp = xp + 5 WHERE id=1');
                    db.commit()
                    st.rerun()
    else:
        st.info("Neural core mastered for today.")

elif st.session_state.page == "MATH NEXUS":
    q = st.chat_input("Input problem...")
    if q:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": q}])
        st.markdown(f"<div class='omni-panel'>{res.choices[0].message.content}</div>", unsafe_allow_html=True)

elif st.session_state.page == "AI PHOTO GENERATOR":
    p = st.text_input("Manifest visual thought...")
    if st.button("GENERATE"):
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        img = client.images.generate(model="dall-e-3", prompt=p)
        st.image(img.data[0].url)