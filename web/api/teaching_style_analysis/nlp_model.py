from web.api.api_utils import generate_response

TEACHING_STYLES = ["Hỗ trợ", "Nghiêm khắc", "Sáng tạo", "Phân tích"]

def classify_teaching_style(teacher_feedback):
    """Dùng GPT-4o Mini từ `api_utils.py` để phân tích phong cách giảng dạy"""
    try:
        messages = [
            {"role": "system", "content": "Bạn là một chuyên gia giáo dục có khả năng phân tích phong cách giảng dạy."},
            {"role": "user", "content": f"Phản hồi từ giáo viên: {teacher_feedback}\n"
                                        f"Hãy xác định phong cách giảng dạy phù hợp từ danh sách sau: {', '.join(TEACHING_STYLES)}."
                                        f"Chỉ trả lời bằng một trong các phong cách giảng dạy đã cho."}
        ]

        response = generate_response(messages)
        return response.strip()
    except Exception as e:
        print(f"❌ Lỗi khi gọi OpenAI: {str(e)}")
        return f"Lỗi khi gọi OpenAI: {str(e)}"
