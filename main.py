import streamlit as st
import openai
import base64
import json

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


def render_math():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Math Terminal</h1>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Math Image", type=["jpg", "jpeg", "png"])
    if uploaded_file: st.image(uploaded_file, width=300)

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

                # STRICTOR SYSTEM PROMPT TO FORCE PROPER FORMATTING
                messages = [{
                    "role": "system",
                    "content": """You are Math Prime. 
                    NEVER use square brackets like [x+y] or parentheses like (20x) for equations. 
                    ALWAYS use double dollar signs for centered equations: $$x + y = \\frac{200}{3}$$
                    ALWAYS use single dollar signs for math inside sentences: $20x$.
                    Format fractions as \\frac{a}{b}."""
                }]

                if uploaded_file:
                    base64_img = encode_image(uploaded_file)
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": p if p else "Solve this."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                        ]
                    })
                else:
                    messages.append({"role": "user", "content": p})

                stream = client.chat.completions.create(model="gpt-4o", messages=messages, stream=True)
                resp = st.write_stream(stream)
                st.session_state.math_history.append({"role": "assistant", "content": resp})
            except Exception as e:
                st.error("API Key error. Please check your secrets.")


def render_study_lab():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Study Lab</h1>", unsafe_allow_html=True)


def render_vision():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Vision Studio</h1>", unsafe_allow_html=True)


# --- 5. ROUTER ---
pages = {"Home": render_home, "Math": render_math, "Study": render_study_lab, "Vision": render_vision}
pages[st.session_state.active_page]()