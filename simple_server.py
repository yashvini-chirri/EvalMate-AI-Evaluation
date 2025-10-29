#!/usr/bin/env python3

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import sqlite3
import hashlib
import random
from datetime import datetime

# Add the current directory to Python path
sys.path.append('/Users/kathir/EvalMate')
sys.path.append('/Users/kathir/EvalMate/backend')

class EvalMateHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the base directory to serve files from
        super().__init__(*args, directory='/Users/kathir/EvalMate', **kwargs)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        # Add CORS headers
        def add_cors_headers():
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        
        if path == '/webapp-simple.html':
            try:
                with open('/Users/kathir/EvalMate/webapp-simple.html', 'r') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                add_cors_headers()
                self.end_headers()
                self.wfile.write(content.encode())
                return
            except:
                pass
        
        elif path == '/api/students/':
            query = parse_qs(urlparse(self.path).query)
            standard = query.get('standard', [''])[0]
            section = query.get('section', [''])[0]
            
            # Generate mock students
            students = []
            names = ["Rahul", "Priya", "Aarav", "Anita", "Arjun", "Kavya", "Ravi", "Sneha", 
                    "Vikram", "Meera", "Suresh", "Divya", "Kiran", "Pooja", "Manoj", "Lakshmi",
                    "Rajesh", "Deepika", "Amit", "Sita"]
            
            for i in range(20):  # 20 students per section
                roll_num = i + 1
                students.append({
                    "id": i + 1,
                    "username": f"student_{standard.lower()}_{section.lower()}_{roll_num:02d}",
                    "name": f"{names[i]} {standard}{section}",
                    "first_name": names[i],
                    "last_name": f"{standard}{section}",
                    "email": f"student_{standard.lower()}_{section.lower()}_{roll_num:02d}@evalmate.edu",
                    "standard": standard,
                    "section": section,
                    "roll_number": roll_num
                })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            add_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(students).encode())
            return
        
        elif path == '/api/tests/':
            # Return empty list for tests initially
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            add_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps([]).encode())
            return
        
        # Default behavior for other files
        super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        
        def add_cors_headers():
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        
        if path == '/api/auth/login/examiner':
            # Simple login check
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Parse form data
            params = parse_qs(post_data)
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]
            
            if username == 'admin' and password == 'admin123':
                token = "mock_admin_token_12345"
                response = {
                    "access_token": token,
                    "token_type": "bearer",
                    "user_type": "examiner"
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                add_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                add_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"detail": "Invalid credentials"}).encode())
            return
        
        elif path == '/api/tests/':
            # Mock test creation
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            add_cors_headers()
            self.end_headers()
            response = {
                "id": random.randint(1, 1000),
                "message": "Test created successfully",
                "name": "Test Created"
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        elif path == '/api/evaluations/evaluate':
            # Mock evaluation
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            add_cors_headers()
            self.end_headers()
            
            # Generate random evaluation result
            obtained_marks = random.randint(60, 95)
            total_marks = 100
            percentage = (obtained_marks / total_marks) * 100
            
            if percentage >= 90:
                grade = "A+"
            elif percentage >= 80:
                grade = "A"
            elif percentage >= 70:
                grade = "B"
            elif percentage >= 60:
                grade = "C"
            else:
                grade = "D"
            
            response = {
                "message": "Answer sheet evaluated successfully",
                "evaluation_id": random.randint(1, 1000),
                "total_score": f"{obtained_marks}/{total_marks}",
                "percentage": f"{percentage:.1f}%",
                "grade": grade,
                "questions_evaluated": "5",
                "status": "completed"
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Default response for other POST requests
        self.send_response(404)
        add_cors_headers()
        self.end_headers()

def run_server():
    """Run the simple HTTP server"""
    server_address = ('0.0.0.0', 8000)
    httpd = HTTPServer(server_address, EvalMateHandler)
    print(f"🚀 EvalMate Simple Server running on http://localhost:8000")
    print(f"📱 Open: http://localhost:8000/webapp-simple.html")
    print(f"🔑 Login: admin / admin123")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⛔ Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()