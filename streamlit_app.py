import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components
import time

# Set page config first
st.set_page_config(
    page_title="💬 CHATBOT AI",
)

st.markdown(
    """
    <!-- Maze universal snippet -->
    <script>
    (function (m, a, z, e) {
      var s, t;
      try {
        t = m.sessionStorage.getItem('maze-us');
      } catch (err) {}
      if (!t) {
        t = new Date().getTime();
        try {
          m.sessionStorage.setItem('maze-us', t);
        } catch (err) {}
      }
      s = a.createElement('script');
      s.src = z + '?apiKey=' + e;
      s.async = true;
      a.getElementsByTagName('head')[0].appendChild(s);
      m.mazeUniversalSnippetApiKey = e;
    })(window, document, 'https://snippet.maze.co/maze-universal-loader.js', '16abf1fc-3397-439b-9561-75896a7f1306');
    </script>

    <!-- Optional: automatically fire a Maze custom event on any outbound link click -->
    <script>
    document.addEventListener('click', function(e) {
      const link = e.target.closest('a[target="_blank"]');
      if (link && window.maze) {
        // replace 'outbound_click' with your preferred event name
        maze('track', 'outbound_click', { url: link.href });
      }
    });
    </script>
    """,
    unsafe_allow_html=True,
)

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

# Add a special system card link that will communicate with Qualtrics
st.markdown("""
<div style="margin: 20px 0; padding: 10px; border: 1px solid #e0e0e0; border-radius: 5px; background-color: #f8f9fa;">
    <p style="margin-bottom: 5px;">💡🧠🤓 <strong>Want to learn how I come up with responses?</strong></p>
    <a href="javascript:void(0);" 
       onclick="parent.postMessage({'type':'system_card_click','card':'1'}, '*')" 
       style="color: #007BFF; text-decoration: none;">
       Read more here →
    </a>
</div>
""", unsafe_allow_html=True)

# Use the API key from Streamlit secrets
openai_api_key = st.secrets["openai_api_key"]

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)

# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"],unsafe_allow_html=True)
        
# Create a chat input field to allow the user to enter a message. 
if prompt := st.chat_input("What would you like to know today?"):
    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Send a message to Qualtrics to track this interaction
    st.markdown(
        """
        <script>
        parent.postMessage({'type': 'interaction'}, '*');
        </script>
        """,
        unsafe_allow_html=True
    )
        
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
        
        # Continue streaming the assistant's response
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                response_container.markdown(full_response, unsafe_allow_html=True)
    
        # Store the final response in session state
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Send another interaction message to Qualtrics
        st.markdown(
            """
            <script>
            parent.postMessage({'type': 'interaction'}, '*');
            </script>
            """,
            unsafe_allow_html=True
        )
