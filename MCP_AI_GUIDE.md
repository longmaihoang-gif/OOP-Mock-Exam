# 🤖 HƯỚNG DẪN TÍCH HỢP & VẬN HÀNH MCP SERVER `MockExam`
### Dành cho AI Assistants, Coding Copilots & Hệ thống Cố vấn C++ OOP

---

## 📌 1. TỔNG QUAN HỆ THỐNG
Hệ thống **MCP Server `MockExam`** (`exam_arena_mcp.py`) là cầu nối hai chiều chuẩn **JSON-RPC 2.0 (stdio Transport)** giữa các trợ lý AI và đấu trường trắc nghiệm lập trình **GDD C++ Mock Exam Arena**.

### Lợi ích cốt lõi dành cho AI:
1. **Zero External API Cost**: Tận dụng chính năng lực suy luận của AI đang chat với người dùng để phân tích lỗi và tạo câu hỏi phục thù. **Không phát sinh thêm chi phí/quota Gemini API**.
2. **G++ Compiler Sandbox**: Tự động biên dịch `g++ -std=c++11` và chạy thử code trong môi trường cô lập trước khi lưu. Ngăn chặn 100% tình trạng AI sinh code lỗi cú pháp hoặc segfault/timeout.
3. **Automated Revenge Pipeline**: Tự động cấp phát ID mới, ghi file `source/q*.cpp`, cập nhật `question.csv` chuẩn 12 cột, và nạp thẳng vào hàng chờ `mistakes.json` để người học có thể vào làm ngay trên web bằng nút **"🔥 LÀM LẠI CÂU SAI"**.

---

## ⚙️ 2. HƯỚNG DẪN CÀI ĐẶT & KÍCH HOẠT MCP SERVER

### Cách 1: Trong Antigravity IDE
#### Cấu hình theo Workspace (Khuyên dùng):
Tạo hoặc chỉnh sửa file `.agents/mcp_config.json` tại thư mục gốc của project:
```json
{
  "mcpServers": {
    "MockExam": {
      "command": "python",
      "args": [
        "Outside/ExamSystem/exam_arena_mcp.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

#### Cấu hình Global (Áp dụng cho mọi project):
Chỉnh sửa file `c:/Users/<Username>/.gemini/config/mcp_config.json`:
```json
{
  "mcpServers": {
    "MockExam": {
      "command": "python",
      "args": [
        "c:/Users/maiho/OneDrive/Tài liệu/C++/Outside/ExamSystem/exam_arena_mcp.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### Cách 2: Trong Claude Desktop / Cursor
Thêm vào file cấu hình MCP (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "mock-exam": {
      "command": "python",
      "args": [
        "C:\\Users\\maiho\\OneDrive\\Tài liệu\\C++\\Outside\\ExamSystem\\exam_arena_mcp.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

---

## 🛠️ 3. DANH MỤC CÔNG CỤ (MCP TOOL REFERENCE)

### 1. `get_recent_exams(limit=5)`
* **Mục đích**: Lấy danh sách tóm tắt các lần thi đấu gần nhất của người học.
* **Tham số**:
  - `limit` (integer, mặc định `5`): Số lượng bài thi gần nhất cần lấy.
* **Dữ liệu trả về**: Mảng các đối tượng chứa `id`, `date`, `mode`, `score`, `percent`, `duration`, `failed_question_ids`.

### 2. `get_failed_questions(exam_id="latest")`
* **Mục đích**: Trích xuất chi tiết các câu hỏi mà người học đã làm sai trong một bài thi cụ thể để AI tiến hành phân tích điểm yếu.
* **Tham số**:
  - `exam_id` (string, mặc định `"latest"`): ID bài thi cần phân tích (hoặc `"latest"` để lấy bài mới nhất).
* **Dữ liệu trả về**: Chi tiết từng câu sai: ID, đề bài, toàn bộ mã nguồn C++, phương án người học chọn, đáp án chuẩn, và giải thích.

### 3. `get_mistake_bank()`
* **Mục đích**: Truy vấn tất cả các câu hỏi đang còn tồn đọng trong danh sách câu sai (`mistakes.json`) chưa được người học vượt qua.
* **Tham số**: Không có.

### 4. `get_question_detail(question_id)`
* **Mục đích**: Xem chi tiết nội dung và mã nguồn C++ của một câu hỏi bất kỳ theo ID.
* **Tham số**:
  - `question_id` (integer, bắt buộc): ID câu hỏi cần tra cứu.

### 5. `verify_and_save_revenge_question(...)`
* **Mục đích**: **Công cụ trọng tâm của quy trình phục thù**. Biên dịch và chạy thử code qua sandbox `g++ -std=c++11`. Nếu vượt qua kiểm định, tự động cấp phát ID tiếp theo, lưu mã nguồn vào `source/q{N}.cpp`, ghi câu hỏi vào `question.csv`, và tự động đưa ID vào `mistakes.json`.
* **Tham số**:
  - `cpp_source` (string, bắt buộc): Mã nguồn C++ hoàn chỉnh có hàm `main()`.
  - `question_text` (string, bắt buộc): Nội dung đề bài trắc nghiệm (tiếng Việt).
  - `options` (array of strings, bắt buộc): Danh sách 4 hoặc 5 phương án lựa chọn.
  - `correct_index` (integer, bắt buộc): Vị trí (0-indexed) của phương án đúng trong `options`.
  - `explanation` (string, bắt buộc): Lời giải thích cặn kẽ tại sao phương án đó đúng.
  - `topic` (string, tùy chọn, mặc định `"OOP_Revenge_Quest"`): Chủ đề câu hỏi.
  - `difficulty` (string, tùy chọn, mặc định `"Trap"`): `Easy`, `Medium`, `Hard`, `Trap`, `Smokescreen`.
  - `question_type` (string, tùy chọn, mặc định `"Output"`): `Output`, `Error_Check`, `Order_Trace`, `Concept_Apply`, `Calculation`, `Code_Completion`.
  - `failed_question_id` (integer, tùy chọn): ID của câu hỏi gốc mà người học làm sai dẫn đến câu phục thù này.

### 6. `audit_question_bank(recent_count=10, question_id=None)`
* **Mục đích**: Quét kiểm định độ an toàn của ngân hàng câu hỏi bằng `g++`. Tối ưu hóa token tối đa (**Silent on Success** chỉ trả về ~25 tokens khi toàn bộ câu hỏi đều hợp lệ).
* **Tham số**:
  - `recent_count` (integer, tùy chọn, mặc định `10`): Số lượng câu hỏi mới nhất cần audit.
  - `question_id` (integer, tùy chọn): ID câu hỏi cụ thể cần audit (nếu truyền tham số này sẽ bỏ qua `recent_count`).

---

## 🔄 4. QUY TRÌNH SƯ PHẠM CHUẨN DÀNH CHO AI (PEDAGOGICAL WORKFLOW)

Khi người học yêu cầu: *"Hãy phân tích bài thi vừa rồi và tạo câu hỏi phục thù cho tôi!"*, AI cần tuân thủ 5 bước chuẩn mực sau:

```
[BƯỚC 1: Lấy dữ liệu bài thi]
   └── Gọi tool: get_failed_questions(exam_id="latest")
         │
         ├── Nếu 100%: Khen ngợi và chúc mừng người học!
         └── Nếu có câu sai: Tiếp tục Bước 2.
                 │
[BƯỚC 2: Chẩn đoán điểm yếu (Diagnosis)]
   └── Phân tích câu hỏi người học làm sai:
         * Khái niệm bị nhầm lẫn (Vòng đời, explicit, static, deep copy, v.v.)
         * Bẫy tâm lý nào đã khiến người học chọn sai?
                 │
[BƯỚC 3: Thiết kế câu hỏi phục thù (Revenge Quest Synthesis)]
   └── Tự tạo mã nguồn C++ và đề bài bẫy tương tự nhưng biến thể:
         * Mã nguồn phải chứa đầy đủ #include và hàm main()
         * Logic phải chặt chẽ, không có hành vi bất định (Undefined Behavior)
                 │
[BƯỚC 4: Kiểm định và Lưu trữ tự động]
   └── Gọi tool: verify_and_save_revenge_question(...)
         │
         ├── Nếu SANDBOX_FAILED: Đọc log lỗi g++ trả về, sửa lại code và gọi lại.
         └── Nếu SUCCESS: Hệ thống đã tự động nạp câu mới vào mistakes.json!
                 │
[BƯỚC 5: Hướng dẫn người học thực chiến]
   └── Báo cáo ID câu mới và mời người học:
         "Hãy mở Web App và bấm nút '🔥 LÀM LẠI CÂU SAI' để chiến ngay!"
```

---

## ⚠️ 5. CÁC QUY TẮC SỐNG CÒN DÀNH CHO AI ASSISTANT

1. **Tuyệt đối không gọi thêm API bên ngoài**: Toàn bộ logic giải thích và sinh đề phục thù phải do chính AI thực hiện bằng trí tuệ của mình. MCP Server chỉ đóng vai trò là cây cầu dữ liệu và trình biên dịch sandbox.
2. **Luôn cung cấp mã C++ hoàn chỉnh**: Mã C++ gửi vào `verify_and_save_revenge_question` bắt buộc phải có `#include <iostream>`, `using namespace std;` (hoặc tiền tố `std::`), và hàm `int main()`. Không gửi mã giả (pseudo-code) hoặc đoạn mã dang dở.
3. **Tuân thủ quy ước UTF-8**: Mọi chuỗi ký tự tiếng Việt (đề bài, phương án, giải thích) phải dùng bảng mã UTF-8 chuẩn.
4. **Cơ chế đảo vị trí đáp án**: Trong `verify_and_save_revenge_question`, AI chỉ cần chỉ định `correct_index` đúng với vị trí trong mảng `options`. MCP server sẽ tự động trích xuất phương án đó thành `opt1` (đáp án chuẩn) trong `question.csv` theo quy ước của hệ thống.
5. **Cơ chế xóa câu sai**: Khi người học làm bài trong chế độ **Làm Lại Câu Sai**, bất kỳ câu nào trả lời đúng sẽ tự động được gỡ bỏ khỏi `mistakes.json`. AI có thể gọi `get_mistake_bank()` bất cứ lúc nào để theo dõi tiến độ quét sạch lỗi của người học.
6. **Quy tắc tạo câu Điền khuyết mã nguồn (`Code_Completion`)**: Trong mã nguồn `cpp_source`, bắt buộc đặt duy nhất 1 vị trí đánh dấu là `// [ĐIỀN CODE TẠI ĐÂY]`. Phương án đúng (chỉ định qua `correct_index`) khi điền vào vị trí này phải giúp chương trình biên dịch thành công và chạy đúng logic mong muốn. MCP server sẽ tự động thế phương án đúng vào placeholder để sandbox test bằng `g++` trước khi lưu trữ.
