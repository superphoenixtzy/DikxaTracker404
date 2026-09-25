from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import cgi
from pathlib import Path

PORT = 8081
BASE = Path(__file__).resolve().parent
UPLOAD_DIR = BASE / "DikxaTracker"
HTML_DIR = BASE / "html"

UPLOAD_DIR.mkdir(exist_ok=True)
HTML_DIR.mkdir(exist_ok=True)

ALLOWED = {".jpg", ".jpeg", ".png", ".webp"}

def next_filename(ext):
    n = 1
    while True:
        path = UPLOAD_DIR / f"foto_{n:03d}{ext}"
        if not path.exists():
            return path
        n += 1

class Handler(BaseHTTPRequestHandler):
    def send_text(self, code, text):
        data = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            index = HTML_DIR / "index.html"
            if not index.exists():
                self.send_text(404, "index.html belum dibuat.")
                return
            data = index.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        self.send_text(404, "Not Found")

    def do_POST(self):
        if self.path != "/upload":
            self.send_text(404, "Endpoint tidak ditemukan.")
            return

        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            self.send_text(400, "Gunakan multipart/form-data.")
            return

        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    "REQUEST_METHOD": "POST",
                    "CONTENT_TYPE": content_type,
                    "CONTENT_LENGTH": self.headers.get("Content-Length", "0"),
                },
            )

            if "file" not in form:
                self.send_text(400, "Field upload harus bernama 'file'.")
                return

            item = form["file"]
            filename = item.filename or ""
            ext = Path(filename).suffix.lower()

            if ext not in ALLOWED:
                self.send_text(400, "Format yang didukung: JPG, JPEG, PNG, WEBP.")
                return

            target = next_filename(ext)
            with target.open("wb") as f:
                f.write(item.file.read())

            print(f"[+] Upload: {target.name}")
            self.send_text(200, f"Upload berhasil: {target.name}")

        except Exception as e:
            print(f"[!] Upload error: {e}")
            self.send_text(500, "Upload gagal.")

if __name__ == "__main__":
    print("====================================")
    print("       DIKXA CYBER PRODUCT UPLOAD")
    print("====================================")
    print(f"Server : http://127.0.0.1:{PORT}")
    print(f"Folder : {UPLOAD_DIR}")
    print("CTRL+C untuk berhenti.")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
