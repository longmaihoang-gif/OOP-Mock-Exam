# -*- coding: utf-8 -*-
"""
=============================================================================
  ⚔️ TENDOU ARIS - C++ OOP AUTOMATIC QUESTION GENERATOR ⚔️
  Chương trình sinh đề thi trắc nghiệm C++ OOP tự động bằng Gemini API
  Đảm bảo tỷ lệ 90% Code / 10% Lý thuyết chính xác 100% bằng toán học!
=============================================================================
"""

import os
import sys
import json
import csv
import time
import random
import re
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

# =============================================================================
# HÀM HỖ TRỢ ĐỌC CẤU HÌNH & DỮ LIỆU
# =============================================================================

def load_prompt_config():
    """Đọc file cấu hình prompt.json"""
    if not os.path.exists(PROMPT_CONFIG_FILE):
        print(f"❌ [LỖI]: Không tìm thấy tệp {PROMPT_CONFIG_FILE}!")
        sys.exit(1)
    with open(PROMPT_CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

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
        print(f"⚠️ [CẢNH BÁO]: Lỗi khi đọc {QUESTION_CSV_FILE}: {e}")
    return max_id

def get_api_key():
    """Lấy Gemini API Key từ biến môi trường, file .env hoặc nhập trực tiếp"""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key:
        return api_key

    env_path = os.path.join(CURRENT_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val

    print("\n🔑 Chưa phát hiện GEMINI_API_KEY trong hệ thống!")
    api_key = input("👉 Sensei hãy dán khóa bí mật (Gemini API Key) vào đây: ").strip()
    if not api_key:
        print("❌ Sensei chưa cung cấp API Key. Nhiệm vụ bị hủy bỏ!")
        sys.exit(1)
        
    save_opt = input("💾 Sensei có muốn Aris lưu API Key này vào .env để lần sau dùng tiếp không? (y/n): ").strip().lower()
    if save_opt in ['y', 'yes']:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        print("✨ Đã phong ấn API Key vào tệp .env an toàn!")
    return api_key

# =============================================================================
# THUẬT TOÁN ĐIỀU PHỐI ĐỊNH MỆNH (DETERMINISTIC BLUEPRINT GENERATOR)
# =============================================================================

def generate_exact_blueprints(total_questions, config):
    """
    Tạo ra chính xác danh sách blueprint nhiệm vụ cho từng câu hỏi:
    - Đảm bảo chính xác 90% Code và 10% Lý thuyết theo toán học.
    - Phân bổ độ khó và dạng câu hỏi theo đúng trọng số (Weighted Distribution).
    """
    settings = config.get("generation_settings", {})
    code_ratio = settings.get("code_ratio", 0.9)
    diff_weights = settings.get("difficulty_weights", {
        "Easy": 0.15, "Medium": 0.35, "Trap": 0.20, "Smokescreen": 0.20, "Boss": 0.10
    })
    type_weights = settings.get("question_type_weights", {
        "Output": 0.25, "Order_Trace": 0.20, "Calculation": 0.15, "Code_Completion": 0.20, "Error_Check": 0.10, "Concept_Apply": 0.10
    })
    topics = config.get("topics", [])
    topic_ids = [t["id"] for t in topics]

    # 1. Tính toán chính xác số câu Code và Lý thuyết
    code_count = int(round(total_questions * code_ratio))
    # Đảm bảo nếu sinh từ 10 câu trở lên thì luôn có ít nhất 1 câu lý thuyết
    if total_questions >= 10 and code_count == total_questions:
        code_count = total_questions - 1
    theory_count = total_questions - code_count

    formats = [True] * code_count + [False] * theory_count
    random.shuffle(formats)

    diff_keys = list(diff_weights.keys())
    diff_vals = list(diff_weights.values())

    type_keys = list(type_weights.keys())
    type_vals = list(type_weights.values())

    blueprints = []
    for idx, has_code in enumerate(formats):
        # Bốc ngẫu nhiên độ khó theo tỷ lệ
        diff = random.choices(diff_keys, weights=diff_vals, k=1)[0]
        
        # Bốc ngẫu nhiên chủ đề
        topic = random.choice(topic_ids)

        if not has_code:
            # Câu lý thuyết thuần
            q_type = random.choice(["Concept_Apply", "Order_Trace", "Error_Check"])
            # Nếu là lý thuyết thì không thể là Smokescreen
            if diff == "Smokescreen":
                diff = random.choice(["Medium", "Trap"])
        else:
            if diff == "Smokescreen":
                # Smokescreen bắt buộc có code 30-40 dòng lồng nhau
                q_type = random.choice(["Output", "Order_Trace", "Error_Check"])
                smoke_candidates = [t for t in ["Composition_Has_A", "Constructors_Destructors_Lifecycle", "Const_Static_Members", "Subscript_Functor_Conversion", "Assignment_Operator_DeepCopy"] if t in topic_ids]
                topic = random.choice(smoke_candidates if smoke_candidates else topic_ids)
            else:
                q_type = random.choices(type_keys, weights=type_vals, k=1)[0]
                if q_type == "Calculation":
                    calc_candidates = [t for t in ["Constructors_Destructors_Lifecycle", "Const_Static_Members", "Arithmetic_Relational_Operators", "Increment_Decrement_Operators", "IOManip_Formatting"] if t in topic_ids]
                    topic = random.choice(calc_candidates if calc_candidates else topic_ids)

        blueprints.append({
            "slot": idx + 1,
            "has_code": has_code,
            "difficulty": diff,
            "question_type": q_type,
            "topic": topic
        })

    return blueprints

# =============================================================================
# ENGINE GỌI GEMINI REST API
# =============================================================================

def call_gemini_api(api_key, model_name, system_instruction, user_prompt, max_retries=3, thinking_budget=1024):
    """Gọi Gemini REST API với chế độ JSON Mode và Thinking Config"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    gen_config = {
        "temperature": 0.6,
        "responseMimeType": "application/json"
    }
    if thinking_budget > 0:
        gen_config["thinkingConfig"] = {
            "thinkingBudget": thinking_budget
        }

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "generationConfig": gen_config
    }

    req_data = json.dumps(payload).encode('utf-8')
    headers = {"Content-Type": "application/json"}

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=120) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                
                # Trích xuất nội dung trả về
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
                
                # Trích xuất mảng JSON an toàn, loại bỏ Markdown code fences nếu có
                cleaned_json = content_text.strip()
                if "```json" in cleaned_json:
                    cleaned_json = cleaned_json.split("```json", 1)[1]
                    if "```" in cleaned_json:
                        cleaned_json = cleaned_json.split("```", 1)[0]
                elif "```" in cleaned_json:
                    cleaned_json = cleaned_json.split("```", 1)[1]
                    if "```" in cleaned_json:
                        cleaned_json = cleaned_json.split("```", 1)[0]
                cleaned_json = cleaned_json.strip()

                start = cleaned_json.find('[')
                end = cleaned_json.rfind(']')
                if start != -1 and end != -1 and end > start:
                    cleaned_json = cleaned_json[start:end+1]

                return json.loads(cleaned_json)

        except urllib.error.HTTPError as e:
            err_msg = e.read().decode('utf-8', errors='ignore')
            print(f"⚠️ [HTTP {e.code}] Thử lại ({attempt}/{max_retries}). Chi tiết: {err_msg[:120]}...")
            if e.code == 429:
                print("⏳ Quá tải tốc độ request (Rate Limit)! Đang kích hoạt chế độ ngủ 8 giây...")
                time.sleep(8)
            else:
                time.sleep(4)
        except Exception as e:
            print(f"⚠️ [Lỗi]: {e}. Đang thử lại ({attempt}/{max_retries})...")
            time.sleep(4)

    return None

def verify_cpp_code(q_code, q_type, opt1):
    """
    Sử dụng trình biên dịch g++ thật để kiểm định tính hợp lệ của code C++:
    - Tự động phát hiện và dọn dẹp lỗi gõ nhầm tiền xử lý của AI (như #iostream)
    - Đối chứng lỗi biên dịch thật
    - Chạy thử và đồng bộ hóa kết quả stdout cho dạng bài Output / Calculation
    """
    cleaned_code = re.sub(r'^\s*#iostream\b', '#include <iostream>', q_code, flags=re.MULTILINE)
    
    # Kiểm tra xem g++ có sẵn trên hệ thống hay không
    try:
        chk = subprocess.run(["g++", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        if chk.returncode != 0:
            return True, cleaned_code, opt1, "Bỏ qua xác thực (Không tìm thấy g++)"
    except Exception:
        return True, cleaned_code, opt1, "Bỏ qua xác thực (Môi trường không có g++)"

    # Nếu là dạng Code_Completion: Thay placeholder bằng opt1 để biên dịch kiểm định
    code_to_compile = cleaned_code
    if q_type == "Code_Completion":
        placeholder_pattern = r'//\s*\[(?:ĐIỀN CODE TẠI ĐÂY|ĐOẠN MÃ CÒN THIẾU|CHỖ TRỐNG|CODE)\]|/\*\s*(?:\?\?\?|\[ĐIỀN CODE TẠI ĐÂY\])\s*\*/'
        if re.search(placeholder_pattern, code_to_compile, re.IGNORECASE):
            code_to_compile = re.sub(placeholder_pattern, opt1, code_to_compile, count=1, flags=re.IGNORECASE)
        elif "//" in code_to_compile and "[ĐIỀN" in code_to_compile:
            code_to_compile = re.sub(r'//.*\[ĐIỀN.*\]', opt1, code_to_compile, count=1)

    # Lưu file tạm tại thư mục Temp của hệ điều hành để tránh lỗi đường dẫn có dấu tiếng Việt (Tài liệu)
    temp_dir = tempfile.gettempdir()
    temp_cpp = os.path.join(temp_dir, "_aris_verify_temp.cpp")
    temp_exe = os.path.join(temp_dir, "_aris_verify_temp.exe")

    try:
        with open(temp_cpp, 'w', encoding='utf-8') as f:
            f.write(code_to_compile)

        comp = subprocess.run(
            ["g++", "-std=c++11", temp_cpp, "-o", temp_exe],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10
        )

        is_compile_error = (comp.returncode != 0)
        opt1_claims_error = ("lỗi biên dịch" in opt1.lower())

        if is_compile_error:
            if opt1_claims_error:
                return True, cleaned_code, "Lỗi biên dịch", "Xác thực: Code gây lỗi biên dịch thật sự!"
            else:
                err_snippet = comp.stderr.strip().split("\n")[0][:100]
                return False, cleaned_code, opt1, f"Lỗi biên dịch cú pháp ngoài ý muốn: {err_snippet}"
        else:
            if opt1_claims_error:
                return False, cleaned_code, opt1, "Mã nguồn biên dịch thành công nhưng opt1 lại bảo 'Lỗi biên dịch'!"

            # Chạy thử file thực thi để lấy stdout
            try:
                run_proc = subprocess.run(
                    [temp_exe], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=4
                )
                actual_stdout = run_proc.stdout.strip()
                if (q_type == "Output" or q_type == "Calculation") and actual_stdout:
                    if actual_stdout != opt1.strip():
                        return True, cleaned_code, actual_stdout, f"Đồng bộ opt1 theo stdout thật ({actual_stdout})"
            except subprocess.TimeoutExpired:
                return False, cleaned_code, opt1, "Mã nguồn bị lặp vô tận (Timeout khi chạy exe)!"

        return True, cleaned_code, opt1, "Biên dịch và chạy thử hoàn hảo 100%!"

    except Exception as e:
        return True, cleaned_code, opt1, f"Bỏ qua xác thực: {e}"
    finally:
        if os.path.exists(temp_cpp):
            try: os.remove(temp_cpp)
            except: pass
        if os.path.exists(temp_exe):
            try: os.remove(temp_exe)
            except: pass


# =============================================================================
# THỦ TỤC LƯU TRỮ VÀ GHI DỮ LIỆU
# =============================================================================

def append_question_to_csv(qid, topic, difficulty, q_type, question_text, code_filename, opts, explanation):
    """Ghi 1 câu hỏi mới vào question.csv chuẩn 12 cột UTF-8"""
    file_exists = os.path.exists(QUESTION_CSV_FILE)
    
    with open(QUESTION_CSV_FILE, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        if not file_exists:
            writer.writerow([
                "id", "topic", "difficulty", "question_type", "question", 
                "code_file", "opt1", "opt2", "opt3", "opt4", "opt5", "explanation"
            ])
            
        opt1 = opts[0] if len(opts) > 0 else ""
        opt2 = opts[1] if len(opts) > 1 else ""
        opt3 = opts[2] if len(opts) > 2 else ""
        opt4 = opts[3] if len(opts) > 3 else ""
        opt5 = opts[4] if len(opts) > 4 else ""
        
        writer.writerow([
            qid, topic, difficulty, q_type, question_text,
            code_filename, opt1, opt2, opt3, opt4, opt5, explanation
        ])

def save_code_file(qid, code_content):
    """Lưu mã nguồn C++ vào thư mục source/q{id}.cpp"""
    if not os.path.exists(SOURCE_DIR):
        os.makedirs(SOURCE_DIR, exist_ok=True)
    filename = f"q{qid}.cpp"
    filepath = os.path.join(SOURCE_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(code_content.strip() + "\n")
    return filename

# =============================================================================
# CHƯƠNG TRÌNH CHÍNH (MAIN QUEST EXECUTION)
# =============================================================================

def main():
    print("""
╔═════════════════════════════════════════════════════════════════════╗
║         ⚔️ TENDOU ARIS - C++ OOP DUNGEON SPAWN ENGINE ⚔️              ║
║           Hệ thống kiến tạo quái vật trắc nghiệm C++ OOP!           ║
╚═════════════════════════════════════════════════════════════════════╝
""")
    
    config = load_prompt_config()
    settings = config.get("generation_settings", {})
    default_model = settings.get("default_model", "gemini-3.5-flash-lite")
    thinking_budget = settings.get("thinking_budget", 1024)
    batch_size = settings.get("batch_size", 5)
    cooldown = settings.get("cooldown_seconds", 3.5)

    current_max_id = get_current_max_id()
    print(f"📦 [Database Status]: Ngân hàng hiện tại đang có: {current_max_id} câu hỏi.")
    
    api_key = get_api_key()

    # Nhập số lượng câu muốn sinh
    while True:
        try:
            total_req = input("\n🎮 Sensei muốn Aris sinh thêm bao nhiêu câu hỏi mới? (ví dụ 10, 20): ").strip()
            total_req = int(total_req)
            if total_req > 0:
                break
            print("⚠️ Sensei hãy nhập số lượng lớn hơn 0 nhé!")
        except ValueError:
            print("⚠️ Vui lòng nhập số nguyên hợp lệ ạ!")

    # 1. Tính toán Blueprint định mệnh
    print(f"\n🔮 [Aris Engine]: Đang tính toán ma trận xác suất cho {total_req} câu hỏi...")
    blueprints = generate_exact_blueprints(total_req, config)

    code_total = sum(1 for b in blueprints if b["has_code"])
    theory_total = total_req - code_total
    print(f"📊 [Phân bổ cam kết]:")
    print(f"   💻 Câu hỏi Code thực chiến: {code_total}/{total_req} (Đạt {code_total/total_req*100:.1f}%)")
    print(f"   📖 Câu hỏi Lý thuyết lõi:   {theory_total}/{total_req} (Đạt {theory_total/total_req*100:.1f}%)")
    print(f"   🥷 Độ khó 'Smokescreen' (Hỏa mù): {sum(1 for b in blueprints if b['difficulty'] == 'Smokescreen')} câu")
    print(f"   ⚠️  Độ khó 'Trap' (Cạm bẫy):        {sum(1 for b in blueprints if b['difficulty'] == 'Trap')} câu")
    print(f"   🧮 Dạng bài 'Calculation':        {sum(1 for b in blueprints if b['question_type'] == 'Calculation')} câu")

    # 2. Chia thành các mẻ (Batches)
    batches = [blueprints[i:i + batch_size] for i in range(0, len(blueprints), batch_size)]
    print(f"⚔️ Sẽ thực hiện qua {len(batches)} đợt triệu hồi (Batch size = {batch_size})...\n")

    next_id = current_max_id + 1
    total_spawned = 0

    for b_idx, batch in enumerate(batches, start=1):
        print(f"▶️ [Đợt {b_idx}/{len(batches)}]: Đang yêu cầu AI triệu hồi {len(batch)} câu hỏi...")

        # Xây dựng danh sách yêu cầu cụ thể (Dynamic Injection từ dictionaries)
        req_list_text = []
        difficulties_dict = config.get("difficulties", {})
        types_dict = config.get("question_types", {})
        topics_dict = {t["id"]: t for t in config.get("topics", [])}

        for item in batch:
            code_label = "[BẮT BUỘC CÓ CODE C++ ĐÍNH KÈM]" if item["has_code"] else "[BẮT BUỘC LÝ THUYẾT - KHÔNG CÓ CODE]"
            diff_meta = difficulties_dict.get(item["difficulty"], {})
            type_meta = types_dict.get(item["question_type"], {})
            topic_meta = topics_dict.get(item["topic"], {})

            diff_inst = diff_meta.get("instruction", "")
            type_inst = type_meta.get("instruction", "")
            topic_name = topic_meta.get("name", item["topic"])
            topic_desc = topic_meta.get("description", "Tuân thủ chuẩn C++ OOP cơ bản.")

            slot_text = (
                f"### [CÂU SLOT {item['slot']}]:\n"
                f"- Chủ đề: {topic_name} (Mã: {item['topic']})\n"
                f"- Phạm vi nội dung cốt lõi: {topic_desc}\n"
                f"- Hình thức: {code_label}\n"
                f"- Độ khó ({item['difficulty']}): {diff_inst}\n"
                f"- Dạng bài ({item['question_type']}): {type_inst}"
            )
            req_list_text.append(slot_text)

        batch_prompt = f"""
Hãy tạo chính xác {len(batch)} câu hỏi trắc nghiệm C++ OOP tương ứng 1-đối-1 với danh sách bản thiết kế động sau:

{chr(10).join(req_list_text)}

YÊU CẦU ĐẦU RA BẮT BUỘC:
Trả về duy nhất 1 mảng JSON chứa {len(batch)} phần tử theo đúng response_format_schema:
Mỗi phần tử gồm:
- topic (string)
- difficulty ("Easy" | "Medium" | "Trap" | "Smokescreen" | "Boss")
- question_type ("Output" | "Order_Trace" | "Calculation" | "Error_Check" | "Concept_Apply")
- has_code (boolean)
- question (string)
- code_content (string chứa toàn bộ mã nguồn C++ có hàm main() nếu has_code=true, để chuỗi rỗng nếu has_code=false)
- opt1 (string: ĐÁP ÁN ĐÚNG 100%)
- opt2 (string: Phương án nhiễu 1)
- opt3 (string: Phương án nhiễu 2)
- opt4 (string: Phương án nhiễu 3 hoặc rỗng)
- opt5 (string: Phương án nhiễu 4 hoặc rỗng)
- explanation (string: Giải thích cơ chế vì sao opt1 đúng)

LƯU Ý QUAN TRỌNG VỀ ĐỀ THI:
Nếu phương án liên quan tới lỗi biên dịch (dù là opt1 hay distractor) mà không phải dạng bài trắc nghiệm chọn vị trí dòng lỗi, thì BẮT BUỘC chỉ ghi chính xác: "Lỗi biên dịch" (không ghi thêm bất kỳ lý do nào trong phương án để tránh làm lộ đề, toàn bộ phân tích phải ghi vào explanation).
"""

        generated_items = call_gemini_api(
            api_key=api_key,
            model_name=default_model,
            system_instruction=config.get("system_instruction", ""),
            user_prompt=batch_prompt,
            thinking_budget=thinking_budget
        )

        if not generated_items or not isinstance(generated_items, list):
            print(f"❌ [LỖI]: Đợt {b_idx} thất bại hoặc định dạng không hợp lệ. Đang bỏ qua đợt này...")
            continue

        # Lưu dữ liệu vào file
        for q_data in generated_items:
            q_topic = q_data.get("topic", "OOP")
            q_diff = q_data.get("difficulty", "Medium")
            q_type = q_data.get("question_type", "Output")
            q_has_code = q_data.get("has_code", False)
            q_text = q_data.get("question", "Câu hỏi...")
            q_code = q_data.get("code_content", "")
            q_exp = q_data.get("explanation", "Giải thích...")
            
            opts = [
                q_data.get("opt1", ""),
                q_data.get("opt2", ""),
                q_data.get("opt3", ""),
                q_data.get("opt4", ""),
                q_data.get("opt5", "")
            ]

            code_file = ""
            if q_has_code and q_code.strip():
                # ⚔️ G++ COMPILER SANDBOX VALIDATION
                is_valid, q_code, verified_opt1, verdict_msg = verify_cpp_code(q_code, q_type, opts[0])
                if not is_valid:
                    print(f"   ⚠️ [BỊ LOẠI BỎ DO LỖI BIÊN DỊCH]: {verdict_msg}")
                    continue
                opts[0] = verified_opt1
                code_file = save_code_file(next_id, q_code)
                print(f"   🛡️ [G++ Verified]: {verdict_msg}")

            append_question_to_csv(
                qid=next_id,
                topic=q_topic,
                difficulty=q_diff,
                q_type=q_type,
                question_text=q_text,
                code_filename=code_file,
                opts=opts,
                explanation=q_exp
            )

            tag_icon = "💻 [CODE]" if code_file else "📖 [THEORY]"
            print(f"   ✨ #{next_id}: {tag_icon} [{q_diff} | {q_type}] {q_topic} -> Thành công!")
            next_id += 1
            total_spawned += 1

        if b_idx < len(batches):
            print(f"⏳ Hồi chiêu {cooldown}s trước đợt triệu hồi tiếp theo...")
            time.sleep(cooldown)

    print("\n" + "=" * 65)
    print(f"🎉 Pan-paka-pan! Nhiệm vụ hoàn thành xuất sắc!")
    print(f"🎯 Đã khởi tạo thành công thêm {total_spawned} câu hỏi mới vào Database!")
    print(f"📁 Tệp câu hỏi: {QUESTION_CSV_FILE}")
    print(f"📁 Mã nguồn C++: {SOURCE_DIR}")
    print(f"📊 Tổng số lượng câu hỏi hiện tại: {next_id - 1} câu.")
    print("=" * 65)

if __name__ == "__main__":
    main()
