import streamlit as st
import time
from together import Together
import streamlit_speech_recognition as sr
from gtts import gTTS
import os
from tempfile import NamedTemporaryFile


# 🔐 Replace with st.secrets["TOGETHER_API_KEY"] for deployment
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"] # ⬅️ Replace this!
client = Together(api_key=TOGETHER_API_KEY)

# Model name from Together
model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

# Streamlit UI
st.title("🤖 Konan - GPT Assistant (Powered by LLaMA 3.3 70B)")
st.write("Chat with a LLaMA model using Together API + typing effect + tone!")

# Choose tone
style = st.selectbox("Choose a style", ["Default", "Funny", "Formal", "Smart"])

# Session memory
if "history" not in st.session_state:
    st.session_state.history = []

# Prompt style formatter
def apply_style(prompt, style):
    if style == "Funny":
        return f"Make this funny: {prompt}"
    elif style == "Formal":
        return f"Respond formally: {prompt}"
    elif style == "Smart":
        return f"Give a high-IQ smart answer: {prompt}"
    return prompt

# Typing animation
def stream_text(text):
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.markdown(displayed)
        time.sleep(0.015)

# Clean LLaMA reply
def clean_reply(text):
    lines = text.splitlines()
    cleaned = [line for line in lines if not line.strip().startswith("User:")]
    return "\n".join(cleaned).strip()

# Chat Input
st.markdown("🎤 Speak or type your message:")
user_input = ""

# Voice input
speech_text = sr.speech_recognition()
if speech_text:
    st.success(f"Recognized: {speech_text}")
    user_input = speech_text
else:
    user_input = st.text_input("You:", key="text_input")


if st.button("Send") and user_input:
    styled_prompt = apply_style(user_input, style)

    # Build message list for Together API
    messages = []
    for q, a in st.session_state.history:
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": styled_prompt})

    # Call Together API
    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        reply = response.choices[0].message.content
        reply = clean_reply(reply)
    # Text-to-Speech
with NamedTemporaryFile(delete=True) as fp:
    tts = gTTS(text=reply)
    tts.save(fp.name + ".mp3")
    audio_file = fp.name + ".mp3"
    st.audio(audio_file, format="audio/mp3")


    # Save to history
    st.session_state.history.append((user_input, reply))

    # Display chat
    for q, a in st.session_state.history:
        st.markdown(f"**You:** {q}")
        st.markdown("**Konanara:**")
        stream_text(a)
