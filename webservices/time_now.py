from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import json


class TimeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/time":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"time": datetime.now(datetime.timezone.utc).isoformat()}
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def main():
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, TimeHandler)
    print("Serving on port 8000...")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
