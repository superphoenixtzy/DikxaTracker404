from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re

PORT = 8081
BASE = Path(__file__).resolve().parent
UPLOAD_DIR = BASE / "DikxaTracker"
HTML_DIR = BASE / "html"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
HTML_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED = {".jpg", ".jpeg", ".png", ".webp"}

def next_filename(ext):
    n = 1
    while True:
        p = UPLOAD_DIR / f"foto_{n:03d}{ext}"
        if not p.exists(): return p
        n += 1

def parse_multipart(body, content_type):
    m = re.search(r'boundary=(?:"([^"]+)"|([^;]+))', content_type)
    if not m: raise ValueError("Boundary multipart tidak ditemukan")
    boundary = (m.group(1) or m.group(2)).encode()
    for part in body.split(b"--" + boundary):
        if not part or part in (b"--", b"--\r\n"): continue
        if part.startswith(b"\r\n"): part = part[2:]
        if part.endswith(b"\r\n"): part = part[:-2]
        pos = part.find(b"\r\n\r\n")
        if pos < 0: continue
        headers = part[:pos].decode("utf-8", "replace")
        data = part[pos+4:]
        if 'name="file"' not in headers: continue
        fm = re.search(r'filename="([^"]*)"', headers)
        return (fm.group(1) if fm else ""), data
    return None, None

class Handler(BaseHTTPRequestHandler):
    def reply(self, code, msg):
        data = msg.encode()
        self.send_response(code)
        self.send_header("Content-Type","text/plain; charset=utf-8")
        self.send_header("Content-Length",str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/","/index.html"):
            p = HTML_DIR/"index.html"
            if not p.exists(): return self.reply(404,"index.html belum ada")
            data=p.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length",str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.reply(404,"Not Found")

    def do_POST(self):
        if self.path != "/upload": return self.reply(404,"Endpoint tidak ditemukan")
        try:
            length=int(self.headers.get("Content-Length","0"))
            if length <= 0: return self.reply(400,"File kosong")
            if length > 20*1024*1024: return self.reply(413,"Maksimal 20 MB")
            ct=self.headers.get("Content-Type","")
            if not ct.startswith("multipart/form-data"):
                return self.reply(400,"Gunakan multipart/form-data")
            filename,data=parse_multipart(self.rfile.read(length),ct)
            if not filename or data is None: return self.reply(400,'Field "file" tidak ditemukan')
            ext=Path(filename).suffix.lower()
            if ext not in ALLOWED: return self.reply(400,"Format: JPG, JPEG, PNG, WEBP")
            target=next_filename(ext)
            target.write_bytes(data)
            print(f"[+] Upload berhasil: {target.name}")
            self.reply(200,f"Upload berhasil: {target.name}")
        except Exception as e:
            print("[!] Error:",e)
            self.reply(500,"Upload gagal")

print("DIKXA CYBER PRODUCT UPLOAD")
print(f"Server: http://127.0.0.1:{PORT}")
print(f"Folder: {UPLOAD_DIR}")
ThreadingHTTPServer(("0.0.0.0",PORT),Handler).serve_forever()
