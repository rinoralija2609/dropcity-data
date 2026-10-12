"""
JARVIS mit Browser-Oberfläche: animierte Kugel, Spracheingabe und Stimme.
Start:  py jarvis_ui.py   → öffnet http://127.0.0.1:8765 (am besten in Edge oder Chrome)
"""

import json
import queue
import secrets
import threading
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import anthropic
import jarvis

HOST, PORT = "127.0.0.1", 8765  # nur lokal erreichbar – nie auf 0.0.0.0 ändern
TOKEN = secrets.token_urlsafe(24)  # schützt die API vor fremden Webseiten im Browser
PAGE = (Path(__file__).parent / "ui" / "index.html").read_text(encoding="utf-8")


class UiBridge:
    """Verbindet den Agenten mit dem Browser: Ereignisse raus (SSE), Bestätigungen rein."""

    def __init__(self):
        self.clients: list[queue.Queue] = []
        self.pending: dict[str, dict] = {}
        self.lock = threading.Lock()

    def emit(self, event, **data):
        msg = f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
        with self.lock:
            for q in self.clients:
                q.put(msg)

    def confirm(self, action: str) -> bool:
        cid = uuid.uuid4().hex
        entry = {"event": threading.Event(), "ok": False}
        self.pending[cid] = entry
        self.emit("confirm", id=cid, action=action)
        entry["event"].wait(timeout=300)  # ohne Antwort nach 5 Min. gilt: abgelehnt
        self.pending.pop(cid, None)
        return entry["ok"]

    def answer(self, cid: str, ok: bool):
        entry = self.pending.get(cid)
        if entry:
            entry["ok"] = ok
            entry["event"].set()


bridge = UiBridge()
jarvis.ui = bridge
history: list = []
busy = threading.Lock()


def run_task(text: str):
    if not busy.acquire(blocking=False):
        bridge.emit("fail", message="Ich arbeite noch am letzten Auftrag.")
        return
    try:
        bridge.emit("status", state="thinking")
        answer = jarvis.ask_jarvis(history, text)
        bridge.emit("answer", text=answer)
    except jarvis.RefusalError:
        bridge.emit("fail", message="Diese Anfrage wurde vom Modell abgelehnt.")
    except anthropic.RateLimitError:
        bridge.emit("fail", message="Rate-Limit erreicht – bitte kurz warten.")
    except anthropic.APIConnectionError:
        bridge.emit("fail", message="Keine Verbindung zur API.")
    except anthropic.APIStatusError as e:
        bridge.emit("fail", message=f"API-Fehler {e.status_code}: {e.message}")
    except Exception as e:
        bridge.emit("fail", message=f"Fehler: {e}")
    finally:
        busy.release()
        bridge.emit("status", state="idle")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, body=b"", ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            html = PAGE.replace("__TOKEN__", TOKEN).replace("__MODEL__", jarvis.MODEL)
            return self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
        if self.path == f"/events?t={TOKEN}":
            return self._stream()
        self._send(404)

    def _stream(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        q: queue.Queue = queue.Queue()
        with bridge.lock:
            bridge.clients.append(q)
        try:
            while True:
                try:
                    msg = q.get(timeout=15)
                except queue.Empty:
                    msg = ": ping\n\n"  # hält die Verbindung offen
                self.wfile.write(msg.encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        finally:
            with bridge.lock:
                bridge.clients.remove(q)

    def do_POST(self):
        if self.headers.get("X-Token") != TOKEN:
            return self._send(403)
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        if self.path == "/ask":
            text = (body.get("text") or "").strip()
            if text:
                threading.Thread(target=run_task, args=(text,), daemon=True).start()
        elif self.path == "/confirm":
            bridge.answer(body.get("id", ""), bool(body.get("ok")))
        elif self.path == "/reset":
            if busy.locked():
                return self._send(409)
            history.clear()
        else:
            return self._send(404)
        self._send(200, b"{}")


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    jarvis.say(f"J.A.R.V.I.S. Oberfläche läuft auf {url}  ·  Beenden mit Strg+C")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        jarvis.say("Jarvis fährt herunter. Bis bald.")


if __name__ == "__main__":
    main()
