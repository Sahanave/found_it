import os
from io import BytesIO
from typing import IO
import requests as rq
import streamlit as st
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

# Initialize langflow API
langflow_api_url = os.getenv("LANGFLOW_API_URL")
langflow_flow_id = os.getenv("LANGFLOW_FLOW_ID")
api_key = os.getenv("LANGFLOW_API_KEY")

# Initialize Eleven Labs API
client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)
voice = os.getenv("ELEVENLABS_VOICE_ID")


def run_flow(text: str) -> str:
    """
    Run a flow with a given message and optional tweaks.

    :param text: The message to send to the flow
    :return: The JSON response from the flow
    """
    api_url = f"{langflow_api_url}/api/v1/run/{langflow_flow_id}"
    print(api_url)

    payload = {"input_value": text,
               "output_type": "chat",
               "input_type": "chat"}
    headers = {"x-api-key": api_key}

    response = rq.post(api_url, json=payload, headers=headers, timeout=300)
    return response.json()


def chat(text: str):
    with current_chat_message:
        # Block input to prevent sending messages whilst AI is responding
        st.session_state.disabled = True

        # Add user message to chat history
        st.session_state.messages.append(
            {
                "id": len(st.session_state.messages)-1,
                "role": "human",
                "content": text,
                "audio": None
            })

        # Display user message in chat message container
        with st.chat_message("human"):
            st.markdown(text)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            # Get complete chat history, including latest question as last message
            history = "\n".join(
                [f"{msg["role"]}: {msg["content"]
                                   }" for msg in st.session_state.messages]
            )

            query = f"{history}"

            _output = run_flow(query)

            print("output from the model is: ")
            print(_output)
            try:
                output = _output['outputs'][0]["outputs"][0]["results"]["message"]["text"]
            except Exception:
                output = f"Application error : {_output}"

            placeholder = st.empty()

            # write response without "▌" to indicate completed message.
            with placeholder:
                st.markdown(output)

    # Log AI response to chat history
    st.session_state.messages.append(
        {
            "id": len(st.session_state.messages),
            "role": "assistant",
            "content": output,
        })
    # Unblock chat input
    st.session_state.disabled = False

    st.rerun()


def text_to_speech(text: str) -> IO[bytes]:
    """
    Convert the given text to speech using the ElevenLabs API.

    This function takes a text input and generates an audio data
    using the specified voice and model from ElevenLabs.

    Args:
        text (str): The text to be converted to speech.

    Returns:
        audio_data (BytesIO): audio data that can be played.
    """
    audio_stream = client.generate(
        text=text, voice=voice, model="eleven_turbo_v2_5")
    # Create a BytesIO object to hold the audio data in memory
    audio_data = BytesIO()

    # Write each chunk of audio data to the stream
    for chunk in audio_stream:
        if chunk:
            audio_data.write(chunk)

    # Reset stream position to the beginning
    audio_data.seek(0)

    # Return the stream for further use
    return audio_data


st.set_page_config(page_title="Building GenAI apps")
st.title("Building GenAI apps")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "id": 0,
            "role": "assistant",
            "content": "Hi! I'm your chatbot",
            "audio": None
        }
    ]

if "disabled" not in st.session_state:
    # `disable` flag to prevent user from sending messages whilst the AI is responding
    st.session_state.disabled = False

# Write message history to UI
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

    # Display button for the TTS of the assistant's message
    if message["role"] == "assistant":
        if st.button("🔊", key=f"speak_{message["id"]}"):
            try:
                audio = text_to_speech(message["content"])
                st.audio(data=audio, format="audio/mp3")
            except Exception as e:
                st.write(f"Error generating audio: {e}")


current_chat_message = st.container()
prompt = st.chat_input("What would you like to ask?",
                       disabled=st.session_state.disabled)

if prompt:
    chat(prompt)
