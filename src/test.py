import streamlit as st

# Set page title
st.set_page_config(page_title="AI Chatbot Assistant")

# CSS styling
st.markdown("""
<style>
.chat-container {
    height: 400px; /* Adjust height as needed */
    overflow-y: scroll;
    padding: 10px;
    border: 1px solid #ccc;
}
.chat-bubble {
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
    max-width: 70%; /* Adjust width as needed */
}
.user-bubble {
    background-color: #dcf8c6; /* Example user bubble color */
}
</style>
""", unsafe_allow_html=True)

# Layout using columns
col1, col2 = st.columns([1, 3])  # Adjust ratio as needed

# Profile section (left column)
with col1:
    st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=150)  # Default image
    st.write("AI Chatbot")
    st.write("Assistant")
    st.button("Start a Call")  # Placeholder button

# Chat container (right column)
with col2:
    chat_container = st.container()
    with chat_container:
        # Initial welcome message
        st.markdown("<div class='chat-bubble'>Hello! How can I assist you today?</div>", unsafe_allow_html=True)

        # Placeholder for user input
        user_input = st.text_input("Message AI Chatbot Assistant...")

        # Example chat messages (replace with your chatbot logic)
        if st.button("Send"):
            st.markdown(f"<div class='chat-bubble user-bubble'>{user_input}</div>", unsafe_allow_html=True)
            # Here you would typically integrate your chatbot logic
            # to generate a response based on user_input
            st.markdown("<div class='chat-bubble'>This is an example response from the chatbot.</div>", unsafe_allow_html=True)