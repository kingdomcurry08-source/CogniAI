import streamlit as st
import openai
import json
import pdfplumber
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- 1. NEURAL INTERFACE (CYBER-GLOW) ---
st.set_page_config(page_title="CogniAI | Sentient Study", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(0, 255, 65, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(0, 255, 65, 0); } 100% { box-shadow: 0 0 0 0 rgba(0, 255, 65, 0); } }
    .stApp { background: #000; color: #00FF41; }
    .alive-card {
        border: 1px solid #00FF41; padding: 25px; border-radius: 15px;
        background: rgba(0, 255, 65, 0.02); animation: pulse 2s infinite;
        margin-bottom: 20px;
    }
    .mastery-stat { font-family: 'Fira Code', monospace; font-size: 24px; color: #00FF41; }
    </style>
    """, unsafe_allow_html=True)


# --- 2. PERSISTENT MEMORY ---
def init_db():
    conn = sqlite3.connect('cogniai_omega.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS user_data (id INT PRIMARY KEY, xp INT, level INT, energy INT)')
    conn.execute('CREATE TABLE IF NOT EXISTS cards (q TEXT, a TEXT, mastery INT)')
    if not conn.execute('SELECT * FROM user_data WHERE id=1').fetchone():
        conn.execute('INSERT INTO user_data VALUES (1, 0, 1, 100)')
    conn.commit()
    return conn


db = init_db()


# --- 3. VOICE & VISION (THE "ALIVE" PART) ---
def speak(text):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    response = client.audio.speech.create(model="tts-1", voice="nova", input=text[:4096])
    return response.content


def process_visual_reasoning(text):
    # This simulates "Neural Thought"
    with st.status("🧠 Deep-Scanning Neural Pathways...", expanded=True) as status:
        st.write("Initializing context windows...")
        time.sleep(1)
        st.write("Extracting semantic entities...")
        time.sleep(1)
        st.write("Synthesizing mastery nodes...")
        status.update(label="Sync Complete!", state="complete", expanded=False)


# --- 4. THE HUD (Heads-Up Display) ---
xp, level, energy = db.execute('SELECT xp, level, energy FROM user_data WHERE id=1').fetchone()

with st.sidebar:
    st.markdown(f"<div class='alive-card'>", unsafe_allow_html=True)
    st.title("👤 ARCHITECT")
    st.markdown(f"<div class='mastery-stat'>LVL: {level}</div>", unsafe_allow_html=True)
    st.progress(xp / 100)
    st.write(f"⚡ Energy: {energy}%")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("☣️ PURGE CORE"):
        db.execute('DELETE FROM cards');
        db.commit();
        st.rerun()

# --- 5. MAIN OMNI-TERMINAL ---
tabs = st.tabs(["⚡ SYNC", "🧠 RECALL", "🎤 BRIEFING", "🖼️ GENERATOR"])

with tabs[0]:  # SYNC
    st.markdown("<div class='alive-card'>", unsafe_allow_html=True)
    mode = st.radio("Select Ingestion Mode", ["Digital PDF", "Mental Paste"], horizontal=True)

    input_text = ""
    if mode == "Digital PDF":
        up = st.file_uploader("Drop Neural Data (PDF)")
        if up:
            with pdfplumber.open(up) as pdf: input_text = "\n".join(
                [p.extract_text() for p in pdf.pages if p.extract_text()])
    else:
        input_text = st.text_area("Paste Raw Intelligence...", height=200)

    if st.button("🔥 INITIATE DEEP SYNC"):
        process_visual_reasoning(input_text)
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": "Generate 15 flashcards. Return JSON: {'cards':[{'q':'','a':''}]}"},
                      {"role": "user", "content": input_text}]
        )
        data = json.loads(res.choices[0].message.content)
        for c in data['cards']:
            db.execute('INSERT INTO cards VALUES (?,?,0)', (c['q'], c['a']))
        db.execute('UPDATE user_data SET xp = xp + 20 WHERE id=1')
        db.commit()
        st.balloons()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]:  # RECALL
    st.subheader("Neural Practice Exam")
    nodes = db.execute('SELECT q, a FROM cards').fetchall()
    if nodes:
        node = random.choice(nodes)
        st.markdown(f"<div class='alive-card'><h3>{node[0]}</h3></div>", unsafe_allow_html=True)
        if st.button("REVEAL"):
            st.success(node[1])
            if st.button("I MASTERED THIS (+5 XP)"):
                db.execute('UPDATE user_data SET xp = xp + 5 WHERE id=1');
                db.commit()
                st.rerun()
    else:
        st.info("Neural core empty. Awaiting ingestion.")

with tabs[2]:  # BRIEFING
    st.subheader("Vocal Briefing")
    st.write("The AI will summarize your notes into a 2-minute audio briefing.")
    if st.button("🎧 PLAY NEURAL SUMMARY"):
        # Logic to grab the latest summary and play via 'speak' function
        pass

with tabs[3]:  # PHOTO
    st.subheader("AI PHOTO GENERATOR")
    prompt = st.text_input("Manifest visual thought...")
    if st.button("MANIFEST"):
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        img = client.images.generate(model="dall-e-3", prompt=prompt)
        st.image(img.data[0].url)