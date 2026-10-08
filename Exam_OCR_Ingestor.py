# -*- coding: utf-8 -*-
"""
=============================================================================
  EXAM OCR & INGESTION ENGINE (VISION MULTIMODAL PIPELINE) - V2 (DEDUPLICATED)
  Hệ thống trích xuất và giải đề tự động từ ảnh chụp đề thi LMS (DUT)
  - Đọc trực tiếp ảnh chụp màn hình LMS Bách Khoa Đà Nẵng
  - Bóc tách nhiều câu hỏi trong 1 ảnh (Multi-question handling)
  - Bộ lọc toàn vẹn (Truncation Guard: bỏ qua câu bị khuất mép ảnh)
  - Giải đề độc lập (Bỏ qua lựa chọn của sinh viên trong ảnh)
  - CHỐNG TRÙNG LẶP THÔNG MINH (Deduplication Guard: tự đối chiếu ngân hàng)
  - Ghi chuẩn xác vào question.csv và dời ảnh sang processed_images
=============================================================================
"""

import os
import sys
import json
import csv
import time
import base64
import glob
import shutil
import re
import urllib.request
import urllib.error
from difflib import SequenceMatcher

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_CONFIG_FILE = os.path.join(CURRENT_DIR, "prompt.json")
QUESTION_CSV_FILE = os.path.join(CURRENT_DIR, "question.csv")
INPUT_IMAGES_DIR = os.path.join(CURRENT_DIR, "input_images")
PROCESSED_IMAGES_DIR = os.path.join(CURRENT_DIR, "processed_images")

def get_api_key():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key:
        return api_key

    candidate_env_paths = [
        os.path.join(CURRENT_DIR, ".env"),
        os.path.join(os.path.dirname(CURRENT_DIR), ".env"),
    ]
    for env_path in candidate_env_paths:
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
    return api_key

def load_prompt_config():
    if os.path.exists(PROMPT_CONFIG_FILE):
        try:
            with open(PROMPT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r'[\s\n\r\t]+', ' ', text)
    text = re.sub(r'[\.,\?\!\:;\'"\(chọn tất cả đáp án đúng\)|\(chọn tất cả các đáp án đúng\)]', '', text)
    return text.strip()

def load_existing_questions():
    """Tải ngân hàng câu hỏi hiện có để đối chiếu trùng lặp"""
    if not os.path.exists(QUESTION_CSV_FILE):
        return [], 0
    questions = []
    max_id = 0
    try:
        with open(QUESTION_CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if row and len(row) >= 12:
                    try:
                        qid = int(row[0].strip())
                        if qid > max_id:
                            max_id = qid
                    except ValueError:
                        pass
                    questions.append({
                        "id": row[0].strip(),
                        "norm_q": normalize_text(row[4]),
                        "norm_opt1": normalize_text(row[6]),
                        "opts_combined": normalize_text(" ".join(row[6:10]))
                    })
    except Exception as e:
        print(f"⚠️ [Cảnh báo]: Không thể đọc question.csv ({e})")
    return questions, max_id

def is_duplicate(new_q, existing_questions):
    """Kiểm tra xem câu hỏi mới có bị trùng lặp với câu nào đã có trong ngân hàng không"""
    new_norm_q = normalize_text(new_q.get("question", ""))
    new_norm_opt1 = normalize_text(new_q.get("opt1", ""))
    new_opts_combined = normalize_text(" ".join([new_q.get(f"opt{i}", "") for i in range(1, 5)]))

    is_generic = len(new_norm_q) < 40 and "phát biểu nào sau đây là đúng" in new_norm_q

    for old_q in existing_questions:
        if is_generic:
            opt1_sim = SequenceMatcher(None, new_norm_opt1, old_q["norm_opt1"]).ratio()
            opts_sim = SequenceMatcher(None, new_opts_combined, old_q["opts_combined"]).ratio()
            if opt1_sim > 0.85 or opts_sim > 0.8:
                return True, old_q["id"]
        else:
            q_sim = SequenceMatcher(None, new_norm_q[:120], old_q["norm_q"][:120]).ratio()
            opt1_sim = SequenceMatcher(None, new_norm_opt1[:60], old_q["norm_opt1"][:60]).ratio()
            if q_sim > 0.85 and opt1_sim > 0.7:
                return True, old_q["id"]

    return False, None

SYSTEM_PROMPT = """Bạn là Chuyên gia Khảo thí và Giảng viên Cao cấp môn NGUYÊN LÝ HỆ ĐIỀU HÀNH (Operating Systems) tại Đại học Bách Khoa (DUT LMS).
Nhiệm vụ của bạn là phân tích ảnh chụp màn hình bài thi LMS, bóc tách toàn bộ câu hỏi và giải đề độc lập với độ chính xác học thuật 100%.

QUY TẮC BẤT BIẾN:
1. ĐỘC LẬP GIẢI ĐỀ (CRUCIAL): Bức ảnh có thể chứa vết tích tick chọn hoặc đáp án của sinh viên. MẶC KỆ VÀ BỎ QUA HOÀN TOÀN các lựa chọn này (vì có thể sinh viên làm SAI)! Bạn phải tự mình phân tích, vẽ biểu đồ Gantt, tính toán hoặc áp dụng lý thuyết để tìm ra đáp án đúng 100%.
2. BẢO VỆ TÍNH TOÀN VẸN (TRUNCATION GUARD):
   - Một bức ảnh có thể chứa 1, 2, 3 hoặc nhiều câu hỏi. Hãy bóc tách TẤT CẢ các câu hỏi trọn vẹn.
   - NẾU một câu hỏi ở mép trên hoặc mép dưới bị cắt ngang (ví dụ: mất một phần đề bài, thiếu dữ liệu, hoặc không thấy đủ các lựa chọn A, B, C, D) -> BẮT BUỘC BỎ QUA câu đó. Thà bỏ sót chứ KHÔNG đoán mò!
3. CHUẨN HÓA BẢNG VÀ SƠ ĐỒ CÂY:
   - Nếu đề bài có bảng tiến trình (Arrival Time, Burst Time, Priority...), hãy chuyển thành định dạng bảng văn bản rõ ràng, dễ đọc trong trường 'question'.
   - Nếu đề bài có sơ đồ cây thư mục Linux, hãy vẽ lại bằng cây văn bản/ASCII chuẩn trong trường 'question'.
4. PHÂN LOẠI DẠNG BÀI:
   - Câu trắc nghiệm chọn 1 đáp án: 'question_type' là một trong các dạng: 'Calculation', 'Order_Trace', 'Concept_Apply', 'Error_Check', 'Scenario_Analysis'. Trường 'opt1' là ĐÁP ÁN ĐÚNG NHẤT, 'opt2'..'opt4' là các đáp án gây nhiễu, 'opt5' để rỗng "".
   - Câu trắc nghiệm chọn nhiều đáp án (Multi-Select, ô vuông checkbox, hoặc có chữ "chọn tất cả"): 'question_type' có dạng 'Multi_Select:K' (K là số lượng ý đúng). K đáp án ĐÚNG phải nằm liên tiếp từ 'opt1' đến 'optK'.
5. GIẢI THÍCH CHUYÊN SÂU (EXPLANATION):
   - Nêu rõ bản chất cơ chế của Hệ điều hành, giải thích vì sao đáp án đúng và chỉ ra sai sót của các phương án khác.
   - TUYỆT ĐỐI KHÔNG dùng các từ biến kỹ thuật như 'opt1', 'opt2', 'opt3', 'opt4' hay 'Ý 1', 'Ý 2' trong lời giải thích (vì client sẽ xáo trộn các đáp án A, B, C, D). Hãy trích dẫn trực tiếp nội dung hoặc khái niệm.
6. TOPIC PHÙ HỢP: Gán một trong 15 topic chuẩn của môn học.

ĐỊNH DẠNG ĐẦU RA (JSON ARRAY BẮT BUỘC):
[
  {
    "topic": "Tên_Topic_Chuẩn",
    "difficulty": "Easy|Medium|Trap|Smokescreen|Boss",
    "question_type": "Concept_Apply|Calculation|Multi_Select:K|...",
    "question": "Nội dung đầy đủ của câu hỏi",
    "opt1": "Nội dung đáp án đúng",
    "opt2": "Nội dung đáp án gây nhiễu",
    "opt3": "Nội dung đáp án gây nhiễu",
    "opt4": "Nội dung đáp án gây nhiễu",
    "opt5": "",
    "explanation": "Giải thích chi tiết chuẩn mực sư phạm..."
  }
]
Nếu bức ảnh KHÔNG có câu hỏi nào trọn vẹn, hãy trả về mảng rỗng `[]`.
"""

def call_gemini_vision(api_key, image_path, preferred_model="gemini-3.8-flash", thinking_budget=8192):
    with open(image_path, 'rb') as f:
        img_bytes = f.read()
    b64_data = base64.b64encode(img_bytes).decode('utf-8')

    mime_type = "image/jpeg"
    ext = os.path.splitext(image_path)[1].lower()
    if ext == ".png":
        mime_type = "image/png"

    candidate_models = [preferred_model, "gemini-3.5-flash", "gemini-2.5-flash"]
    seen = set()
    models_to_try = []
    for m in candidate_models:
        if m and m not in seen:
            seen.add(m)
            models_to_try.append(m)

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": "Hãy phân tích bức ảnh đề thi này và bóc tách danh sách câu hỏi theo đúng hướng dẫn hệ thống."},
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": b64_data
                        }
                    }
                ]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    if thinking_budget > 0:
        payload["generationConfig"]["thinkingConfig"] = {
            "thinkingBudget": thinking_budget
        }

    req_data = json.dumps(payload).encode('utf-8')
    headers = {"Content-Type": "application/json"}

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        print(f"   📡 Đang gửi ảnh tới model: {model_name}...")
        for attempt in range(1, 3):
            try:
                req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=90) as response:
                    res_body = response.read().decode('utf-8')
                    res_json = json.loads(res_body)

                    candidates = res_json.get("candidates", [])
                    if not candidates:
                        raise ValueError("Không nhận được candidate nào từ Gemini!")

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

                    start = cleaned.find('[')
                    end = cleaned.rfind(']')
                    if start != -1 and end != -1 and end > start:
                        cleaned = cleaned[start:end+1]

                    parsed = json.loads(cleaned)
                    if isinstance(parsed, list):
                        return parsed, model_name

            except urllib.error.HTTPError as e:
                err_text = e.read().decode('utf-8', errors='ignore')
                print(f"   ⚠️ [HTTP {e.code}] ({model_name} lần {attempt}): {err_text[:90]}...")
                if e.code == 503 or e.code == 429:
                    time.sleep(3)
                    break
                time.sleep(2)
            except Exception as e:
                print(f"   ⚠️ Lỗi ({model_name} lần {attempt}): {e}")
                time.sleep(2)

    return None, None

def append_to_question_csv(question_item, next_id):
    row = [
        str(next_id),
        question_item.get("topic", "OS_Overview_Classification"),
        question_item.get("difficulty", "Medium"),
        question_item.get("question_type", "Concept_Apply"),
        question_item.get("question", "").strip(),
        "",
        question_item.get("opt1", "").strip(),
        question_item.get("opt2", "").strip(),
        question_item.get("opt3", "").strip(),
        question_item.get("opt4", "").strip(),
        question_item.get("opt5", "").strip(),
        question_item.get("explanation", "").strip()
    ]

    with open(QUESTION_CSV_FILE, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(row)

def main():
    print("""
╔═════════════════════════════════════════════════════════════════════╗
║         DUT LMS EXAM OCR & QUESTION INGESTION ENGINE                ║
║    Trích xuất & Giải đề thi Hệ Điều Hành từ ảnh thực tế bằng AI     ║
║            (Tích hợp bộ lọc chống trùng lặp Deduplication)          ║
╚═════════════════════════════════════════════════════════════════════╝
""")

    if not os.path.exists(INPUT_IMAGES_DIR):
        print(f"❌ Không tìm thấy thư mục ảnh đầu vào: {INPUT_IMAGES_DIR}")
        return

    os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)

    image_patterns = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.PNG"]
    image_files = []
    for pat in image_patterns:
        image_files.extend(glob.glob(os.path.join(INPUT_IMAGES_DIR, pat)))
    image_files = sorted(list(set(image_files)))

    if not image_files:
        print(f"📦 Không còn bức ảnh nào trong {INPUT_IMAGES_DIR} để xử lý!")
        return

    config = load_prompt_config()
    settings = config.get("generation_settings", {})
    preferred_model = settings.get("default_model", "gemini-3.8-flash")
    thinking_budget = settings.get("thinking_budget", 8192)

    api_key = get_api_key()
    existing_questions, current_max_id = load_existing_questions()

    print(f"📂 Tìm thấy: {len(image_files)} bức ảnh trong hàng đợi xử lý.")
    print(f"🎯 Ngân hàng hiện tại đang có: {len(existing_questions)} câu hỏi (Max ID: {current_max_id})")
    print(f"🤖 Mô hình ưu tiên: {preferred_model} (Thinking budget: {thinking_budget})\n")

    next_id = current_max_id + 1
    total_ingested = 0

    for idx, img_path in enumerate(image_files, start=1):
        filename = os.path.basename(img_path)
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📸 [{idx}/{len(image_files)}] Đang phân tích: {filename}...")

        extracted_questions, model_used = call_gemini_vision(
            api_key=api_key,
            image_path=img_path,
            preferred_model=preferred_model,
            thinking_budget=thinking_budget
        )

        if extracted_questions is None:
            print(f"❌ Thất bại khi phân tích ảnh {filename}. Giữ nguyên ảnh trong thư mục để kiểm tra lại.")
            continue

        if len(extracted_questions) == 0:
            print(f"⚠️ Không tìm thấy câu hỏi trọn vẹn nào trong ảnh.")
        else:
            print(f"✨ Trích xuất được {len(extracted_questions)} câu hỏi (qua model: {model_used}):")
            for q_idx, q in enumerate(extracted_questions, start=1):
                # Kiểm tra trùng lặp
                dup, dup_id = is_duplicate(q, existing_questions)
                if dup:
                    print(f"   ⚠️ [BỎ QUA DO TRÙNG LẶP]: Trùng với câu ID {dup_id} trong ngân hàng!")
                    continue

                q_text = q.get("question", "")[:60].replace('\n', ' ')
                q_type = q.get("question_type", "")
                q_opt1 = q.get("opt1", "")[:40].replace('\n', ' ')
                print(f"   [{q_idx}] ID {next_id} ({q_type}): {q_text}...")
                print(f"       ✅ Đáp án đúng: {q_opt1}...")

                append_to_question_csv(q, next_id)
                existing_questions.append({
                    "id": str(next_id),
                    "norm_q": normalize_text(q.get("question", "")),
                    "norm_opt1": normalize_text(q.get("opt1", "")),
                    "opts_combined": normalize_text(" ".join([q.get(f"opt{i}", "") for i in range(1, 5)]))
                })
                next_id += 1
                total_ingested += 1

        dest_path = os.path.join(PROCESSED_IMAGES_DIR, filename)
        try:
            shutil.move(img_path, dest_path)
            print(f"📦 Đã di chuyển ảnh sang: processed_images/{filename}")
        except Exception as e:
            print(f"⚠️ Không thể di chuyển ảnh {filename}: {e}")

        time.sleep(2.5)

    print("\n" + "═"*65)
    print(f"🎉 CHIẾN DỊCH KHAI QUẬT HOÀN TẤT!")
    print(f"✅ Đã bổ sung thành công: {total_ingested} câu hỏi mới độc bản vào question.csv")
    print(f"📊 Tổng số câu hỏi hiện tại trong ngân hàng: {len(existing_questions)}")
    print("═"*65)

if __name__ == "__main__":
    main()
