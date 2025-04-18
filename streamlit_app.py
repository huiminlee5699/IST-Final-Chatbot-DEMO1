import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import time
import uuid
import json
import os
from datetime import datetime

# Setup page configuration
st.set_page_config(
    page_title="💬 CHATBOT AI",
)

# Generate a unique participant ID if one doesn't exist
if "participant_id" not in st.session_state:
    st.session_state.participant_id = str(uuid.uuid4())

# Track if the system card link was clicked
if "link_clicked" not in st.session_state:
    st.session_state.link_clicked = False

# Apply custom styling
st.markdown("""
<style>
    /* Import fonts */
    @import url("https://fonts.googleapis.com/css2?family=Inria+Sans:ital,wght@0,300;0,400;0,700;1,300;1,400;1,700&display=swap");
    @import url("https://fonts.googleapis.com/css2?family=Inria+Sans:ital,wght@0,300;0,400;0,700;1,300;1,400;1,700&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap");
    
    /* Title font (Inria Sans) */
    .main h1 {
        font-family: 'Inria Sans', sans-serif !important; 
        color: #3f39e3 !important;
    }
    /* Additional selectors to ensure title styling */
    .st-emotion-cache-10trblm h1, 
    .stMarkdown h1 {
        font-family: 'Inria Sans', sans-serif !important; 
        color: #3f39e3 !important;
    }
    
    /* All other text (Inter) */
    body, p, div, span, li, a, button, input, textarea, .stTextInput label {
        font-family: 'Inter', sans-serif !important;
    } 
</style>
""", unsafe_allow_html=True)

# Show title and description
st.markdown("<h1 style='font-family: \"Inria Sans\", sans-serif; color: #3f39e3;'>💬 CHATBOT AI</h1>", unsafe_allow_html=True)

st.write(
    "Welcome to Chatbot, a new OpenAI-powered chatbot! "
    "Feel free to ask me anything!"
)

# JavaScript for tracking link clicks with callback to Streamlit
link_click_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Wait for the footer to be added to the DOM
    setTimeout(function() {
        const systemCardLink = document.querySelector('footer a');
        if (systemCardLink) {
            systemCardLink.addEventListener('click', function(e) {
                // Send data to Streamlit using the streamlit.setComponentValue API
                const data = {
                    clicked: true,
                    timestamp: new Date().toISOString(),
                    participant_id: "%s"
                };
                
                // Log click data to local storage as backup
                const existingData = localStorage.getItem('linkClickData') ? 
                    JSON.parse(localStorage.getItem('linkClickData')) : [];
                existingData.push(data);
                localStorage.setItem('linkClickData', JSON.stringify(existingData));
                
                // Use Streamlit custom component communication if available
                if (window.parent.streamlitPyCallbackManager) {
                    window.parent.streamlitPyCallbackManager.setComponentValue(data);
                }
                
                // Continue with the link click (open in new tab)
                // The original link will still work
            });
        }
    }, 1000); // Give a bit of time for elements to load
});
</script>
""" % st.session_state.participant_id

# Create a custom component for the JS
components.html(link_click_js, height=0)

# Add custom CSS for footer with the system card link
st.markdown("""
<style>
footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: transparent;
    padding: 15px;
    font-size: 0.9rem;
    font-family: sans-serif;
    text-align: center;
    z-index: 998;
}

/* Add padding to the bottom of the page to prevent content from being hidden by the footer */
.main .block-container {
    padding-bottom: 80px;
}

/* Ensure the chat input stays above the footer */
.stChatInputContainer {
    z-index: 999;
    position: relative;
    background: transparent;
    margin-bottom: 10px;
}
</style>

<footer>
    💡🧠🤓 <strong>Want to learn how I come up with responses?</strong>
    <a href="https://www.figma.com/proto/ZeWFZShKd7Pu8N3Wwj8wri/Transparency-card?page-id=0%3A1&node-id=1-2&p=f&viewport=54%2C476%2C0.2&t=z8tiRCZcXZC9N553-8&scaling=min-zoom&content-scaling=fixed&hide-ui=1" 
       target="_blank" 
       style="color: #007BFF; text-decoration: none;"
       id="system-card-link"
       onclick="trackLinkClick()">
        Read more here →
    </a>
</footer>

<script>
function trackLinkClick() {
    // We'll use the Streamlit component API to communicate back
    const data = {
        clicked: true,
        timestamp: new Date().toISOString(),
        participant_id: "%s"
    };
    
    // Store in localStorage as backup
    const clickData = localStorage.getItem('systemCardClicks') ? 
        JSON.parse(localStorage.getItem('systemCardClicks')) : [];
    clickData.push(data);
    localStorage.setItem('systemCardClicks', JSON.stringify(clickData));
    
    // Using fetch to send data to a backend endpoint (uncomment and configure if needed)
    /*
    fetch('https://your-backend-url.com/track-click', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
    */
    
    // Return true to allow the default link behavior
    return true;
}
</script>
""" % st.session_state.participant_id, unsafe_allow_html=True)

# Create a callback handler for the link click
def handle_link_click():
    st.session_state.link_clicked = True
    
    # Create data directory if it doesn't exist
    os.makedirs("click_data", exist_ok=True)
    
    # Save click data to a JSON file
    click_data = {
        "participant_id": st.session_state.participant_id,
        "timestamp": datetime.now().isoformat(),
        "clicked": True
    }
    
    # Append to a JSON file
    with open(f"click_data/click_data.json", "a") as f:
        f.write(json.dumps(click_data) + "\n")

# Use the API key from Streamlit secrets
openai_api_key = st.secrets["openai_api_key"]

# Create an OpenAI client
client = OpenAI(api_key=openai_api_key)

# Create a session state variable to store the chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field
if prompt := st.chat_input("What would you like to know today?"):
    # Store and display the current prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate a response using the OpenAI API
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ],
        stream=True,
    )
    
    time.sleep(1)
    
    # Stream the assistant response
    with st.chat_message("assistant"):
        response_container = st.empty()
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                response_container.markdown(full_response)
        
        # Final display of the complete response
        response_container.markdown(full_response)
        
        # Store the final response in session state
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Hidden element to display tracking status (for debugging - can be removed in production)
if st.checkbox("Show tracking status (admin only)", value=False):
    st.write(f"Participant ID: {st.session_state.participant_id}")
    st.write(f"System card link clicked: {st.session_state.link_clicked}")
    
    # You could also add a download button for the click data
    if os.path.exists("click_data/click_data.json"):
        with open("click_data/click_data.json", "r") as f:
            click_data = f.readlines()
        st.download_button(
            label="Download click data",
            data="\n".join(click_data),
            file_name="system_card_click_data.json",
            mime="application/json"
        )
