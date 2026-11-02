#!/usr/bin/env python3
"""
Lightweight Web Server for Huffman Coding Interactive Studio.
Serves the local directory and opens index.html in the default web browser.

Usage:
    python server.py [--port 8000] [--no-browser]
"""

import sys
import os
import argparse
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler


class QuietHandler(SimpleHTTPRequestHandler):
    """Clean HTTP request handler with custom logging format."""
    def log_message(self, format, *args):
        # Format clean console logs
        sys.stdout.write(f"[HTTP {self.log_date_time_string()}] {args[0]} {args[1]}\n")
        sys.stdout.flush()


def run_server(port: int = 8000, open_browser: bool = True):
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)

    server_address = ("", port)
    try:
        httpd = HTTPServer(server_address, QuietHandler)
    except OSError as e:
        print(f"[ERROR] Could not bind to port {port}: {e}")
        print(f"[RETRY] Trying port {port + 1}...")
        port += 1
        server_address = ("", port)
        httpd = HTTPServer(server_address, QuietHandler)

    url = f"http://localhost:{port}/index.html"
    print("=" * 65)
    print(" HUFFMAN CODING INTERACTIVE DAA DASHBOARD")
    print("=" * 65)
    print(f" Web Studio running at: {url}")
    print(f" Serving root directory: {web_dir}")
    print(" Press Ctrl+C in this terminal to stop the server.")
    print("=" * 65)

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server gracefully stopped.")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run local Huffman visualizer web server")
    parser.add_argument("--port", type=int, default=8000, help="Port to serve on (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not auto-open browser")
    args = parser.parse_args()

    run_server(port=args.port, open_browser=not args.no_browser)
