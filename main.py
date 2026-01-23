import streamlit as st
import openai
import json
import re
import PyPDF2
import time
from datetime import datetime

# --- 1. CYBER-MINIMALIST UI ENGINE ---
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

    /* NEON HUD COMPONENTS */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid rgba(0, 242, 255, 0.2); }
    .stTabs [data-baseweb="tab"] { color: #666 !important; transition: 0.3s; }
    .stTabs [aria-selected="true"] { color: var(--neon) !important; text-shadow: 0 0 10px var(--neon); }

    .bento-node {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px; padding: 25px;
        box-shadow: inset 0 0 20px rgba(112, 0, 255, 0.05);
    }

    .stButton>button {
        background: linear-gradient(45deg, var(--plasma), var(--neon)) !important;
        border: none !important; border-radius: 12px !important; color: white !important;
        font-weight: 700 !important; letter-spacing: 1px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)


# --- 2. THE NEURAL CORE (SCHEMA GUARDIAN + AUTO-PARSE) ---
def neural_engine(input_text, mode="sync"):
    try:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        sys_msg = "Return JSON ONLY. Keys: 'mindmap' (Mermaid code), 'cards' (Q/A), 'quiz' (MCQ), 'summary'."

        res = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": input_text[:5000]}]
        )

        raw = res.choices[0].message.content
        data = json.loads(re.sub(r'```json|```', '', raw).strip())

        # Normalize Keys (The Schema Guardian)
        return {
            "mindmap": data.get("mindmap") or "graph TD\nA[Topic] --> B[Detail]",
            "cards": data.get("cards") or data.get("flashcards") or [],
            "quiz": data.get("quiz") or data.get("questions") or [],
            "summary": data.get("summary") or "Sync Complete."
        }
    except Exception as e:
        return {"error": str(e)}


# --- 3. PERSISTENT STATE ---
states = {'active_page': 'HOME', 'xp': 0, 'lvl': 1, 'data': None}
for k, v in states.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 4. NAVIGATION HUD ---
st.markdown("<h2 style='text-align:center; color:var(--neon);'>∞ INFINITY</h2>", unsafe_allow_html=True)
cols = st.columns([1, 1, 1, 1])
if cols[0].button("🛰️ HOME"): st.session_state.active_page = "HOME"
if cols[1].button("🧠 LAB"): st.session_state.active_page = "LAB"
if cols[2].button("🔭 VISION"): st.session_state.active_page = "VISION"
if cols[3].button("⚡ MATH"): st.session_state.active_page = "MATH"


# --- 5. PAGE MODULES ---

def render_home():
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"<h1>WELCOME TO LVL {st.session_state.lvl}</h1>", unsafe_allow_html=True)
        st.progress(st.session_state.xp / 100)
        st.write(f"Neural Sync XP: {st.session_state.xp}/100")
    with c2:
        st.markdown(
            "<div class='bento-node'><h3>System Status</h3><p>🟢 GPT-4o Online</p><p>🟢 Vision Engine Active</p></div>",
            unsafe_allow_html=True)


def render_lab():
    st.title("Neural Study Lab")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("<div class='bento-node'>", unsafe_allow_html=True)
        file = st.file_uploader("Upload Knowledge (PDF)", type=["pdf"])
        voice = st.audio_input("Voice Ingest")

        if st.button("EXECUTE SYNC"):
            content = ""
            if file:
                pdf = PyPDF2.PdfReader(file)
                content = "".join([p.extract_text() for p in pdf.pages])
            elif voice:
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                trans = client.audio.transcriptions.create(model="whisper-1", file=voice)
                content = trans.text

            if content:
                with st.spinner("Synthesizing..."):
                    st.session_state.data = neural_engine(content)
                    st.session_state.xp += 20
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        if st.session_state.data:
            t1, t2, t3 = st.tabs(["🧠 MIND MAP", "🗂️ CARDS", "🛡️ EXAM"])
            with t1:
                st.markdown(f"```mermaid\n{st.session_state.data['mindmap']}\n```")
            with t2:
                for c in st.session_state.data['cards']:
                    with st.expander(c.get('q', 'Question')): st.write(c.get('a', 'Answer'))
            with t3:
                score = 0
                for i, q in enumerate(st.session_state.data['quiz']):
                    st.write(f"**{i + 1}. {q.get('q')}**")
                    ans = st.radio("Response:", q.get('o', []), key=f"q_{i}")
                    if ans == q.get('a'): score += 1
                if st.button("Finalize Exam"):
                    st.balloons()
                    st.session_state.xp += 30


def render_vision():
    st.title("Vision Studio")
    prompt = st.text_input("Manifest reality...")
    if st.button("GENERATE"):
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        img = client.images.generate(model="dall-e-3", prompt=prompt)
        st.image(img.data[0].url)


def render_math():
    st.title("Math Terminal")
    p = st.chat_input("Enter equation...")
    if p:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": p}])
        st.write(res.choices[0].message.content)


# --- 6. ROUTER ---
if st.session_state.xp >= 100:
    st.session_state.lvl += 1
    st.session_state.xp = 0

routes = {"HOME": render_home, "LAB": render_lab, "VISION": render_vision, "MATH": render_math}
routes[st.session_state.active_page]()