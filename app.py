import streamlit as st
import requests

API_BASE = "https://api.reverb.com/api"

st.set_page_config(page_title="Reverb Messages Tool", layout="wide")
st.title("📬 Reverb Messages Inbox")

# --- Ask for token EVERY time ---
api_token = st.text_input(
    "Enter your Reverb API Token",
    type="password",
    help="Token is not saved. Required each session."
)

if not api_token:
    st.info("Please enter your API token to continue.")
    st.stop()

headers = {
    "Authorization": f"Bearer {api_token}",
    "Accept": "application/hal+json",
    "Content-Type": "application/hal+json",
    "Accept-Version": "3.0"
}

# --- API functions ---
def get_conversations():
    url = f"{API_BASE}/my/conversations"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error("Failed to load conversations. Check token.")
        return []
    return r.json().get("conversations", [])

def get_conversation(conv_id):
    url = f"{API_BASE}/my/conversations/{conv_id}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error("Failed to load conversation.")
        return {}
    return r.json()

def send_reply(conv_id, message):
    url = f"{API_BASE}/my/conversations/{conv_id}/messages"
    payload = {"body": message}
    r = requests.post(url, json=payload, headers=headers)
    return r.status_code in [200, 201]

# --- Load conversations ---
if st.button("📥 Load My Conversations"):
    st.session_state["conversations"] = get_conversations()

conversations = st.session_state.get("conversations", [])

if conversations:
    st.subheader("Conversations")

    conv_map = {
        f"{c['id']} — {c.get('last_message_preview', '')}": c["id"]
        for c in conversations
    }

    selected = st.selectbox(
        "Select a conversation",
        options=list(conv_map.keys())
    )

    conv_id = conv_map[selected]
    data = get_conversation(conv_id)

    st.divider()
    st.subheader("Messages")

    for msg in data.get("messages", []):
        sender = msg.get("sender_name", "Unknown")
        body = msg.get("body", "")
        created = msg.get("created_at", "")
        st.markdown(f"**{sender}**  \n{body}  \n🕒 {created}")
        st.markdown("---")

    st.subheader("✉️ Reply")
    reply_text = st.text_area("Your message")

    if st.button("Send Reply"):
        if reply_text.strip():
            success = send_reply(conv_id, reply_text)
            if success:
                st.success("Message sent successfully.")
            else:
                st.error("Failed to send message.")
        else:
            st.warning("Message cannot be empty.")
