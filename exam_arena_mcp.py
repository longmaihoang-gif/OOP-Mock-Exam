#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Millennium Science School - Game Development Department (GDD)
C++ Mock Exam Arena - MCP Server (stdio Transport)

Cung cấp các công cụ MCP chuẩn JSON-RPC 2.0:
1. get_recent_exams: Lấy lịch sử các trận thi đấu gần nhất
2. get_failed_questions: Phân tích các câu hỏi làm sai trong bài thi
3. get_mistake_bank: Lấy danh sách câu sai đang chờ phục thù
4. verify_and_save_revenge_question: Sandbox g++ (-std=c++11), tự động lưu đề phục thù vào question.csv + source/ và sync vào mistakes.json
5. get_question_detail: Xem chi tiết câu hỏi và code C++
6. audit_question_bank: Quét nhanh độ tin cậy bằng g++ sandbox (tối ưu token)
"""

import sys
import os
import io
import json
import csv
import re
import tempfile
import subprocess
import traceback

# Cấu hình UTF-8 cho stdio trên Windows
if sys.platform == "win32":
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTION_CSV = os.path.join(BASE_DIR, "question.csv")
SOURCE_DIR = os.path.join(BASE_DIR, "source")
HISTORY_FILE = os.path.join(BASE_DIR, "exam_history.json")
MISTAKES_FILE = os.path.join(BASE_DIR, "mistakes.json")

def log_debug(msg):
    """Ghi log chẩn đoán ra stderr để không làm hỏng luồng stdout JSON-RPC"""
    sys.stderr.write(f"[GDD-MCP-DEBUG] {msg}\n")
    sys.stderr.flush()

# =============================================================================
# CÁC HÀM TIỆN ÍCH DỮ LIỆU
# =============================================================================

def read_json_file(filepath, default_val=None):
    if default_val is None:
        default_val = []
    if not os.path.exists(filepath):
        return default_val
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_debug(f"Lỗi đọc {filepath}: {e}")
        return default_val

def write_json_file(filepath, data):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        log_debug(f"Lỗi ghi {filepath}: {e}")
        return False

def load_question_csv():
    """Đọc toàn bộ question.csv thành danh sách dict"""
    if not os.path.exists(QUESTION_CSV):
        return []
    questions = []
    try:
        with open(QUESTION_CSV, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return []
            has_type_col = any(h.strip().lower() == "question_type" for h in header)

            for idx, row in enumerate(reader, start=1):
                if len(row) < 6:
                    continue
                try:
                    qid = int(row[0])
                except ValueError:
                    qid = idx

                if has_type_col:
                    topic = row[1] if len(row) > 1 else "OOP"
                    diff = row[2] if len(row) > 2 else "Medium"
                    q_type = row[3] if len(row) > 3 else "Output"
                    q_text = row[4] if len(row) > 4 else ""
                    c_file = row[5].strip() if len(row) > 5 else ""
                    opt_start = 6
                    explanation = row[11] if len(row) > 11 else ""
                else:
                    topic = row[1] if len(row) > 1 else "OOP"
                    diff = row[2] if len(row) > 2 else "Medium"
                    q_text = row[3] if len(row) > 3 else ""
                    c_file = row[4].strip() if len(row) > 4 else ""
                    q_type = "Code" if c_file else "Concept_Apply"
                    opt_start = 5
                    explanation = row[10] if len(row) > 10 else ""

                opts = [row[i].strip() for i in range(opt_start, min(opt_start + 5, len(row))) if row[i].strip()]

                questions.append({
                    "id": qid,
                    "topic": topic,
                    "difficulty": diff,
                    "question_type": q_type,
                    "question": q_text,
                    "code_file": c_file,
                    "options": opts,  # opts[0] luôn là đáp án đúng
                    "correct_answer": opts[0] if opts else "",
                    "explanation": explanation
                })
    except Exception as e:
        log_debug(f"Lỗi đọc question.csv: {e}")
    return questions

def get_code_content(code_file):
    if not code_file:
        return ""
    file_path = os.path.join(SOURCE_DIR, code_file)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
    return ""

def get_max_question_id():
    questions = load_question_csv()
    if not questions:
        return 0
    return max(q["id"] for q in questions)

# =============================================================================
# G++ SANDBOX TEST ENGINE
# =============================================================================

def test_compile_and_run(cpp_code, timeout_compile=10, timeout_run=4):
    """
    Biên dịch và chạy thử code C++ qua g++:
    - Trả về (success, stdout, stderr_or_error)
    """
    # Dọn dẹp lỗi gõ nhầm tiền xử lý phổ biến
    cleaned_code = re.sub(r'^\s*#iostream\b', '#include <iostream>', cpp_code, flags=re.MULTILINE)

    # Kiểm tra g++
    try:
        chk = subprocess.run(["g++", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        if chk.returncode != 0:
            return False, "", "Hệ thống không tìm thấy trình biên dịch g++ hợp lệ."
    except Exception as e:
        return False, "", f"Không thể kích hoạt g++: {e}"

    temp_dir = tempfile.gettempdir()
    temp_cpp = os.path.join(temp_dir, f"_aris_mcp_{os.getpid()}_{id(cpp_code)}.cpp")
    temp_exe = os.path.join(temp_dir, f"_aris_mcp_{os.getpid()}_{id(cpp_code)}.exe")

    try:
        with open(temp_cpp, "w", encoding="utf-8") as f:
            f.write(cleaned_code)

        # Biên dịch C++11
        comp = subprocess.run(
            ["g++", "-std=c++11", "-O2", temp_cpp, "-o", temp_exe],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout_compile
        )

        if comp.returncode != 0:
            err = comp.stderr.strip()
            return False, "", f"Lỗi biên dịch (Compile Error):\n{err}"

        # Chạy thử nghiệm
        try:
            run_proc = subprocess.run(
                [temp_exe], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout_run
            )
            return True, run_proc.stdout.strip(), ""
        except subprocess.TimeoutExpired:
            return False, "", "Lỗi thời gian chạy: Mã nguồn bị lặp vô tận (Execution Timeout)!"
        except Exception as e:
            return False, "", f"Lỗi thực thi (Runtime Error): {e}"

    finally:
        if os.path.exists(temp_cpp):
            try: os.remove(temp_cpp)
            except: pass
        if os.path.exists(temp_exe):
            try: os.remove(temp_exe)
            except: pass

# =============================================================================
# CÁC TOOL IMPLEMENTATION
# =============================================================================

def tool_get_recent_exams(args):
    limit = args.get("limit", 5)
    history = read_json_file(HISTORY_FILE, [])
    if not history:
        return "Chưa có dữ liệu bài thi nào trong lịch sử (exam_history.json đang trống)."

    recent = history[:limit]
    res = {
        "total_exams_recorded": len(history),
        "showing": len(recent),
        "exams": []
    }
    for item in recent:
        res["exams"].append({
            "id": item.get("id", "N/A"),
            "date": item.get("date", "N/A"),
            "mode": item.get("mode", "Thi Thử"),
            "score": item.get("score", "N/A"),
            "percent": item.get("percent", "N/A"),
            "duration": item.get("duration", "N/A"),
            "failed_question_ids": item.get("failed_question_ids", [])
        })
    return json.dumps(res, ensure_ascii=False, indent=2)

def tool_get_failed_questions(args):
    exam_id = args.get("exam_id", "latest")
    history = read_json_file(HISTORY_FILE, [])
    if not history:
        return "Không có lịch sử thi đấu nào được ghi nhận."

    target_exam = None
    if exam_id == "latest":
        target_exam = history[0]
    else:
        for exam in history:
            if exam.get("id") == exam_id:
                target_exam = exam
                break

    if not target_exam:
        return f"Không tìm thấy bài thi có ID '{exam_id}'."

    failed_ids = target_exam.get("failed_question_ids", [])
    if not failed_ids:
        return f"Tuyệt vời! Trong bài thi {target_exam.get('id')} ({target_exam.get('date')}), Sensei đã đạt 100% điểm số và không làm sai câu nào!"

    all_questions = {q["id"]: q for q in load_question_csv()}
    attempted_map = {}
    for att in target_exam.get("questions_attempted", []):
        attempted_map[att.get("id")] = att

    details = []
    for qid in failed_ids:
        q_info = all_questions.get(qid)
        code_str = ""
        if q_info and q_info.get("code_file"):
            code_str = get_code_content(q_info["code_file"])

        att_info = attempted_map.get(qid, {})
        details.append({
            "question_id": qid,
            "topic": q_info.get("topic", "OOP") if q_info else "N/A",
            "difficulty": q_info.get("difficulty", "Medium") if q_info else "N/A",
            "question_type": q_info.get("question_type", "Output") if q_info else "N/A",
            "question_text": q_info.get("question", "") if q_info else "Không tìm thấy nội dung câu hỏi trong CSV",
            "code_file": q_info.get("code_file", "") if q_info else "",
            "cpp_source": code_str,
            "user_selected": att_info.get("user_answer", "Không trả lời"),
            "correct_answer": q_info.get("correct_answer", "") if q_info else "",
            "all_options": q_info.get("options", []) if q_info else [],
            "explanation": q_info.get("explanation", "") if q_info else ""
        })

    result = {
        "exam_id": target_exam.get("id"),
        "date": target_exam.get("date"),
        "score": target_exam.get("score"),
        "percent": target_exam.get("percent"),
        "total_failed": len(details),
        "failed_questions": details
    }
    return json.dumps(result, ensure_ascii=False, indent=2)

def tool_get_mistake_bank(args):
    mistake_ids = read_json_file(MISTAKES_FILE, [])
    if not mistake_ids:
        return json.dumps({"count": 0, "mistakes": [], "message": "Ngân hàng câu sai hiện đang trống!"}, ensure_ascii=False, indent=2)

    all_questions = {q["id"]: q for q in load_question_csv()}
    items = []
    for qid in mistake_ids:
        q = all_questions.get(int(qid))
        if q:
            items.append({
                "id": q["id"],
                "topic": q["topic"],
                "difficulty": q["difficulty"],
                "question": q["question"],
                "code_file": q["code_file"],
                "correct_answer": q["correct_answer"],
                "explanation": q["explanation"]
            })
        else:
            items.append({"id": qid, "status": "Không tìm thấy trong CSV"})

    return json.dumps({
        "count": len(items),
        "mistake_ids": mistake_ids,
        "questions": items
    }, ensure_ascii=False, indent=2)

def tool_get_question_detail(args):
    qid = args.get("question_id")
    if qid is None:
        return "Vui lòng cung cấp question_id."

    try:
        qid = int(qid)
    except ValueError:
        return f"question_id '{qid}' không hợp lệ."

    all_questions = {q["id"]: q for q in load_question_csv()}
    q = all_questions.get(qid)
    if not q:
        return f"Không tìm thấy câu hỏi mang ID {qid} trong question.csv."

    code_str = ""
    if q.get("code_file"):
        code_str = get_code_content(q["code_file"])

    res = dict(q)
    res["cpp_source"] = code_str
    return json.dumps(res, ensure_ascii=False, indent=2)

def tool_verify_and_save_revenge_question(args):
    cpp_source = args.get("cpp_source", "").strip()
    question_text = args.get("question_text", "").strip()
    options = args.get("options", [])
    correct_index = args.get("correct_index", 0)
    explanation = args.get("explanation", "").strip()
    topic = args.get("topic", "OOP_Revenge_Quest")
    difficulty = args.get("difficulty", "Trap")
    q_type = args.get("question_type", "Output")
    failed_qid = args.get("failed_question_id")

    if not cpp_source:
        return "Lỗi: cpp_source không được để trống."
    if not question_text:
        return "Lỗi: question_text không được để trống."
    if not options or len(options) < 2:
        return "Lỗi: options phải có ít nhất 2 phương án lựa chọn."
    if not (0 <= correct_index < len(options)):
        return f"Lỗi: correct_index ({correct_index}) vượt quá phạm vi của danh sách options (độ dài {len(options)})."

    # 1. Sandbox Verification qua g++
    is_compile_error_intended = ("lỗi biên dịch" in options[correct_index].lower())
    
    code_to_test = cpp_source
    if q_type == "Code_Completion":
        placeholder_pattern = r'//\s*\[(?:ĐIỀN CODE TẠI ĐÂY|ĐOẠN MÃ CÒN THIẾU|CHỖ TRỐNG|CODE)\]|/\*\s*(?:\?\?\?|\[ĐIỀN CODE TẠI ĐÂY\])\s*\*/'
        if re.search(placeholder_pattern, code_to_test, re.IGNORECASE):
            code_to_test = re.sub(placeholder_pattern, options[correct_index], code_to_test, count=1, flags=re.IGNORECASE)
        elif "//" in code_to_test and "[ĐIỀN" in code_to_test:
            code_to_test = re.sub(r'//.*\[ĐIỀN.*\]', options[correct_index], code_to_test, count=1)

    success, stdout_out, err_msg = test_compile_and_run(code_to_test)

    if not success:
        if is_compile_error_intended and "Lỗi biên dịch" in err_msg:
            # Đây là câu hỏi cố tình bẫy lỗi biên dịch, hợp lệ!
            stdout_out = "Lỗi biên dịch (Xác thực thực tế)"
        else:
            return json.dumps({
                "status": "SANDBOX_FAILED",
                "error": err_msg,
                "message": "Mã nguồn C++ không vượt qua được sandbox kiểm định. Vui lòng sửa lại code dựa theo log lỗi trên."
            }, ensure_ascii=False, indent=2)
    else:
        if is_compile_error_intended:
            return json.dumps({
                "status": "SANDBOX_FAILED",
                "error": "Mã C++ biên dịch thành công hoàn toàn, nhưng phương án đúng lại tuyên bố là 'Lỗi biên dịch'!",
                "actual_stdout": stdout_out
            }, ensure_ascii=False, indent=2)

    # 2. Chuẩn bị dữ liệu CSV chuẩn Millennium: opt1 luôn là phương án đúng
    correct_opt = options[correct_index]
    other_opts = [opt for i, opt in enumerate(options) if i != correct_index]
    reordered_opts = [correct_opt] + other_opts

    # 3. Cấp phát ID mới
    next_id = get_max_question_id() + 1
    code_filename = f"q{next_id}.cpp"

    # 4. Lưu file C++ vào thư mục source/
    if not os.path.exists(SOURCE_DIR):
        os.makedirs(SOURCE_DIR, exist_ok=True)
    code_path = os.path.join(SOURCE_DIR, code_filename)
    with open(code_path, "w", encoding="utf-8") as f:
        f.write(cpp_source.strip() + "\n")

    # 5. Ghi vào question.csv chuẩn 12 cột UTF-8
    with open(QUESTION_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        opt1 = reordered_opts[0] if len(reordered_opts) > 0 else ""
        opt2 = reordered_opts[1] if len(reordered_opts) > 1 else ""
        opt3 = reordered_opts[2] if len(reordered_opts) > 2 else ""
        opt4 = reordered_opts[3] if len(reordered_opts) > 3 else ""
        opt5 = reordered_opts[4] if len(reordered_opts) > 4 else ""
        writer.writerow([
            next_id, topic, difficulty, q_type, question_text,
            code_filename, opt1, opt2, opt3, opt4, opt5, explanation
        ])

    # 6. Tự động thêm ID câu hỏi phục thù vào mistakes.json
    mistakes = read_json_file(MISTAKES_FILE, [])
    if next_id not in mistakes:
        mistakes.append(next_id)
        write_json_file(MISTAKES_FILE, mistakes)

    res = {
        "status": "SUCCESS",
        "question_id": next_id,
        "code_file": code_filename,
        "correct_answer": correct_opt,
        "actual_stdout": stdout_out,
        "added_to_mistakes_queue": True,
        "total_mistakes_pending": len(mistakes),
        "message": f"Pan-paka-pan! Đã tạo thành công câu hỏi phục thù mang ID {next_id}! Câu hỏi đã được nạp trực tiếp vào hàng chờ 'LÀM LẠI CÂU SAI' trên web để Sensei vào chiến ngay!"
    }
    if failed_qid:
        res["avenged_question_id"] = failed_qid

    return json.dumps(res, ensure_ascii=False, indent=2)

def tool_audit_question_bank(args):
    """
    Audit bằng g++ sandbox.
    Tối ưu token: Silent on Success hoặc rút gọn tối đa.
    """
    qid = args.get("question_id")
    recent_count = args.get("recent_count", 10)

    all_questions = load_question_csv()
    if not all_questions:
        return "Ngân hàng question.csv đang trống."

    if qid is not None:
        target_list = [q for q in all_questions if q["id"] == int(qid)]
        if not target_list:
            return f"Không tìm thấy câu hỏi {qid} để audit."
    else:
        target_list = all_questions[-recent_count:]

    results = []
    has_error = False

    for q in target_list:
        code_file = q.get("code_file")
        if not code_file:
            continue
        code_content = get_code_content(code_file)
        if not code_content:
            results.append({"id": q["id"], "file": code_file, "status": "MISSING_FILE"})
            has_error = True
            continue

        is_compile_error_intended = ("lỗi biên dịch" in q.get("correct_answer", "").lower())
        
        q_type = q.get("question_type", "")
        code_to_compile = code_content
        if q_type == "Code_Completion":
            placeholder_pattern = r'//\s*\[(?:ĐIỀN CODE TẠI ĐÂY|ĐOẠN MÃ CÒN THIẾU|CHỖ TRỐNG|CODE)\]|/\*\s*(?:\?\?\?|\[ĐIỀN CODE TẠI ĐÂY\])\s*\*/'
            correct_opt = q.get("correct_answer", "")
            if re.search(placeholder_pattern, code_to_compile, re.IGNORECASE):
                code_to_compile = re.sub(placeholder_pattern, correct_opt, code_to_compile, count=1, flags=re.IGNORECASE)
            elif "//" in code_to_compile and "[ĐIỀN" in code_to_compile:
                code_to_compile = re.sub(r'//.*\[ĐIỀN.*\]', correct_opt, code_to_compile, count=1)

        ok, stdout_res, err = test_compile_and_run(code_to_compile)

        if not ok:
            if is_compile_error_intended and "Lỗi biên dịch" in err:
                pass # Intended
            else:
                has_error = True
                results.append({
                    "id": q["id"],
                    "file": code_file,
                    "status": "FAILED",
                    "error": err[:120]
                })
        else:
            if is_compile_error_intended:
                has_error = True
                results.append({
                    "id": q["id"],
                    "file": code_file,
                    "status": "LOGIC_ERROR",
                    "error": "Code compiles fine but correct answer claims compile error!"
                })

    if not has_error:
        return f"OK: Đã audit an toàn {len(target_list)} câu hỏi. Toàn bộ mã nguồn biên dịch và chạy đúng chuẩn 100%!"
    else:
        return json.dumps({
            "status": "AUDIT_WARNING",
            "total_checked": len(target_list),
            "issues": results
        }, ensure_ascii=False, indent=2)

# =============================================================================
# DANH MỤC CÁC TOOLS ĐĂNG KÝ VỚI PROTOCOL
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "get_recent_exams",
        "description": "Lấy danh sách các bài thi gần nhất từ exam_history.json (ID bài thi, thời gian, điểm số, tỷ lệ, thời lượng, chế độ thi, và danh sách ID các câu làm sai). Dùng để nắm bắt phong độ và lịch sử làm bài của học viên.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Số lượng bài thi gần nhất cần lấy (mặc định: 5)",
                    "default": 5
                }
            }
        }
    },
    {
        "name": "get_failed_questions",
        "description": "Lấy chi tiết các câu hỏi mà học viên làm sai trong một bài thi cụ thể (mặc định lấy bài thi mới nhất). Bao gồm ID câu hỏi, đề bài, mã C++, đáp án học viên chọn, đáp án đúng, và lời giải thích để AI cố vấn phân tích điểm yếu.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "exam_id": {
                    "type": "string",
                    "description": "ID của bài thi (ví dụ: 'latest' để lấy bài mới nhất, hoặc 'exam_1740000000')",
                    "default": "latest"
                }
            }
        }
    },
    {
        "name": "get_mistake_bank",
        "description": "Lấy danh sách toàn bộ các câu hỏi đang nằm trong ngân hàng câu làm sai (mistakes.json) chờ người học ôn tập phục thù.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_question_detail",
        "description": "Lấy thông tin chi tiết một câu hỏi theo ID từ question.csv và file mã nguồn tương ứng trong thư mục source/.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question_id": {
                    "type": "integer",
                    "description": "ID câu hỏi (ví dụ: 12)"
                }
            },
            "required": ["question_id"]
        }
    },
    {
        "name": "verify_and_save_revenge_question",
        "description": "Biên dịch và chạy thử mã C++ bằng g++ sandbox (-std=c++11), sau đó lưu câu hỏi phục thù vào question.csv, source/q{N}.cpp, và tự động thêm ID vào mistakes.json để người học có thể bấm nút 'LÀM LẠI CÂU SAI' trên web làm ngay.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "cpp_source": {
                    "type": "string",
                    "description": "Mã nguồn C++ hoàn chỉnh có hàm main."
                },
                "question_text": {
                    "type": "string",
                    "description": "Đề bài trắc nghiệm (tiếng Việt)."
                },
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Danh sách 4 hoặc 5 phương án lựa chọn."
                },
                "correct_index": {
                    "type": "integer",
                    "description": "Vị trí chỉ số (0-indexed) của phương án đúng trong mảng options."
                },
                "explanation": {
                    "type": "string",
                    "description": "Lời giải thích cặn kẽ tại sao phương án đó đúng."
                },
                "topic": {
                    "type": "string",
                    "description": "Chủ đề câu hỏi (ví dụ: 'Polymorphism', 'Destructor_Order')",
                    "default": "OOP_Revenge_Quest"
                },
                "difficulty": {
                    "type": "string",
                    "description": "Độ khó (Easy, Medium, Hard, Trap, Smokescreen)",
                    "default": "Trap"
                },
                "question_type": {
                    "type": "string",
                    "description": "Dạng câu hỏi (Output, Error_Check, Order_Trace, Concept_Apply, Calculation, Code_Completion)",
                    "default": "Output"
                },
                "failed_question_id": {
                    "type": "integer",
                    "description": "ID của câu hỏi mà học viên đã làm sai trước đó dẫn đến quest phục thù này (nếu có)."
                }
            },
            "required": ["cpp_source", "question_text", "options", "correct_index", "explanation"]
        }
    },
    {
        "name": "audit_question_bank",
        "description": "Kiểm tra tính hợp lệ của mã nguồn C++ trong ngân hàng câu hỏi bằng g++ sandbox. Tối ưu token: mặc định chỉ kiểm tra N câu gần nhất hoặc 1 câu chỉ định. Trả về thông báo siêu ngắn gọn nếu tất cả hợp lệ (Silent on Success).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "recent_count": {
                    "type": "integer",
                    "description": "Số lượng câu hỏi mới nhất cần audit (mặc định: 10)",
                    "default": 10
                },
                "question_id": {
                    "type": "integer",
                    "description": "ID câu hỏi cụ thể cần audit. Nếu truyền tham số này sẽ bỏ qua recent_count."
                }
            }
        }
    }
]

TOOL_HANDLERS = {
    "get_recent_exams": tool_get_recent_exams,
    "get_failed_questions": tool_get_failed_questions,
    "get_mistake_bank": tool_get_mistake_bank,
    "get_question_detail": tool_get_question_detail,
    "verify_and_save_revenge_question": tool_verify_and_save_revenge_question,
    "audit_question_bank": tool_audit_question_bank
}

# =============================================================================
# JSON-RPC 2.0 PROTOCOL LOOP
# =============================================================================

def send_response(response_dict):
    msg = json.dumps(response_dict, ensure_ascii=False)
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()

def handle_request(req):
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        send_response({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "exam-arena-mcp",
                    "version": "1.0.0"
                }
            }
        })
    elif method == "notifications/initialized":
        # Client báo đã khởi tạo xong, không cần trả lời
        pass
    elif method == "ping":
        send_response({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        })
    elif method == "tools/list":
        send_response({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOL_DEFINITIONS
            }
        })
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        handler = TOOL_HANDLERS.get(tool_name)

        if not handler:
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Error: Tool '{tool_name}' not found."}],
                    "isError": True
                }
            })
            return

        try:
            output_text = handler(args)
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": str(output_text)}],
                    "isError": False
                }
            })
        except Exception as e:
            err_trace = traceback.format_exc()
            log_debug(f"Exception in tool {tool_name}: {err_trace}")
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Tool execution failed: {e}\n{err_trace}"}],
                    "isError": True
                }
            })
    else:
        if req_id is not None:
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            })

def main():
    log_debug("Tendou Aris MCP Server started in stdio mode.")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            handle_request(req)
        except json.JSONDecodeError as e:
            log_debug(f"JSON decode error: {e}")
            send_response({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {e}"
                }
            })
        except Exception as e:
            log_debug(f"Unhandled error in main loop: {e}")

if __name__ == "__main__":
    main()
