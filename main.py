import streamlit as st
import openai
import json
import re
import PyPDF2
import sqlite3
from datetime import datetime

# --- 1. HUD ARCHITECTURE (EMERALD VOID) ---
st.set_page_config(page_title="CogniAI | Singularity", page_icon="♾️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Fira+Code:wght@300;500&display=swap');

    .stApp {
        background: #020202 !important;
        background-image: 
            radial-gradient(at 50% 0%, rgba(0, 255, 136, 0.12) 0px, transparent 50%),
            linear-gradient(rgba(0, 255, 136, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 136, 0.02) 1px, transparent 1px) !important;
        background-size: 100% 100%, 30px 30px, 30px 30px !important;
        color: #e0e0e0 !important; font-family: 'Space Grotesk', sans-serif;
    }

    .omni-panel {
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 20px; padding: 30px; margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    .stButton>button {
        background: transparent !important; color: #00ff88 !important;
        border: 2px solid #00ff88 !important; border-radius: 10px !important;
        font-family: 'Fira Code', monospace !important; font-weight: 700 !important;
        letter-spacing: 2px; transition: 0.4s all; width: 100%;
    }
    .stButton>button:hover {
        background: #00ff88 !important; color: black !important;
        box-shadow: 0 0 40px #00ff88; transform: translateY(-2px);
    }

    .fira { font-family: 'Fira Code', monospace; color: #00ff88; }
    [data-testid="stHeader"] { display: none; }
    .stTabs [data-baseweb="tab-list"] { background: transparent; }
    .stTabs [data-baseweb="tab"] { color: #666 !important; }
    .stTabs [aria-selected="true"] { color: #00ff88 !important; border-bottom-color: #00ff88 !important; }
    </style>
    """, unsafe_allow_html=True)


# --- 2. PERSISTENCE LAYER ---
def init_db():
    conn = sqlite3.connect('cogniai_omega.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS stats (id INT PRIMARY KEY, xp INT, lvl INT, rank TEXT)')
    if not conn.execute('SELECT * FROM stats WHERE id=1').fetchone():
        conn.execute('INSERT INTO stats VALUES (1, 0, 1, "NEOPHYTE")')
    conn.commit()
    return conn


# --- 3. RECURSIVE DEEP SYNTHESIS ENGINE ---
def deep_synthesis(full_text, creativity, velocity_mode):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    model = "gpt-4o" if velocity_mode == "Deep Logic" else "gpt-4o-mini"

    # Split 12+ pages into 5,000 character Knowledge Blocks
    chunks = [full_text[i:i + 5000] for i in range(0, len(full_text), 5000)]

    final_data = {"map": "", "cards": [], "quiz": [], "vision": ""}

    progress = st.progress(0)
    for i, chunk in enumerate(chunks):
        st.toast(f"Synchronizing Block {i + 1} of {len(chunks)}...", icon="🧠")
        res = client.chat.completions.create(
            model=model,
            temperature=creativity,
            response_format={"type": "json_object"},
            messages=[{
                "role": "system",
                "content": "HIGH CAPACITY MODE: Generate 8+ complex flashcards and 4+ quiz questions for this specific chunk. Use LaTeX for math. Return JSON."
            }, {"role": "user", "content": chunk}]
        )
        batch = json.loads(res.choices[0].message.content)

        # Aggregate logic
        final_data["cards"].extend(batch.get("cards", []))
        final_data["quiz"].extend(batch.get("quiz", []))
        if i == 0:
            final_data["map"] = batch.get("map", "graph TD\nNode[Synthesis Active]")
            final_data["vision"] = batch.get("vision", "")

        progress.progress((i + 1) / len(chunks))

    return final_data


# --- 4. SESSION ARCHITECTURE ---
db = init_db()
if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'memory' not in st.session_state: st.session_state.memory = None
st.session_state.xp, st.session_state.lvl, st.session_state.rank = db.execute(
    'SELECT xp, lvl, rank FROM stats WHERE id=1').fetchone()

# --- 5. NAVIGATION HUB ---
st.markdown(
    "<h1 style='text-align:center; color:#00ff88; letter-spacing:12px; margin-bottom:5px;'>COGNIAI</h1><p style='text-align:center; opacity:0.4; letter-spacing:3px;'>INFINITY OS // SINGULARITY BUILD</p>",
    unsafe_allow_html=True)

nav = st.columns(4)
nav_items = ["HOME", "STUDY LAB", "MATH NEXUS", "VISION"]
for i, item in enumerate(nav_items):
    if nav[i].button(item, use_container_width=True):
        st.session_state.page = item
        st.rerun()


# --- 6. DREAM MODULES ---

def render_home():
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(
            f"<div class='omni-panel'><h2>SYNC LEVEL: {st.session_state.lvl}</h2><p class='fira'>RANK: {st.session_state.rank}</p>",
            unsafe_allow_html=True)
        st.progress(st.session_state.xp / 100)
        st.write(f"Neural Progress: {st.session_state.xp}/100 XP to next level.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='omni-panel'><h3>Focus Neural-Stream</h3>", unsafe_allow_html=True)
        st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(
            "<div class='omni-panel'><h3>Engine Logs</h3><p class='fira'>- Uptime: Stable<br>- Model: GPT-4o Omni<br>- Memory: SQL Persistent<br>- Context: High-Cap Active</p></div>",
            unsafe_allow_html=True)


def render_study_lab():
    l, r = st.columns([1, 2])
    with l:
        st.markdown("<div class='omni-panel'><h3>Config Engine</h3>", unsafe_allow_html=True)
        creativity = st.slider("Neural Entropy (Creativity)", 0.0, 1.0, 0.7)
        velocity = st.select_slider("Engine Velocity", options=["Deep Logic", "Fast Velocity"])
        st.divider()
        up = st.file_uploader("Upload Knowledge (PDF)", type=['pdf'])
        if up and st.button("EXECUTE DEEP SYNC"):
            reader = PyPDF2.PdfReader(up)
            full_txt = "".join([p.extract_text() for p in reader.pages])
            st.session_state.memory = deep_synthesis(full_txt, creativity, velocity)

            # Update XP
            st.session_state.xp += 40
            if st.session_state.xp >= 100:
                st.session_state.lvl += 1
                st.session_state.xp = 0
            db.execute('UPDATE stats SET xp=?, lvl=? WHERE id=1', (st.session_state.xp, st.session_state.lvl))
            db.commit()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with r:
        if st.session_state.memory:
            st.markdown("<div class='omni-panel'>", unsafe_allow_html=True)
            t1, t2, t3 = st.tabs([f"MAP", f"RECALL ({len(st.session_state.memory['cards'])})",
                                  f"EXAM ({len(st.session_state.memory['quiz'])})"])
            with t1:
                st.markdown(f"```mermaid\n{st.session_state.memory['map']}\n```")
            with t2:
                for c in st.session_state.memory['cards']:
                    with st.expander(f"Q: {c.get('q')}"): st.markdown(f"<p class='fira'>{c.get('a')}</p>",
                                                                      unsafe_allow_html=True)
            with t3:
                for idx, q in enumerate(st.session_state.memory['quiz']):
                    st.write(f"**{idx + 1}. {q.get('q')}**")
                    st.radio("Analyze Options:", q.get('o', []), key=f"ex_{idx}")
            st.markdown("</div>", unsafe_allow_html=True)


def render_math_nexus():
    st.markdown("<div class='omni-panel'><h3>MATH NEXUS</h3>", unsafe_allow_html=True)
    q = st.chat_input("Input problem for resolution...")
    if q:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": q}])
        st.markdown(f"<div class='fira'>{res.choices[0].message.content}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_vision():
    st.markdown("<div class='omni-panel'><h3>VISION STUDIO</h3>", unsafe_allow_html=True)
    with st.form("vision_form"):
        p = st.text_input("Manifest Latent Vision",
                          value=st.session_state.memory.get('vision', '') if st.session_state.memory else "")
        if st.form_submit_button("GENERATE IMAGE"):
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            img = client.images.generate(model="dall-e-3", prompt=p)
            st.image(img.data[0].url)
    st.markdown("</div>", unsafe_allow_html=True)


# --- 7. ROUTER ---
router = {
    "HOME": render_home,
    "STUDY LAB": render_study_lab,
    "MATH NEXUS": render_math_nexus,
    "VISION": render_vision
}
router.get(st.session_state.page, render_home)()