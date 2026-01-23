import streamlit as st
import openai
import json
import re
import PyPDF2
import sqlite3
from datetime import datetime

# --- 1. GOD-TIER UI ENGINE (AERO-GLASS & NEON) ---
st.set_page_config(page_title="INFINITY OS | NEURAL INTERFACE", page_icon="♾️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Fira+Code:wght@300;500&display=swap');

    :root {
        --glow: #00f2ff;
        --bg: #030303;
        --card: rgba(255, 255, 255, 0.03);
    }

    /* GLOBAL RESET */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1a1a2e 0%, #030303 80%) !important;
        color: #e0e0e0 !important;
        font-family: 'Space Grotesk', sans-serif;
    }

    /* GLASSMORPHISM CARDS */
    .bento-node {
        background: var(--card);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .bento-node:hover {
        border-color: var(--glow);
        transform: translateY(-5px);
        box-shadow: 0 0 30px rgba(0, 242, 255, 0.15);
    }

    /* NAVIGATION HUD */
    .nav-container {
        display: flex; justify-content: space-around;
        padding: 20px; background: rgba(0,0,0,0.5);
        border-radius: 100px; border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 40px;
    }

    /* NEON BUTTONS */
    .stButton>button {
        background: transparent !important;
        color: var(--glow) !important;
        border: 1px solid var(--glow) !important;
        border-radius: 50px !important;
        padding: 10px 25px !important;
        font-family: 'Fira Code', monospace !important;
        text-transform: uppercase; letter-spacing: 2px;
        transition: 0.3s all !important;
    }
    .stButton>button:hover {
        background: var(--glow) !important;
        color: black !important;
        box-shadow: 0 0 20px var(--glow);
    }

    /* TERMINAL TEXT */
    code, .fira { font-family: 'Fira Code', monospace; color: var(--glow); }

    [data-testid="stHeader"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


# --- 2. THE PERSISTENCE LAYER (SQLITE) ---
def init_db():
    conn = sqlite3.connect('neural_archive.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS stats (id INT PRIMARY KEY, xp INT, lvl INT)')
    c.execute('SELECT count(*) FROM stats')
    if c.fetchone()[0] == 0: c.execute('INSERT INTO stats VALUES (1, 0, 1)')
    conn.commit()
    return conn


# --- 3. THE NEURAL CORE (GPT-4o + SCHEMA GUARDIAN) ---
def neural_engine(raw_content):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system",
                 "content": "You are the Infinity OS Core. Analyze data and return JSON: {'mindmap': 'mermaid string', 'cards': [{'q':'','a':''}], 'quiz': [{'q':'','o':[],'a':''}], 'key_concepts': []}"},
                {"role": "user", "content": raw_content[:6000]}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"NEURAL SYNC FAILURE: {e}")
        return None


# --- 4. SESSION STATE ---
if 'active_page' not in st.session_state: st.session_state.active_page = "HOME"
if 'neural_data' not in st.session_state: st.session_state.neural_data = None
conn = init_db()
st.session_state.xp, st.session_state.lvl = conn.execute('SELECT xp, lvl FROM stats WHERE id=1').fetchone()

# --- 5. TOP NAVIGATION ---
st.markdown(
    "<h1 style='text-align:center; letter-spacing:10px; color:#fff;'>INFINITY<span style='color:#00f2ff;'>OS</span></h1>",
    unsafe_allow_html=True)
nav_cols = st.columns(4)
pages = ["HOME", "LAB", "VISION", "MATH"]
for i, p in enumerate(pages):
    if nav_cols[i].button(p, use_container_width=True):
        st.session_state.active_page = p
        st.rerun()


# --- 6. PAGE MODULES ---

def render_home():
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='bento-node'><h3>LEVEL</h3><h1 class='fira'>{st.session_state.lvl}</h1></div>",
                         unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='bento-node'><h3>XP PROGRESS</h3>", unsafe_allow_html=True)
        st.progress(st.session_state.xp / 100)
        st.markdown("</div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='bento-node'><h3>NEURAL STATUS</h3><p class='fira'>CONNECTED</p></div>",
                         unsafe_allow_html=True)


def render_lab():
    l, r = st.columns([1, 2])
    with l:
        st.markdown("<div class='bento-node'><h3>INGESTION</h3>", unsafe_allow_html=True)
        file = st.file_uploader("UPLOAD DATA", type=['pdf', 'txt'])
        voice = st.audio_input("VOICE SYNC")
        if st.button("EXECUTE ANALYSIS"):
            content = ""
            if file:
                reader = PyPDF2.PdfReader(file)
                content = "".join([page.extract_text() for page in reader.pages])
            elif voice:
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                trans = client.audio.transcriptions.create(model="whisper-1", file=voice)
                content = trans.text

            if content:
                with st.spinner("SYNCHRONIZING..."):
                    st.session_state.neural_data = neural_engine(content)
                    st.session_state.xp += 25
                    if st.session_state.xp >= 100:
                        st.session_state.xp = 0
                        st.session_state.lvl += 1
                    conn.execute('UPDATE stats SET xp=?, lvl=? WHERE id=1', (st.session_state.xp, st.session_state.lvl))
                    conn.commit()
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with r:
        if st.session_state.neural_data:
            t1, t2, t3 = st.tabs(["MIND MAP", "FLASHCARDS", "EXAM"])
            with t1:
                st.markdown(f"```mermaid\n{st.session_state.neural_data['mindmap']}\n```")
            with t2:
                for c in st.session_state.neural_data['cards']:
                    with st.expander(c['q']): st.write(c['a'])
            with t3:
                for idx, q in enumerate(st.session_state.neural_data['quiz']):
                    st.write(f"**{idx + 1}. {q['q']}**")
                    st.radio("SELECT RESPONSE:", q['o'], key=f"q_{idx}")


def render_vision():
    st.markdown("<div class='bento-node'><h3>LATENT SPACE MANIFESTATION</h3>", unsafe_allow_html=True)
    p = st.text_input("INPUT PROMPT")
    if st.button("MANIFEST"):
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        img = client.images.generate(model="dall-e-3", prompt=p)
        st.image(img.data[0].url)
    st.markdown("</div>", unsafe_allow_html=True)


def render_math():
    st.markdown("<div class='bento-node'><h3>MATH TERMINAL</h3>", unsafe_allow_html=True)
    p = st.chat_input("Input problem...")
    if p:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": p}])
        st.markdown(res.choices[0].message.content)
    st.markdown("</div>", unsafe_allow_html=True)


# --- 7. ROUTER ---
router = {"HOME": render_home, "LAB": render_lab, "VISION": render_vision, "MATH": render_math}
router.get(st.session_state.active_page, render_home)()