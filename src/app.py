import streamlit as st
import requests


# API endpoints
API_BASE_URL = "http://localhost:8000"  # Change this to your actual API base URL


# Sidebar for feature selection
st.sidebar.title("Chatbot Features")
feature = st.sidebar.selectbox("Choose a feature:", [
    "AI Reflection Chat",
    "Reflective Dialogue",
    "Simulated Teaching Scenarios",
    "Knowledge Recall Assistant",
    "Time Management Assistant",
    "Teaching Style Analysis"
])


st.title(feature)


# Function to send API request
def call_api(endpoint, data):
    response = requests.post(f"{API_BASE_URL}/{endpoint}", json=data)
    return response.json() if response.status_code == 200 else {"error": "Failed to fetch response"}


match feature:
    case "AI Reflection Chat":
        st.header("Chat with AI")
        session_id = st.text_input("Session ID", value="default_session")
        user_input = st.text_area("Enter your message:")

        if st.button("Send Message"):
            if user_input.strip():
                response = requests.post("http://localhost:8000/talk_to_yourself", json={
                    "session_id": session_id,
                    "user_input": user_input
                })

                if response.status_code == 200:
                    st.success("Response received!")
                    st.write("**AI:**", response.json()["response"])
                else:
                    st.error("Error in API request.")

        if st.button("Load Chat History"):
            history_response = requests.get(f"http://localhost:8000/get_chat_history?session_id={session_id}")

            if history_response.status_code == 200:
                history_data = history_response.json().get("chat_history", [])
                for chat in history_data:
                    role = "User" if chat["role"] == "user" else "AI"
                    st.write(f"**{role}:** {chat['content']}")
            else:
                st.error("Error retrieving chat history.")

    case "Reflective Dialogue":
        st.header("Reflective Dialogue")

        # Ensure session state is initialized
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        # Input for user message
        session_id = st.text_input("Session ID", value="default_session")
        user_input = st.text_area("Enter your reflection:")

        if st.button("Submit"):
            if user_input.strip():
                response = requests.post(f"{API_BASE_URL}/reflective_dialogue",
                                         json={"session_id": session_id, "user_input": user_input})
                if response.status_code == 200:
                    result = response.json()["response"]
                    st.session_state["chat_history"].append(("You", user_input))
                    st.session_state["chat_history"].append(("AI", result))
                else:
                    st.error("Error connecting to the server.")

        # Display chat history
        for role, message in st.session_state.get("chat_history", []):
            with st.chat_message("user" if role == "You" else "assistant"):
                st.markdown(message)

    case "Simulated Teaching Scenarios":
            user_input = st.text_area("Describe the teaching scenario:")
            if st.button("Generate"):
                response = call_api("simulated_teaching", {"scenario": user_input})
                st.write("Scenario:", response)

    case "Knowledge Recall Assistant":
        query = st.text_input("Enter your knowledge query:")
        if st.button("Search"):
            response = requests.get(f"{API_BASE_URL}/search_knowledge", params={"query": query})
            st.write("Result:", response.json())

    case "Time Management Assistant":
        task = st.text_input("Enter your task:")
        duration = st.text_input("Enter duration (e.g., 3h):")
        if st.button("Get Schedule"):
            response = call_api("time_management_assistant/pomodoro", {"task": task, "duration": duration})
            st.write("Schedule:", response)

    case "Teaching Style Analysis":
        teaching_text = st.text_area("Enter a teaching sample:")
        if st.button("Analyze"):
            response = call_api("teaching_style_analysis", {"text": teaching_text})
            st.write("Analysis:", response)

st.sidebar.write("Demo.")
