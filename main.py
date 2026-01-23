import streamlit as st
import openai
import json
import pdfplumber
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- 1. SYSTEM INITIALIZATION ---
st.set_page_config(page_title="CogniAI | God Tier", page_icon="♾️", layout="wide")


def init_db():
    conn = sqlite3.connect('cogniai_omega.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS profile (id INT PRIMARY KEY, xp INT, lvl INT, rank TEXT)')
    conn.execute('''CREATE TABLE IF NOT EXISTS memory_nodes
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY,
                        q
                        TEXT,
                        a
                        TEXT,
                        easiness
                        REAL,
                        interval
                        INT,
                        next_review
                        DATE
                    )''')
    if not conn.execute('SELECT * FROM profile WHERE id=1').fetchone():
        conn.execute('INSERT INTO profile VALUES (1, 0, 1, "NEOPHYTE")')
    conn.commit()
    return conn


db = init_db()


# --- 2. THE FAIL-SAFE SYNTHESIS ENGINE ---
def robust_sync(text, creativity, velocity):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    model = "gpt-4o" if velocity == "Deep Logic" else "gpt-4o-mini"

    # Split 12+ pages into 5000-character blocks
    chunks = [text[i:i + 5000] for i in range(0, len(text), 5000)]

    st.info(f"System detected {len(text)} characters. Processing {len(chunks)} Neural Blocks...")

    for i, chunk in enumerate(chunks):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=creativity,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system",
                     "content": "You are CogniAI. You MUST extract 10-15 detailed flashcards from this text. Return JSON: {'cards': [{'q':'','a':''}]}"},
                    {"role": "user", "content": chunk}
                ]
            )
            raw_res = response.choices[0].message.content
            data = json.loads(raw_res)

            if "cards" in data:
                for card in data['cards']:
                    db.execute('INSERT INTO memory_nodes (q, a, easiness, interval, next_review) VALUES (?,?,?,?,?)',
                               (card['q'], card['a'], 2.5, 0, datetime.now().date()))
                db.commit()
            else:
                st.warning(f"Block {i + 1} returned no cards. Check AI response format.")
        except Exception as e:
            st.error(f"Neural Error in Block {i + 1}: {str(e)}")
            continue


# --- 3. UI COSMETICS ---
st.markdown("""
    <style>
    .stApp { background: #000; color: #00FF41; font-family: 'Courier New', monospace; }
    .omni-panel { border: 1px solid #00FF41; padding: 20px; border-radius: 10px; background: rgba(0,255,65,0.05); }
    [data-testid="stHeader"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "HOME"
st.title("♾️ COGNIAI")
c1, c2, c3, c4 = st.columns(4)
if c1.button("HOME"): st.session_state.page = "HOME"
if c2.button("STUDY LAB"): st.session_state.page = "LAB"
if c3.button("MATH NEXUS"): st.session_state.page = "MATH"
if c4.button("AI PHOTO GENERATOR"): st.session_state.page = "PHOTO"

# --- 5. MODULES ---
if st.session_state.page == "HOME":
    st.markdown("<div class='omni-panel'><h2>SYSTEM ACTIVE</h2><p>Ready for Data Ingestion.</p></div>",
                unsafe_allow_html=True)
    st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")

elif st.session_state.page == "LAB":
    l, r = st.columns([1, 2])
    with l:
        st.subheader("Data Ingest")
        src = st.selectbox("Source", ["PDF", "URL", "Text Paste"])
        raw_txt = ""

        if src == "PDF":
            up = st.file_uploader("Upload Notes")
            if up:
                with pdfplumber.open(up) as pdf:
                    raw_txt = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        elif src == "URL":
            u = st.text_input("URL")
            if u: raw_txt = BeautifulSoup(requests.get(u).text, 'html.parser').get_text()
        else:
            raw_txt = st.text_area("Paste text here...", height=300)

        if st.button("SYNCHRONIZE") and raw_txt:
            robust_sync(raw_txt, 0.7, "Deep Logic")
            st.rerun()

    with r:
        st.subheader("Neural Recall")
        nodes = db.execute('SELECT q, a FROM memory_nodes').fetchall()
        if nodes:
            st.write(f"Loaded {len(nodes)} total nodes.")
            for n in nodes[::-1][:20]:  # Show latest 20
                with st.expander(f"SCAN: {n[0]}"): st.write(n[1])
        else:
            st.info("Neural Core empty. Synchronize notes to begin.")

elif st.session_state.page == "MATH":
    st.subheader("Math Nexus")
    # ... Math Logic ...

elif st.session_state.page == "PHOTO":
    st.subheader("AI Photo Generator")
    # ... DALL-E Logic ...