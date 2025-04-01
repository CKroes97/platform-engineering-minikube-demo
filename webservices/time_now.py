from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import json


class TimeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/time':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"time":  datetime.now(datetime.timezone.utc).isoformat()}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


def main():
    server = HTTPServer(('0.0.0.0', 80), TimeHandler)
    print("Server running on port 80...")
    server.serve_forever()


if __name__ == '__main__':
    main()
