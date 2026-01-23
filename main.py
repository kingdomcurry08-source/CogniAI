import streamlit as st
import openai
import base64
import json
from PIL import Image
import io

# --- 1. SYSTEM CORE ---
st.set_page_config(page_title="CogniAI | Infinity OS", page_icon="♾️", layout="wide")

# --- 2. THE "COMPETITOR" AESTHETIC (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.1) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.1) 0px, transparent 50%);
        color: #ffffff !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    [data-testid="stHeader"] { display: none; }
    .nav-bar {
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 75px;
        background: rgba(0,0,0,0.8);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255,255,255,0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 5%;
        z-index: 9999;
    }

    .flashcard {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 30px;
        text-align: center;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 20px;
    }

    .bento {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 30px;
        padding: 30px;
        margin-bottom: 20px;
    }

    .stButton>button {
        background: #ffffff !important;
        color: #000 !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        padding: 10px 25px !important;
        border: none !important;
    }

    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. STATE ENGINE ---
if 'active_page' not in st.session_state: st.session_state.active_page = 'Home'
if 'math_history' not in st.session_state: st.session_state.math_history = []
if 'flashcards' not in st.session_state: st.session_state.flashcards = []

# Top Nav
st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
with c1: st.markdown("<h2 style='margin:0; font-family:Space Grotesk;'>COGNIAI</h2>", unsafe_allow_html=True)
with c2:
    if st.button("Home", key="n1"): st.session_state.active_page = 'Home'
with c3:
    if st.button("Math", key="n2"): st.session_state.active_page = 'Math'
with c4:
    if st.button("Study Lab", key="n3"): st.session_state.active_page = 'Study'
with c5:
    if st.button("Vision", key="n4"): st.session_state.active_page = 'Vision'
st.markdown('</div>', unsafe_allow_html=True)


def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')


# --- 4. PAGE MODULES ---

def render_home():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:80px; font-family:Space Grotesk; text-align:center;'>THE END OF<br>AVERAGE.</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:#888; font-size:20px;'>The first AI operating system for academic mastery.</p>",
        unsafe_allow_html=True)


def render_math():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Math Terminal</h1>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Math Image", type=["jpg", "jpeg", "png"])

    # Display History with LaTeX support
    for m in st.session_state.math_history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if p := st.chat_input("Ask or upload a problem..."):
        st.session_state.math_history.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.markdown(p)

        with st.chat_message("assistant"):
            try:
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                # Updated System Prompt to ensure proper LaTeX formatting
                messages = [{
                    "role": "system",
                    "content": "You are Math Prime. Solve step-by-step. Use LaTeX for ALL math equations (e.g., use $...$ for inline and $$...$$ for blocks). Ensure fractions use \\frac{a}{b}."
                }]

                if uploaded_file:
                    base64_img = encode_image(uploaded_file)
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": p if p else "Solve the problem in this image."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                        ]
                    })
                else:
                    messages.append({"role": "user", "content": p})

                stream = client.chat.completions.create(model="gpt-4o", messages=messages, stream=True)
                # write_stream automatically handles Markdown + LaTeX
                resp = st.write_stream(stream)
                st.session_state.math_history.append({"role": "assistant", "content": resp})
            except Exception as e:
                st.error("Please add your OPENAI_API_KEY to .streamlit/secrets.toml")


def render_study_lab():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Study Lab</h1>", unsafe_allow_html=True)

    notes = st.file_uploader("Upload Notes (PDF/TXT)", type=["pdf", "txt"])

    if notes and st.button("✨ Generate AI Flashcards", use_container_width=True):
        with st.spinner("Processing..."):
            try:
                content = ""
                if notes.type == "text/plain":
                    content = notes.read().decode()
                else:
                    import PyPDF2
                    pdf = PyPDF2.PdfReader(notes)
                    for page in pdf.pages: content += page.extract_text()

                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system",
                               "content": "Create 4 flashcards from these notes. Return ONLY a JSON list: [{'q': 'question', 'a': 'answer'}]. Use LaTeX for math."},
                              {"role": "user", "content": content[:4000]}]
                )
                st.session_state.flashcards = json.loads(response.choices[0].message.content)
            except:
                st.error("Make sure PyPDF2 is installed and API Key is valid.")

    if st.session_state.flashcards:
        cols = st.columns(2)
        for i, card in enumerate(st.session_state.flashcards):
            with cols[i % 2]:
                with st.expander(f"Topic {i + 1}: {card['q']}"):
                    st.write(card['a'])


def render_vision():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Vision Studio</h1>", unsafe_allow_html=True)
    with st.form("v_form"):
        prompt = st.text_input("Creative Prompt")
        if st.form_submit_button("Generate") and prompt:
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            res = client.images.generate(model="dall-e-3", prompt=prompt)
            st.image(res.data[0].url)


# --- 5. ROUTER ---
pages = {"Home": render_home, "Math": render_math, "Study": render_study_lab, "Vision": render_vision}
pages[st.session_state.active_page]()