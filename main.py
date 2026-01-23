import streamlit as st
import openai
import base64
from PIL import Image
import io
import requests

# --- 1. SYSTEM CORE ---
st.set_page_config(page_title="CogniAI | Infinity OS", page_icon="♾️", layout="wide")

# --- 2. CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #000000 !important;
    background-image: radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.1) 0px, transparent 50%),
                      radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.1) 0px, transparent 50%);
    color: #ffffff !important;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

[data-testid="stHeader"] { display: none; }
.nav-bar { position: fixed; top:0; left:0; right:0; height:75px; background: rgba(0,0,0,0.8);
    backdrop-filter: blur(20px); border-bottom: 1px solid rgba(255,255,255,0.08);
    display:flex; align-items:center; justify-content:space-between; padding:0 5%; z-index:9999;}
.flashcard { background: rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1);
    border-radius:24px; padding:40px; text-align:center; min-height:250px;
    display:flex; flex-direction:column; justify-content:center; transition:0.4s; cursor:pointer; }
.flashcard:hover { border-color:#00f2ff; box-shadow:0 0 30px rgba(0,242,255,0.1); }
.stFileUploader { background: rgba(255,255,255,0.02); border:2px dashed rgba(255,255,255,0.1); border-radius:20px; padding:20px;}
.bento { background: rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.08); border-radius:30px; padding:30px; margin-bottom:20px;}
.stButton>button { background:#ffffff !important; color:#000 !important; border-radius:50px !important; font-weight:700 !important; padding:10px 25px !important; border:none !important;}
[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'active_page' not in st.session_state: st.session_state.active_page = 'Home'
if 'math_history' not in st.session_state: st.session_state.math_history = []
if 'study_history' not in st.session_state: st.session_state.study_history = []

# --- 4. NAVBAR ---
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


# --- 5. HELPER ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')


# --- 6. PAGES ---
def render_home():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:80px; font-family:Space Grotesk; text-align:center;'>THE END OF<br>AVERAGE.</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:#888; font-size:20px;'>The first AI operating system designed to destroy academic barriers.</p>",
        unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown(
            "<div class='bento'><h2>📸 Scan & Solve</h2><p style='color:#666;'>Upload a photo of your math textbook or notes. CogniAI solves it step-by-step instantly.</p></div>",
            unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800")
    with col_r:
        st.markdown(
            "<div class='bento'><h2>📝 Note-to-Test</h2><p style='color:#666;'>Upload lecture slides or notes. CogniAI generates flashcards and practice tests automatically.</p></div>",
            unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1454165833767-027eeef1593e?w=800")


def render_math():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Math Terminal</h1>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Math Image (JPG/PNG)", type=["jpg", "jpeg", "png"])

    for m in st.session_state.math_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    col_input, col_send = st.columns([4, 1])
    with col_input:
        user_input = st.text_input("Ask or upload a problem...", key="math_input")
    with col_send:
        send = st.button("Send", key="math_send")

    if send and user_input:
        st.session_state.math_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            client = openai.OpenAI(api_key=st.secrets["openai"]["api_key"])
            messages = [{"role": "system", "content": "You are Math Prime. Solve step-by-step. NO LaTeX."}]
            if uploaded_file:
                base64_img = encode_image(uploaded_file)
                messages.append({"role": "user", "content": [{"type": "text", "text": user_input}, {"type": "image_url",
                                                                                                    "image_url": {
                                                                                                        "url": f"data:image/jpeg;base64,{base64_img}"}}]})
            else:
                messages.append({"role": "user", "content": user_input})
            stream = client.chat.completions.create(model="gpt-4o", messages=messages, stream=True)
            resp = st.write_stream(stream)
            st.session_state.math_history.append({"role": "assistant", "content": resp})


def render_study_lab():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Study Lab</h1>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center; color:#888;'>Upload your notes to generate flashcards and practice tests.</div><br>",
        unsafe_allow_html=True)

    notes = st.file_uploader("Drop notes or images here", type=["pdf", "png", "jpg", "txt"])

    tab1, tab2 = st.tabs(["🗂️ Flashcards", "📝 Practice Test"])

    with tab1:
        col_input, col_send = st.columns([4, 1])
        with col_input:
            question_input = st.text_input("Ask a study question...", key="study_input")
        with col_send:
            send_question = st.button("Send", key="study_send")

        if send_question and question_input:
            st.session_state.study_history.append({"role": "user", "content": question_input})
            with st.chat_message("user"): st.markdown(question_input)
            with st.chat_message("assistant"):
                client = openai.OpenAI(api_key=st.secrets["openai"]["api_key"])
                messages = [{"role": "system", "content": "You are Study Lab AI. Generate study answers step-by-step."}]
                messages.append({"role": "user", "content": question_input})
                stream = client.chat.completions.create(model="gpt-4o", messages=messages, stream=True)
                resp = st.write_stream(stream)
                st.session_state.study_history.append({"role": "assistant", "content": resp})

    with tab2:
        if notes:
            st.markdown("### Generated Exam")
            st.markdown("1. Example question generated from notes")
            st.text_area("Your Answer")
            st.button("Grade My Exam")
        else:
            st.info("Upload notes to generate exam questions.")


def render_vision():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Vision Studio</h1>", unsafe_allow_html=True)

    col_input, col_send = st.columns([4, 1])
    with col_input:
        prompt_input = st.text_input("Describe your vision...", key="vision_input")
    with col_send:
        send_prompt = st.button("Generate", key="vision_send")

    if send_prompt and prompt_input:
        try:
            client = openai.OpenAI(api_key=st.secrets["openai"]["api_key"])
            with st.spinner("Generating image..."):
                response = client.images.generate(
                    model="gpt-image-1",
                    prompt=prompt_input,
                    size="1024x1024",
                    n=1
                )
                image_url = response.data[0].url
                image = Image.open(io.BytesIO(requests.get(image_url).content))
                st.image(image, caption="Generated by CogniAI")
        except KeyError:
            st.error("OpenAI API key not found! Add it in Streamlit secrets first.")
        except (openai.error.APIError, openai.error.InvalidRequestError, openai.error.AuthenticationError) as e:
            if hasattr(e, "http_status") and e.http_status == 403:
                st.warning(
                    "Your API key does not have image generation access. "
                    "Upgrade your OpenAI plan to use Vision Studio."
                )
            else:
                st.error(f"OpenAI API error: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")


# --- 7. ROUTER ---
if st.session_state.active_page == 'Home':
    render_home()
elif st.session_state.active_page == 'Math':
    render_math()
elif st.session_state.active_page == 'Study':
    render_study_lab()
elif st.session_state.active_page == 'Vision':
    render_vision()
