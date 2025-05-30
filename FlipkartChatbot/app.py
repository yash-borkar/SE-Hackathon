# app.py
import streamlit as st
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
import re
from groq import Groq

# Set page config FIRST, before any other Streamlit commands
st.set_page_config(
    page_title="Chatbot",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="auto"
)

# Constants
CHAT_HISTORY_DIR = "chat_history"
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

# Import configurations and prompts
from config import GROQ_API_KEY, GROQ_MODEL_NAME
from prompts import SYSTEM_PROMPT, PRODUCT_DATA_INSTRUCTION, ORDER_DATA_INSTRUCTION

# Custom CSS for modern aesthetic
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }

    .chat-message {
        animation: fadeIn 0.5s ease-in;
        margin-bottom: 1rem;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
        width: 100%;
        margin-bottom: 0.5rem;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }

    .chat-history-item {
        padding: 0.5rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s;
    }

    .chat-history-item:hover {
        background-color: rgba(102, 126, 234, 0.1);
    }

    .sidebar .stButton > button {
        font-size: 0.9rem;
        padding: 0.4rem 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


# --- Helper Functions ---
def detect_language(text):
    """Detect if text is in Hindi or English"""
    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    if devanagari_pattern.search(text):
        return "hi"

    hindi_words = ['mera', 'kya', 'kahan', 'kaise', 'hai', 'mein', 'ka', 'ki', 'ko', 'aur', 'order', 'karna', 'chahta',
                   'chahte']
    text_lower = text.lower()

    hindi_indicators = sum(1 for word in hindi_words if word in text_lower)
    english_words = ['the', 'and', 'or', 'but', 'what', 'how', 'where', 'when', 'why', 'is', 'are', 'can', 'do', 'does',
                     'will', 'would', 'should', 'could']
    english_indicators = sum(1 for word in english_words if word in text_lower)

    return "hi" if hindi_indicators > english_indicators else "en"


def text_to_speech_js(text):
    """Generate JavaScript for text-to-speech"""
    clean_text = text.replace('\n', ' ').replace('*', '').replace('#', '').replace('`', '')
    return f"""
    <script>
    function speakText() {{
        const text = `{clean_text}`;
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.8;
        utterance.pitch = 1;
        utterance.volume = 0.8;
        speechSynthesis.speak(utterance);
    }}
    speakText();
    </script>
    """


def scroll_to_bottom_js():
    """JavaScript to scroll to bottom smoothly"""
    return """
    <script>
    function scrollToBottom() {
        setTimeout(function() {
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }
    scrollToBottom();
    </script>
    """


def get_chat_preview(messages):
    """Generate a preview snippet from chat messages"""
    if not messages:
        return "No messages"

    user_msg = next((m for m in messages if m['role'] == 'user'), None)
    assistant_msg = next((m for m in messages if m['role'] == 'assistant'), None)

    preview = ""
    if user_msg:
        preview += f"Q: {user_msg['content'][:50]}"
        if len(user_msg['content']) > 50:
            preview += "..."
    if assistant_msg:
        preview += f"\nA: {assistant_msg['content'][:50]}"
        if len(assistant_msg['content']) > 50:
            preview += "..."
    return preview


def load_saved_chats():
    """Load all saved chats from the chat history directory"""
    saved_chats = []
    for file in Path(CHAT_HISTORY_DIR).glob("*.json"):
        try:
            with open(file, 'r') as f:
                chat_data = json.load(f)
                saved_chats.append({
                    'id': file.stem,
                    'title': chat_data.get('title', 'Untitled Chat'),
                    'timestamp': chat_data.get('timestamp'),
                    'preview': get_chat_preview(chat_data['messages'])
                })
        except Exception as e:
            st.error(f"Error loading chat {file}: {e}")
    st.session_state.saved_chats = sorted(
        saved_chats,
        key=lambda x: x.get('timestamp', ''),
        reverse=True
    )


def save_current_chat(title=None):
    """Save the current chat to a JSON file"""
    if not st.session_state.messages:
        st.warning("No messages to save")
        return

    if not title:
        first_user_msg = next((m for m in st.session_state.messages if m['role'] == 'user'), None)
        title = first_user_msg['content'][:30] + "..." if first_user_msg else "Untitled Chat"

    chat_data = {
        'id': st.session_state.current_chat_id,
        'title': title,
        'timestamp': datetime.now().isoformat(),
        'messages': st.session_state.messages
    }

    file_path = os.path.join(CHAT_HISTORY_DIR, f"{st.session_state.current_chat_id}.json")
    with open(file_path, 'w') as f:
        json.dump(chat_data, f, indent=2)

    load_saved_chats()
    st.success(f"Chat saved as '{title}'")


def load_chat(chat_id):
    """Load a chat from history"""
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json")
    try:
        with open(file_path, 'r') as f:
            chat_data = json.load(f)
            st.session_state.messages = chat_data['messages']
            st.session_state.current_chat_id = chat_id
            st.session_state.auto_scroll = True
            st.rerun()
    except Exception as e:
        st.error(f"Error loading chat: {e}")


def start_new_chat():
    """Start a fresh chat session"""
    st.session_state.messages = [{
        "role": "assistant",
        "content": "👋 Hello! I'm Chatbot. How can I help you today?"
    }]
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.auto_scroll = True
    st.rerun()


# --- Data Loading ---
@st.cache_data
def load_product_data():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(current_dir, "data", "products.json")
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("products.json not found. Make sure it's in the 'data/' directory.")
        return []
    except json.JSONDecodeError:
        st.error("Error decoding products.json. Please check file format.")
        return []


@st.cache_data
def load_order_data():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(current_dir, "data", "orders.json")
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning("orders.json not found. Creating sample order data.")
        return []
    except json.JSONDecodeError:
        st.error("Error decoding orders.json. Please check file format.")
        return []


products = load_product_data()
orders = load_order_data()

# Prepare data for LLM
product_info_for_llm = json.dumps(products, indent=2)
order_info_for_llm = json.dumps(orders, indent=2)

system_prompt_with_data = (
        SYSTEM_PROMPT + "\n\n" +
        PRODUCT_DATA_INSTRUCTION.format(product_data=product_info_for_llm) + "\n\n" +
        ORDER_DATA_INSTRUCTION.format(order_data=order_info_for_llm)
)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Hello! I'm Chatbot. I can help you with:\n\nHow can I assist you today?"
    })

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = []
    load_saved_chats()

if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = False

if "processing" not in st.session_state:
    st.session_state.processing = False



if "auto_scroll" not in st.session_state:
    st.session_state.auto_scroll = False

# Initialize Groq client
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Failed to initialize Groq client. Please check your API key: {e}")
    st.stop()


# --- Response Generation Functions ---
def generate_response_stream(api_messages_payload):
    """Generate AI response and stream it."""
    try:
        stream = client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=api_messages_payload,
            stream=True,
            temperature=0.7,
            max_tokens=800
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"😔 I apologize, but I encountered an error: {e}."


def add_quick_action_buttons_streamlit(response_text, user_lang="en", message_index=0):
    """Add contextual quick action buttons using Streamlit buttons"""
    buttons_to_show = []

    if any(word in response_text.lower() for word in ['return', 'refund', 'रिटर्न']):
        if user_lang == "hi":
            buttons_to_show.extend([
                ("🔄 रिटर्न शुरू करें", "मैं एक आइटम वापस करना चाहता हूं"),
                ("📋 रिटर्न पॉलिसी", "रिटर्न पॉलिसी क्या है?")
            ])
        else:
            buttons_to_show.extend([
                ("🔄 Initiate Return", "I want to initiate a return"),
                ("📋 Return Policy", "What is your return policy?")
            ])

    if any(word in response_text.lower() for word in ['order', 'tracking', 'ऑर्डर']):
        if user_lang == "hi":
            buttons_to_show.append(("📦 दूसरा ऑर्डर ट्रैक करें", "मैं दूसरा ऑर्डर ट्रैक करना चाहता हूं"))
        else:
            buttons_to_show.append(("📦 Track Another Order", "I want to track another order"))




# --- UI Layout ---
st.markdown("""
<div class="main-header">
    <h1>🛍️ Customer Support</h1>
    <p>Your intelligent assistant for seamless e-commerce experience</p>
</div>
""", unsafe_allow_html=True)

# --- Process New User Input ---
new_user_prompt_content = None



typed_prompt = st.chat_input("💬 Ask me anything about your order, products, or services...",
                             disabled=st.session_state.processing,
                             key="chat_input_main")
if typed_prompt and not st.session_state.processing:
    new_user_prompt_content = typed_prompt

if new_user_prompt_content:
    st.session_state.messages.append({"role": "user", "content": new_user_prompt_content})
    st.session_state.processing = True

# Main chat area
col1, col2 = st.columns([3, 1])

with col1:
    # Display chat messages
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and i > 0:
                if st.button(f"🔊 Listen", key=f"tts_{i}"):
                    st.components.v1.html(text_to_speech_js(message["content"]), height=0)

                if i == len(st.session_state.messages) - 1 and not st.session_state.processing:
                    user_lang = "en"
                    if i > 0 and st.session_state.messages[i - 1]["role"] == "user":
                        user_lang = detect_language(st.session_state.messages[i - 1]["content"])
                    add_quick_action_buttons_streamlit(message["content"], user_lang, i)

    # Generate bot response
    if st.session_state.processing and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Typing... ⏳")
            full_response = ""

            api_messages_payload = [{"role": "system", "content": system_prompt_with_data}]
            history_plus_current = st.session_state.messages[-9:]
            for msg_content in history_plus_current:
                api_messages_payload.append({"role": msg_content["role"], "content": msg_content["content"]})

            try:
                for content_chunk in generate_response_stream(api_messages_payload):
                    full_response += content_chunk
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"😔 I apologize, but I encountered an error: {e}."
                message_placeholder.error(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.session_state.processing = False
            st.session_state.auto_scroll = True
            st.rerun()

def delete_chat(chat_id):
    """Delete a saved chat from history"""
    try:
        file_path = os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            load_saved_chats()  # Refresh the chat list
            st.success("Chat deleted successfully!")
            st.rerun()
        else:
            st.error("Chat file not found")
    except Exception as e:
        st.error(f"Error deleting chat: {e}")

# Chat history sidebar
with st.sidebar:
    st.markdown("### 💬 Chat History")

    if st.button("➕ New Chat", use_container_width=True):
        start_new_chat()

    if st.session_state.messages and len([m for m in st.session_state.messages if m['role'] == 'user']) > 0:
        with st.expander("💾 Save Current Chat"):
            chat_title = st.text_input(
                "Chat Title",
                value=next((m['content'][:30] + "..." for m in st.session_state.messages if m['role'] == 'user'),
                           "Untitled Chat"),
                max_chars=50
            )
            if st.button("Save", disabled=not chat_title):
                save_current_chat(chat_title)

    st.markdown("### 📂 Recent Chats")
    if not st.session_state.saved_chats:
        st.info("No saved chats yet")
    else:
        for chat in st.session_state.saved_chats:
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"**{chat['title']}**")
                st.caption(
                    f"{datetime.fromisoformat(chat['timestamp']).strftime('%Y-%m-%d %H:%M') if chat.get('timestamp') else 'No timestamp'}")
                st.caption(chat.get('preview', 'No preview'))
            with col2:
                if st.button("↩️", key=f"load_{chat['id']}"):
                    load_chat(chat['id'])
            with col3:
                if st.button("🗑️", key=f"delete_{chat['id']}"):
                    delete_chat(chat['id'])

            st.divider()

    # Import/Export
    with st.expander("🔄 Import/Export"):
        if st.session_state.messages:
            chat_json = json.dumps({
                'messages': st.session_state.messages,
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'chat_id': st.session_state.current_chat_id
                }
            }, indent=2)

            st.download_button(
                label="📤 Export Current Chat",
                data=chat_json,
                file_name=f"shopease_chat_{st.session_state.current_chat_id[:8]}.json",
                mime="application/json"
            )

        uploaded_file = st.file_uploader("📥 Import Chat", type=["json"])
        if uploaded_file is not None:
            try:
                chat_data = json.load(uploaded_file)
                if 'messages' in chat_data:
                    st.session_state.messages = chat_data['messages']
                    if 'metadata' in chat_data and 'chat_id' in chat_data['metadata']:
                        st.session_state.current_chat_id = chat_data['metadata']['chat_id']
                    else:
                        st.session_state.current_chat_id = str(uuid.uuid4())
                    st.success("Chat imported successfully!")
                    st.session_state.auto_scroll = True
                    st.rerun()
                else:
                    st.error("Invalid chat format: missing 'messages' field")
            except Exception as e:
                st.error(f"Error importing chat: {e}")

# Auto-scroll to bottom if needed
if st.session_state.auto_scroll:
    st.components.v1.html(scroll_to_bottom_js(), height=0)
    st.session_state.auto_scroll = False