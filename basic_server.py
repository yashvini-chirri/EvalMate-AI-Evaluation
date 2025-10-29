#!/usr/bin/env python3

import http.server
import socketserver
import os
import sys

# Change to the directory where the webapp files are located
os.chdir('/Users/kathir/EvalMate')

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

PORT = 8000

try:
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 Server running at http://localhost:{PORT}")
        print(f"📱 Open: http://localhost:{PORT}/webapp-simple.html")
        print(f"🔑 Login: admin / admin123")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\n⛔ Server stopped")
except Exception as e:
    print(f"❌ Error: {e}")