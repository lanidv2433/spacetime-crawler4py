from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) :
        self.send_response(200)
        self.end_headers()
        # Send HTML content
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Hello Page</title>
        </head>
        <body>
            <h1>Hello</h1>
            <p>This is a simple HTML response.</p>
            <a href="https://www.informatics.uci.edu/">Visit Informatics</a>
        </body>
        </html>
        """
        self.wfile.write(html_content.encode('utf-8'))
                         
def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port = 8090) :
    server_address = ('', port)
    httpd = server_class (server_address, handler_class)
    print(f"Starting server on port {port}..")
    httpd.serve_forever()
    print ("Crawler connected to server.")
if __name__ == '__main__':
    run()
