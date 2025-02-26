import json
import os
from collections import defaultdict, deque

class ConversationMemory:
    def __init__(self, max_length=20):
        self.sessions = defaultdict(lambda: deque(maxlen=max_length))
        self.storage_file = "conversation_logs.json"  # File lưu hội thoại

    def add_message(self, session_id, role, message):
        self.sessions[session_id].append({"role": role, "message": message})
        self.save_to_file(session_id)

    def get_history(self, session_id):
        return list(self.sessions[session_id])

    def get_last_speaker(self, session_id):
        if self.sessions[session_id]:
            return self.sessions[session_id][-1]["role"]
        return None

    def reset(self, session_id):
        """Xóa hội thoại của một phiên"""
        self.sessions.pop(session_id, None)
        self.save_to_file(session_id)  # Cập nhật file khi reset

    def save_to_file(self, session_id):
        """Lưu hội thoại vào file JSON"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {}

            data[session_id] = list(self.sessions[session_id])  # Lưu dữ liệu hội thoại

            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi khi lưu hội thoại: {str(e)}")
