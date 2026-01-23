import streamlit as st
import openai
import json
import re
import PyPDF2
import sqlite3

# --- 1. COGNIAI HUD UI (EMERALD VOID) ---
st.set_page_config(page_title="CogniAI | Infinity OS", page_icon="♾️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Fira+Code:wght@300;500&display=swap');

    .stApp {
        background: #020202 !important;
        background-image: 
            radial-gradient(at 50% 0%, rgba(0, 255, 136, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(112, 0, 255, 0.05) 0px, transparent 50%) !important;
        color: #e0e0e0 !important;
        font-family: 'Space Grotesk', sans-serif;
    }

    .omni-panel {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 15px;
        padding: 30px;
        margin-bottom: 20px;
        backdrop-filter: blur(15px);
    }

    .stButton>button {
        background: transparent !important;
        color: #00ff88 !important;
        border: 2px solid #00ff88 !important;
        border-radius: 12px !important;
        font-family: 'Fira Code', monospace !important;
        font-weight: 700 !important;
        transition: 0.3s all;
    }
    .stButton>button:hover {
        background: #00ff88 !important;
        color: black !important;
        box-shadow: 0 0 30px #00ff88;
    }

    .fira { font-family: 'Fira Code', monospace; color: #00ff88; }
    [data-testid="stHeader"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


# --- 2. ARCHIVE ENGINE ---
def get_db():
    conn = sqlite3.connect('cogniai_archive.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS stats (id INT PRIMARY KEY, xp INT, lvl INT)')
    if not conn.execute('SELECT * FROM stats WHERE id=1').fetchone():
        conn.execute('INSERT INTO stats VALUES (1, 0, 1)')
    conn.commit()
    return conn


def neural_process(text, creativity, speed_mode):
    model = "gpt-4o-mini" if speed_mode == "Velocity (Fast)" else "gpt-4o"
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    res = client.chat.completions.create(
        model=model,
        temperature=creativity,
        response_format={"type": "json_object"},
        messages=[{"role": "system",
                   "content": "Return JSON: {'mindmap': 'Mermaid String', 'cards': [{'q':'','a':''}], 'quiz': [{'q':'','o':[],'a':''}], 'vision': ''}"},
                  {"role": "user", "content": f"Deconstruct: {text[:8000]}"}]
    )
    return json.loads(res.choices[0].message.content)


# --- 3. STATE & DB ---
db = get_db()
if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'brain' not in st.session_state: st.session_state.brain = None
st.session_state.xp, st.session_state.lvl = db.execute('SELECT xp, lvl FROM stats WHERE id=1').fetchone()

# --- 4. NAVIGATION ---
st.markdown(
    "<h1 style='text-align:center; color:#00ff88; letter-spacing:8px;'>COGNIAI <span style='font-weight:100; opacity:0.3;'>| INFINITY OS</span></h1>",
    unsafe_allow_html=True)
nav = st.columns(4)
nav_items = ["HOME", "STUDY LAB", "VISION", "TERMINAL"]
for i, item in enumerate(nav_items):
    if nav[i].button(item, use_container_width=True):
        st.session_state.page = item
        st.rerun()


# --- 5. MODULES ---

def render_home():
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("<div class='omni-panel'>", unsafe_allow_html=True)
        st.title(f"SYNC LEVEL: {st.session_state.lvl}")
        st.progress(st.session_state.xp / 100)
        st.write(f"Neural Progress: {st.session_state.xp}% towards Level {st.session_state.lvl + 1}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='omni-panel'><h3>Focus Stream</h3>", unsafe_allow_html=True)
        st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(
            "<div class='omni-panel'><h3>Engine Status</h3><p class='fira'>- CogniAI: Online<br>- Memory: Persistence Active<br>- UI: Emerald Void</p></div>",
            unsafe_allow_html=True)


def render_study_lab():
    l, r = st.columns([1, 2])
    with l:
        st.markdown("<div class='omni-panel'><h3>Configuration</h3>", unsafe_allow_html=True)
        creativity = st.slider("Neural Entropy", 0.0, 1.0, 0.7)
        speed = st.select_slider("Engine Velocity", options=["Deep Logic", "Velocity"])
        st.divider()
        up = st.file_uploader("Upload Study Material", type=['pdf'])
        if up and st.button("SYNCHRONIZE"):
            reader = PyPDF2.PdfReader(up)
            txt = "".join([p.extract_text() for p in reader.pages])
            st.session_state.brain = neural_process(txt, creativity, speed)
            st.session_state.xp += 25
            if st.session_state.xp >= 100: st.session_state.lvl += 1; st.session_state.xp = 0
            db.execute('UPDATE stats SET xp=?, lvl=? WHERE id=1', (st.session_state.xp, st.session_state.lvl))
            db.commit()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with r:
        if st.session_state.brain:
            st.markdown("<div class='omni-panel'>", unsafe_allow_html=True)
            t1, t2, t3 = st.tabs(["MIND MAP", "FLASHCARDS", "PRACTICE TEST"])
            with t1:
                st.markdown(f"```mermaid\n{st.session_state.brain['mindmap']}\n```")
            with t2:
                for c in st.session_state.brain['cards']:
                    with st.expander(f"Q: {c['q']}"): st.markdown(f"<p class='fira'>{c['a']}</p>",
                                                                  unsafe_allow_html=True)
            with t3:
                for idx, q in enumerate(st.session_state.brain['quiz']):
                    st.write(f"**{idx + 1}. {q['q']}**")
                    st.radio("Options:", q['o'], key=f"ex_{idx}")
            st.markdown("</div>", unsafe_allow_html=True)


def render_vision():
    st.markdown("<div class='omni-panel'>", unsafe_allow_html=True)
    with st.form("vision_manifest"):
        p = st.text_input("Manifest Vision",
                          value=st.session_state.brain.get('vision', '') if st.session_state.brain else "")
        if st.form_submit_button("GENERATE IMAGE"):
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            img = client.images.generate(model="dall-e-3", prompt=p)
            st.image(img.data[0].url)
    st.markdown("</div>", unsafe_allow_html=True)


def render_terminal():
    st.markdown("<div class='omni-panel'>", unsafe_allow_html=True)
    q = st.chat_input("Direct Brain-Link Query...")
    if q:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": q}])
        st.markdown(f"<div class='fira'>{res.choices[0].message.content}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# --- ROUTER ---
router = {"HOME": render_home, "STUDY LAB": render_study_lab, "VISION": render_vision, "TERMINAL": render_terminal}
router.get(st.session_state.page, render_home)()