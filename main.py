import streamlit as st
import openai
import base64
import json

# --- 1. SYSTEM CORE ---
st.set_page_config(page_title="CogniAI | Infinity OS", page_icon="♾️", layout="wide")

# --- 2. PREMIUM OS AESTHETIC (CSS) ---
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
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 80px;
        background: rgba(0,0,0,0.8);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255,255,255,0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 5%;
        z-index: 9999;
    }

    .vision-container {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 32px;
        padding: 40px;
        backdrop-filter: blur(10px);
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

# Top Nav - BUTTON NAMES MUST MATCH ROUTER KEYS
st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
with c1: st.markdown("<h2 style='margin:0; font-family:Space Grotesk;'>COGNIAI</h2>", unsafe_allow_html=True)
with c2:
    if st.button("Home"): st.session_state.active_page = 'Home'
with c3:
    if st.button("Math"): st.session_state.active_page = 'Math'
with c4:
    if st.button("Study Lab"): st.session_state.active_page = 'Study'
with c5:
    if st.button("Vision"): st.session_state.active_page = 'Vision'
st.markdown('</div>', unsafe_allow_html=True)


def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')


# --- 4. PAGE MODULES ---

def render_home():
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:80px; font-family:Space Grotesk; text-align:center;'>INFINITY OS</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888;'>Select a module from the navigation bar to begin.</p>",
                unsafe_allow_html=True)


def render_math():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    col_t, col_c = st.columns([4, 1])
    with col_t:
        st.markdown("<h1>Math Terminal</h1>", unsafe_allow_html=True)
    with col_c:
        if st.button("🗑️ Clear Chat"):
            st.session_state.math_history = []
            st.rerun()

    uploaded_file = st.file_uploader("Upload Math Image", type=["jpg", "jpeg", "png"])

    for m in st.session_state.math_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("Ask a question..."):
        st.session_state.math_history.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.markdown(p)

        with st.chat_message("assistant"):
            try:
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                messages = [{
                    "role": "system",
                    "content": "You are a math solver. ALWAYS wrap math in double dollar signs $$...$$ for blocks and single $...$ for inline. Example: $$\\frac{x}{y}$$. NEVER use raw brackets [ ] or parentheses ( ) for equations."
                }]

                if uploaded_file:
                    base64_img = encode_image(uploaded_file)
                    messages.append({"role": "user", "content": [{"type": "text", "text": p}, {"type": "image_url",
                                                                                               "image_url": {
                                                                                                   "url": f"data:image/jpeg;base64,{base64_img}"}}]})
                else:
                    messages.append({"role": "user", "content": p})

                stream = client.chat.completions.create(model="gpt-4o", messages=messages, stream=True)
                resp = st.write_stream(stream)
                st.session_state.math_history.append({"role": "assistant", "content": resp})
            except:
                st.error("API Key error.")


def render_study_lab():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1>Study Lab</h1>", unsafe_allow_html=True)
    st.info("Module ready for PDF upload and AI note processing.")


def render_vision():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Vision Studio</h1>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="vision-container">', unsafe_allow_html=True)
        with st.form("v_form"):
            prompt = st.text_area("Prompt", placeholder="Enter your vision...")
            if st.form_submit_button("✨ Launch Generation") and prompt:
                try:
                    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                    with st.spinner("Processing..."):
                        res = client.images.generate(model="dall-e-3", prompt=prompt)
                        st.image(res.data[0].url, use_container_width=True)
                except Exception as e:
                    st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)


# --- 5. ROUTER (The KeyError Fix) ---
pages = {
    "Home": render_home,
    "Math": render_math,
    "Study Lab": render_study_lab,  # Key matches exactly with button name
    "Vision": render_vision
}

# Run current page
if st.session_state.active_page in pages:
    pages[st.session_state.active_page]()
else:
    render_home()