import streamlit as st
import openai
import base64
from PIL import Image
import io

# --- 1. SYSTEM CORE ---
st.set_page_config(page_title="CogniAI | Infinity OS", page_icon="♾️", layout="wide")

# --- 2. THE "COMPETITOR" AESTHETIC (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&display=swap');

    /* DARK MODE 2.0 */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.1) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.1) 0px, transparent 50%);
        color: #ffffff !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* NEON GLASS NAV */
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

    /* FLASHCARD UI */
    .flashcard {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 40px;
        text-align: center;
        min-height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: 0.4s;
        cursor: pointer;
        margin-bottom: 20px;
    }
    .flashcard:hover {
        border-color: #00f2ff;
        box-shadow: 0 0 30px rgba(0, 242, 255, 0.1);
    }

    /* BENTO CARDS */
    .bento {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 30px;
        padding: 30px;
        margin-bottom: 20px;
    }

    /* BUTTONS */
    .stButton>button {
        background: #ffffff !important;
        color: #000 !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        padding: 10px 25px !important;
        border: none !important;
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        background: #00f2ff !important;
    }

    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. STATE ENGINE ---
if 'active_page' not in st.session_state: st.session_state.active_page = 'Home'
if 'math_history' not in st.session_state: st.session_state.math_history = []
if 'notes_processed' not in st.session_state: st.session_state.notes_processed = False

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


# Helper: Convert Image to Base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')


# --- 4. PAGE MODULES ---

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
            "<div class='bento'><h2>📸 Scan & Solve</h2><p style='color:#ccc;'>Upload a photo of your math textbook or handwritten notes. Our neural engine deconstructs the logic and provides a step-by-step walkthrough instantly.</p></div>",
            unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800")
    with col_r:
        st.markdown(
            "<div class='bento'><h2>📝 Note-to-Test</h2><p style='color:#ccc;'>Drop your lecture slides or notes. CogniAI generates custom flashcards and full-length practice exams based 100% on your specific material.</p></div>",
            unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1454165833767-027eeef1593e?w=800")


def render_math():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Math Terminal</h1>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Math Image (JPG/PNG)", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Analyzing Problem...", width=300)

    for m in st.session_state.math_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("Ask or upload a problem..."):
        st.session_state.math_history.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.markdown(p)

        with st.chat_message("assistant"):
            try:
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                messages = [{"role": "system",
                             "content": "You are Math Prime. Solve step-by-step. Use plain text formatting, avoid complex LaTeX."}]

                if uploaded_file:
                    base64_img = encode_image(uploaded_file)
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": p if p else "Solve this problem."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                        ]
                    })
                else:
                    messages.append({"role": "user", "content": p})

                stream = client.chat.completions.create(model="gpt-4o", messages=messages, stream=True)
                resp = st.write_stream(stream)
                st.session_state.math_history.append({"role": "assistant", "content": resp})
            except Exception as e:
                st.error("API Key not found or invalid. Please check your secrets.")


def render_study_lab():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Study Lab</h1>", unsafe_allow_html=True)

    st.markdown(
        "<div style='text-align:center; color:#888;'>Upload your notes to generate practice materials.</div><br>",
        unsafe_allow_html=True)

    notes = st.file_uploader("Drop notes or images here", type=["pdf", "png", "jpg", "txt"])

    if notes:
        if st.button("✨ Generate Study Materials", use_container_width=True):
            st.session_state.notes_processed = True

    tab1, tab2 = st.tabs(["🗂️ Flashcards", "📝 Practice Test"])

    with tab1:
        if notes and st.session_state.notes_processed:
            st.success("Notes Processed.")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    "<div class='flashcard'><h3>What is photosynthesis?</h3><p style='color:#555;'>(Click to flip)</p></div>",
                    unsafe_allow_html=True)
            with c2:
                st.markdown(
                    "<div class='flashcard'><h3>Define Mitochondria</h3><p style='color:#555;'>(Click to flip)</p></div>",
                    unsafe_allow_html=True)
        else:
            st.info("Upload notes and click 'Generate' to see flashcards.")

    with tab2:
        if notes and st.session_state.notes_processed:
            st.markdown("### Generated Exam: Chapter 1")
            st.markdown("1. Explain the process of cellular respiration.")
            st.text_area("Your Answer", placeholder="Type your response here...")
            st.button("Grade My Exam")
        else:
            st.info("Upload notes to generate a custom test.")


def render_vision():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Vision Studio</h1>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='bento'>", unsafe_allow_html=True)
        with st.form("vision_engine"):
            prompt = st.text_input("Describe your vision...", placeholder="A futuristic laboratory in space...")
            style = st.selectbox("Style", ["Photorealistic", "Cinematic", "Digital Art", "Cyberpunk"])
            submit = st.form_submit_button("Generate Masterpiece")

            if submit:
                if prompt:
                    st.info(f"Generating {style} image: {prompt}...")
                    # DALL-E 3 Logic would go here
                else:
                    st.warning("Please provide a prompt.")
        st.markdown("</div>", unsafe_allow_html=True)


# --- 5. ROUTER ---
if st.session_state.active_page == 'Home':
    render_home()
elif st.session_state.active_page == 'Math':
    render_math()
elif st.session_state.active_page == 'Study':
    render_study_lab()
elif st.session_state.active_page == 'Vision':
    render_vision()