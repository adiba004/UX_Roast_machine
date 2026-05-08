import streamlit as st
from openai import OpenAI
from PIL import Image
import base64, io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UI Roast Machine",
    page_icon="🔥",
    layout="wide",
)


# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    background-color: #0a0a0a !important;
    color: #f0ede6 !important;
    font-family: 'DM Mono', monospace !important;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 2rem 4rem 2rem !important; max-width: 780px !important; }

/* ── Hero title ── */
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(3.5rem, 10vw, 6.5rem);
    line-height: 0.92;
    letter-spacing: 0.02em;
    color: #f0ede6;
    margin: 0 0 0.15em 0;
}
.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #ff4d00;
    margin-bottom: 2.8rem;
}

/* ── Mode selector cards ── */
.mode-row {
    display: flex;
    gap: 12px;
    margin-bottom: 2rem;
}
.mode-card {
    flex: 1;
    border: 1.5px solid #2a2a2a;
    padding: 1rem 0.75rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.15s ease;
    background: #111;
}
.mode-card:hover { border-color: #ff4d00; background: #1a1a1a; }
.mode-card.active { border-color: #ff4d00; background: #1a0a00; }

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    border: 1.5px dashed #2a2a2a !important;
    border-radius: 0 !important;
    background: #111 !important;
    padding: 1.2rem !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover { border-color: #ff4d00 !important; }
[data-testid="stFileUploader"] label { color: #888 !important; font-size: 0.78rem !important; }

/* ── Radio buttons → hidden, use our cards ── */
div[data-testid="stRadio"] > label { display: none !important; }
div[data-testid="stRadio"] > div {
    display: flex !important;
    gap: 10px !important;
    flex-direction: row !important;
}
div[data-testid="stRadio"] > div > label {
    display: flex !important;
    flex: 1 !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    border: 1.5px solid #2a2a2a !important;
    background: #111 !important;
    padding: 1rem 0.5rem !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    border-radius: 0 !important;
    font-size: 0.8rem !important;
    color: #888 !important;
    gap: 4px !important;
}
div[data-testid="stRadio"] > div > label:hover {
    border-color: #ff4d00 !important;
    color: #f0ede6 !important;
    background: #1a1a1a !important;
}
div[data-testid="stRadio"] > div > label[data-baseweb="radio"]:has(input:checked),
div[data-testid="stRadio"] > div > label[aria-checked="true"] {
    border-color: #ff4d00 !important;
    background: #1a0a00 !important;
    color: #ff4d00 !important;
}
div[data-testid="stRadio"] input { display: none !important; }

/* ── Roast button ── */
.stButton > button {
    width: 100% !important;
    background: #ff4d00 !important;
    color: #0a0a0a !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.4rem !important;
    letter-spacing: 0.12em !important;
    padding: 0.75rem 0 !important;
    cursor: pointer !important;
    transition: background 0.15s ease !important;
    margin-top: 0.5rem !important;
}
.stButton > button:hover { background: #e64400 !important; }
.stButton > button:disabled {
    background: #2a2a2a !important;
    color: #555 !important;
    cursor: not-allowed !important;
}

/* ── Divider ── */
hr { border-color: #1e1e1e !important; margin: 2rem 0 !important; }

/* ── Roast output box ── */
.roast-box {
    border-left: 3px solid #ff4d00;
    background: #111;
    padding: 1.4rem 1.6rem;
    margin-top: 1.5rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.88rem;
    line-height: 1.9;
    color: #f0ede6;
    white-space: pre-wrap;
}
.roast-line {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.55rem;
    letter-spacing: 0.03em;
    color: #ff4d00;
    line-height: 1.3;
    margin-bottom: 1rem;
    display: block;
}
.fix-label {
    color: #666;
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.fix-value { color: #f0ede6; }

/* ── Streamed text placeholder ── */
[data-testid="stText"] { font-family: 'DM Mono', monospace !important; }

/* ── Image preview ── */
[data-testid="stImage"] img {
    border: 1px solid #1e1e1e !important;
    filter: grayscale(15%);
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #ff4d00 !important; }

/* ── Section label ── */
.section-label {
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #444;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Constants (UNCHANGED) ─────────────────────────────────────────────────────
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=API_KEY,
    timeout=60.0,
)

ROAST_MODES = {
    "1": {
        "label": "🌶️  Mild",
        "prompt": (
            "You are a senior UI/UX consultant. Look at this design image.\n"
            "Respond in this EXACT format, nothing more:\n\n"
            "🌶️ [One single sarcastic but friendly one-liner roast about the design]\n\n"
            "Typography — [one sharp fix]\n"
            "Color — [one sharp fix]\n"
            "Layout — [one sharp fix]\n"
            "Whitespace — [one sharp fix]\n"
            "Consistency — [one sharp fix]\n\n"
            "Each fix must be under 10 words. No fluff, no preamble."
        )
    },
    "2": {
        "label": "🔥  Brutal",
        "prompt": (
            "You are a brutally honest senior UI/UX consultant. Look at this design image.\n"
            "Respond in this EXACT format, nothing more:\n\n"
            "🔥 [One savage sarcastic one-liner roast that actually stings]\n\n"
            "Typography — [one brutal fix]\n"
            "Color — [one brutal fix]\n"
            "Layout — [one brutal fix]\n"
            "Whitespace — [one brutal fix]\n"
            "Consistency — [one brutal fix]\n\n"
            "Each fix must be under 10 words. No fluff, no preamble."
        )
    },
    "3": {
        "label": "💀  Savage",
        "prompt": (
            "You are a no-filter senior UI/UX consultant who has seen too many bad designs. Look at this design image.\n"
            "Respond in this EXACT format, nothing more:\n\n"
            "💀 [One absolutely devastating, funny, roast-battle-level one-liner about this design]\n\n"
            "Typography — [one savage fix]\n"
            "Color — [one savage fix]\n"
            "Layout — [one savage fix]\n"
            "Whitespace — [one savage fix]\n"
            "Consistency — [one savage fix]\n\n"
            "Each fix must be under 10 words. Make it hurt but be accurate."
        )
    }
}

# ── Core functions (UNCHANGED) ────────────────────────────────────────────────
def compress_image(image_bytes, max_size_kb=500):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    if max(img.size) > 1024:
        img.thumbnail((1024, 1024), Image.LANCZOS)
    buf = io.BytesIO()
    quality = 85
    while True:
        buf.seek(0); buf.truncate()
        img.save(buf, format="JPEG", quality=quality)
        if buf.tell() / 1024 <= max_size_kb or quality < 30:
            break
        quality -= 10
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def roast_ui_stream(image_bytes, mode):
    image_b64 = compress_image(image_bytes)
    image_url = f"data:image/jpeg;base64,{image_b64}"
    selected = ROAST_MODES[mode]

    response = client.chat.completions.create(
        model="CohereLabs/aya-vision-32b:cohere",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": selected["prompt"]},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        }],
        max_tokens=200,
        stream=True,
    )

    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

# ── UI Layout ─────────────────────────────────────────────────────────────────
st.markdown('<p class="hero-title">UI ROAST<br>MACHINE</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Senior UX Consultant · Zero Filter · All Receipts</p>', unsafe_allow_html=True)

# Upload
st.markdown('<p class="section-label">01 — Drop your design</p>', unsafe_allow_html=True)
uploaded = st.file_uploader(
    "Upload a screenshot, mockup, or any UI image",
    type=["png", "jpg", "jpeg", "webp"],
    label_visibility="collapsed"
)

if uploaded:
    col_img, col_space = st.columns([1, 1])
    with col_img:
        st.image(uploaded, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Mode picker
st.markdown('<p class="section-label">02 — Choose your pain level</p>', unsafe_allow_html=True)
mode_labels = {
    "1": "🌶️\nMild",
    "2": "🔥\nBrutal",
    "3": "💀\nSavage",
}
mode_choice = st.radio(
    "Mode",
    options=list(mode_labels.keys()),
    format_func=lambda x: mode_labels[x],
    horizontal=True,
    label_visibility="collapsed",
    index=1,
)

st.markdown("<br>", unsafe_allow_html=True)

# Roast button
roast_clicked = st.button(
    "ROAST IT",
    disabled=uploaded is None,
    use_container_width=True,
)

# Output
if roast_clicked and uploaded:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f'<p class="section-label">03 — {ROAST_MODES[mode_choice]["label"].strip()} Verdict</p>',
        unsafe_allow_html=True
    )

    output_box = st.empty()
    full_text = ""

    with st.spinner("Analyzing your sins..."):
        for token in roast_ui_stream(uploaded.getvalue(), mode_choice):
            full_text += token
            output_box.markdown(
                f'<div class="roast-box">{full_text}▌</div>',
                unsafe_allow_html=True
            )

    # Final render without cursor
    output_box.markdown(
        f'<div class="roast-box">{full_text}</div>',
        unsafe_allow_html=True
    )

elif not uploaded:
    st.markdown(
        '<p style="color:#333; font-size:0.75rem; text-align:center; margin-top:1rem; letter-spacing:0.1em;">↑ UPLOAD A DESIGN TO UNLOCK THE BUTTON</p>',
        unsafe_allow_html=True
    )