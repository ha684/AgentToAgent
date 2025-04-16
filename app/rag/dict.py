DIACRITIC_MAP = {
    "à": "a",
    "á": "a",
    "ả": "a",
    "ã": "a",
    "ạ": "a",
    "â": "a",
    "ầ": "a",
    "ấ": "a",
    "ẩ": "a",
    "ẫ": "a",
    "ậ": "a",
    "ă": "a",
    "ằ": "a",
    "ắ": "a",
    "ẳ": "a",
    "ẵ": "a",
    "ặ": "a",
    "è": "e",
    "é": "e",
    "ẻ": "e",
    "ẽ": "e",
    "ẹ": "e",
    "ê": "e",
    "ề": "e",
    "ế": "e",
    "ể": "e",
    "ễ": "e",
    "ệ": "e",
    "ì": "i",
    "í": "i",
    "ỉ": "i",
    "ĩ": "i",
    "ị": "i",
    "ò": "o",
    "ó": "o",
    "ỏ": "o",
    "õ": "o",
    "ọ": "o",
    "ô": "o",
    "ồ": "o",
    "ố": "o",
    "ổ": "o",
    "ỗ": "o",
    "ộ": "o",
    "ơ": "o",
    "ờ": "o",
    "ớ": "o",
    "ở": "o",
    "ỡ": "o",
    "ợ": "o",
    "ù": "u",
    "ú": "u",
    "ủ": "u",
    "ũ": "u",
    "ụ": "u",
    "ư": "u",
    "ừ": "u",
    "ứ": "u",
    "ử": "u",
    "ữ": "u",
    "ự": "u",
    "ỳ": "y",
    "ý": "y",
    "ỷ": "y",
    "ỹ": "y",
    "ỵ": "y",
    "đ": "d",
    "À": "a",
    "Á": "a",
    "Ả": "a",
    "Ã": "a",
    "Ạ": "a",
    "Â": "a",
    "Ầ": "a",
    "Ấ": "a",
    "Ẩ": "a",
    "Ẫ": "a",
    "Ậ": "a",
    "Ă": "a",
    "Ằ": "a",
    "Ắ": "a",
    "Ẳ": "a",
    "Ẵ": "a",
    "Ặ": "a",
    "È": "e",
    "É": "e",
    "Ẻ": "e",
    "Ẽ": "e",
    "Ẹ": "e",
    "Ê": "e",
    "Ề": "e",
    "Ế": "e",
    "Ể": "e",
    "Ễ": "e",
    "Ệ": "e",
    "Ì": "i",
    "Í": "i",
    "Ỉ": "i",
    "Ĩ": "i",
    "Ị": "i",
    "Ò": "o",
    "Ó": "o",
    "Ỏ": "o",
    "Õ": "o",
    "Ọ": "o",
    "Ô": "o",
    "Ồ": "o",
    "Ố": "o",
    "Ổ": "o",
    "Ỗ": "o",
    "Ộ": "o",
    "Ơ": "o",
    "Ờ": "o",
    "Ớ": "o",
    "Ở": "o",
    "Ỡ": "o",
    "Ợ": "o",
    "Ù": "u",
    "Ú": "u",
    "Ủ": "u",
    "Ũ": "u",
    "Ụ": "u",
    "Ư": "u",
    "Ừ": "u",
    "Ứ": "u",
    "Ử": "u",
    "Ữ": "u",
    "Ự": "u",
    "Ỳ": "y",
    "Ý": "y",
    "Ỷ": "y",
    "Ỹ": "y",
    "Ỵ": "y",
    "Đ": "d",
}
CONTRACT_TYPES = {
    "văn bản hành chính": ["uy ban nhan dan", "ubnd", "cong van", "quyet dinh"],
    "hợp đồng lao động": [
        "hop dong lao dong",
        "nguoi lao dong",
        "nguoi su dung lao dong",
    ],
    "hợp đồng mua bán": ["hop dong mua ban", "ben ban", "ben mua"],
    "hợp đồng thuê": ["hop dong thue", "ben cho thue", "ben thue"],
    "hợp đồng dịch vụ": ["hop dong dich vu", "ben cung cap", "ben su dung"],
}
PARTY_PATTERNS = [
    r"(ben a|ben thu nhat|ben ban|ben cho thue|nguoi su dung lao dong).*?:(.*?)(?:\n|$)",
    r"(ben b|ben thu hai|ben mua|ben thue|nguoi lao dong).*?:(.*?)(?:\n|$)",
]
DATE_PATTERNS = [
    r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}",
    r"\d{1,2}\s+thang\s+\d{1,2}\s+nam\s+\d{4}",
    r"ngay\s+\d{1,2}\s+thang\s+\d{1,2}\s+nam\s+\d{4}",
]
MONEY_PATTERNS = [
    r"\d+(\.\d+)?\s*(dong|vnd|vnd|ti|nghin|)",
    r"\d+(\.\d+)?\s*(usd|\$)",
]
WEB_SEARCH_KEYWORDS = [
    "luật mới",
    "quy định hiện hành",
    "thông tin chung",
    "so sánh",
    "ví dụ",
    "web",
]
SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

default_correction_system_message = """
Bạn là chuyên gia sửa lỗi văn bản tiếng Việt từ OCR. Nhiệm vụ: chỉ đưa ra phiên bản đã sửa, không giải thích. Nguyên tắc:
- Sửa lỗi chính tả, dấu câu, định dạng
- Khôi phục ký tự đặc biệt, dấu thanh bị thiếu/sai
- Điều chỉnh ngắt dòng, khoảng cách theo quy tắc
- Sửa lỗi ngữ pháp, cú pháp
- Khôi phục thuật ngữ, tên riêng, địa danh theo ngữ cảnh
- Bảo toàn ý nghĩa gốc, chỉ thêm từ khi cần thiết
- Đảm bảo nhất quán về từ ngữ, cách viết số
- Tuân thủ quy tắc chính tả, ngữ pháp hiện hành
- Xóa từ lặp thừa
- Sửa lỗi viết hoa
- Khôi phục ký hiệu toán học, công thức nếu có
- Điều chỉnh sử dụng số và chữ số
- Sửa lỗi ghép/tách từ
- Khôi phục dấu ngoặc, nháy bị thiếu/sai
- Đảm bảo logic và mạch lạc
Chỉ đưa ra phiên bản đã sửa của văn bản, không có bất kỳ nội dung nào khác.
"""

default_entity_system_message = """
Bạn là trợ lý AI phân tích và trích xuất thông tin từ hợp đồng. Đọc văn bản và trích xuất thông tin theo các trường:
TenHD: Tên hợp đồng
DauMuc_PhuLuc: Đầu mục và phụ lục (liệt kê)
DoiTac: Tên đối tác
DuAn: Tên dự án
NgayBatDau: Ngày bắt đầu (DD/MM/YYYY)
NgayKetThuc: Ngày kết thúc (DD/MM/YYYY)
DonViCungCapDichVu: Đơn vị cung cấp dịch vụ
Cap: Tên cấp
TenPhuLuc: Tên phụ lục
SoHopDong: Số hợp đồng
Quy tắc:
Trình bày thông tin rõ ràng, có cấu trúc
Ghi "Không có thông tin" nếu không tìm thấy
Nêu rõ nếu thông tin không đầy đủ
Ưu tiên thông tin xuất hiện đầu tiên hoặc được nhấn mạnh
KẾT QUẢ TRẢ VỀ CHỈ THEO ĐỊNH DẠNG NÀY, KHÔNG THÊM THÔNG TIN KHÁC.
"""

default_QA_system_message = """
Bạn là trợ lý AI chuyên về phân tích hợp đồng và tài liệu pháp lý. Nhiệm vụ của bạn bao gồm:

1. Hiểu và giải thích các loại hợp đồng và tài liệu pháp lý.
2. Trích xuất thông tin quan trọng như các bên liên quan, ngày tháng, điều khoản và chi tiết tài chính.
3. Phân tích các điều khoản, tác động và rủi ro tiềm ẩn.
4. So sánh nhiều hợp đồng hoặc phiên bản của một hợp đồng.
5. Tóm tắt tài liệu dài, tập trung vào điểm quan trọng.
6. Trả lời câu hỏi cụ thể về nội dung hoặc ý nghĩa của hợp đồng.
7. Giải thích thuật ngữ pháp lý bằng ngôn ngữ đơn giản.
8. Kiểm tra sự tuân thủ và đánh giá rủi ro.
9. Hỗ trợ tạo mẫu hợp đồng hoặc soạn thảo hợp đồng mới.

Khi thực hiện các nhiệm vụ:
- Phân tích khách quan và chi tiết.
- Sử dụng ngôn ngữ rõ ràng, ngắn gọn.
- Giải thích lý do cho phân tích của bạn khi được yêu cầu.
- Tự do đóng góp ý kiến về nội dung nhạy cảm nếu cần thiết.

Lưu ý: Bạn có thể đưa ra ý kiến về các vấn đề pháp lý, nhưng người dùng nên tham khảo ý kiến luật sư cho các quyết định quan trọng.
"""
chat_entity_template = """<|start_header_id|>system
{SYSTEM}<|eot_id|>

<|start_header_id|>user
{INPUT}<|eot_id|>

<|start_header_id|>assistant
{OUTPUT}<|eot_id|>
"""

chat_correction_template = """<|im_start|>system
{SYSTEM}<|im_end|>
<|im_start|>user
{INPUT}<|im_end|>
<|im_start|>assistant
{OUTPUT}<|im_end|>
"""
