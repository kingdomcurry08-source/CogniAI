import streamlit as st
import openai
import base64
import re

# --- 1. SYSTEM CORE ---
st.set_page_config(page_title="CogniAI | Infinity OS", page_icon="♾️", layout="wide")

# --- 2. PREMIUM OS UI (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.15) 0px, transparent 50%);
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
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px; padding: 30px; margin-bottom: 20px;
        transition: 0.3s ease;
    }

    .bento-card:hover { border-color: #3b82f6; background: rgba(255, 255, 255, 0.05); }

    .stButton>button {
        background: #ffffff !important; color: #000 !important;
        border-radius: 50px !important; font-weight: 700 !important;
        padding: 10px 25px !important; border: none !important;
    }

    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


# --- 3. THE MATH FORMATTER ENGINE ---
def latex_fixer(text):
    """Scan and convert raw LaTeX strings into Streamlit-friendly $ symbols."""
    # Wraps \frac{...}{...} in dollar signs
    text = re.sub(r'(\\frac\{.*?\}.*?\}|\\sqrt\{.*?\})', r' $\1$ ', text)
    # Fixes variables like (x) or (y) into $x$ and $y$
    text = re.sub(r'\(([a-zA-Z0-9])\)', r'$\1$', text)
    # Fixes raw equations like x + y = 60
    text = re.sub(r'(\d+[a-zA-Z]\s*[\+\-\*\/]\s*\d+[a-zA-Z]\s*\=\s*\d+)', r' $$\1$$ ', text)
    return text


# --- 4. STATE ENGINE ---
if 'active_page' not in st.session_state: st.session_state.active_page = 'Home'
if 'math_history' not in st.session_state: st.session_state.math_history = []

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
    st.markdown("<h1 style='font-size:90px; font-family:Space Grotesk; text-align:center;'>INFINITY OS</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666;'>Automating intelligence. Choose a module to begin.</p>",
                unsafe_allow_html=True)


def render_math():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1>Math Terminal</h1>", unsafe_allow_html=True)

    for m in st.session_state.math_history:
        with st.chat_message(m["role"]):
            # Applying the fixer here so the user sees symbols, not code
            st.markdown(latex_fixer(m["content"]))

    if p := st.chat_input("Input equation or upload screen..."):
        st.session_state.math_history.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.markdown(p)
        with st.chat_message("assistant"):
            try:
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                stream = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "You are a math solver. Use LaTeX format."},
                              {"role": "user", "content": p}],
                    stream=True
                )
                resp = st.write_stream(stream)
                st.session_state.math_history.append({"role": "assistant", "content": resp})
            except:
                st.error("Add OpenAI Key to secrets.")


def render_study_lab():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1>Study Lab</h1>", unsafe_allow_html=True)

    col_upload, col_display = st.columns([1, 2])

    with col_upload:
        st.markdown(
            "<div class='bento-card'><h3>📁 Source Material</h3><p>Upload PDFs, images of notes, or text files.</p></div>",
            unsafe_allow_html=True)
        uploaded_notes = st.file_uploader("Drop files here", type=["pdf", "txt", "png", "jpg"])

        if uploaded_notes:
            st.success("File Received.")
            if st.button("✨ Generate Active Recall"):
                st.session_state.recall_ready = True

    with col_display:
        st.markdown("<div class='bento-card' style='min-height:400px;'><h3>🧠 Active Recall Studio</h3>",
                    unsafe_allow_html=True)
        if st.session_state.get('recall_ready'):
            st.info("AI is deconstructing your notes into flashcards...")
            # Here we would call the GPT-4o logic to create flashcards
        else:
            st.write("Your generated study materials will appear here once you upload a file.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_vision():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1>Vision Studio</h1>", unsafe_allow_html=True)
    with st.form("vision_form"):
        prompt = st.text_input("Enter Prompt")
        if st.form_submit_button("Generate"):
            st.info("Creating image...")


# --- 6. ROUTER ---
pages = {
    "Home": render_home,
    "Math": render_math,
    "Study Lab": render_study_lab,
    "Vision": render_vision
}

# Run the page
pages.get(st.session_state.active_page, render_home)()