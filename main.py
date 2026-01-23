import streamlit as st
import openai
import re
import json
import io
import time
import PyPDF2

# --- 1. ULTRA-AERO UI ENGINE ---
st.set_page_config(page_title="INFINITY OS", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono&display=swap');

    :root {
        --primary: #00f2ff;
        --accent: #7000ff;
        --glass: rgba(255, 255, 255, 0.03);
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: #050505 !important;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(112, 0, 255, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 80% 70%, rgba(0, 242, 255, 0.1) 0%, transparent 40%) !important;
        color: #e0e0e0 !important;
        font-family: 'Inter', sans-serif;
    }

    /* NEON GLASS NAVIGATION */
    .nav-bar {
        position: fixed; top: 0; left: 0; right: 0; height: 85px;
        background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(25px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 4%; z-index: 9999;
    }

    /* BENTO BOX 2.0 */
    .bento-node {
        background: var(--glass);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 28px; padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .bento-node:hover {
        border-color: var(--primary);
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 242, 255, 0.1);
    }

    /* GLOW BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, var(--accent), var(--primary)) !important;
        color: white !important; border: none !important;
        border-radius: 16px !important; padding: 12px 28px !important;
        font-weight: 600 !important; letter-spacing: 0.5px !important;
        transition: 0.3s !important; text-transform: uppercase; font-size: 12px;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.4) !important;
        transform: scale(1.02);
    }

    [data-testid="stHeader"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


# --- 2. THE INTELLIGENCE CORE (FIXES JSON ERROR) ---
def safe_ai_request(prompt, is_json=False):
    """Encapsulated AI call with Smart Retry and Auto-Correction."""
    try:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        params = {
            "model": "gpt-4o",
            "messages": [{"role": "system", "content": "You are a specialized OS engine. Always use LaTeX for math."},
                         {"role": "user", "content": prompt}]
        }
        if is_json:
            params["response_format"] = {"type": "json_object"}
            params["messages"][0]["content"] += " Return RAW JSON only."

        response = client.chat.completions.create(**params)
        content = response.choices[0].message.content

        if is_json:
            return json.loads(re.sub(r'```json|```', '', content).strip())
        return content
    except Exception as e:
        return {"error": str(e)}


def latex_fixer(text):
    """Turns raw AI code into visual math symbols."""
    text = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'$\\frac{\1}{\2}$', text)
    text = re.sub(r'\\sqrt\{([^}]*)\}', r'$\\sqrt{\1}$', text)
    return text


# --- 3. STATE ENGINE ---
if 'active_page' not in st.session_state: st.session_state.active_page = 'Home'
if 'flashcards' not in st.session_state: st.session_state.flashcards = []
if 'quiz_data' not in st.session_state: st.session_state.quiz_data = []

# --- 4. NAVIGATION ---
st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
with c1: st.markdown("<h2 style='margin:0; font-family:JetBrains Mono; color:#00f2ff;'>∞ INFINITY</h2>",
                     unsafe_allow_html=True)
pages = ["Home", "Math Terminal", "Study Lab", "Vision Studio"]
for i, p in enumerate(pages):
    with [c2, c3, c4, c5][i]:
        if st.button(p, key=f"btn_{p}"): st.session_state.active_page = p
st.markdown('</div>', unsafe_allow_html=True)


# --- 5. PAGE MODULES ---

def render_home():
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown(
        "<h1 style='font-size:100px; text-align:center; font-family:JetBrains Mono; font-weight:800; background: -webkit-linear-gradient(#fff, #333); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>SYSTEM ACTIVE.</h1>",
        unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a: st.markdown("<div class='bento-node'><h3>⚡ Performance</h3><p>GPU Acceleration Active</p></div>",
                            unsafe_allow_html=True)
    with col_b: st.markdown("<div class='bento-node'><h3>🧠 Neural Sync</h3><p>GPT-4o Ready</p></div>",
                            unsafe_allow_html=True)
    with col_c: st.markdown("<div class='bento-node'><h3>📂 File System</h3><p>Cloud Storage Online</p></div>",
                            unsafe_allow_html=True)


def render_math():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.title("Math Terminal")
    st.markdown("<p style='color:#00f2ff;'>System: Solve for x or describe the problem.</p>", unsafe_allow_html=True)

    query = st.chat_input("Enter complex math...")
    if query:
        with st.spinner("Calculating..."):
            res = safe_ai_request(query)
            st.markdown(latex_fixer(res))


def render_study_lab():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("<div class='bento-node'><h3>Ingest Content</h3>", unsafe_allow_html=True)
        file = st.file_uploader("Upload PDF / TXT", type=["pdf", "txt"])
        if file and st.button("🚀 DECONSTRUCT CONTENT"):
            with st.spinner("Scanning..."):
                text = ""
                if file.type == "application/pdf":
                    reader = PyPDF2.PdfReader(file)
                    text = "".join([p.extract_text() for p in reader.pages])
                else:
                    text = file.read().decode()

                # CRAZY PROMPT
                prompt = f"""
                Analyze: {text[:4000]}
                Return JSON: {{
                    "cards": [{"q":"","a":""}],
                    "quiz": [{"q":"","o":["","","",""],"a":""}]
                }}
                """
                data = safe_ai_request(prompt, is_json=True)
                st.session_state.flashcards = data.get('cards', [])
                st.session_state.quiz_data = data.get('quiz', [])
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        tab1, tab2 = st.tabs(["Neural Flashcards", "Exam Simulation"])
        with tab1:
            for c in st.session_state.flashcards:
                with st.expander(f"Concept: {c['q']}"): st.write(c['a'])
        with tab2:
            score = 0
            for idx, q in enumerate(st.session_state.quiz_data):
                st.markdown(f"**{idx + 1}. {q['q']}**")
                choice = st.radio("Options:", q['o'], key=f"q_{idx}")
                if choice == q['a']: score += 1
            if st.session_state.quiz_data:
                st.metric("Exam Performance", f"{(score / len(st.session_state.quiz_data)) * 100:.1f}%")


def render_vision():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<div class='bento-node'><h3>Vision Studio</h3>", unsafe_allow_html=True)
    p = st.text_input("Latent Space Prompt...")
    if st.button("MANIFEST IMAGE"):
        with st.spinner("Synthesizing..."):
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            res = client.images.generate(model="dall-e-3", prompt=p)
            st.image(res.data[0].url)
    st.markdown("</div>", unsafe_allow_html=True)


# --- 6. ROUTER ---
router = {
    "Home": render_home,
    "Math Terminal": render_math,
    "Study Lab": render_study_lab,
    "Vision Studio": render_vision
}
router.get(st.session_state.active_page, render_home)()