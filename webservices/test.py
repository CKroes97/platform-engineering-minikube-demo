from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json

class SimpleAddHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path != '/add':
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
            return

        query = parse_qs(parsed_path.query)
        try:
            a = float(query.get('a', [None])[0])
            b = float(query.get('b', [None])[0])
            result = {'a': a, 'b': b, 'sum': a + b}
            response = json.dumps(result).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(response)
        except (TypeError, ValueError):
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_msg = {'error': 'Please provide valid numeric values for "a" and "b".'}
            self.wfile.write(json.dumps(error_msg).encode('utf-8'))

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleAddHandler)
    print('Serving on port 8000...')
    httpd.serve_forever()