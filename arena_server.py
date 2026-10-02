#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDD Exam Arena - Dedicated Local HTTP & Sync Server
Millennium Science School • C++ OOP Division

Cung cấp:
1. Static File Server cho Web App (MockExam.html, MockExam.js, MockExam.css, question.csv, source/*.cpp)
2. REST API đồng bộ kết quả thi đấu (/api/save-exam -> exam_history.json)
3. REST API đồng bộ danh sách câu sai (/api/mistakes -> mistakes.json)
"""

import http.server
import json
import os
import sys
import urllib.parse

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "exam_history.json")
MISTAKES_FILE = os.path.join(BASE_DIR, "mistakes.json")

class ArenaRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        # Thêm CORS headers để tránh lỗi chặn cục bộ
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/mistakes":
            self.handle_get_mistakes()
            return
        elif path == "/api/history":
            self.handle_get_history()
            return

        # Mặc định phục vụ static files
        super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else '{}'

        try:
            data = json.loads(post_body)
        except Exception:
            data = {}

        if path == "/api/save-exam":
            self.handle_save_exam(data)
        elif path == "/api/mistakes":
            self.handle_save_mistakes(data)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Endpoint not found"}')

    def handle_get_mistakes(self):
        mistakes = []
        if os.path.exists(MISTAKES_FILE):
            try:
                with open(MISTAKES_FILE, "r", encoding="utf-8") as f:
                    mistakes = json.load(f)
            except Exception:
                mistakes = []

        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(mistakes, ensure_ascii=False).encode('utf-8'))

    def handle_save_mistakes(self):
        pass  # Signature match, will handle in handle_save_mistakes(data)

    def handle_save_mistakes(self, data):
        # data có thể là list các ID hoặc dict {"mistakes": [...]}
        if isinstance(data, dict):
            new_ids = data.get("mistakes", [])
        elif isinstance(data, list):
            new_ids = data
        else:
            new_ids = []

        # Chuẩn hóa về int và lọc unique
        clean_ids = []
        seen = set()
        for item in new_ids:
            try:
                val = int(item)
                if val not in seen:
                    clean_ids.append(val)
                    seen.add(val)
            except (ValueError, TypeError):
                continue

        with open(MISTAKES_FILE, "w", encoding="utf-8") as f:
            json.dump(clean_ids, f, ensure_ascii=False, indent=2)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success", "count": len(clean_ids)}).encode('utf-8'))

    def handle_get_history(self):
        history = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []

        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(history, ensure_ascii=False).encode('utf-8'))

    def handle_save_exam(self, data):
        if not data:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error": "Empty payload"}')
            return

        history = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []

        # Thêm bài thi mới vào đầu danh sách
        history.insert(0, data)
        # Giữ tối đa 50 trận đấu gần nhất
        if len(history) > 50:
            history = history[:50]

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        # Nếu có danh sách câu sai đi kèm, đồng bộ tự động vào mistakes.json
        failed_ids = data.get("failed_question_ids", [])
        if failed_ids and isinstance(failed_ids, list):
            current_mistakes = []
            if os.path.exists(MISTAKES_FILE):
                try:
                    with open(MISTAKES_FILE, "r", encoding="utf-8") as f:
                        current_mistakes = json.load(f)
                except Exception:
                    current_mistakes = []

            seen = set(current_mistakes)
            for fid in failed_ids:
                try:
                    val = int(fid)
                    if val not in seen:
                        current_mistakes.append(val)
                        seen.add(val)
                except (ValueError, TypeError):
                    continue

            with open(MISTAKES_FILE, "w", encoding="utf-8") as f:
                json.dump(current_mistakes, f, ensure_ascii=False, indent=2)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'{"status": "success", "message": "Exam history synced successfully"}')


def main():
    print("=" * 65)
    print("  💻 HE THONG THI THU TRAC NGHIEM C++ OOP - LOCAL SERVER")
    print(f"  May chu dang lang nghe tai: http://localhost:{PORT}")
    print(f"  Thu muc goc: {BASE_DIR}")
    print("  Ho tro API: /api/save-exam | /api/mistakes | /api/history")
    print("=" * 65)

    server = http.server.ThreadingHTTPServer(('0.0.0.0', PORT), ArenaRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Server] Da tat may chu noi bo.")
        server.server_close()


if __name__ == "__main__":
    main()
