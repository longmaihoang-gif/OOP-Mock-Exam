# -*- coding: utf-8 -*-
"""
=============================================================================
  MULTI-IMAGE BATCH C++ CODE OCR (VISION REST ENGINE)
  Chế độ: Gửi 10 ảnh / 1 lượt request -> Tối ưu hóa lượt gọi API và Mana
  Model mặc định: Gemini 3.5 Flash Lite (Cooldown: 3.0s sau khi xong mỗi mẻ)
  Tự động kích hoạt Resume Engine (bỏ qua các file .cpp đã tồn tại)
=============================================================================
"""

import os
import sys
import json
import time
import base64
import glob
import re
import urllib.request
import urllib.error
from pathlib import Path

# Thiết lập bảng mã UTF-8 cho console Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# 1. HÀM LẤY API KEY (DÙNG CHUNG VỚI AutomaticQuestionGenerator.py)
# =============================================================================

def get_api_key():
    """Lấy Gemini API Key từ biến môi trường hoặc file .env của hệ thống"""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key:
        return api_key

    candidate_env_paths = [
        os.path.join(CURRENT_DIR, ".env"),
        os.path.join(CURRENT_DIR, "Outside", "ExamSystem", ".env"),
        os.path.join(os.path.dirname(CURRENT_DIR), "ExamSystem", ".env")
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

    target_env = os.path.join(CURRENT_DIR, ".env")
    with open(target_env, 'w', encoding='utf-8') as f:
        f.write(f"GEMINI_API_KEY={api_key}\n")
    print(f"✨ Đã lưu API Key vào tệp {target_env} an toàn!")
    return api_key


# =============================================================================
# 2. THẦN CHÚ PROMPT GOM NHIỀU ẢNH (MULTI-IMAGE BATCH PROMPT)
# =============================================================================

PROMPT_MULTI_IMAGE_INSTRUCTION = """
Bạn là một chuyên gia OCR mã nguồn C++.
Dưới đây là một nhóm các bức ảnh chụp mã nguồn C++ (mỗi ảnh được gán nhãn [TÊN_FILE_ẢNH]).

YÊU CẦU QUAN TRỌNG:
1. Đối với MỖI bức ảnh, trích xuất CHÍNH XÁC và ĐẦY ĐỦ toàn bộ mã nguồn C++.
2. BỎ QUA hoàn toàn tiêu đề câu hỏi (ví dụ: "Câu 32/45:...", "Kết quả thực hiện..."), số thứ tự câu và các lựa chọn đáp án (A, B, C, D, E...).
3. Tuyệt đối không thêm lời bình luận, giải thích, hay ghi chú.
4. Giữ nguyên cấu trúc thụt đầu dòng, cú pháp, biến, thư viện như trong ảnh.

ĐỊNH DẠNG ĐẦU RA BẮT BUỘC:
Trả về DUY NHẤT một mảng JSON theo cấu trúc sau:
[
  {
    "filename": "tên_file_ảnh_1",
    "code": "nội dung code C++ hoàn chỉnh của ảnh 1"
  },
  {
    "filename": "tên_file_ảnh_2",
    "code": "nội dung code C++ hoàn chỉnh của ảnh 2"
  }
]
"""

def clean_json_response(raw_text: str) -> list:
    """Bóc tách mảng JSON từ phản hồi của model"""
    cleaned = raw_text.strip()
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

    try:
        return json.loads(cleaned)
    except Exception as e:
        print(f"\n⚠️ Lỗi phân tích cú pháp JSON: {e}")
        return []

def clean_code_block(code_text: str) -> str:
    """Loại bỏ bọc markdown ```cpp thừa trong code nếu có"""
    c = code_text.strip()
    m = re.search(r"^```(?:cpp|c\+\+|c)?\s*\n(.*?)\n```$", c, re.DOTALL)
    if m:
        return m.group(1).strip()
    return c


# =============================================================================
# 3. ENGINE REST API GỬI 10 ẢNH ĐỒNG THỜI
# =============================================================================

def process_batch_images(api_key: str, batch_images: list, model_name: str = "gemini-3.1-flash-lite", max_retries: int = 3) -> list:
    """
    Gửi cùng lúc danh sách ảnh trong batch (tối đa 10 ảnh) lên Gemini REST API.
    batch_images là danh sách dict: [{'path': ..., 'name': ...}, ...]
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    parts = [
        {"text": PROMPT_MULTI_IMAGE_INSTRUCTION}
    ]

    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
    }

    # Đính kèm toàn bộ 10 ảnh vào parts cùng với nhãn tên file
    for item in batch_images:
        ext = os.path.splitext(item['name'])[1].lower()
        mime_type = mime_map.get(ext, "image/jpeg")

        with open(item['path'], "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")

        parts.append({
            "text": f"\n--- [ẢNH ĐẦU VÀO: {item['name']}] ---"
        })
        parts.append({
            "inlineData": {
                "mimeType": mime_type,
                "data": b64_data
            }
        })

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": parts
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
            "maxOutputTokens": 8192
        }
    }

    req_data = json.dumps(payload).encode('utf-8')
    headers = {"Content-Type": "application/json"}

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=180) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)

                candidates = res_json.get("candidates", [])
                if not candidates:
                    raise ValueError("Gemini không trả về candidate nào!")

                c_parts = candidates[0].get("content", {}).get("parts", [])
                content_text = ""
                for p in c_parts:
                    if not p.get("thought", False) and "text" in p:
                        content_text += p["text"]
                if not content_text and c_parts:
                    content_text = c_parts[-1].get("text", "")

                return clean_json_response(content_text)

        except urllib.error.HTTPError as e:
            err_msg = e.read().decode('utf-8', errors='ignore')
            print(f"\n⚠️ HTTP Error {e.code} ở lần thử {attempt}/{max_retries}: {err_msg[:200]}")
            # Nếu gặp 429 (Rate Limit), nghỉ ngơi nhiều hơn
            if e.code == 429:
                sleep_time = 10 * attempt
                print(f"⏳ Bị giới hạn tốc độ (Rate Limit), đang nghỉ {sleep_time}s...")
                time.sleep(sleep_time)
            elif e.code == 404 and model_name != "gemini-3.1-flash-lite":
                print("🔄 Thử chuyển sang model dự phòng 'gemini-3.1-flash-lite'...")
                return process_batch_images(api_key, batch_images, model_name="gemini-3.1-flash-lite", max_retries=1)
            elif attempt < max_retries:
                time.sleep(4 * attempt)
        except Exception as e:
            print(f"\n⚠️ Lỗi kết nối ở lần thử {attempt}/{max_retries}: {e}")
            if attempt < max_retries:
                time.sleep(4 * attempt)

    return []


# =============================================================================
# 4. CHIẾN DỊCH TÁC CHIẾN GOM 10 ẢNH (BATCH OCR RUNNER)
# =============================================================================

def run_multi_batch_ocr(
    input_dir: str = "input_images",
    output_dir: str = "extracted_cpp",
    batch_size: int = 10,
    cooldown_seconds: float = 3.0,
    model_name: str = "gemini-3.1-flash-lite"
):
    """
    Quét toàn bộ ảnh, gom theo mẻ 10 ảnh/request, nghỉ 3.0s sau mỗi lượt xong.
    Tự động bỏ qua file đã có trong output_dir (Resume Engine).
    """
    input_path = os.path.join(CURRENT_DIR, input_dir)
    output_path = os.path.join(CURRENT_DIR, output_dir)
    os.makedirs(input_path, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)

    image_extensions = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.webp")
    all_image_paths = []
    for ext in image_extensions:
        all_image_paths.extend(glob.glob(os.path.join(input_path, ext)))

    if not all_image_paths:
        print(f"📁 [THÔNG BÁO]: Chưa có ảnh nào trong thư mục: {input_path}")
        print("👉 Vui lòng sao chép các ảnh bài tập C++ vào thư mục này rồi chạy lại!")
        return

    # 1. Quét danh sách cần làm (Resume Engine: Lọc ảnh chưa có code)
    pending_images = []
    skipped_count = 0
    for p in all_image_paths:
        name = os.path.basename(p)
        base = os.path.splitext(name)[0]
        out_cpp = os.path.join(output_path, f"{base}.cpp")
        if os.path.exists(out_cpp) and os.path.getsize(out_cpp) > 0:
            skipped_count += 1
        else:
            pending_images.append({'path': p, 'name': name, 'base': base})

    print("==================================================================")
    print(f"⚔️ [TIẾN TRÌNH BATCH OCR C++]")
    print(f"🎯 Model triệu hồi:  {model_name}")
    print(f"📦 Kích thước đợt:   {batch_size} ảnh / 1 request")
    print(f"⏳ Thời gian hồi chiêu: {cooldown_seconds}s (tính từ lúc mẻ làm xong)")
    print(f"🖼️ Tổng số ảnh tìm thấy:  {len(all_image_paths)}")
    if skipped_count > 0:
        print(f"⏩ Đã bỏ qua (đã có code): {skipped_count} ảnh")
    print(f"🔥 Số ảnh cần càn quét:   {len(pending_images)} ảnh")
    print("==================================================================\n")

    if not pending_images:
        print("🎉 Toàn bộ ảnh đã được trích xuất thành file .cpp từ trước! Không cần làm gì thêm!")
        return

    api_key = get_api_key()

    # 2. Chia các ảnh cần làm thành từng mẻ (Batches)
    batches = [pending_images[i:i + batch_size] for i in range(0, len(pending_images), batch_size)]
    total_batches = len(batches)
    total_success = skipped_count

    for b_idx, batch in enumerate(batches, start=1):
        names_str = ", ".join([item['name'] for item in batch])
        print(f"🚀 [Đợt {b_idx}/{total_batches}] Đang gửi {len(batch)} ảnh ({names_str})...", flush=True)

        batch_results = process_batch_images(api_key, batch, model_name=model_name)

        # Lưu kết quả trả về
        saved_in_batch = 0
        result_map = {res.get('filename', '').strip(): res.get('code', '') for res in batch_results if isinstance(res, dict)}

        for item in batch:
            # Tìm code tương ứng theo tên file hoặc tên gốc
            code = result_map.get(item['name'])
            if not code:
                # Tìm kiếm tương đối nếu model trả về hơi khác tên mở rộng
                for k, v in result_map.items():
                    if item['base'] in k:
                        code = v
                        break

            out_cpp_path = os.path.join(output_path, f"{item['base']}.cpp")
            if code and len(code.strip()) > 0:
                clean_code = clean_code_block(code)
                with open(out_cpp_path, 'w', encoding='utf-8') as f:
                    f.write(clean_code + "\n")
                saved_in_batch += 1
                total_success += 1
            else:
                print(f"   ⚠️ Không lấy được code của ảnh: {item['name']}")

        print(f"   ✅ [Đợt {b_idx}/{total_batches}] Hoàn tất! Đã lưu {saved_in_batch}/{len(batch)} file .cpp")

        # Thời gian hồi chiêu: đúng 3s tính từ lúc hoàn thành mẻ (nếu chưa phải mẻ cuối)
        if b_idx < total_batches and cooldown_seconds > 0:
            print(f"   ⏳ Tạm dừng {cooldown_seconds}s chống quá tải API...\n")
            time.sleep(cooldown_seconds)

    print("\n==================================================================")
    print(f"🎉 TẤT CẢ CÁC ĐỢT ĐÃ HOÀN TẤT! Tổng cộng: {total_success}/{len(all_image_paths)} file .cpp.")
    print(f"📂 Thư mục xuất mã nguồn: {output_path}")
    print("==================================================================")


if __name__ == "__main__":
    run_multi_batch_ocr(
        input_dir="input_images",
        output_dir="extracted_cpp",
        batch_size=10,             # 10 ảnh cùng lúc
        cooldown_seconds=3.0,       # 3 giây tính từ lúc làm xong
        model_name="gemini-3.1-flash-lite"  # Model tối ưu hạn mức 15 RPM / 500 RPD
    )
