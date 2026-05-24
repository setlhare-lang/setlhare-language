from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer


class Request:
    def __init__(self, path, method="GET"):
        self.path = path
        self.method = method


class Response:
    def __init__(self, body, status=200, headers=None):
        self.body = str(body)
        self.status = status
        self.headers = headers or {"Content-Type": "text/plain; charset=utf-8"}


def serve(host, port, handler):
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            resp = handler(Request(self.path, "GET"))
            if not isinstance(resp, Response):
                resp = Response(resp)
            self.send_response(resp.status)
            for k, v in resp.headers.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(resp.body.encode("utf-8"))

    server = HTTPServer((host, int(port)), H)
    print(f"Setlhare HTTP listening on http://{host}:{port}")
    server.serve_forever()
