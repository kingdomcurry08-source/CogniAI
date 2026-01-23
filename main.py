import streamlit as st
import openai
import json
import re
import PyPDF2
import sqlite3

# --- 1. UI ARCHITECTURE ---
st.set_page_config(page_title="CogniAI | Infinity OS", page_icon="♾️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Fira+Code:wght@300;500&display=swap');
    .stApp { background: #010101; color: #e0e0e0; font-family: 'Space Grotesk', sans-serif; }
    .omni-panel {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid #00ff88;
        border-radius: 15px; padding: 25px; margin-bottom: 20px;
    }
    .stButton>button {
        background: transparent !important; color: #00ff88 !important;
        border: 2px solid #00ff88 !important; border-radius: 10px !important;
        font-family: 'Fira Code', monospace !important; width: 100%;
    }
    .stButton>button:hover { background: #00ff88 !important; color: black !important; box-shadow: 0 0 30px #00ff88; }
    .fira { font-family: 'Fira Code', monospace; color: #00ff88; }
    [data-testid="stHeader"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


# --- 2. DATA PERSISTENCE ---
def get_db():
    conn = sqlite3.connect('cogniai_final.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS stats (id INT PRIMARY KEY, xp INT, lvl INT)')
    if not conn.execute('SELECT * FROM stats WHERE id=1').fetchone():
        conn.execute('INSERT INTO stats VALUES (1, 0, 1)')
    conn.commit()
    return conn


# --- 3. THE RECOVERY ENGINE (FIXES THE "0" ISSUE) ---
def deep_synthesis(full_text, creativity, velocity):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    model = "gpt-4o" if velocity == "Deep Logic" else "gpt-4o-mini"

    # Clean text of null bytes or weird formatting that breaks AI
    clean_text = full_text.replace('\x00', '').strip()
    # Split into manageable chunks (approx 4 pages each)
    chunks = [clean_text[i:i + 7000] for i in range(0, len(clean_text), 7000)]

    final_data = {"map": "graph TD\nStart --> Analysis", "cards": [], "quiz": [], "vision": ""}

    prog = st.progress(0)
    for i, chunk in enumerate(chunks):
        try:
            res = client.chat.completions.create(
                model=model,
                temperature=creativity,
                response_format={"type": "json_object"},
                messages=[{
                    "role": "system",
                    "content": "You are CogniAI. Generate 10 complex flashcards and 5 quiz questions. Return ONLY JSON."
                }, {"role": "user", "content": f"Block {i + 1}: {chunk}"}]
            )
            batch = json.loads(res.choices[0].message.content)
            final_data["cards"].extend(batch.get("cards", []))
            final_data["quiz"].extend(batch.get("quiz", []))
            if i == 0: final_data["vision"] = batch.get("vision", "")
        except Exception as e:
            st.error(f"Sync error in Block {i + 1}. Skipping corrupted data.")
            continue
        prog.progress((i + 1) / len(chunks))

    return final_data


# --- 4. NAVIGATION & STATE ---
db = get_db()
if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'memory' not in st.session_state: st.session_state.memory = None
st.session_state.xp, st.session_state.lvl = db.execute('SELECT xp, lvl FROM stats WHERE id=1').fetchone()

st.markdown("<h1 style='text-align:center; color:#00ff88; letter-spacing:10px;'>COGNIAI</h1>", unsafe_allow_html=True)
nav = st.columns(4)
items = ["HOME", "STUDY LAB", "MATH NEXUS", "VISION"]
for i, x in enumerate(items):
    if nav[i].button(x, use_container_width=True):
        st.session_state.page = x
        st.rerun()


# --- 5. PAGE MODULES ---

def render_home():
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(
            f"<div class='omni-panel'><h2>LVL {st.session_state.lvl}</h2><p>XP: {st.session_state.xp}/100</p></div>",
            unsafe_allow_html=True)
        st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")
    with c2:
        st.markdown(
            "<div class='omni-panel'><h3>System Status</h3><p class='fira'>- Neural Link: Stable<br>- Model: gpt-4o<br>- Archive: Connected</p></div>",
            unsafe_allow_html=True)


def render_lab():
    l, r = st.columns([1, 2])
    with l:
        st.markdown("<div class='omni-panel'><h3>Lab Config</h3>", unsafe_allow_html=True)
        creativity = st.slider("Neural Entropy", 0.0, 1.0, 0.7)
        velocity = st.select_slider("Engine Velocity", options=["Deep Logic", "Fast Velocity"])
        up = st.file_uploader("Upload PDF", type=['pdf'])
        if up and st.button("SYNCHRONIZE"):
            reader = PyPDF2.PdfReader(up)
            txt = "".join([p.extract_text() for p in reader.pages])
            if not txt.strip():
                st.warning("Could not extract text. Try a different PDF.")
            else:
                st.session_state.memory = deep_synthesis(txt, creativity, velocity)
                st.session_state.xp += 30
                if st.session_state.xp >= 100: st.session_state.lvl += 1; st.session_state.xp = 0
                db.execute('UPDATE stats SET xp=?, lvl=? WHERE id=1', (st.session_state.xp, st.session_state.lvl))
                db.commit()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with r:
        if st.session_state.memory:
            st.markdown("<div class='omni-panel'>", unsafe_allow_html=True)
            t1, t2, t3 = st.tabs(["MAP", f"CARDS ({len(st.session_state.memory['cards'])})", "EXAM"])
            with t1:
                st.markdown(f"```mermaid\n{st.session_state.memory['map']}\n```")
            with t2:
                for c in st.session_state.memory['cards']:
                    with st.expander(f"Q: {c.get('q', 'Question')}"): st.write(c.get('a', 'Answer'))
            with t3:
                for idx, q in enumerate(st.session_state.memory['quiz']):
                    st.write(f"**{idx + 1}. {q.get('q')}**")
                    st.radio("Options:", q.get('o', []), key=f"ex_{idx}")
            st.markdown("</div>", unsafe_allow_html=True)


def render_math():
    st.markdown("<div class='omni-panel'><h3>MATH NEXUS</h3>", unsafe_allow_html=True)
    q = st.chat_input("Input problem...")
    if q:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": q}])
        st.markdown(f"<div class='fira'>{res.choices[0].message.content}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_vision():
    st.markdown("<div class='omni-panel'><h3>VISION STUDIO</h3>", unsafe_allow_html=True)
    with st.form("vis"):
        p = st.text_input("Manifest Vision",
                          value=st.session_state.memory.get('vision', '') if st.session_state.memory else "")
        if st.form_submit_button("GENERATE"):
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            img = client.images.generate(model="dall-e-3", prompt=p)
            st.image(img.data[0].url)
    st.markdown("</div>", unsafe_allow_html=True)


# --- 6. ROUTER ---
router = {"HOME": render_home, "STUDY LAB": render_lab, "MATH NEXUS": render_math, "VISION": render_vision}
router.get(st.session_state.page, render_home)()