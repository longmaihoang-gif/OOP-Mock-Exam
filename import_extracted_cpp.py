# -*- coding: utf-8 -*-
"""
=============================================================================
  BATCH C++ OCR IMPORT ENGINE (2-TIER ARCHITECTURE)
  Pipeline xử lý thông minh kết hợp Gom Nhóm (Batching 5 câu/lượt):
  - Giai đoạn 1: Local Pre-Filter bằng g++ thật (0 token, cực nhanh).
  - Giai đoạn 2: Batch Processing cho các câu chạy được (5 câu / 1 request).
  - Giai đoạn 3: Batch Academic Trap & OCR Glitch Heuristic cho các câu lỗi.
  - Tối ưu hóa lượt gọi API, bảo vệ Mana, tự động đồng bộ vào question.csv!
=============================================================================
"""

import os
import sys
import json
import csv
import glob
import re
import time
import subprocess
import tempfile
import urllib.request
import urllib.error

# Thiết lập bảng mã UTF-8 cho console Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_CONFIG_FILE = os.path.join(CURRENT_DIR, "prompt.json")
QUESTION_CSV_FILE = os.path.join(CURRENT_DIR, "question.csv")
SOURCE_DIR = os.path.join(CURRENT_DIR, "source")
EXTRACTED_DIR = os.path.join(CURRENT_DIR, "extracted_cpp")
BATCH_SIZE = 5

# =============================================================================
# 1. HỖ TRỢ ĐỌC CẤU HÌNH & QUẢN LÝ DỮ LIỆU
# =============================================================================

def get_api_key():
    """Lấy Gemini API Key từ môi trường hoặc tệp .env"""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key:
        return api_key

    candidate_envs = [
        os.path.join(CURRENT_DIR, ".env"),
        os.path.join(CURRENT_DIR, "Outside", "ExamSystem", ".env"),
        os.path.join(os.path.dirname(CURRENT_DIR), "ExamSystem", ".env")
    ]
    for env_path in candidate_envs:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val

    print("\n🔑 Chưa phát hiện GEMINI_API_KEY trong hệ thống!")
    api_key = input("👉 Vui lòng nhập Gemini API Key vào đây: ").strip()
    if not api_key:
        print("❌ Chưa cung cấp API Key. Tiến trình bị hủy bỏ!")
        sys.exit(1)

    target_env = os.path.join(CURRENT_DIR, ".env")
    with open(target_env, 'w', encoding='utf-8') as f:
        f.write(f"GEMINI_API_KEY={api_key}\n")
    print(f"✨ Đã lưu API Key vào tệp {target_env} an toàn!")
    return api_key


def load_topic_ids():
    """Đọc danh sách Topic ID tinh gọn từ prompt.json (Không làm phình prompt)"""
    if not os.path.exists(PROMPT_CONFIG_FILE):
        return ["OOP_Basic", "Inheritance", "Polymorphism", "Operator_Overloading", "Operator_Precedence_Associativity"]
    try:
        with open(PROMPT_CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            topics = cfg.get("topics", [])
            topic_ids = [t["id"] for t in topics if "id" in t]
            return topic_ids if topic_ids else ["OOP_Basic"]
    except Exception as e:
        print(f"⚠️ Không thể đọc topic_ids từ prompt.json: {e}")
        return ["OOP_Basic"]


def get_current_max_id():
    """Quét question.csv để lấy ID lớn nhất hiện tại (Resume Engine)"""
    if not os.path.exists(QUESTION_CSV_FILE):
        return 0
    max_id = 0
    try:
        with open(QUESTION_CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if row and len(row) > 0:
                    try:
                        qid = int(row[0].strip())
                        if qid > max_id:
                            max_id = qid
                    except ValueError:
                        pass
    except Exception as e:
        print(f"⚠️ Lỗi khi đọc {QUESTION_CSV_FILE}: {e}")
    return max_id


# =============================================================================
# 2. G++ COMPILER & EXECUTION ENGINE (LOCAL SANDBOX)
# =============================================================================

def clean_code_before_compile(code_str: str) -> str:
    """Loại bỏ các lệnh dừng màn hình (system pause, cin.get, getch) gây treo tiến trình ngầm"""
    c = re.sub(r'^\s*#iostream\b', '#include <iostream>', code_str, flags=re.MULTILINE)
    # Loại bỏ system("pause") hoặc system("PAUSE")
    c = re.sub(r'^\s*system\s*\(\s*["\']pause["\']\s*\)\s*;?', '', c, flags=re.IGNORECASE | re.MULTILINE)
    # Loại bỏ cin.get()
    c = re.sub(r'^\s*cin\s*\.\s*get\s*\(\s*\)\s*;?', '', c, flags=re.MULTILINE)
    # Loại bỏ getch()
    c = re.sub(r'^\s*getch\s*\(\s*\)\s*;?', '', c, flags=re.MULTILINE)
    # Loại bỏ #include <conio.h>
    c = re.sub(r'^\s*#include\s*<conio\.h>\s*', '', c, flags=re.MULTILINE)
    return c.strip()


def test_compile_and_run(code_str: str, timeout_sec: int = 4):
    """
    Sử dụng g++ thật để biên dịch và chạy thử code:
    Trả về: (is_success, stdout_str, stderr_str)
    """
    cleaned_code = clean_code_before_compile(code_str)

    temp_dir = tempfile.gettempdir()
    temp_cpp = os.path.join(temp_dir, "_import_batch_temp.cpp")
    temp_exe = os.path.join(temp_dir, "_import_batch_temp.exe")

    try:
        with open(temp_cpp, 'w', encoding='utf-8') as f:
            f.write(cleaned_code)

        comp = subprocess.run(
            ["g++", "-std=c++11", temp_cpp, "-o", temp_exe],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10
        )

        if comp.returncode != 0:
            return False, "", comp.stderr.strip()

        # Thực thi chương trình với stdin=DEVNULL chống treo tuyệt đối!
        run = subprocess.run(
            [temp_exe],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout_sec
        )
        return True, run.stdout.strip(), ""

    except subprocess.TimeoutExpired:
        return False, "", "Execution Timeout (Vòng lặp vô tận hoặc chờ input)"
    except Exception as e:
        return False, "", f"Compiler Exception: {str(e)}"
    finally:
        for p in [temp_cpp, temp_exe]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass


# =============================================================================
# 3. GEMINI REST API ENGINE
# =============================================================================

def call_gemini_json(api_key: str, prompt_text: str, model_name: str = "gemini-3.5-flash-lite", max_retries: int = 3):
    """Gọi Gemini REST API với JSON mode trả về Python dict/list"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt_text}]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json"
        }
    }

    req_data = json.dumps(payload).encode('utf-8')

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=90) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)

                candidates = res_json.get("candidates", [])
                if not candidates:
                    raise ValueError("Gemini không trả về candidate nào!")

                parts = candidates[0].get("content", {}).get("parts", [])
                content_text = ""
                for p in parts:
                    if not p.get("thought", False) and "text" in p:
                        content_text += p["text"]
                if not content_text and parts:
                    content_text = parts[-1].get("text", "")

                cleaned = content_text.strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json", 1)[1]
                    if "```" in cleaned:
                        cleaned = cleaned.split("```", 1)[0]
                elif "```" in cleaned:
                    cleaned = cleaned.split("```", 1)[1]
                    if "```" in cleaned:
                        cleaned = cleaned.split("```", 1)[0]
                cleaned = cleaned.strip()

                return json.loads(cleaned)

        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"⏳ [Rate Limit] Đang ngủ 6s trước khi thử lại ({attempt}/{max_retries})...")
                time.sleep(6)
            else:
                print(f"⚠️ [HTTP {e.code}] Thử lại ({attempt}/{max_retries})...")
                time.sleep(3)
        except Exception as e:
            print(f"⚠️ [API Lỗi]: {e}. Đang thử lại ({attempt}/{max_retries})...")
            time.sleep(3)

    return None


# =============================================================================
# 4. CÁC THẦN CHÚ PROMPT GOM NHÓM (BATCH PROMPTS)
# =============================================================================

def build_batch_prompt_valid(items: list, topic_ids: list) -> str:
    """Prompt gom nhóm nhiều đoạn code C++ đã chạy thành công ra stdout"""
    items_json_str = json.dumps([
        {
            "item_id": it["item_id"],
            "filename": it["filename"],
            "code": it["code"],
            "actual_stdout": it["stdout"]
        }
        for it in items
    ], ensure_ascii=False, indent=2)

    return f"""
Bạn là Chuyên gia Khảo thí và Giảng viên Cao cấp về C++ và Lập trình Hướng đối tượng (OOP) trình độ Đại học.
Dưới đây là một NHÓM các bài code C++ đã được trình biên dịch g++ (chuẩn C++11) biên dịch THÀNH CÔNG và chạy ra kết quả stdout thực tế.

DANH SÁCH BÀI CẦN XỬ LÝ:
{items_json_str}

DANH SÁCH TOPIC_ID HỢP LỆ:
{json.dumps(topic_ids, ensure_ascii=False)}

YÊU CẦU CHO TỪNG BÀI:
1. item_id: Giữ đúng item_id tương ứng.
2. topic: Chọn 1 topic_id CHÍNH XÁC NHẤT từ danh sách trên.
3. difficulty: Chọn "Easy", "Medium", "Trap", hoặc "Smokescreen".
4. question_type: Chọn "Output", "Calculation", hoặc "Order_Trace".
5. question: Viết câu hỏi trắc nghiệm theo văn phong học thuật, chuẩn mực của đề thi đại học (Ví dụ: "Cho đoạn mã C++ sau. Hãy xác định kết quả xuất ra màn hình khi chương trình thực thi:" hoặc "Phân tích đoạn mã C++ sau, giá trị của biến x sau khi chạy hàm main là bao nhiêu?").
6. opt1: BẮT BUỘC PHẢI LÀ CHÍNH XÁC GIÁ TRỊ actual_stdout của bài đó!
7. opt2, opt3, opt4: 3 phương án gây nhiễu thông minh, hợp lý.
8. opt5: Để trống "" hoặc thêm phương án nhiễu thứ 4.
9. explanation: Lời giải thích khoa học, chỉ rõ nguyên lý hoạt động của C++.

TRẢ VỀ DUY NHẤT 1 MẢNG JSON CÁC ĐỐI TƯỢNG:
[
  {{
    "item_id": 1,
    "topic": "tên_topic",
    "difficulty": "Medium",
    "question_type": "Output",
    "question": "Câu hỏi...",
    "opt1": "actual_stdout",
    "opt2": "nhiễu 1",
    "opt3": "nhiễu 2",
    "opt4": "nhiễu 3",
    "opt5": "",
    "explanation": "Lời giải thích..."
  }}
]
"""


def build_batch_prompt_errors(items: list, topic_ids: list) -> str:
    """Prompt gom nhóm các bài bị lỗi biên dịch: Phân loại Bẫy Học Thuật vs Nhiễu Quét Ảnh"""
    items_json_str = json.dumps([
        {
            "item_id": it["item_id"],
            "filename": it["filename"],
            "code": it["code"],
            "compiler_error": it["stderr"]
        }
        for it in items
    ], ensure_ascii=False, indent=2)

    return f"""
Bạn là Chuyên gia Khảo thí và Giảng viên Cao cấp về C++ và Lập trình Hướng đối tượng (OOP) trình độ Đại học.
Dưới đây là một NHÓM các đoạn mã C++ bị trình biên dịch g++ (chuẩn C++11) báo lỗi.

DANH SÁCH BÀI LỖI:
{items_json_str}

DANH SÁCH TOPIC_ID HỢP LỆ:
{json.dumps(topic_ids, ensure_ascii=False)}

[BỘ LỌC PHÂN ĐỊNH LỖI (ZERO-BLOAT HEURISTIC)]:
Đối với MỖI bài, hãy phân loại lỗi thành 1 trong 2 trường hợp:
1. "ACADEMIC_TRAP" (Bẫy học thuật cố ý của Đề thi):
   - Mã nguồn viết nắn nót, hoàn chỉnh, có ý đồ kiểm tra kiến thức C++ OOP sâu sắc.
   - Cố tình vi phạm nguyên lý ngữ nghĩa C++ (ví dụ: gọi hàm nạp chồng bị ambiguous do default argument; nạp chồng operator<< trùng với member std::ostream; sử dụng con trỏ 'this' trong static member function; dùng toán tử -> trên đối tượng lvalue; gán int* vào mảng int; v.v.).
   ==> HÀNH ĐỘNG: GIỮ NGUYÊN 100% CODE GỐC! Tạo câu hỏi dạng 'Error_Check' với opt1 là "Lỗi biên dịch".

2. "OCR_GLITCH" (Nhiễu cơ học do quét ảnh):
   - Code bị rách chữ, mất dấu ngoặc nhọn '}}' cuối cùng do crop ảnh, gõ nhầm '#iostream' thiếu '<>', nhầm 'O' với '0', thiếu ';' ở vị trí hiển nhiên.
   ==> HÀNH ĐỘNG: Cung cấp mã nguồn đã được vá sửa lỗi chính xác (healed_code) để biên dịch lại.

TRẢ VỀ DUY NHẤT 1 MẢNG JSON CÁC ĐỐI TƯỢNG THEO CẤU TRÚC:
[
  {{
    "item_id": 1,
    "trap_type": "ACADEMIC_TRAP",
    "topic": "chọn 1 topic_id từ danh sách",
    "difficulty": "Trap",
    "question_type": "Error_Check",
    "question": "Cho đoạn mã sau, kết quả khi biên dịch và thực thi chương trình là gì?",
    "opt1": "Lỗi biên dịch",
    "opt2": "dự đoán kết quả nếu giả sử code chạy được",
    "opt3": "dự đoán kết quả khác",
    "opt4": "Lỗi thời gian chạy (Runtime Error)",
    "opt5": "",
    "explanation": "Chỉ rõ chính xác dòng gây lỗi và nguyên lý C++ bị vi phạm..."
  }},
  {{
    "item_id": 2,
    "trap_type": "OCR_GLITCH",
    "healed_code": "toàn bộ mã nguồn sau khi đã vá để có thể biên dịch"
  }}
]
"""


# =============================================================================
# 5. GHI DỮ LIỆU VÀO DATABASE
# =============================================================================

def append_to_question_csv(q_record: dict):
    """Ghi 1 câu hỏi vào question.csv chuẩn RFC 4180"""
    file_exists = os.path.exists(QUESTION_CSV_FILE)
    with open(QUESTION_CSV_FILE, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        if not file_exists or os.path.getsize(QUESTION_CSV_FILE) == 0:
            writer.writerow([
                "id", "topic", "difficulty", "question_type",
                "question", "code_file",
                "opt1", "opt2", "opt3", "opt4", "opt5",
                "explanation"
            ])
        writer.writerow([
            q_record["id"],
            q_record["topic"],
            q_record["difficulty"],
            q_record["question_type"],
            q_record["question"],
            q_record["code_file"],
            q_record["opt1"],
            q_record["opt2"],
            q_record["opt3"],
            q_record["opt4"],
            q_record["opt5"],
            q_record["explanation"]
        ])


def save_single_quest(q_data: dict, code_content: str, current_id: int, default_topic: str) -> int:
    """Lưu 1 câu hỏi đã hoàn thiện vào source/q{id}.cpp và question.csv"""
    source_filename = f"q{current_id}.cpp"
    dest_source_path = os.path.join(SOURCE_DIR, source_filename)

    with open(dest_source_path, 'w', encoding='utf-8') as f:
        f.write(code_content.strip() + "\n")

    q_record = {
        "id": current_id,
        "topic": q_data.get("topic", default_topic),
        "difficulty": q_data.get("difficulty", "Medium"),
        "question_type": q_data.get("question_type", "Output"),
        "question": q_data.get("question", "Cho đoạn mã sau, màn hình sẽ in ra kết quả gì khi chạy hàm main()?"),
        "code_file": source_filename,
        "opt1": q_data.get("opt1", ""),
        "opt2": q_data.get("opt2", ""),
        "opt3": q_data.get("opt3", ""),
        "opt4": q_data.get("opt4", ""),
        "opt5": q_data.get("opt5", ""),
        "explanation": q_data.get("explanation", "")
    }

    append_to_question_csv(q_record)
    print(f"  🎉 [LEVEL UP]: Đã nhập Quest #{current_id} ({q_record['question_type']} | {q_record['topic']}) -> {source_filename}")
    return current_id


# =============================================================================
# 6. CHƯƠNG TRÌNH CHÍNH (BATCH PIPELINE)
# =============================================================================

def main():
    print("=" * 75)
    print("  C++ OCR SOURCE IMPORT PIPELINE (BATCH MODE)")
    print("=" * 75)

    if not os.path.exists(EXTRACTED_DIR):
        print(f"❌ Không tìm thấy thư mục: {EXTRACTED_DIR}")
        return

    cpp_files = sorted(glob.glob(os.path.join(EXTRACTED_DIR, "*.cpp")))
    if not cpp_files:
        print(f"⚠️ Không có file .cpp nào trong {EXTRACTED_DIR}!")
        return

    os.makedirs(SOURCE_DIR, exist_ok=True)
    api_key = get_api_key()
    topic_ids = load_topic_ids()
    current_id = get_current_max_id()

    print(f"🎯 Phát hiện {len(cpp_files)} file mã nguồn OCR.")
    print(f"📚 Đã nạp {len(topic_ids)} Topic ID tinh gọn từ prompt.json.")
    print(f"🆔 ID khởi đầu tiếp theo trong question.csv: #{current_id + 1}\n")

    # -------------------------------------------------------------------------
    # GIAI ĐOẠN 1: LOCAL PRE-FILTER BẰNG G++ (0 TOKEN, CHẠY CỰC NHANH)
    # -------------------------------------------------------------------------
    print("⏳ [GIAI ĐOẠN 1]: Đang quét và kiểm thử biên dịch bằng g++ local...")
    valid_items = []
    error_items = []

    for idx, fpath in enumerate(cpp_files, start=1):
        fname = os.path.basename(fpath)
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            code_text = f.read().strip()

        if not code_text:
            continue

        cleaned_code_text = clean_code_before_compile(code_text)
        is_ok, stdout_res, stderr_res = test_compile_and_run(cleaned_code_text)
        if is_ok:
            valid_items.append({
                "item_id": idx,
                "filename": fname,
                "code": cleaned_code_text,
                "stdout": stdout_res
            })
            print(f"  [{idx:02d}] {fname[:20]}... -> ✅ COMPILE OK (stdout: '{stdout_res.replace(chr(10), ' ')[:30]}')")
        else:
            error_items.append({
                "item_id": idx,
                "filename": fname,
                "code": cleaned_code_text,
                "stderr": stderr_res
            })
            print(f"  [{idx:02d}] {fname[:20]}... -> ⚠️ COMPILE FAIL ({stderr_res.split(chr(10))[0][:40]})")

    print(f"\n📊 Kết quả lọc Local: {len(valid_items)} file Biên dịch OK | {len(error_items)} file Gặp lỗi.")

    success_count = 0
    trap_count = 0
    healed_count = 0

    # -------------------------------------------------------------------------
    # GIAI ĐOẠN 2: BATCH PROCESSING CÁC BÀI BIÊN DỊCH OK (5 CÂU / 1 REQUEST)
    # -------------------------------------------------------------------------
    if valid_items:
        print(f"\n🚀 [GIAI ĐOẠN 2]: Gom nhóm xử lý {len(valid_items)} bài thành công (Mỗi mẻ {BATCH_SIZE} câu)...")
        for b_start in range(0, len(valid_items), BATCH_SIZE):
            batch = valid_items[b_start : b_start + BATCH_SIZE]
            batch_num = (b_start // BATCH_SIZE) + 1
            total_batches = (len(valid_items) + BATCH_SIZE - 1) // BATCH_SIZE

            print(f"\n📦 [BATCH #{batch_num}/{total_batches}] Đang gửi {len(batch)} câu lên Gemini...")
            prompt = build_batch_prompt_valid(batch, topic_ids)
            res_list = call_gemini_json(api_key, prompt)

            if isinstance(res_list, list):
                # Ánh xạ theo item_id
                res_map = {item.get("item_id"): item for item in res_list if isinstance(item, dict)}
                for it in batch:
                    q_data = res_map.get(it["item_id"])
                    if not q_data and len(res_list) > 0:
                        q_data = res_list.pop(0)

                    if q_data:
                        current_id += 1
                        q_data["opt1"] = it["stdout"] # Bảo đảm 100% khớp stdout
                        save_single_quest(q_data, it["code"], current_id, topic_ids[0])
                        success_count += 1
                    else:
                        print(f"  ❌ Bỏ sót dữ liệu câu: {it['filename']}")
            else:
                print(f"  ⚠️ Lỗi định dạng phản hồi từ AI trong Batch #{batch_num}!")

            time.sleep(2.0)

    # -------------------------------------------------------------------------
    # GIAI ĐOẠN 3: BATCH PROCESSING CÁC BÀI LỖI (BẪY HỌC THUẬT VS NHIỄU OCR)
    # -------------------------------------------------------------------------
    if error_items:
        print(f"\n🛡️ [GIAI ĐOẠN 3]: Thẩm định {len(error_items)} bài bị lỗi biên dịch...")
        prompt_err = build_batch_prompt_errors(error_items, topic_ids)
        err_res_list = call_gemini_json(api_key, prompt_err)

        if isinstance(err_res_list, list):
            err_res_map = {item.get("item_id"): item for item in err_res_list if isinstance(item, dict)}
            for it in error_items:
                eval_data = err_res_map.get(it["item_id"])
                if not eval_data and len(err_res_list) > 0:
                    eval_data = err_res_list.pop(0)

                if not eval_data:
                    continue

                trap_type = eval_data.get("trap_type", "")
                if trap_type == "ACADEMIC_TRAP":
                    print(f"  🎓 BẪY HỌC THUẬT CỦA ĐỀ THI: {it['filename']} -> Giữ 100% code, dạng Error_Check.")
                    current_id += 1
                    eval_data["opt1"] = "Lỗi biên dịch"
                    save_single_quest(eval_data, it["code"], current_id, topic_ids[0])
                    trap_count += 1

                elif trap_type == "OCR_GLITCH":
                    healed_code = eval_data.get("healed_code", "")
                    if healed_code:
                        h_ok, h_stdout, h_stderr = test_compile_and_run(healed_code)
                        if h_ok:
                            print(f"  ✨ Vá lỗi quét ảnh thành công cho {it['filename']}! Stdout: '{h_stdout}'")
                            # Sinh câu hỏi hoàn chỉnh cho code đã vá
                            single_prompt = build_batch_prompt_valid([{
                                "item_id": it["item_id"],
                                "filename": it["filename"],
                                "code": healed_code,
                                "stdout": h_stdout
                            }], topic_ids)
                            single_res = call_gemini_json(api_key, single_prompt)
                            if isinstance(single_res, list) and len(single_res) > 0:
                                current_id += 1
                                q_d = single_res[0]
                                q_d["opt1"] = h_stdout
                                save_single_quest(q_d, healed_code, current_id, topic_ids[0])
                                healed_count += 1
                        else:
                            print(f"  ❌ Vá thất bại cho {it['filename']}: {h_stderr.split(chr(10))[0][:50]}")
        else:
            print("  ⚠️ Không thể thẩm định nhóm bài lỗi bằng AI!")

    # -------------------------------------------------------------------------
    # TỔNG KẾT CHIẾN DỊCH
    # -------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("  🏆 BÁO CÁO HOÀN THÀNH CHIẾN DỊCH IMPORT MÃ NGUỒN OCR (BATCH ENGINE) 🏆")
    print(f"  - Tổng số file duyệt: {len(cpp_files)}")
    print(f"  - Câu hỏi Output chuẩn: {success_count}")
    print(f"  - Bẫy học thuật (Error_Check): {trap_count}")
    print(f"  - Vá lỗi OCR thành công: {healed_count}")
    print(f"  - Tổng ID hiện tại của đấu trường: #{current_id}")
    print("=" * 75)


if __name__ == "__main__":
    main()
