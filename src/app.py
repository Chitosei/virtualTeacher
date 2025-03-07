import json

import streamlit as st
import requests


# API endpoints
API_BASE_URL = "http://localhost:8000"  # Change this to your actual API base URL

st.set_page_config(page_title="AI Chatbot Assistant")

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

    # AI Reflection Chat UI
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
                    response_data = response.json()
                    st.success("Response received!")
                    st.write("**AI:**", response.json()["response"])
                    url = response_data["audio_url"]

                    # ✅ Fetch and play audio with unique filename
                    audio_url = f"http://localhost:8000{url}"
                    st.audio(audio_url, format="audio/mp3")

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


    # Reflective Dialogue UI
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


    # Simulated Teaching Scenarios UI
    case "Simulated Teaching Scenarios":
        st.header("Simulated Teaching Scenarios")

        # Ensure session state for chat history
        if "teaching_chat_history" not in st.session_state:
            st.session_state["teaching_chat_history"] = []

        # Input for session details
        session_id = st.text_input("Session ID", value="default_session")
        role = st.selectbox("Select Role", ["Teacher", "Student"])
        user_input = st.text_area("Enter your message:")

        if st.button("Send"):
            if user_input.strip():
                response = requests.post(f"{API_BASE_URL}/teaching_simulation",
                                         json={"session_id": session_id, "role": role.lower(),
                                               "user_input": user_input})
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result["response"]
                    next_role = result["role"]

                    # Update session state
                    st.session_state["teaching_chat_history"].append((role, user_input))
                    st.session_state["teaching_chat_history"].append((next_role.capitalize(), ai_response))
                else:
                    st.error("Error connecting to the server.")

        # Display conversation history
        for speaker, message in st.session_state["teaching_chat_history"]:
            with st.chat_message("user" if speaker == "Teacher" else "assistant"):
                st.markdown(f"**{speaker}:** {message}")


    # Knowledge Recall Assistant UI
    case "Knowledge Recall Assistant":
        st.header("📚 Knowledge Recall Assistant")

        st.subheader("🔍 Search Knowledge")
        query = st.text_input("Enter your question")

        if st.button("Search"):
            if query:
                response = requests.get(f"{API_BASE_URL}/search_knowledge", params={"query": query})
                if response.status_code == 200:
                    result = response.json()["result"]
                    st.write(f"🧠 AI Response: {result}")
                else:
                    st.error(response.json().get("detail", "Error retrieving knowledge."))


    # Time Management Assistant UI
    case "Time Management Assistant":
        st.header("📅 Pomodoro Cycles & Task Scheduling")

        # Select feature
        option = st.selectbox("Choose an option", ["Task Scheduling", "Task Prioritization", "Pomodoro Recommendation"])
        match option:
            # **Option 1: Task Scheduling**
            case "Task Scheduling":
                st.subheader("📌 Schedule a Task")
                task_name = st.text_input("Task Name")
                estimated_time_hours = st.number_input("Estimated Time (hours)", min_value=1, step=1)
                deadline = st.text_input("Deadline (YYYY-MM-DDTHH:MM:SS)", placeholder="2025-03-01T23:59:59")

                if st.button("Schedule Task"):
                    if task_name and deadline:
                        response = requests.post(f"{API_BASE_URL}/schedule_task",
                                                 json={"task_name": task_name, "estimated_time_hours": estimated_time_hours,
                                                       "deadline": deadline})
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Task scheduled from {result['scheduled_start']} to {result['scheduled_end']}")
                        else:
                            st.error(response.json().get("detail", "Error scheduling task"))

                # **View Scheduled Tasks**
                st.subheader("📅 View Scheduled Tasks")
                if st.button("Get Schedule"):
                    response = requests.get(f"{API_BASE_URL}/get_schedule")
                    if response.status_code == 200:
                        tasks = response.json()["tasks"]
                        if tasks:
                            for task in tasks:
                                st.write(
                                    f"📌 **{task['task_name']}** - ⏳ {task['scheduled_start']} → {task['scheduled_end']}")
                        else:
                            st.write("No scheduled tasks found.")
                    else:
                        st.error("Error retrieving schedule.")

            # **Option 2: Task Prioritization**
            case "Task Prioritization":
                st.subheader("🔝 Prioritize Tasks")
                tasks_input = st.text_area("Enter tasks in JSON format",
                                           placeholder='[{"task_name": "Math Homework", "duration": 2, '
                                                       '"deadline": "2025-03-01T10:00:00"}]')

                if st.button("Prioritize Tasks"):
                    try:
                        tasks_data = json.loads(tasks_input)
                        response = requests.post(f"{API_BASE_URL}/prioritize_tasks", json=tasks_data)
                        if response.status_code == 200:
                            prioritized_tasks = response.json()["prioritized_tasks"]
                            for task in prioritized_tasks:
                                st.write(
                                    f"🔢 Priority {task['priority']}: **{task['task_name']}** (Deadline: {task['deadline']})")
                        else:
                            st.error(response.json().get("detail", "Error prioritizing tasks"))
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format. Please enter valid task data.")

            # **Option 3: Pomodoro Recommendation**
            case "Pomodoro Recommendation":
                st.subheader("⏳ Pomodoro Study Recommendation")
                pomodoro_task = st.text_input("Task Name for Pomodoro")
                pomodoro_duration = st.text_input("Duration (e.g., 25min, 50min)")

                if st.button("Recommend Pomodoro"):
                    if pomodoro_task and pomodoro_duration:
                        response = requests.post(f"{API_BASE_URL}/recommend_pomodoro",
                                                 json={"task": pomodoro_task, "duration": pomodoro_duration})
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"🕒 Recommended Pomodoro Schedule: {result['message']}")
                        else:
                            st.error(response.json().get("detail", "Error generating Pomodoro schedule."))

    # Teaching Style Analysis UI
    case "Teaching Style Analysis":
        st.header("Teaching Style Analysis")

        # Ensure session state for feedback history
        if "teaching_feedback_history" not in st.session_state:
            st.session_state["teaching_feedback_history"] = {}

        # Input fields
        session_id = st.text_input("Session ID", value="default_session")
        teacher_feedback = st.text_area("Enter your teaching feedback:")

        if st.button("Analyze"):
            if teacher_feedback.strip():
                response = requests.post(f"{API_BASE_URL}/analyze_teaching_style",
                                         json={"session_id": session_id, "teacher_feedback": teacher_feedback})
                if response.status_code == 200:
                    result = response.json()
                    teaching_style = result["teaching_style"]

                    # Update session state with new feedback
                    if session_id not in st.session_state["teaching_feedback_history"]:
                        st.session_state["teaching_feedback_history"][session_id] = []

                    st.session_state["teaching_feedback_history"][session_id].append(
                        {"feedback": teacher_feedback, "style": teaching_style}
                    )

                    # Display results
                    st.success(f"**Teaching Style:** {teaching_style}")
                else:
                    st.error("Error connecting to the server.")

        # Display previous feedback history
        if session_id in st.session_state["teaching_feedback_history"]:
            st.subheader("Previous Feedback")
            for entry in st.session_state["teaching_feedback_history"][session_id]:
                st.write(f"- **Feedback:** {entry['feedback']}")
                st.write(f"  **Teaching Style:** {entry['style']}")
                st.write("---")


st.sidebar.write("Demo.")
