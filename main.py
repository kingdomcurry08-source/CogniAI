import streamlit as st
import openai
import base64
import re
import io

# --- 1. SYSTEM CORE ---
st.set_page_config(page_title="CogniAI | Infinity OS", page_icon="♾️", layout="wide")

# --- 2. THE OS UI (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        background-image: radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.15) 0px, transparent 50%);
        color: #ffffff !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    [data-testid="stHeader"] { display: none; }
    .nav-bar {
        position: fixed; top: 0; left: 0; right: 0; height: 80px;
        background: rgba(0,0,0,0.8); backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255,255,255,0.1);
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 5%; z-index: 9999;
    }
    .bento-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px; padding: 30px; margin-bottom: 20px;
    }
    .stButton>button {
        background: #ffffff !important; color: #000 !important;
        border-radius: 50px !important; font-weight: 700 !important;
        padding: 10px 25px !important; border: none !important;
    }
    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


# --- 3. THE MATH FORMATTER ---
def latex_fixer(text):
    """Ensures math is rendered as symbols, not code."""
    text = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'$\\frac{\1}{\2}$', text)
    text = re.sub(r'\\sqrt\{([^}]*)\}', r'$\\sqrt{\1}$', text)
    return text


# --- 4. STATE ENGINE ---
if 'active_page' not in st.session_state: st.session_state.active_page = 'Home'
if 'math_history' not in st.session_state: st.session_state.math_history = []
if 'flashcards' not in st.session_state: st.session_state.flashcards = []

# Top Nav
st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
with c1: st.markdown("<h2 style='margin:0; font-family:Space Grotesk;'>COGNIAI</h2>", unsafe_allow_html=True)
with c2:
    if st.button("Home"): st.session_state.active_page = 'Home'
with c3:
    if st.button("Math"): st.session_state.active_page = 'Math'
with c4:
    if st.button("Study Lab"): st.session_state.active_page = 'Study Lab'
with c5:
    if st.button("Vision"): st.session_state.active_page = 'Vision'
st.markdown('</div>', unsafe_allow_html=True)


# --- 5. PAGE MODULES ---

def render_home():
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:80px; font-family:Space Grotesk; text-align:center;'>INFINITY OS</h1>",
                unsafe_allow_html=True)


def render_math():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1>Math Terminal</h1>", unsafe_allow_html=True)
    for m in st.session_state.math_history:
        with st.chat_message(m["role"]): st.markdown(latex_fixer(m["content"]))
    if p := st.chat_input("Ask math..."):
        st.session_state.math_history.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.markdown(p)
        with st.chat_message("assistant"):
            try:
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                stream = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": p}],
                                                        stream=True)
                resp = st.write_stream(stream)
                st.session_state.math_history.append({"role": "assistant", "content": resp})
            except:
                st.error("Key Error.")


def render_study_lab():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1>Study Lab</h1>", unsafe_allow_html=True)

    col_upload, col_display = st.columns([1, 2])

    with col_upload:
        st.markdown("<div class='bento-card'><h3>📁 Source</h3><p>Upload PDF to generate cards.</p></div>",
                    unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Notes", type=["pdf", "txt"])

        if uploaded_file and st.button("✨ Generate Recall Cards"):
            try:
                import PyPDF2
                text = ""
                if uploaded_file.type == "application/pdf":
                    reader = PyPDF2.PdfReader(uploaded_file)
                    for page in reader.pages: text += page.extract_text()
                else:
                    text = uploaded_file.read().decode()

                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system",
                               "content": "Create 5 Q&A flashcards from this text. Format as JSON: [{'q':'question','a':'answer'}]"},
                              {"role": "user", "content": text[:4000]}]
                )
                import json
                st.session_state.flashcards = json.loads(response.choices[0].message.content)
                st.success("Cards Ready!")
            except Exception as e:
                st.error(f"Error: {e}. Ensure 'pip install PyPDF2' is run.")

    with col_display:
        st.markdown("<div class='bento-card' style='min-height:400px;'><h3>🧠 Active Recall Studio</h3>",
                    unsafe_allow_html=True)
        if st.session_state.flashcards:
            for card in st.session_state.flashcards:
                with st.expander(f"Question: {card['q']}"):
                    st.write(card['a'])
        else:
            st.write("Upload notes to start.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_vision():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1>Vision Studio</h1>", unsafe_allow_html=True)
    with st.form("v"):
        p = st.text_input("Prompt")
        if st.form_submit_button("Generate"):
            st.info("Creating...")


# --- 6. ROUTER ---
pages = {"Home": render_home, "Math": render_math, "Study Lab": render_study_lab, "Vision": render_vision}
pages.get(st.session_state.active_page, render_home)()