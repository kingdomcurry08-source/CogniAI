import streamlit as st
import openai
import json
import re
import PyPDF2
import sqlite3
import time
from datetime import datetime

# --- 1. CORE OS STYLING (THE HUD) ---
st.set_page_config(page_title="INFINITY OS", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
    :root { --neon: #00f2ff; --void: #050505; --plasma: #7000ff; }
    html, body, [data-testid="stAppViewContainer"] {
        background: var(--void) !important;
        background-image: radial-gradient(circle at 50% 10%, rgba(112, 0, 255, 0.15) 0%, transparent 50%) !important;
        color: #e0e0e0 !important; font-family: 'JetBrains Mono', monospace;
    }
    .stButton>button {
        background: linear-gradient(45deg, var(--plasma), var(--neon)) !important;
        border: none !important; border-radius: 12px !important; color: white !important;
        font-weight: 700 !important; letter-spacing: 1px; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 20px var(--plasma); }
    .bento-node {
        background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px; padding: 25px; margin-bottom: 20px;
    }
    [data-testid="stHeader"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


# --- 2. DATABASE ARCHIVE (PERSISTENCE LAYER) ---
def init_db():
    conn = sqlite3.connect('infinity_archive.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_stats
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY,
                     xp
                     INTEGER,
                     lvl
                     INTEGER,
                     last_sync
                     TEXT
                 )''')
    c.execute('SELECT count(*) FROM user_stats')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO user_stats (xp, lvl, last_sync) VALUES (0, 1, ?)', (str(datetime.now()),))
    conn.commit()
    return conn


def load_stats():
    conn = init_db()
    return conn.execute('SELECT xp, lvl FROM user_stats WHERE id=1').fetchone()


def save_stats(xp, lvl):
    conn = init_db()
    conn.execute('UPDATE user_stats SET xp=?, lvl=?, last_sync=? WHERE id=1', (xp, lvl, str(datetime.now())))
    conn.commit()


# --- 3. NEURAL ENGINE (THE BRAIN) ---
def neural_engine(input_text):
    try:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system",
                 "content": "Return JSON. Keys: 'mindmap' (Mermaid code), 'cards' (Q&A), 'quiz' (MCQ with 'q', 'o', 'a' keys). Use LaTeX for math."},
                {"role": "user", "content": f"Analyze and deconstruct: {input_text[:5000]}"}
            ]
        )
        data = json.loads(res.choices[0].message.content)
        return {
            "mindmap": data.get("mindmap", "graph TD\nA[No Data]"),
            "cards": data.get("cards") or data.get("flashcards") or [],
            "quiz": data.get("quiz") or []
        }
    except Exception as e:
        st.error(f"Neural Core Error: {e}")
        return None


# --- 4. SESSION INITIALIZATION ---
db_xp, db_lvl = load_stats()
if 'xp' not in st.session_state: st.session_state.xp = db_xp
if 'lvl' not in st.session_state: st.session_state.lvl = db_lvl
if 'active_page' not in st.session_state: st.session_state.active_page = "HOME"
if 'data' not in st.session_state: st.session_state.data = None

# --- 5. NAVIGATION ---
st.markdown("<h1 style='text-align:center; color:var(--neon); letter-spacing:5px;'>∞ INFINITY OS</h1>",
            unsafe_allow_html=True)
nav_cols = st.columns(4)
nav_items = ["HOME", "STUDY LAB", "VISION", "MATH"]
for i, item in enumerate(nav_items):
    if nav_cols[i].button(item):
        st.session_state.active_page = item
        st.rerun()


# --- 6. MODULES ---

def render_home():
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"<h1 style='font-size: 70px;'>LEVEL {st.session_state.lvl}</h1>", unsafe_allow_html=True)
        st.progress(st.session_state.xp / 100)
        st.write(f"Neural Sync Progress: {st.session_state.xp}/100 XP")
    with c2:
        st.markdown(
            "<div class='bento-node'><h3>System Hub</h3><p>🟢 Database: Active</p><p>🟢 GPT-4o: Connected</p></div>",
            unsafe_allow_html=True)


def render_lab():
    col_in, col_out = st.columns([1, 2])
    with col_in:
        st.markdown("<div class='bento-node'><h3>Ingest</h3>", unsafe_allow_html=True)
        file = st.file_uploader("PDF Knowledge", type=["pdf"])
        voice = st.audio_input("Voice Memo")
        if st.button("EXECUTE SYNC"):
            content = ""
            if file:
                reader = PyPDF2.PdfReader(file)
                content = "".join([p.extract_text() for p in reader.pages])
            elif voice:
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                trans = client.audio.transcriptions.create(model="whisper-1", file=voice)
                content = trans.text

            if content:
                st.session_state.data = neural_engine(content)
                st.session_state.xp += 25
                if st.session_state.xp >= 100:
                    st.session_state.lvl += 1
                    st.session_state.xp = 0
                save_stats(st.session_state.xp, st.session_state.lvl)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_out:
        if st.session_state.data:
            t1, t2, t3 = st.tabs(["MIND MAP", "RECALL", "EXAM"])
            with t1:
                st.markdown(f"```mermaid\n{st.session_state.data['mindmap']}\n```")
            with t2:
                for c in st.session_state.data['cards']:
                    with st.expander(c.get('q', 'Question')): st.write(c.get('a', 'Answer'))
            with t3:
                for i, q in enumerate(st.session_state.data['quiz']):
                    st.write(f"**{i + 1}. {q.get('q')}**")
                    st.radio("Options:", q.get('o', []), key=f"q_v3_{i}")


def render_vision():
    p = st.text_input("Prompt for DALL-E 3")
    if st.button("GENERATE"):
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.images.generate(model="dall-e-3", prompt=p)
        st.image(res.data[0].url)


def render_math():
    query = st.chat_input("Enter math problem...")
    if query:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": query}])
        st.markdown(res.choices[0].message.content)


# --- 7. ROUTER ---
routes = {
    "HOME": render_home,
    "STUDY LAB": render_lab,
    "VISION": render_vision,
    "MATH": render_math
}
routes.get(st.session_state.active_page, render_home)()