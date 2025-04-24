import streamlit as st
from openai import OpenAI
import time
import streamlit_analytics

# Set page config first
st.set_page_config(
    page_title="💬 CHATBOT AI",
)

# Initialize streamlit analytics tracking
with streamlit_analytics.track():
    # Original styling - unchanged
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

    # Show title and description.
    st.markdown("<h1 style='font-family: \"Inria Sans\", sans-serif; color: #3f39e3;'>💬 CHATBOT AI</h1>", unsafe_allow_html=True)

    st.write(
        "Welcome to Chatbot, a new OpenAI-powered chatbot! "
        "Feel free to ask me anything!"
    )

    # Use the API key from Streamlit secrets
    openai_api_key = st.secrets["openai_api_key"]

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create session state variables for tracking
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "link_shown_count" not in st.session_state:
        st.session_state.link_shown_count = 0
        
    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
            
    # Create a chat input field to allow the user to enter a message. 
    if prompt := st.chat_input("What would you like to know today?"):
        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        
        time.sleep(1)
        
        # Stream the assistant response while building it up
        with st.chat_message("assistant"):
            response_container = st.empty()  # placeholder for streaming text
            full_response = ""
            
            # Count previous assistant messages
            assistant_messages = [
                msg for msg in st.session_state.messages if msg["role"] == "assistant"
            ]
            
            # If this is after the second assistant message (2nd, 4th, etc.), prepend the message
            prepend_message = ""
            if len(assistant_messages) == 1:  # Changed condition to display after 2nd response
                # Track that system card link was shown
                st.session_state.link_shown_count += 1
                
                # Use HTML for tracking clicks with a special class
                system_card_url = "https://www.figma.com/proto/haXTVr4wZaeSC344BqDBpR/Text-Transparency-Card?page-id=0%3A1&node-id=1-33&p=f&viewport=144%2C207%2C0.47&t=Hp8ZCw5Fg7ahsiq1-8&scaling=min-zoom&content-scaling=fixed&hide-ui=1"
                
                prepend_message = (
                    "💡🧠🤓 <strong>Want to learn how I come up with responses?</strong>\n"
                    f"<a href=\"{system_card_url}\" target=\"_blank\" style=\"color: #007BFF; text-decoration: none;\" "
                    f"class=\"system-card-link\">"
                    "Read more here →\n"
                    "</a>\n\n ---------------- \n"
                )
                  
                full_response += prepend_message
                response_container.markdown(full_response, unsafe_allow_html=True)
            
            # Continue streaming the assistant's response
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_container.markdown(full_response, unsafe_allow_html=True)
        
            # Store the final response in session state
            st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Admin section in sidebar
    with st.sidebar:
        st.title("Admin Panel")
        password = st.text_input("Enter password to view analytics", type="password")
        
        if password == "admin123":
            st.subheader("Analytics Dashboard")
            
            # Display custom tracking metrics
            st.metric("System Card Links Shown", st.session_state.link_shown_count)
            
            # Show Streamlit Analytics dashboard with options from the documentation
            if st.button("View Full Analytics"):
                streamlit_analytics.analyze(
                    min_occurences=1,           # Only show events that occurred at least once
                    hide_index=True,            # Hide the index column
                    events_by_time_granularity="day"  # Group events by day
                )
