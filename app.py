import streamlit as st
import requests

# ---------------- CONFIG ----------------
API_BASE = "https://api.reverb.com/api"

st.set_page_config(
    page_title="tst",
    layout="wide"
)

st.title("📬")

# ---------------- TOKEN INPUT ----------------
api_token = st.text_input(
    "code",
    type="password",
    help="Token is required every session and is never saved."
)

if not api_token:
    st.info("tst.")
    st.stop()

headers = {
    "Authorization": f"Bearer {api_token}",
    "Accept": "application/hal+json",
    "Content-Type": "application/hal+json",
    "Accept-Version": "3.0"
}

# ---------------- API FUNCTIONS ----------------
def get_conversations():
    url = f"{API_BASE}/my/conversations"
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        st.error("Failed. Invalid error.")
        return []

    return r.json().get("conversations", [])

def extract_conversation_id(c):
    """
    Safely extract conversation ID from multiple possible formats
    """
    return (
        c.get("id")
        or c.get("conversation_id")
        or c.get("_links", {})
             .get("self", {})
             .get("href", "")
             .split("/")[-1]
    )

def get_conversation(conv_id):
    url = f"{API_BASE}/my/conversations/{conv_id}"
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        st.error("Failed.")
        return {}

    return r.json()

def send_reply(conv_id, message):
    url = f"{API_BASE}/my/conversations/{conv_id}/messages"
    payload = {"body": message}

    r = requests.post(url, json=payload, headers=headers)
    return r.status_code in [200, 201]

# ---------------- LOAD CONVERSATIONS ----------------
if st.button("📥"):
    st.session_state["conversations"] = get_conversations()

conversations = st.session_state.get("conversations", [])

# ---------------- DISPLAY CONVERSATIONS ----------------
if conversations:
    st.subheader("Your Conversations")

    conv_map = {}

    for c in conversations:
        conv_id = extract_conversation_id(c)
        if not conv_id:
            continue

        preview = c.get("last_message_preview", "No preview")
        label = f"{conv_id} — {preview}"

        conv_map[label] = conv_id

    if not conv_map:
        st.warning("No valid conversations found.")
        st.stop()

    selected_label = st.selectbox(
        "Select a conversation",
        options=list(conv_map.keys())
    )

    selected_conv_id = conv_map[selected_label]

    # ---------------- LOAD MESSAGES ----------------
    conversation = get_conversation(selected_conv_id)

    st.divider()
    st.subheader("Messages")

    messages = conversation.get("messages", [])

    if not messages:
        st.info("No messages in this conversation yet.")
    else:
        for msg in messages:
            sender = msg.get("sender_name", "Unknown")
            body = msg.get("body", "")
            created = msg.get("created_at", "")

            st.markdown(
                f"""
                **{sender}**  
                {body}  
                🕒 {created}
                """
            )
            st.markdown("---")

    # ---------------- REPLY ----------------
    st.subheader("✉️ Reply")
    reply_text = st.text_area(
        "Type your reply here",
        height=120
    )

    if st.button("Send Reply"):
        if not reply_text.strip():
            st.warning("Reply message cannot be empty.")
        else:
            success = send_reply(selected_conv_id, reply_text)
            if success:
                st.success("Reply sent successfully.")
            else:
                st.error("Failed to send reply.")

else:
    st.info("Click **Load My Conversations** to fetch your messages.")
