import streamlit as st
import openai
import json
import re
import PyPDF2
import sqlite3
import time
from datetime import datetime

# --- 1. THE ULTIMATE UI: DARK FIBER & EMERALD GLOW ---
st.set_page_config(page_title="CogniAI | Singularity", page_icon="♾️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Fira+Code:wght@300;500&display=swap');

    /* THE VOID THEME */
    .stApp {
        background: #010101 !important;
        background-image: 
            linear-gradient(rgba(0, 255, 136, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 136, 0.02) 1px, transparent 1px) !important;
        background-size: 50px 50px !important;
        color: #e0e0e0 !important;
        font-family: 'Space Grotesk', sans-serif;
    }

    /* NEURAL PULSE ANIMATION */
    @keyframes pulse {
        0% { box-shadow: 0 0 5px rgba(0, 255, 136, 0.2); }
        50% { box-shadow: 0 0 20px rgba(0, 255, 136, 0.5); }
        100% { box-shadow: 0 0 5px rgba(0, 255, 136, 0.2); }
    }

    .omni-panel {
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 20px;
        padding: 35px;
        margin-bottom: 25px;
        animation: pulse 4s infinite ease-in-out;
    }

    /* BUTTONS: THE SINGULARITY LOOK */
    .stButton>button {
        background: linear-gradient(45deg, #002b18, #000) !important;
        color: #00ff88 !important;
        border: 1px solid #00ff88 !important;
        border-radius: 4px !important;
        font-family: 'Fira Code', monospace !important;
        text-transform: uppercase;
        letter-spacing: 3px;
        transition: 0.5s all;
    }
    .stButton>button:hover {
        background: #00ff88 !important;
        color: #000 !important;
        box-shadow: 0 0 40px #00ff88;
        transform: translateY(-2px);
    }

    .fira { font-family: 'Fira Code', monospace; color: #00ff88; }
    [data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)


# --- 2. ARCHIVE ENGINE (SQLITE) ---
def get_db():
    conn = sqlite3.connect('cogniai_dream.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS stats (id INT PRIMARY KEY, xp INT, lvl INT, rank TEXT)')
    if not conn.execute('SELECT * FROM stats WHERE id=1').fetchone():
        conn.execute('INSERT INTO stats VALUES (1, 0, 1, "NEOPHYTE")')
    conn.commit()
    return conn


def update_rank(lvl):
    ranks = {1: "NEOPHYTE", 5: "SENTINEL", 10: "ARCHITECT", 20: "SINGULARITY"}
    return ranks.get(lvl, "ADEPT")


# --- 3. NEURAL SYNTHESIS ENGINE ---
def synth_engine(text, temp, model_type):
    model = "gpt-4o" if model_type == "Deep Logic" else "gpt-4o-mini"
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    res = client.chat.completions.create(
        model=model,
        temperature=temp,
        response_format={"type": "json_object"},
        messages=[{"role": "system",
                   "content": "Return JSON: {'map': 'Mermaid String', 'cards': [{'q':'','a':''}], 'quiz': [{'q':'','o':[],'a':''}], 'concept': '', 'vision': ''}"},
                  {"role": "user", "content": f"Synthesize: {text[:10000]}"}]
    )
    return json.loads(res.choices[0].message.content)


# --- 4. STATE MANAGEMENT ---
db = get_db()
if 'page' not in st.session_state: st.session_state.page = "DASHBOARD"
if 'memory' not in st.session_state: st.session_state.memory = None
st.session_state.xp, st.session_state.lvl, st.session_state.rank = db.execute(
    'SELECT xp, lvl, rank FROM stats WHERE id=1').fetchone()

# --- 5. TOP HUD NAVIGATION ---
st.markdown(
    f"<h1 style='text-align:center; color:#00ff88; letter-spacing:15px; margin-bottom:5px;'>COGNIAI</h1><p style='text-align:center; font-family:Fira Code; opacity:0.5;'>RANK: {st.session_state.rank} | VERSION 4.0.0</p>",
    unsafe_allow_html=True)

nav = st.columns(4)
for i, x in enumerate(["DASHBOARD", "STUDY LAB", "MATH NEXUS", "VISION"]):
    if nav[i].button(x, use_container_width=True):
        st.session_state.page = x
        st.rerun()


# --- 6. DREAM MODULES ---

def render_dashboard():
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(
            f"<div class='omni-panel'><h2>SYSTEM STATS</h2><h1 class='fira'>LVL {st.session_state.lvl}</h1><p>XP: {st.session_state.xp}/100</p></div>",
            unsafe_allow_html=True)
        st.progress(st.session_state.xp / 100)

        st.markdown("<div class='omni-panel'><h3>QUICK TERMINAL</h3>", unsafe_allow_html=True)
        q = st.text_input("Direct Command")
        if q: st.write("Processing command...")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='omni-panel'><h3>NEURAL FOCUS AUDIO</h3>", unsafe_allow_html=True)
        st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")
        st.markdown("</div>", unsafe_allow_html=True)


def render_study_lab():
    l, r = st.columns([1, 2])
    with l:
        st.markdown("<div class='omni-panel'><h3>CONFIG ENGINE</h3>", unsafe_allow_html=True)
        creativity = st.select_slider("Neural Entropy", options=[0.0, 0.3, 0.7, 1.0], value=0.7)
        velocity = st.radio("Core Processor", ["Deep Logic", "Velocity (Fast)"])

        up = st.file_uploader("Upload Knowledge (PDF/TXT)", type=['pdf', 'txt'])
        if up and st.button("SYNCHRONIZE DATA"):
            with st.spinner("Decoding DNA..."):
                txt = ""
                if up.type == "application/pdf":
                    reader = PyPDF2.PdfReader(up)
                    txt = "".join([p.extract_text() for p in reader.pages])
                else:
                    txt = up.read().decode()

                st.session_state.memory = synth_engine(txt, creativity, velocity)
                st.session_state.xp += 30
                if st.session_state.xp >= 100:
                    st.session_state.lvl += 1;
                    st.session_state.xp = 0
                    st.session_state.rank = update_rank(st.session_state.lvl)
                db.execute('UPDATE stats SET xp=?, lvl=?, rank=? WHERE id=1',
                           (st.session_state.xp, st.session_state.lvl, st.session_state.rank))
                db.commit()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with r:
        if st.session_state.memory:
            st.markdown("<div class='omni-panel'>", unsafe_allow_html=True)
            t1, t2, t3 = st.tabs(["KNOWLEDGE MAP", "FLASHCARDS", "EXAM"])
            with t1:
                st.markdown(f"```mermaid\n{st.session_state.memory['map']}\n```")
            with t2:
                for c in st.session_state.memory['cards']:
                    with st.expander(f"RECALL: {c['q']}"): st.markdown(f"<p class='fira'>{c['a']}</p>",
                                                                       unsafe_allow_html=True)
            with t3:
                for idx, q in enumerate(st.session_state.memory['quiz']):
                    st.write(f"**{idx + 1}. {q['q']}**")
                    st.radio("Analyze:", q['o'], key=f"ex_{idx}")
            st.markdown("</div>", unsafe_allow_html=True)


def render_math():
    st.markdown("<div class='omni-panel'><h3>MATH NEXUS</h3>", unsafe_allow_html=True)
    m_query = st.chat_input("Input equation for resolution...")
    if m_query:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": m_query}])
        st.markdown(f"<div class='fira'>{res.choices[0].message.content}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_vision():
    st.markdown("<div class='omni-panel'><h3>VISION STUDIO</h3>", unsafe_allow_html=True)
    with st.form("vis"):
        prompt = st.text_input("Prompt",
                               value=st.session_state.memory.get('vision', '') if st.session_state.memory else "")
        if st.form_submit_button("MANIFEST"):
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            img = client.images.generate(model="dall-e-3", prompt=prompt)
            st.image(img.data[0].url)
    st.markdown("</div>", unsafe_allow_html=True)


# --- 7. ROUTER ---
pages = {"DASHBOARD": render_dashboard, "STUDY LAB": render_study_lab, "MATH NEXUS": render_math,
         "VISION": render_vision}
pages.get(st.session_state.page, render_dashboard)()