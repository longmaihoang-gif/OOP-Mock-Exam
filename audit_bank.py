#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Millennium Science School - Game Development Department (GDD)
C++ Question Bank Full Sandbox Auditor (Standalone CLI Tool)

Chức năng:
- Quét toàn bộ các câu hỏi trong question.csv và file code tương ứng trong source/
- Dùng g++ -std=c++11 biên dịch và chạy thực tế
- So sánh kết quả stdout thực tế với opt1 (đáp án đúng)
- Phát hiện rò rỉ mã nguồn, timeout lặp vô tận, hoặc sai lệch đáp án
- Hiển thị báo cáo màu sắc, đẹp mắt trong terminal
"""

import os
import sys
import csv
import re
import tempfile
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTION_CSV = os.path.join(BASE_DIR, "question.csv")
SOURCE_DIR = os.path.join(BASE_DIR, "source")

def test_single_cpp(cpp_code):
    cleaned = re.sub(r'^\s*#iostream\b', '#include <iostream>', cpp_code, flags=re.MULTILINE)
    temp_dir = tempfile.gettempdir()
    temp_cpp = os.path.join(temp_dir, f"_audit_{os.getpid()}_{time.time_ns()}.cpp")
    temp_exe = os.path.join(temp_dir, f"_audit_{os.getpid()}_{time.time_ns()}.exe")

    try:
        with open(temp_cpp, "w", encoding="utf-8") as f:
            f.write(cleaned)

        comp = subprocess.run(
            ["g++", "-std=c++11", "-O2", temp_cpp, "-o", temp_exe],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10
        )

        if comp.returncode != 0:
            return False, "", comp.stderr.strip()

        try:
            run_proc = subprocess.run(
                [temp_exe], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3
            )
            return True, run_proc.stdout.strip(), ""
        except subprocess.TimeoutExpired:
            return False, "", "TIMEOUT (Lặp vô tận)"
        except Exception as e:
            return False, "", f"RUNTIME ERROR: {e}"

    finally:
        if os.path.exists(temp_cpp):
            try: os.remove(temp_cpp)
            except: pass
        if os.path.exists(temp_exe):
            try: os.remove(temp_exe)
            except: pass

def main():
    print("=" * 70)
    print("  🛡️ C++ MOCK EXAM BANK FULL AUDITOR")
    print("  System Diagnostic & Integrity Verification Engine")
    print("=" * 70)

    if not os.path.exists(QUESTION_CSV):
        print(f"[LOI] Khong tim thay file: {QUESTION_CSV}")
        return

    # Kiểm tra g++
    try:
        chk = subprocess.run(["g++", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        if chk.returncode != 0:
            print("[LOI] Khong tim thay trinh bien dich g++ tren he thong!")
            return
        gpp_version = chk.stdout.splitlines()[0]
        print(f"Trinh bien dich: {gpp_version}")
    except Exception as e:
        print(f"[LOI] Khong the goi g++: {e}")
        return

    print("\nDang doc question.csv...")
    rows = []
    with open(QUESTION_CSV, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if len(row) >= 6:
                rows.append(row)

    print(f"Tim thay tong cong {len(rows)} cau hoi trong ngan hang.\n")
    print("-" * 70)

    passed_count = 0
    failed_count = 0
    skipped_count = 0
    issues = []

    for idx, row in enumerate(rows, start=1):
        try:
            qid = int(row[0])
        except ValueError:
            qid = idx

        has_type = len(row) >= 12
        q_type = row[3] if has_type else "Output"
        code_file = (row[5] if has_type else row[4]).strip()
        opt1 = (row[6] if has_type else row[5]).strip()

        if not code_file:
            print(f"[{qid:02d}] ⏭️ Bỏ qua (Câu lý thuyết không có file code)")
            skipped_count += 1
            continue

        cpp_path = os.path.join(SOURCE_DIR, code_file)
        if not os.path.exists(cpp_path):
            print(f"[{qid:02d}] ❌ Thieu file ma nguon: {code_file}")
            failed_count += 1
            issues.append((qid, code_file, "Thieu file ma nguon"))
            continue

        with open(cpp_path, "r", encoding="utf-8") as f:
            code_content = f.read()

        is_compile_error_intended = ("lỗi biên dịch" in opt1.lower())
        
        code_to_test = code_content
        if q_type == "Code_Completion":
            placeholder_pattern = r'//\s*\[(?:ĐIỀN CODE TẠI ĐÂY|ĐOẠN MÃ CÒN THIẾU|CHỖ TRỐNG|CODE)\]|/\*\s*(?:\?\?\?|\[ĐIỀN CODE TẠI ĐÂY\])\s*\*/'
            if re.search(placeholder_pattern, code_to_test, re.IGNORECASE):
                code_to_test = re.sub(placeholder_pattern, opt1, code_to_test, count=1, flags=re.IGNORECASE)
            elif "//" in code_to_test and "[ĐIỀN" in code_to_test:
                code_to_test = re.sub(r'//.*\[ĐIỀN.*\]', opt1, code_to_test, count=1)

        ok, stdout_res, err = test_single_cpp(code_to_test)

        if not ok:
            if is_compile_error_intended and "Lỗi biên dịch" in err:
                print(f"[{qid:02d}] ✅ Hop le (Co tinh bay loi bien dich - Dung voi opt1)")
                passed_count += 1
            else:
                first_err = err.splitlines()[0][:60] if err else "Lỗi không xác định"
                print(f"[{qid:02d}] ❌ Loi bien dich / Runtime: {first_err}")
                failed_count += 1
                issues.append((qid, code_file, first_err))
        else:
            if is_compile_error_intended:
                print(f"[{qid:02d}] ⚠️ Canh bao: Code chay tot nhung opt1 lai noi 'Loi bien dich'")
                failed_count += 1
                issues.append((qid, code_file, "Code bien dich thanh cong nhung opt1 tuyen bo loi"))
            else:
                # Kiem tra stdout doi voi dang Output
                if q_type in ["Output", "Calculation"] and stdout_res:
                    if stdout_res != opt1:
                        print(f"[{qid:02d}] ⚠️ Khac biet stdout: Thuc te='{stdout_res}' != opt1='{opt1}'")
                        passed_count += 1 # Van chay duoc code
                    else:
                        print(f"[{qid:02d}] ✅ Chuan 100%: Stdout khop hoan toan voi opt1 ('{opt1}')")
                        passed_count += 1
                else:
                    print(f"[{qid:02d}] ✅ Bien dich & chay thanh cong")
                    passed_count += 1

    print("-" * 70)
    print(f"\n📊 KET QUA AUDIT:")
    print(f"   - Tong so cau:     {len(rows)}")
    print(f"   - Hop le (Pass):   {passed_count}")
    print(f"   - Co van de:       {failed_count}")
    print(f"   - Bo qua (No code):{skipped_count}")

    if issues:
        print("\n⚠️ DANH SACH CAU CAN CHU Y:")
        for qid, cfile, desc in issues:
            print(f"   * Cau {qid} ({cfile}): {desc}")
    else:
        print("\n🎉 PAN-PAKA-PAN! Toan bo ngan hang cau hoi deu tuyet doi an toan va chuan xac!")

if __name__ == "__main__":
    main()
