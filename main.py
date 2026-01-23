import streamlit as st
import openai
import re
import json
import io
import time
from datetime import datetime

# --- 1. SYSTEM CORE ---
st.set_page_config(page_title="CogniAI | Infinity OS", page_icon="♾️", layout="wide")

# --- 2. PREMIUM UI (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        background-image: radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.12) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.12) 0px, transparent 50%);
        color: #ffffff !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    [data-testid="stHeader"] { display: none; }
    .nav-bar {
        position: fixed; top: 0; left: 0; right: 0; height: 70px;
        background: rgba(0,0,0,0.85); backdrop-filter: blur(15px);
        border-bottom: 1px solid rgba(255,255,255,0.1);
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 5%; z-index: 9999;
    }
    .bento-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px; padding: 25px; margin-bottom: 15px;
    }
    .stButton>button {
        background: #ffffff !important; color: #000 !important;
        border-radius: 12px !important; font-weight: 700 !important;
        border: none !important; width: 100%;
    }
    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


# --- 3. UTILS ---
def latex_fixer(text):
    """Wraps raw LaTeX in $ markers for Streamlit rendering."""
    text = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'$\\frac{\1}{\2}$', text)
    text = re.sub(r'\\sqrt\{([^}]*)\}', r'$\\sqrt{\1}$', text)
    return text


# --- 4. STATE ENGINE ---
state_keys = {
    'active_page': 'Home', 'math_history': [], 'flashcards': [],
    'quiz_questions': [], 'user_answers': {}, 'session_notes': ""
}
for key, val in state_keys.items():
    if key not in st.session_state: st.session_state[key] = val

# Navigation Logic
st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
cols = st.columns([2, 1, 1, 1, 1])
with cols[0]: st.markdown("<h2 style='margin:0; font-family:Space Grotesk;'>COGNIAI</h2>", unsafe_allow_html=True)
pages_list = ["Home", "Math", "Study Lab", "Vision"]
for i, p_name in enumerate(pages_list):
    with cols[i + 1]:
        if st.button(p_name, key=f"nav_{p_name}"): st.session_state.active_page = p_name
st.markdown('</div>', unsafe_allow_html=True)


# --- 5. PAGE MODULES ---

def render_home():
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:70px; font-family:Space Grotesk; text-align:center;'>INFINITY OS</h1>",
                unsafe_allow_html=True)

    # Pomodoro Component
    st.markdown("<div style='max-width:400px; margin:auto;'>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='bento-card' style='text-align:center;'><h3>⏱️ Deep Work Timer</h3>",
                    unsafe_allow_html=True)
        t_min = st.number_input("Minutes", value=25, min_value=1)
        if st.button("Start Focus Session"):
            ph = st.empty()
            for t in range(t_min * 60, 0, -1):
                m, s = divmod(t, 60)
                ph.header(f"{m:02d}:{s:02d}")
                time.sleep(1)
            st.balloons()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_math():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.title("Math Terminal")
    for m in st.session_state.math_history:
        with st.chat_message(m["role"]): st.markdown(latex_fixer(m["content"]))

    if p := st.chat_input("Enter math equation..."):
        st.session_state.math_history.append({"role": "user", "content": p})
        with st.chat_message("assistant"):
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            resp = st.write_stream(client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": p}], stream=True
            ))
            st.session_state.math_history.append({"role": "assistant", "content": resp})


def render_study_lab():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.title("Study Lab")

    col_l, col_r = st.columns([1, 2])

    with col_l:
        st.markdown("<div class='bento-card'><h3>📁 Source Data</h3></div>", unsafe_allow_html=True)
        up = st.file_uploader("Upload Notes (PDF/TXT)", type=["pdf", "txt"])
        if up and st.button("✨ Process Notes"):
            import PyPDF2
            text = ""
            if up.type == "application/pdf":
                pdf = PyPDF2.PdfReader(up);
                text = "".join([p.extract_text() for p in pdf.pages])
            else:
                text = up.read().decode()

            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system",
                           "content": "Return JSON: {'flashcards':[{'q':'','a':''}], 'quiz':[{'question':'','options':[],'answer':''}], 'summary':''}"},
                          {"role": "user", "content": text[:3000]}]
            )
            data = json.loads(res.choices[0].message.content)
            st.session_state.flashcards = data['flashcards']
            st.session_state.quiz_questions = data['quiz']
            st.session_state.session_notes = data['summary']

    with col_r:
        t1, t2, t3 = st.tabs(["🗂️ Flashcards", "📝 Quiz", "📓 Export"])
        with t1:
            for c in st.session_state.flashcards:
                with st.expander(c['q']): st.write(c['a'])
        with t2:
            score = 0
            for i, q in enumerate(st.session_state.quiz_questions):
                st.write(f"**{i + 1}. {q['question']}**")
                ans = st.radio("Select:", q['options'], key=f"q{i}")
                if ans == q['answer']: score += 1
            if st.session_state.quiz_questions:
                st.metric("Score", f"{(score / len(st.session_state.quiz_questions)) * 100:.0f}%")
        with t3:
            st.text_area("Live Notes", value=st.session_state.session_notes, height=200)
            st.download_button("💾 Export to Markdown", st.session_state.session_notes, file_name="notes.md")


def render_vision():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.title("Vision Studio")
    prompt = st.text_input("AI Art Prompt")
    if st.button("Generate"):
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        img = client.images.generate(model="dall-e-3", prompt=prompt)
        st.image(img.data[0].url)


# --- 6. ROUTER ---
pages = {"Home": render_home, "Math": render_math, "Study Lab": render_study_lab, "Vision": render_vision}
pages.get(st.session_state.active_page, render_home)()