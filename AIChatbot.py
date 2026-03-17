import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        color: #f8fafc;
    }

    .main-card {
        background: rgba(255, 255, 255, 0.06);
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.18);
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }

    .hero-subtitle {
        font-size: 1rem;
        color: #cbd5e1;
        margin-bottom: 0.6rem;
    }

    .feature-pill {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        margin: 0.2rem 0.3rem 0.2rem 0;
        border-radius: 999px;
        background: rgba(59, 130, 246, 0.18);
        color: #dbeafe;
        border: 1px solid rgba(96, 165, 250, 0.35);
        font-size: 0.9rem;
    }

    .sidebar-note {
        background: rgba(255,255,255,0.05);
        padding: 0.9rem;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.08);
        color: #e5e7eb;
        font-size: 0.92rem;
    }

    div[data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 0.35rem 0.45rem;
    }

    .small-muted {
        color: #94a3b8;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.title("⚙️ Study Settings")

    mode = st.selectbox(
        "Choose a learning mode",
        ["General Learning", "Exam Prep", "Explain Simply", "Quiz Me"],
    )

    subject = st.text_input("Subject or course", placeholder="e.g. Databases, Networking")

    temperature = st.slider("Response creativity", 0.0, 1.0, 0.4, 0.1)

    st.markdown(
        """
        <div class="sidebar-note">
        <strong>How this app helps</strong><br>
        • Explains topics clearly<br>
        • Gives examples<br>
        • Creates practice questions<br>
        • Helps with exam prep
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="main-card">
        <div class="hero-title">🎓 AI Study Assistant</div>
        <div class="hero-subtitle">
            Learn faster with simple explanations, examples, and practice questions.
        </div>
        <span class="feature-pill">Explanations</span>
        <span class="feature-pill">Examples</span>
        <span class="feature-pill">Practice Questions</span>
        <span class="feature-pill">Exam Prep</span>
    </div>
    """,
    unsafe_allow_html=True,
)

api_key = ""

try:
    api_key = st.secrets.get("OPENAI_API_KEY", "")

    if not api_key:
        api_key = st.text_input("Enter your OpenAI API Key:", type="password")

except Exception:
    api_key = st.text_input("Enter your OpenAI API Key", type="password")

if not api_key:
    st.info("Enter your OpenAI API key to start chatting.")
    st.stop()

client = OpenAI(api_key=api_key)


def build_system_prompt(selected_mode: str, selected_subject: str) -> str:
    base = "You are a helpful AI study assistant for university students. Be accurate, supportive, and easy to understand."

    if selected_mode == "General Learning":
        mode_prompt = (
            "Explain concepts clearly, step by step, with one simple example and 2 practice questions."
        )
    elif selected_mode == "Exam Prep":
        mode_prompt = (
            "Teach the topic in an exam-focused way. Give key points, common mistakes, memory tips, and 3 likely exam questions."
        )
    elif selected_mode == "Explain Simply":
        mode_prompt = (
            "Explain everything in very simple language like to a beginner. Avoid jargon. Use short examples."
        )
    else:  # Quiz Me
        mode_prompt = (
            "Act like a tutor. First give a short explanation, then ask 3 quiz questions, and wait for the student to answer."
        )

    subject_prompt = (
        f"The current subject is {selected_subject}." if selected_subject.strip() else ""
    )

    return f"{base} {mode_prompt} {subject_prompt}".strip()


system_prompt = build_system_prompt(mode, subject)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

if st.session_state.messages[0]["content"] != system_prompt:
    st.session_state.messages[0] = {"role": "system", "content": system_prompt}

col1, col2 = st.columns([3, 1])

with col2:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": system_prompt}]
        st.rerun()

with col1:
    st.markdown(
        f"<div class='small-muted'>Mode: <strong>{mode}</strong></div>",
        unsafe_allow_html=True,
    )

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

user_text = st.chat_input("Ask a question, topic, or concept...")

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})

    with st.chat_message("user"):
        st.markdown(user_text)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages,
                    temperature=temperature,
                )

                bot_text = response.choices[0].message.content or "No response generated."
                st.markdown(bot_text)

        st.session_state.messages.append({"role": "assistant", "content": bot_text})

    except Exception as e:
        st.error(f"Something went wrong: {e}")