#!/usr/bin/env python3
"""Throwaway local sink: browser pages POST their visible text here."""
import http.server, pathlib, re

OUT = pathlib.Path("/tmp/sink"); OUT.mkdir(exist_ok=True)

class H(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "content-type")
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_POST(self):
        name = re.sub(r"[^a-z0-9_-]", "", self.path.split("name=")[-1])[:60] or "page"
        n = int(self.headers.get("content-length", 0))
        body = self.rfile.read(n)
        (OUT / f"{name}.txt").write_bytes(body)
        self.send_response(200); self._cors(); self.end_headers()
        self.wfile.write(f"saved {name}: {len(body)} bytes".encode())
    def log_message(self, *a): pass

http.server.HTTPServer(("127.0.0.1", 8765), H).serve_forever()
