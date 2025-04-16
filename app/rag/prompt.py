from llama_index.core import PromptTemplate
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.vector_stores.types import (
    FilterOperator,
    MetadataFilter,
    MetadataInfo,
    VectorStoreInfo,
    VectorStoreQuerySpec,
)
from llama_index.core.prompts.prompt_type import PromptType

react_prompt = """# System Instructions

## Vai Trò Cơ Bản
Bạn là một trợ lý AI được thiết kế để phản hồi tin nhắn của người dùng. Đối với thông tin thời gian thực, cập nhật, hoặc yêu cầu tìm kiếm, bạn PHẢI sử dụng các công cụ được cung cấp.

## Công Cụ Sẵn Có
Bạn có quyền truy cập vào các công cụ sau để hoàn thành nhiệm vụ:
{tool_desc}

## Định Dạng Phản Hồi

### Khi Nào Cần Dùng Công Cụ
Sử dụng công cụ KHI:
- Câu hỏi yêu cầu tìm kiếm dữ liệu cụ thể
- Câu hỏi yêu cầu truy cập thông tin bên ngoài

Để trả lời câu hỏi khi sử dụng công cụ, vui lòng sử dụng định dạng sau:
```
Thought: Tôi cần sử dụng một công cụ 
Action: tên công cụ (phải là một trong {tool_names}) 
Action Input: tham số công cụ ở định dạng JSON, ví dụ: {{"input": "hello world"}}
```
LUÔN BẮT ĐẦU với một Thought.
Sử dụng định dạng JSON hợp lệ cho Action Input.
Nếu định dạng này được sử dụng, người dùng sẽ phản hồi theo định dạng sau:
```
Observation: phản hồi từ công cụ
```
Bạn có thể tiếp tục lặp lại định dạng trên cho đến khi có đủ thông tin để trả lời câu hỏi.
HOẶC bạn đã có thể trả lời câu hỏi dựa trên phản hồi từ công cụ, Khi đó, bạn PHẢI phản hồi theo định dạng sau:
```
Thought: Tôi có thể trả lời mà không cần sử dụng thêm công cụ. 
Answer: [Câu trả lời chi tiết của bạn]
```
### Khi Không Cần Công Cụ
Trả lời trực tiếp KHI:
- Câu hỏi chung không cần dữ liệu thời gian thực
- Câu hỏi dựa trên kiến thức có sẵn
- Yêu cầu giải thích hoặc hướng dẫn cơ bản
- Không cần truy cập thông tin bên ngoài

Định dạng phản hồi:
Thought: Tôi có thể trả lời mà không cần sử dụng thêm công cụ.
Answer: [Câu trả lời chi tiết của bạn]

## Quy Tắc Quan Trọng
1. LUÔN bắt đầu với "Thought"
2. Sử dụng JSON hợp lệ cho Action Input
3. KHÔNG truyền tham số rỗng cho công cụ
4. Chỉ sử dụng công cụ khi thực sự cần thiết

## Yêu Cầu Về Chất Lượng
- Ngắn gọn nhưng đầy đủ
- Giải thích rõ ràng lý do
- Định dạng để dễ đọc
- Kiểm tra tham số công cụ trước khi sử dụng
- Đảm bảo trả lời đúng yêu cầu người dùng
"""

system_prompt_basic = """Bạn là một trợ lý AI thông minh với kiến thức rộng về nhiều lĩnh vực. Bạn có khả năng phân tích sâu sắc, lập luận logic và tạo ra nội dung chất lượng cao. Hãy tập trung vào việc cung cấp thông tin chính xác, ngắn gọn nhưng đầy đủ, và phù hợp với văn hóa Việt Nam. Luôn duy trì tính chuyên nghiệp và đạo đức trong giao tiếp.
## Quan trọng:
- Khi không biết câu trả lời chính xác cho một câu hỏi, bạn cần phải trả lời một cách trung thực và rõ ràng, nói rằng **"Tôi không biết"** thay vì suy đoán hoặc đưa ra thông tin không chính xác.
Bạn có thể giao tiếp bằng nhiều ngôn ngữ, nhưng ưu tiên sử dụng tiếng Việt. Khi cần thiết, bạn có thể tạo ra các phân tích chuyên sâu, đánh giá phê bình, và các bài viết sáng tạo phản ánh tư duy sâu sắc của con người.
Câu trả lời của bạn nên chính xác và toàn diện khi cần thiết, nhưng ưu tiên sự ngắn gọn mà không làm mất đi ý nghĩa hoặc độ chính xác. Bạn cũng có thể thể hiện sự đồng cảm trong giới hạn của một AI để nâng cao trải nghiệm người dùng.
"""
system_prompt_test = """Tôi là một trợ lý hữu ích với quyền truy cập vào các chức năng. Hãy sử dụng chúng nếu cần thiết.
"""

thinking_budget = 3 * 7
system_prompt = """
Bạn là một trợ lý AI. Vai trò chính của bạn là tạo điều kiện cho cuộc trò chuyện bình thường đồng thời đóng vai trò là một chuyên gia giải quyết vấn đề. Hãy tuân theo các hướng dẫn sau một cách cẩn thận:

1. Dịch thuật: Nếu câu hỏi không phải bằng tiếng Việt, hãy dịch nó sang tiếng Việt.
2. Đặt lại bộ đếm: Đọc kỹ câu hỏi và đặt lại bộ đếm giữa <count> và </count> thành 21.
3. Giải pháp từng bước: Tạo ra một giải pháp chi tiết, hợp lý từng bước, sử dụng tối đa 21 bước. Mỗi bước phải được đóng trong các thẻ <step> và </step>.
4. Đếm ngược: Theo dõi các bước của bạn bằng cách giảm số đếm trong <count> và </count>. Dừng tạo thêm các bước khi số đếm đạt 0; bạn không cần phải sử dụng tất cả các bước có sẵn.
5. Tự suy ngẫm: Nếu không chắc chắn về cách tiếp tục, hãy suy ngẫm về lý luận của bạn và quyết định xem có nên quay lại các bước trước đó không.
6. Tổng hợp các bước: Sau khi hoàn thành các bước, sắp xếp lại và tổng hợp thông tin thành câu trả lời cuối cùng, đóng trong các thẻ <answer> và </answer>.
7. Tự đánh giá: Cung cấp một đánh giá tự phê bình và trung thực về quá trình lập luận của bạn trong các thẻ <reflection> và </reflection>.
8. Điểm chất lượng: Gán một điểm chất lượng cho giải pháp của bạn như một số float giữa 0.0 (chất lượng thấp nhất) và 1.0 (chất lượng cao nhất), đóng trong các thẻ <reward> và </reward>.
9. Dịch lại: Cuối cùng, dịch câu trả lời cuối cùng trở lại ngôn ngữ gốc của câu hỏi đã cho.

Ví dụ về định dạng:            
<count> [ngân sách bắt đầu] </count>
<step> [Nội dung của bước 1] </step>
<count> [ngân sách còn lại] </count>
<step> [Nội dung của bước 2] </step>
<reflection> [Đánh giá các bước cho đến nay] </reflection>
<reward> [Số float giữa 0.0 và 1.0] </reward>
<count> [ngân sách còn lại] </count>
<step> [Nội dung của bước 3 hoặc Nội dung của một bước trước đó] </step>
<count> [ngân sách còn lại] </count>
...
<step>  [Nội dung của bước cuối cùng] </step>
<count> [ngân sách còn lại] </count>
<answer> [Câu trả lời cuối cùng] </answer> (phải đưa ra câu trả lời cuối cùng theo định dạng này)
<reflection> [Đánh giá giải pháp] </reflection>
<reward> [Số float giữa 0.0 và 1.0] </reward>
""".format(
    budget=thinking_budget
)

planner = """Bạn là một trợ lý AI được trang bị một công cụ truy xuất câu trả lời. Khi nhận được câu hỏi, hãy làm theo các bước sau:
1. ĐÁNH GIÁ ĐỘ PHỨC TẠP:
- Đánh giá độ phức tạp của câu hỏi trên thang điểm từ 0-5
- 0: Câu hỏi đơn giản, có thể trả lời trực tiếp
- 5: Câu hỏi phức tạp, cần nhiều thông tin và phân tích sâu
2. LẬP KẾ HOẠCH TRUY XUẤT:
- Nếu độ phức tạp > 3: Chia câu hỏi thành các truy vấn nhỏ hơn
- Với mỗi truy vấn, xác định các từ khóa chính
- Sắp xếp thứ tự truy vấn từ thông tin cơ bản đến chuyên sâu
3. THỰC HIỆN TRUY XUẤT:
Sử dụng công cụ truy_xuất_câu_trả_lời với format:
#E[số] = truy_xuất_câu_trả_lời[
    truy vấn: <câu truy vấn được tối ưu>,
    độ phức tạp: <số từ 0-5>
]
4. TỔNG HỢP KẾT QUẢ:
- Kết hợp các thông tin từ #E[số]
- Đảm bảo câu trả lời:
  + Đầy đủ và chính xác
  + Có cấu trúc rõ ràng
  + Phù hợp với ngữ cảnh câu hỏi
Câu hỏi của người dùng: {question}"""

contextual_retrieval_prompt = """
<document>
{doc_content}
</document>

Đây là đoạn văn bản chúng ta muốn đặt trong bối cảnh của toàn bộ tài liệu:
<chunk>
{chunk_content}
</chunk>

Vui lòng cung cấp một bối cảnh ngắn gọn để đặt đoạn văn bản này trong toàn bộ tài liệu, nhằm mục đích cải thiện việc tìm kiếm và truy xuất đoạn văn bản này.
Chỉ trả lời với bối cảnh ngắn gọn và không thêm thông tin nào khác.
"""

query_gen_str = """Tạo {num_queries} truy vấn phụ từ câu hỏi gốc. Yêu cầu:
- Ngắn gọn, mỗi truy vấn một dòng
- Giữ nguyên ý nghĩa gốc
- Bắt buộc dùng tiếng Việt

Câu hỏi gốc:
<query>
{query}
</query>

Truy vấn phụ:"""

context = """
Vai trò: Bạn là trợ lý pháp lý chuyên nghiệp, tập trung vào văn bản hành chính và hợp đồng.

Nhiệm vụ:
1. Phân tích và trả lời câu hỏi sử dụng các công cụ được cung cấp.
2. Trích dẫn nguồn thông tin:
   - Khi trích xuất thông tin từ web, trích dẫn nguồn ở cuối câu trả lời.

Nguyên tắc làm việc:
- Suy nghĩ kỹ lưỡng và logic trước khi đưa ra câu trả lời.
- Đối với câu hỏi không liên quan trực tiếp đến lĩnh vực pháp lý, sử dụng kiến thức chung để trả lời.
- Luôn trả lời bằng tiếng Việt, đảm bảo ngôn ngữ chuyên nghiệp và dễ hiểu.
- Ưu tiên sự chính xác và đầy đủ của thông tin.

Lưu ý: Nếu không chắc chắn về bất kỳ thông tin nào, hãy thông báo rõ ràng cho người dùng và đề xuất tìm kiếm thêm từ các nguồn đáng tin cậy.
"""

TITLE_NODE_TEMPLATE = """\
Bối cảnh: {context_str}. 
Hãy đưa ra một tiêu đề khái quát, tóm lược các thực thể, chủ đề hoặc điểm nổi bật có trong bối cảnh. 
Tiêu đề: """

TITLE_COMBINE_TEMPLATE = """\
{context_str}. Dựa trên các tiêu đề đã đề xuất và nội dung trên, \
hãy đưa ra tiêu đề tổng quát nhất cho tài liệu này. 
Tiêu đề: """

QUESTION_GEN_TMPL = """\
Dưới đây là bối cảnh:
{context_str}
Dựa trên thông tin từ bối cảnh này, \
hãy đưa ra {num_questions} câu hỏi có thể nhận được câu trả lời cụ thể từ ngữ cảnh. \
Những câu trả lời này nên mang tính độc đáo, khó có thể tìm thấy ở nơi khác.
Ngoài ra, bạn có thể sử dụng các bản tóm tắt cấp cao của bối cảnh để tạo ra \
những câu hỏi sâu sắc và tốt hơn mà bối cảnh này có thể trả lời.
"""


SUMMARY_EXTRACT_TEMPLATE = """\
Nội dung:
{context_str}

Yêu cầu:
1. Xác định 3-5 chủ đề chính quan trọng nhất
2. Liệt kê các thực thể chủ chốt (con người, tổ chức, địa điểm, sự kiện)
3. Tóm tắt trong 2-3 đoạn văn ngắn gọn, súc tích
4. Sắp xếp theo thứ tự ưu tiên/thời gian

Lưu ý: Tập trung vào thông tin thiết yếu, bỏ qua chi tiết phụ.

Bản tóm tắt:"""

KEYWORD_EXTRACT_TEMPLATE = """\
{context_str}. Hãy đưa ra {keywords} từ khóa cho tài liệu này. 
Định dạng theo kiểu cách nhau bằng dấu phẩy. 
Từ khóa: """

EXTRACT_TEMPLATE_STR = """\
Dưới đây là nội dung của phần:
----------------
{context_str}
----------------
Dựa trên thông tin ngữ cảnh, hãy trích xuất một đối tượng {class_name}.
"""

NODE_TEXT_TEMPLATE = """\
Thông tin tài liệu:
{metadata_str}

Nội dung trích đoạn:
-----
{content}
-----\n"""

DEFAULT_KG_TRIPLET_EXTRACT_TMPL = (
    "Dưới đây là một đoạn văn bản. Từ văn bản này, hãy trích xuất tối đa "
    "{max_knowledge_triplets} "
    "bộ ba kiến thức dưới dạng (chủ thể, vị ngữ, tân ngữ). Tránh sử dụng các từ dừng.\n"
    "---------------------\n"
    "Ví dụ:\n"
    "Văn bản: Mai là mẹ của Lan.\n"
    "Bộ ba:\n(Mai, là mẹ của, Lan)\n"
    "Văn bản: Highland là chuỗi cà phê được thành lập tại Sài Gòn vào năm 1999.\n"
    "Bộ ba:\n"
    "(Highland, là, chuỗi cà phê)\n"
    "(Highland, thành lập tại, Sài Gòn)\n"
    "(Highland, thành lập vào, 1999)\n"
    "---------------------\n"
    "Văn bản: {text}\n"
    "Bộ ba:\n"
)

KEYWORD_EXTRACT_TEMPLATE_TMPL = (
    "Một số văn bản được cung cấp dưới đây. Dựa vào văn bản, trích xuất tối đa {max_keywords} "
    "từ khóa từ văn bản. Tránh các từ dừng."
    "---------------------\n"
    "{text}\n"
    "---------------------\n"
    "Cung cấp từ khóa theo định dạng phân tách bằng dấu phẩy sau: 'TỪ KHÓA: <từ khóa>'\n"
)

QA_PROMPT_TMPL = """Here are the retrieved documents for your query:

<documents>
{context_str}
</documents>

Your task is to analyze these documents and provide a response with both Citations and Response sections.

Requirements:
1. CITATIONS SECTION:
   - Must use the format:
    <citation>
    - Document ID: {{doc_id}}
    - Content: {{verbatim quote}}
    </citation>
   - Include only VERBATIM quotes from documents
   - Each citation must be complete and relevant
   - Order citations logically to support your response

2. RESPONSE SECTION:
   - Structure using the format:
    <response>
    {{your complete analysis}}
    </response>
   - Connect each key point to specific citations
   - Present information in clear, logical paragraphs
   - Maintain professional tone throughout

Remember:
- All key facts must have citations
- If information is missing or unclear, state this explicitly
- Stay within the scope of provided documents
- Answer in the user's query language
- For conflicting information, explain the discrepancy

User Query: {query_str}
"""

QA_PROMPT_TMPL_NO_VERIFY = """Here are the retrieved documents for your query:

<documents>
{context_str}
</documents>

Please provide a clear, professional response using the information from these documents when relevant. If the documents don't contain pertinent information, provide a response base on your knowledges.

Remember:
- Structure your response with clear paragraphs
- Stay focused on the query
- Answer in the user's query language
- Note any significant gaps in information
- Maintain professional tone throughout

User Query: {query_str}
"""

DEFAULT_KEYWORD_EXTRACT_TEMPLATE_TMPL = (
    "Dưới đây là một đoạn văn bản. Dựa vào đoạn văn bản này, hãy trích xuất tối đa {max_keywords} "
    "từ khóa từ văn bản. Tránh các từ dừng (stopwords)."
    "---------------------\n"
    "{text}\n"
    "---------------------\n"
    "Hãy cung cấp các từ khóa theo định dạng ngăn cách bởi dấu phẩy như sau: 'KEYWORDS: <từ khóa>'\n"
)

DEFAULT_QUERY_KEYWORD_EXTRACT_TEMPLATE_TMPL = (
    "Dưới đây là một câu hỏi. Dựa vào câu hỏi này, hãy trích xuất tối đa {max_keywords} "
    "từ khóa từ văn bản. Tập trung vào việc trích xuất các từ khóa có thể giúp chúng ta tìm kiếm "
    "câu trả lời tốt nhất cho câu hỏi. Tránh các từ dừng (stopwords).\n"
    "---------------------\n"
    "{question}\n"
    "---------------------\n"
    "Hãy cung cấp các từ khóa theo định dạng ngăn cách bởi dấu phẩy như sau: 'KEYWORDS: <từ khóa>'\n"
)

DEFAULT_TEXT_QA_PROMPT_TMPL = (
    "Bối cảnh:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Hướng dẫn:\n"
    "1. Chỉ sử dụng ĐÚNG các thông tin được cung cấp trong bối cảnh trên.\n"
    "2. Trả lời ngắn gọn, rõ ràng và chính xác.\n"
    "3. Nếu thông tin không đủ để trả lời, hãy nói 'Không đủ thông tin'.\n"
    "\n"
    "Câu hỏi: {query_str}\n"
    "Câu trả lời: "
)

DEFAULT_REFINE_PROMPT_TMPL = (
    "Câu hỏi gốc: {query_str}\n"
    "Câu trả lời hiện tại: {existing_answer}\n"
    "Thông tin bổ sung:\n"
    "------------\n"
    "{context_msg}\n"
    "------------\n"
    "Hãy điều chỉnh câu trả lời để:\n"
    "1. Chính xác hơn\n"
    "2. Bao quát thông tin mới\n"
    "3. Giữ nguyên ý chính nếu không có thông tin mới quan trọng\n"
    "Câu trả lời cải tiến: "
)
DEFAULT_REFINE_PROMPT = PromptTemplate(
    DEFAULT_REFINE_PROMPT_TMPL, prompt_type=PromptType.REFINE
)

TEXT_QA_SYSTEM_PROMPT = ChatMessage(
    content=(
        "Bạn là một hệ thống hỏi đáp chuyên gia được tin cậy trên toàn thế giới.\n"
        "Luôn trả lời câu hỏi dựa trên thông tin ngữ cảnh đã cung cấp, "
        "và không sử dụng kiến thức trước đó.\n"
        "Một số quy tắc cần tuân thủ:\n"
        "1. Không bao giờ tham chiếu trực tiếp đến ngữ cảnh đã cho trong câu trả lời của bạn.\n"
        "2. Tránh các phát biểu như 'Dựa trên ngữ cảnh, ...' hoặc "
        "'Thông tin ngữ cảnh ...' hoặc bất kỳ điều gì tương tự."
    ),
    role=MessageRole.SYSTEM,
)

TEXT_QA_PROMPT_TMPL_MSGS = [
    TEXT_QA_SYSTEM_PROMPT,
    ChatMessage(
        content=(
    "Bối cảnh:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Hướng dẫn:\n"
    "1. Chỉ sử dụng ĐÚNG các thông tin được cung cấp trong bối cảnh trên.\n"
    "2. Trả lời ngắn gọn, rõ ràng và chính xác.\n"
    "3. Nếu thông tin không đủ để trả lời, hãy nói 'Không đủ thông tin'.\n"
    "\n"
    "Câu hỏi: {query_str}\n"
    "Câu trả lời: "
),
        role=MessageRole.USER,
    ),
]

CHAT_REFINE_PROMPT_TMPL_MSGS = [
    ChatMessage(
        content=(
    "Vai trò: Hệ thống hỗ trợ chuyên gia tối ưu hóa câu trả lời\n"
    "Nguyên tắc hoạt động:\n"
    "• Phân tích kỹ lưỡng ngữ cảnh mới và câu trả lời hiện tại\n"
    "• Đưa ra câu trả lời chính xác, súc tích và có giá trị gia tăng\n"
    "\n"
    "Chiến lược xử lý:\n"
    "1. NẾU ngữ cảnh mới chứa thông tin bổ sung/chi tiết hơn:\n"
    "   - Viết lại câu trả lời để tích hợp thông tin mới\n"
    "   - Đảm bảo thông tin chính xác và toàn diện hơn\n"
    "\n"
    "2. NẾU ngữ cảnh mới không cung cấp giá trị gia tăng:\n"
    "   - Giữ nguyên câu trả lời ban đầu\n"
    "   - Không thay đổi nếu không có lý do chính đáng\n"
    "\n"
    "Quy tắc vàng:\n"
    "• Không được nhắc trực tiếp đến câu trả lời gốc\n"
    "• Luôn tập trung vào chất lượng và độ chính xác\n"
    "• Thể hiện tính chuyên nghiệp và khách quan\n"
    "\n"
    "Ngữ cảnh mới: {context_msg}\n"
    "Câu hỏi: {query_str}\n"
    "Câu trả lời gốc: {existing_answer}\n"
    "Câu trả lời mới: "
),
        role=MessageRole.USER,
    )
]
DEFAULT_RESPONSE_TEMPLATE = (
    "Truy vấn Cypher được tạo:\n{query}\n\n" "Phản hồi Cypher:\n{response}"
)

DEFAULT_SUMMARY_TEMPLATE = PromptTemplate(
    """Vai trò: Chuyên gia trả lời câu hỏi chính xác và súc tích

    Nguyên tắc vàng:
    • Sử dụng ĐÚNG và CHÍNH XÁC thông tin được cung cấp
    • Trả lời ngắn gọn, rõ ràng và trực tiếp
    • Loại bỏ mọi diễn giải không cần thiết
    • Không nhắc đến nguồn thông tin
    • Đảm bảo câu trả lời tự nhiên như trao đổi trực tiếp

    Hướng dẫn định dạng:
    1. Bắt đầu trả lời trực tiếp và súc tích
    2. Sử dụng ngôn ngữ dễ hiểu
    3. Không thêm lời giải thích thừa
    4. Tập trung vào trọng tâm của câu hỏi

    Ví dụ mẫu:
    Câu hỏi: Chuyến bay giữa sân bay ANC và SEA dài bao nhiêu dặm?
    Thông tin: [{"r.dist": 1440}]
    Câu trả lời: Chuyến bay giữa sân bay ANC và SEA dài 1440 dặm.

    Câu hỏi: 
    {question}
    
    Thông tin: 
    {context}
    
    Câu trả lời hữu ích:"""
)

DEFAULT_MULTI_SELECT_PROMPT_TMPL = """Dưới đây là một số lựa chọn. Mỗi lựa chọn có số thứ tự (từ 1 đến {num_choices}),
và mỗi số tương ứng với một tóm tắt.\n
---------------------\n
{context_list}
\n---------------------\n
Chỉ dùng các lựa chọn trên, không dùng kiến thức khác, hãy chọn những lựa chọn quan trọng nhất (không quá {max_outputs}) 
để trả lời câu hỏi: '{query_str}'
"""

QUERY_GEN_RPOMPT = """Nhiệm vụ: Tạo các phiên bản mở rộng của truy vấn tìm kiếm bằng cách:
1. Thêm từ khóa liên quan
2. Khôi phục dấu câu nếu thiếu
3. Giữ nguyên ý chính

Input:
- Query: {query}
- Số lượng: {num_queries}
"""

DEFAULT_CHOICE_SELECT_PROMPT_TMPL = """Mô tả danh sách các tài liệu dưới đây. Mỗi tài liệu có một số kèm theo 
với tóm tắt của tài liệu đó. Câu hỏi cũng được đưa ra. \n
Hãy trả lời bằng cách cung cấp các số của các tài liệu mà bạn cần tham khảo để trả lời câu hỏi, theo thứ tự mức độ liên quan, 
cùng với điểm mức độ liên quan. Điểm mức độ liên quan là một con số từ 1-10 dựa trên mức độ liên quan mà bạn nghĩ tài liệu đó có đối với câu hỏi.\n
Đừng bao gồm những tài liệu không liên quan đến câu hỏi. \n
Ví dụ định dạng: \n
Tài liệu 1:\n<tóm tắt tài liệu 1>\n\n
Tài liệu 2:\n<tóm tắt tài liệu 2>\n\n
...\n\n
Tài liệu 10:\n<tóm tắt tài liệu 10>\n\n
Câu hỏi: <câu hỏi>\n
Trả lời:\n
Tài liệu: 9, Mức độ liên quan: 7\n
Tài liệu: 3, Mức độ liên quan: 4\n
Tài liệu: 7, Mức độ liên quan: 3\n\n
Hãy thử làm điều này ngay bây giờ: \n\n
{context_str}\n
Câu hỏi: {query_str}\n
Trả lời:\n
"""

DEFAULT_EXTRACT_TEMPLATE_STR = """Đây là nội dung của phần:
----------------
{context_str}
----------------
Dựa trên thông tin ngữ cảnh, hãy trích xuất một đối tượng {class_name}.
"""

PREFIX = """\
Mục tiêu của bạn là cấu trúc truy vấn của người dùng sao cho phù hợp với sơ đồ yêu cầu được cung cấp dưới đây.

<< Sơ đồ yêu cầu có cấu trúc >>
Khi phản hồi, sử dụng đoạn mã markdown với một đối tượng JSON được định dạng theo sơ đồ \
dưới đây:

{schema_str}

Chuỗi truy vấn chỉ nên chứa văn bản dự kiến khớp với nội dung của các tài liệu. Mọi điều kiện lọc không nên được đề cập trong truy vấn.

Đảm bảo rằng các bộ lọc chỉ tham chiếu đến các thuộc tính tồn tại trong nguồn dữ liệu.
Đảm bảo rằng các bộ lọc xem xét mô tả của các thuộc tính.
Đảm bảo rằng bộ lọc chỉ được sử dụng khi cần thiết. Nếu không có bộ lọc nào cần áp dụng, hãy trả về [] cho giá trị bộ lọc.\

Nếu truy vấn của người dùng có đề cập rõ ràng đến số lượng tài liệu cần lấy, hãy thiết lập `top_k` bằng số đó, nếu không thì không cần thiết lập `top_k`.

"""

example_info = VectorStoreInfo(
    content_info="Lyrics of a song",
    metadata_info=[
        MetadataInfo(name="artist", type="str", description="Name of the song artist"),
        MetadataInfo(
            name="genre",
            type="str",
            description='The song genre, one of "pop", "rock" or "rap"',
        ),
    ],
)
example_query = "What are songs by Taylor Swift or Katy Perry in the dance pop genre"
example_output = VectorStoreQuerySpec(
    query="teenager love",
    filters=[
        MetadataFilter(key="artist", value="Taylor Swift"),
        MetadataFilter(key="artist", value="Katy Perry"),
        MetadataFilter(key="genre", value="pop"),
    ],
)

example_info_2 = VectorStoreInfo(
    content_info="Classic literature",
    metadata_info=[
        MetadataInfo(name="author", type="str", description="Author name"),
        MetadataInfo(
            name="book_title",
            type="str",
            description="Book title",
        ),
        MetadataInfo(
            name="year",
            type="int",
            description="Year Published",
        ),
        MetadataInfo(
            name="pages",
            type="int",
            description="Number of pages",
        ),
        MetadataInfo(
            name="summary",
            type="str",
            description="A short summary of the book",
        ),
    ],
)

example_query_2 = "What are some books by Jane Austen published after 1813 that explore the theme of marriage for social standing?"

example_output_2 = VectorStoreQuerySpec(
    query="Books related to theme of marriage for social standing",
    filters=[
        MetadataFilter(key="year", value="1813", operator=FilterOperator.GT),
        MetadataFilter(key="author", value="Jane Austen"),
    ],
)
EXAMPLES = f"""\
<< Ví dụ 1. >>
Nguồn Dữ Liệu:
```json
{example_info.model_dump_json(indent=4)}
```
Truy vấn của người dùng: {example_query}

Yêu cầu có cấu trúc:
{example_output.model_dump_json()}

<< Ví dụ 2. >>
Nguồn dữ liệu:
```json
{example_info_2.model_dump_json(indent=4)}
```
Truy vấn của người dùng: {example_query_2}

Yêu cầu có cấu trúc:
{example_output_2.model_dump_json()}
""".replace( "{", "{{" ).replace( "}", "}}" )

SUFFIX = """
<< Ví dụ 3. >>
Nguồn Dữ Liệu:
```json
{info_str}
```
Truy vấn của người dùng: {query_str}

Yêu cầu có cấu trúc: """

DEFAULT_VECTOR_STORE_QUERY_PROMPT_TMPL = PREFIX + EXAMPLES + SUFFIX

contextual_retrieval_prompt = """
<document>
{doc_content}
</document>

Đây là đoạn văn bản chúng ta muốn đặt trong bối cảnh của toàn bộ tài liệu:
<chunk>
{chunk_content}
</chunk>

Vui lòng cung cấp một bối cảnh ngắn gọn để đặt đoạn văn bản này trong toàn bộ tài liệu, nhằm mục đích cải thiện việc tìm kiếm và truy xuất đoạn văn bản này.
Chỉ trả lời với bối cảnh ngắn gọn và không thêm thông tin nào khác.
"""

contextual_retrieval_prompt_small = """
<document>
{doc_content}
</document>

Vui lòng cung cấp một bối cảnh ngắn gọn cho tài liệu, nhằm mục đích cải thiện việc tìm kiếm và truy xuất đoạn văn bản này.
Chỉ trả lời với bối cảnh ngắn gọn và không thêm thông tin nào khác.
"""

DEFAULT_TEXT_TO_SQL_TMPL = """The current time is {current_time}. You are an expert in converting conversational input into a precise and optimal {dialect} SQL query. Return ONLY the SQL query without any additional text or explanations.

IMPORTANT: Analyze the ENTIRE conversation history to extract all relevant details for the query. The user's intent may be spread across multiple messages.

Critical rules for accuracy:
1. Use ONLY column names present in the provided schema - no assumptions
2. Always qualify column names with table names (table_name.column_name)
3. For Vietnamese text searches:
   - Preserve ALL diacritics exactly as provided
   - Use exact match first (column = 'value') before trying LIKE
   - When using LIKE, prefer '%exact_phrase%' over breaking into components
4. For string comparisons:
   - Use TRIM() to handle potential whitespace issues
   - Use proper case sensitivity based on dialect (LOWER() or dialect-specific functions)
5. Prioritize specific columns in SELECT when they match information mentioned in the conversation
6. When searching for text/names:
   - Start with most specific columns first (id, name fields)
   - Use targeted WHERE conditions rather than overly broad searches
   - For Vietnamese names, keep full names intact when possible
7. Use table joins ONLY when necessary to answer the question
8. Include appropriate LIMIT clause to prevent excessive results
9. Add ORDER BY for relevant columns to provide meaningful sorting
10. For date comparisons, ensure proper format conversion based on dialect
11. Use relative date references correctly (e.g., "yesterday", "last week", "next month")
12. When information is ambiguous, prioritize the most recent user input

CRITICAL FOR DELETE/UPDATE OPERATIONS:
13. For DELETE operations, ALWAYS check for foreign key constraints first:
   - Examine the schema for tables referencing the target table
   - Generate multiple DELETE statements in correct order (child records first, parent records last)
   - Wrap in transaction if multiple statements are needed (BEGIN; [statements]; COMMIT;)
14. Identify all dependent records that must be deleted first to maintain referential integrity
15. For UPDATE operations affecting primary keys, ensure referential integrity is maintained

Available Schema: {schema}

Review the ENTIRE conversation history above when generating your SQL query.
Output ONLY the SQL query:"""

DEFAULT_TEXT_TO_SQL_PROMPT = PromptTemplate(
    DEFAULT_TEXT_TO_SQL_TMPL,
    prompt_type=PromptType.TEXT_TO_SQL,
)

DEFAULT_RESPONSE_SYNTHESIS_PROMPT_TMPL_V2 = (
    "You are an expert SQL analyst. Below is the result of a database query, along with "
    "information about the query and table structures. Analyze the results and provide an "
    "informative response to the original question.\n\n"
    "Context for analysis:\n"
    "1. Original question: {query_str}\n"
    "2. SQL query executed: {sql_query}\n"
    "3. Query result:\n{context_str}\n\n"
    "Your response should be entirely grounded in the retrieved data and use the same language as the original question. Do not introduce external information or assumptions unless explicitly stating them as such. Do not suggest additional SQL queries.\n\n"
    "Your response:"
)

DEFAULT_RESPONSE_SYNTHESIS_PROMPT_V2 = PromptTemplate(
    DEFAULT_RESPONSE_SYNTHESIS_PROMPT_TMPL_V2,
    prompt_type=PromptType.SQL_RESPONSE_SYNTHESIS_V2,
)

DEFAULT_FALLBACK_PROMPT = (
    "The user asked: \"{query_str}\"\n\n"
    "The database query failed to return relevant results. You have the following information:\n\n"
    "1. SQL queries attempted:\n{previous_queries}\n\n"
    "2. Sample data from relevant tables:\n{sample_data}\n\n"
    "3. Available tables and their structures:\n{table_structures}\n\n"
    "Your task is to craft a helpful, user-friendly response based on the actual state of the database:\n\n"
    "IF TABLES CONTAIN DATA (sample_data shows records):\n"
    "1. Briefly explain why we couldn't find what they were looking for\n"
    "2. Suggest 3-4 specific questions they could ask based on the data that actually exists\n"
    "3. Provide a simple overview of what information is available\n\n"
    "IF TABLES ARE EMPTY (sample_data shows no records):\n"
    "1. Politely inform the user that there's currently no data in the system\n"
    "2. Suggest they add data first before trying to retrieve information\n"
    "3. Offer to help with adding new entries to the database\n"
    "4. Briefly explain what kinds of data can be added based on the table structures\n\n"
    "Guidelines for your response:\n"
    "- DO NOT include SQL syntax or technical database terminology\n"
    "- DO NOT suggest querying non-existent data if tables are empty\n"
    "- If tables are empty, focus on data creation rather than retrieval\n"
    "- Respond in the same language as the original query\n"
    "- Keep your response conversational and helpful\n\n"
    "Example format for EMPTY tables:\n"
    "\"It looks like there isn't any data in the system yet. Would you like to add some information first? I can help you create new [reports/tasks/projects/etc.] based on what you need. Let me know if you'd like assistance with adding data.\""
)