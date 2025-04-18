import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import time
import uuid
import json
import os
import urllib.parse
from datetime import datetime

# Setup page configuration
st.set_page_config(
    page_title="💬 CHATBOT AI",
)

# --- SESSION STATE MANAGEMENT ---
# Generate a unique participant ID if one doesn't exist
if "participant_id" not in st.session_state:
    st.session_state.participant_id = str(uuid.uuid4())

# Track if the system card link was clicked
if "link_clicked" not in st.session_state:
    st.session_state.link_clicked = False

# Track experiment condition
if "condition" not in st.session_state:
    # Assign condition randomly (you can modify this logic based on your specific requirements)
    # 1 = dynamic link, 2 = static link, 3 = no link
    import random
    st.session_state.condition = random.choice([1, 2, 3])

# Track system card version (will be randomly assigned)
if "system_card_version" not in st.session_state:
    # 1 = interactive visualization, 2 = static visualization
    st.session_state.system_card_version = random.choice([1, 2])

# Track chat rounds to ensure minimum engagement
if "chat_rounds" not in st.session_state:
    st.session_state.chat_rounds = 0

# Set up Qualtrics redirect URL (replace with your actual URL)
QUALTRICS_BASE_URL = "https://youruniversity.qualtrics.com/jfe/form/YOUR_SURVEY_ID"

# --- STYLING ---
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

    /* Style for the completion notice */
    .completion-notice {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        border-left: 5px solid #3f39e3;
    }

    /* Button styling */
    .stButton>button {
        background-color: #3f39e3;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #2a26a0;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1 style='font-family: \"Inria Sans\", sans-serif; color: #3f39e3;'>💬 CHATBOT AI</h1>", unsafe_allow_html=True)

st.write(
    "Welcome to Chatbot, a new OpenAI-powered chatbot! "
    "Feel free to ask me anything!"
)

# --- TRACKING FUNCTIONS ---
def log_event(event_type, details=None):
    """Log various events during the experiment"""
    if details is None:
        details = {}
    
    event_data = {
        "participant_id": st.session_state.participant_id,
        "condition": st.session_state.condition,
        "system_card_version": st.session_state.system_card_version,
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        **details
    }
    
    # Create data directory if it doesn't exist
    os.makedirs("experiment_data", exist_ok=True)
    
    # Append to a JSON file
    with open(f"experiment_data/events.json", "a") as f:
        f.write(json.dumps(event_data) + "\n")
    
    return event_data

# --- SYSTEM CARD LINK FUNCTIONALITY ---
# Determine which Figma link to use based on system card version
def get_figma_url():
    base_url = "https://www.figma.com/proto/ZeWFZShKd7Pu8N3Wwj8wri/Transparency-card"
    
    # Add tracking parameters
    params = {
        "page-id": "0%3A1",
        "node-id": "1-2",
        "p": "f",
        "viewport": "54%2C476%2C0.2",
        "t": "z8tiRCZcXZC9N553-8",
        "scaling": "min-zoom",
        "content-scaling": "fixed",
        "hide-ui": "1",
        "participant_id": st.session_state.participant_id,
        "condition": st.session_state.condition,
        "system_card_version": st.session_state.system_card_version,
        "entry_time": datetime.now().isoformat()
    }
    
    # Construct URL with parameters
    param_string = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
    full_url = f"{base_url}?{param_string}"
    
    return full_url

# JavaScript for tracking link clicks with parameters for redirection
link_click_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Wait for the footer to be added to the DOM
    setTimeout(function() {
        const systemCardLink = document.querySelector('footer a');
        if (systemCardLink) {
            systemCardLink.addEventListener('click', function(e) {
                // Track click time
                const clickTime = new Date().toISOString();
                
                // Record click data
                const data = {
                    clicked: true,
                    timestamp: clickTime,
                    participant_id: "%s",
                    condition: %d,
                    system_card_version: %d
                };
                
                // Log click data to local storage as backup
                const existingData = localStorage.getItem('linkClickData') ? 
                    JSON.parse(localStorage.getItem('linkClickData')) : [];
                existingData.push(data);
                localStorage.setItem('linkClickData', JSON.stringify(existingData));
                
                // Send data to our tracking backend (commented out, uncomment if you have a backend)
                /*
                fetch('https://your-tracking-backend.com/track', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                */
                
                // Store entry time for Figma page to calculate time spent
                localStorage.setItem('figmaEntryTime', clickTime);
                
                // Continue with the link click (it will open in a new tab as specified in the link)
            });
        }
    }, 1000);
});

// Function to check if user has returned from Figma
function checkReturnFromFigma() {
    const figmaEntryTime = localStorage.getItem('figmaEntryTime');
    if (figmaEntryTime) {
        const timeSpent = (new Date() - new Date(figmaEntryTime)) / 1000; // Time in seconds
        
        // Clear the entry time
        localStorage.removeItem('figmaEntryTime');
        
        // Record the return data
        const returnData = {
            event: 'return_from_figma',
            participant_id: "%s",
            time_spent_seconds: timeSpent
        };
        
        // Store return data
        const returnEvents = localStorage.getItem('figmaReturns') ? 
            JSON.parse(localStorage.getItem('figmaReturns')) : [];
        returnEvents.push(returnData);
        localStorage.setItem('figmaReturns', JSON.stringify(returnEvents));
        
        // Send this data to Streamlit (would require a component with callback)
        // For now, we'll just log it locally
    }
}

// Check when the page regains focus (user returns from Figma)
window.addEventListener('focus', checkReturnFromFigma);

// Also check on page load (in case user closed Figma and refreshed this page)
window.addEventListener('load', checkReturnFromFigma);
</script>
""" % (st.session_state.participant_id, st.session_state.condition, st.session_state.system_card_version)

# Create a custom component for the JS
components.html(link_click_js, height=0)

# --- SYSTEM CARD FOOTER LINK ---
# Only show link for conditions 1 (dynamic) and 2 (static)
if st.session_state.condition != 3:  # Skip for "no link" condition
    figma_url = get_figma_url()
    
    footer_html = f"""
    <style>
    footer {{
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
    }}

    /* Add padding to the bottom of the page to prevent content from being hidden by the footer */
    .main .block-container {{
        padding-bottom: 80px;
    }}

    /* Ensure the chat input stays above the footer */
    .stChatInputContainer {{
        z-index: 999;
        position: relative;
        background: transparent;
        margin-bottom: 10px;
    }}
    </style>

    <footer>
        💡🧠🤓 <strong>Want to learn how I come up with responses?</strong>
        <a href="{figma_url}" 
           target="_blank" 
           style="color: #007BFF; text-decoration: none;"
           id="system-card-link"
           onclick="trackLinkClick()">
            Read more here →
        </a>
    </footer>

    <script>
    function trackLinkClick() {{
        // Log the click in session state via a callback
        const data = {{
            clicked: true,
            timestamp: new Date().toISOString(),
            participant_id: "{st.session_state.participant_id}"
        }};
        
        // Mark as clicked in local storage
        localStorage.setItem('systemCardClicked', 'true');
        
        // Log entry time for measuring time spent
        localStorage.setItem('figmaEntryTime', new Date().toISOString());
        
        return true;
    }}
    </script>
    """
    
    st.markdown(footer_html, unsafe_allow_html=True)

# --- OPENAI CHAT FUNCTIONALITY ---
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
    # Increment chat rounds
    st.session_state.chat_rounds += 1
    
    # Log the user message
    log_event("user_message", {"message": prompt, "round": st.session_state.chat_rounds})
    
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
        
        # Log the assistant response
        log_event("assistant_response", {"message": full_response, "round": st.session_state.chat_rounds})

# --- COMPLETION NOTICE ---
# Show completion notice after 2+ chat rounds
if st.session_state.chat_rounds >= 2:
    st.markdown("""
    <div class="completion-notice">
        <h3>You've completed the minimum required chat interactions!</h3>
        <p>You may continue chatting or proceed to the next stage of the experiment using the button below.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Determine redirect URL based on conditions
    if st.session_state.condition == 3 or st.session_state.link_clicked:
        # For no-link condition or if they've already clicked the link, go directly to Qualtrics
        redirect_url = f"{QUALTRICS_BASE_URL}?participant_id={st.session_state.participant_id}&condition={st.session_state.condition}&system_card_version={st.session_state.system_card_version}&link_clicked={str(st.session_state.link_clicked).lower()}"
    else:
        # For others who haven't clicked the link yet, go to Figma first
        redirect_url = get_figma_url()
    
    # Proceed button
    if st.button("Proceed to Next Stage"):
        log_event("proceed_clicked", {"destination": "figma" if redirect_url.startswith("https://www.figma.com") else "qualtrics"})
        # Use JavaScript to redirect
        st.markdown(f'<script>window.location.href = "{redirect_url}";</script>', unsafe_allow_html=True)
        st.success("Redirecting you to the next stage...")

# --- HIDDEN ADMIN PANEL ---
# Only show this in development or to admins
if st.sidebar.checkbox("Show Admin Panel", value=False):
    st.sidebar.subheader("Experiment Status")
    st.sidebar.write(f"Participant ID: {st.session_state.participant_id}")
    st.sidebar.write(f"Condition: {st.session_state.condition} ({'Dynamic Link' if st.session_state.condition == 1 else 'Static Link' if st.session_state.condition == 2 else 'No Link'})")
    st.sidebar.write(f"System Card Version: {st.session_state.system_card_version} ({'Interactive' if st.session_state.system_card_version == 1 else 'Static'})")
    st.sidebar.write(f"Chat Rounds: {st.session_state.chat_rounds}")
    st.sidebar.write(f"Link Clicked: {st.session_state.link_clicked}")
    
    # Option to download data
    if os.path.exists("experiment_data/events.json"):
        with open("experiment_data/events.json", "r") as f:
            events_data = f.readlines()
        st.sidebar.download_button(
            label="Download Experiment Data",
            data="\n".join(events_data),
            file_name="experiment_data.json",
            mime="application/json"
        )
