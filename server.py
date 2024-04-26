from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html_content = """
        <html>
        <head><title>Hello World!</title></head>
        <body>
        <h1>Hello World!</h1>
        <p>This is a link: <a href="https://ics.uci.edu/">Example Link</a></p>
        </body>
        </html>
        """
        self.wfile.write(html_content.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port = 8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()
    print("Crawler connected to server.")

if __name__ == '__main__':
    run()
