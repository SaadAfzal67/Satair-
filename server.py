import json
import os
import sqlite3
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

PORT = 3000
ROOT_DIR = Path(__file__).resolve().parent
FEEDBACK_DIR = ROOT_DIR / "feedback"
FEEDBACK_FILE = FEEDBACK_DIR / "feedback.txt"
DB_FILE = ROOT_DIR / "parts.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY,
            part_number TEXT UNIQUE,
            name TEXT,
            description TEXT,
            category TEXT,
            image TEXT
        )
    """)

    sample_parts = [
        ("A320-123", "Landing Gear Assembly", "Main landing gear for A320 aircraft", "Landing Gear", "a320-123.jpg"),
        ("B737-456", "Engine Turbine Blade", "High-pressure turbine blade for B737 engines", "Engine Parts", "b737-456.jpg"),
        ("C130-789", "Avionics Panel", "Control panel for C130 avionics systems", "Avionics", "c130-789.jpg"),
        ("F35-101", "Fuselage Skin Panel", "Composite skin panel for F35 fuselage", "Structure", "f35-101.jpg"),
        ("747-202", "Cargo Door Actuator", "Hydraulic actuator for 747 cargo doors", "Hydraulics", "747-202.jpg"),
        ("A380-333", "Wheel Assembly", "Nose wheel assembly for A380", "Wheels", "a380-333.jpg"),
        ("B777-444", "Fuel Pump", "High-pressure fuel pump for B777", "Fuel Systems", "b777-444.jpg"),
        ("C17-555", "Navigation System", "GPS navigation system for C17", "Avionics", "c17-555.jpg"),
        ("F22-666", "Wing Flap", "Adjustable wing flap for F22", "Structure", "f22-666.jpg"),
        ("787-777", "Oxygen Mask", "Passenger oxygen mask system for 787", "Cabin Equipment", "787-777.jpg"),
    ]

    cursor.executemany("INSERT OR IGNORE INTO parts (part_number, name, description, category, image) VALUES (?, ?, ?, ?, ?)", sample_parts)
    conn.commit()
    conn.close()


def search_parts(query: str) -> list:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT part_number, name, description, category, image
        FROM parts
        WHERE part_number LIKE ? OR name LIKE ? OR description LIKE ?
        ORDER BY part_number
        LIMIT 10
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))
    results = cursor.fetchall()
    conn.close()
    return [{"part_number": r[0], "name": r[1], "description": r[2], "category": r[3], "image": r[4]} for r in results]


def get_all_parts(limit=None) -> list:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    query = """
        SELECT part_number, name, description, category, image
        FROM parts
        ORDER BY part_number
    """
    if limit:
        query += f" LIMIT {limit}"
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return [{"part_number": r[0], "name": r[1], "description": r[2], "category": r[3], "image": r[4]} for r in results]


def _format_entry(payload: dict) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    task = payload.get("task") or "(unknown)"
    success = payload.get("success") or "(unknown)"
    comment = payload.get("comment") or "(no comment)"

    return (
        "---\n"
        f"Date: {timestamp}\n"
        f"Task: {task}\n"
        f"Success: {success}\n"
        f"Comment: {comment}\n"
    )


class FeedbackHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/parts"):
            self.handle_parts_search()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/feedback":
            self.handle_feedback_post()
        else:
            self.send_error(404, "Not found")

    def handle_parts_search(self):
        parsed = urlparse(self.path)
        query_params = parse_qs(parsed.query)
        query = query_params.get("q", [""])[0]
        limit = query_params.get("limit", [None])[0]
        limit = int(limit) if limit and limit.isdigit() else None

        results = search_parts(query) if query else get_all_parts(limit)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(results).encode("utf-8"))

    def handle_feedback_post(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")

        try:
            payload = json.loads(body or "{}")
            entry = _format_entry(payload)

            FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
            with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
                f.write(entry)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
        except Exception as exc:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))


def run():
    init_db()
    os.chdir(ROOT_DIR)
    httpd = HTTPServer(("", PORT), FeedbackHandler)
    print(f"Serving on http://localhost:{PORT} (press Ctrl+C to stop)")
    print(f"Feedback will be appended to: {FEEDBACK_FILE}")
    print(f"Parts database: {DB_FILE}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down")
        httpd.server_close()


if __name__ == "__main__":
    run()
