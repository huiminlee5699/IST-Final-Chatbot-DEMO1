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

    # Initialize session state variables for tracking
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "link_shown_count" not in st.session_state:
        st.session_state.link_shown_count = 0
        
    if "link_click_count" not in st.session_state:
        st.session_state.link_click_count = 0
    
    # Use the API key from Streamlit secrets
    openai_api_key = st.secrets["openai_api_key"]

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)
            
    # Display the existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
            
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
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        
        time.sleep(1)
        
        # Stream the assistant response
        with st.chat_message("assistant"):
            response_container = st.empty()
            full_response = ""
            
            # Count previous assistant messages
            assistant_messages = [
                msg for msg in st.session_state.messages if msg["role"] == "assistant"
            ]
            
            # Check if this is the second response
            if len(assistant_messages) == 1:
                # Track that the system card prompt is shown
                st.session_state.link_shown_count += 1
                
                # Instead of HTML link, we'll add text and then a button
                prepend_message = "💡🧠🤓 **Want to learn how I come up with responses?**\n\n"
                full_response += prepend_message
                response_container.markdown(full_response)
                
                # Add a button that links to the system card
                system_card_url = "https://www.figma.com/proto/haXTVr4wZaeSC344BqDBpR/Text-Transparency-Card?page-id=0%3A1&node-id=1-33&p=f&viewport=144%2C207%2C0.47&t=Hp8ZCw5Fg7ahsiq1-8&scaling=min-zoom&content-scaling=fixed&hide-ui=1"
                
                # Create columns for text and button
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("Read more here →")
                with col2:
                    # Using a button that opens URL when clicked
                    if st.button("→", key="system_card_button"):
                        st.session_state.link_click_count += 1
                        st.markdown(f'<script>window.open("{system_card_url}", "_blank");</script>', unsafe_allow_html=True)
                
                # Add separator line
                full_response += "\n\n---------------- \n\n"
                response_container.markdown(full_response)
            
            # Continue streaming the assistant's response
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_container.markdown(full_response)
        
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
            st.metric("System Card Links Clicked", st.session_state.link_click_count)
            
            # Calculate and display click-through rate
            if st.session_state.link_shown_count > 0:
                ctr = (st.session_state.link_click_count / st.session_state.link_shown_count) * 100
                st.metric("Click-Through Rate", f"{ctr:.1f}%")
            
            # Info about analytics
            st.info("""
            Analytics are being collected in the background.
            
            Basic metrics are shown above. The click count represents the number of times 
            users have clicked the system card button.
            """)
