"""
JARVIS – lokaler KI-Assistent (Claude API)
Kann: Dateien lesen/schreiben, Ordner durchsuchen, Befehle ausführen,
Apps & Webseiten öffnen, im Web suchen, Webseiten lesen, Daten analysieren.
Optional mit Sprachsteuerung:  python jarvis.py --voice
"""

import os
import sys
import json
import platform
import subprocess
import webbrowser
import datetime
import re
from pathlib import Path

from dotenv import load_dotenv
import anthropic

load_dotenv()

MODEL = os.getenv("JARVIS_MODEL", "claude-sonnet-5-5")
WORKSPACE = Path(os.getenv("JARVIS_WORKSPACE", Path.home() / "Jarvis")).resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)
AUTO_APPROVE = os.getenv("JARVIS_AUTO_APPROVE", "false").lower() == "true"
MAX_OUTPUT = 12000  # Zeichen pro Tool-Ergebnis
MAX_STEPS = 25      # max. Agent-Schritte pro Auftrag

# Serverseitiger Fallback bei Ablehnungen (stop_reason "refusal") – nur auf der Claude API
# und nur für Modelle, die "fallbacks" unterstützen. Abschalten mit JARVIS_FALLBACK=false.
FALLBACK_MODELS = {"claude-sonnet-5-5", "claude-opus-5-5", "claude-opus-5", "claude-fable-5-1"}
USE_FALLBACK = os.getenv("JARVIS_FALLBACK", "true").lower() == "true" and MODEL in FALLBACK_MODELS

client = anthropic.Anthropic()  # liest ANTHROPIC_API_KEY aus .env

# ---------------------------------------------------------------- Farben
C = {"j": "\033[96m", "t": "\033[93m", "w": "\033[91m", "g": "\033[90m", "x": "\033[0m"}
if platform.system() == "Windows":
    os.system("")  # ANSI-Farben in der Windows-Konsole aktivieren


def say(text, color="j"):
    print(f"{C[color]}{text}{C['x']}")


def confirm(action: str) -> bool:
    if AUTO_APPROVE:
        return True
    say(f"⚠  Jarvis möchte: {action}", "w")
    return input("   Erlauben? [j/N] ").strip().lower() in ("j", "ja", "y", "yes")


def cut(text: str) -> str:
    return text if len(text) <= MAX_OUTPUT else text[:MAX_OUTPUT] + "\n…[gekürzt]"


def resolve(path: str) -> Path:
    p = Path(os.path.expandvars(os.path.expanduser(path)))
    return (p if p.is_absolute() else WORKSPACE / p).resolve()


# ---------------------------------------------------------------- Tools
def run_command(command: str, timeout: int = 60):
    if not confirm(f"Befehl ausführen → {command}"):
        return "Vom Benutzer abgelehnt."
    shell = ["powershell", "-NoProfile", "-Command", command] if platform.system() == "Windows" else ["bash", "-lc", command]
    try:
        r = subprocess.run(shell, capture_output=True, text=True, timeout=timeout, cwd=WORKSPACE,
                           encoding="utf-8", errors="replace")
        return cut(f"Exit-Code {r.returncode}\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}")
    except subprocess.TimeoutExpired:
        return f"Timeout nach {timeout}s."


def read_file(path: str):
    p = resolve(path)
    if not p.exists():
        return f"Datei nicht gefunden: {p}"
    if p.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
            return cut("\n".join(pg.extract_text() or "" for pg in PdfReader(p).pages))
        except ImportError:
            return "Für PDFs bitte 'pip install pypdf' ausführen."
    if p.suffix.lower() in (".xlsx", ".xls", ".csv"):
        try:
            import pandas as pd
            df = pd.read_csv(p) if p.suffix.lower() == ".csv" else pd.read_excel(p)
            return cut(f"Form: {df.shape}\nSpalten: {list(df.columns)}\n\n{df.head(50).to_string()}\n\nStatistik:\n{df.describe(include='all').to_string()}")
        except ImportError:
            return "Für Tabellen bitte 'pip install pandas openpyxl' ausführen."
    return cut(p.read_text(encoding="utf-8", errors="replace"))


def write_file(path: str, content: str):
    p = resolve(path)
    # is_relative_to statt startswith: sonst gilt z.B. "~/Jarvis2" als innerhalb von "~/Jarvis"
    if not p.is_relative_to(WORKSPACE) and not confirm(f"Außerhalb des Workspace schreiben → {p}"):
        return "Vom Benutzer abgelehnt."
    if p.exists() and not confirm(f"Datei überschreiben → {p}"):
        return "Vom Benutzer abgelehnt."
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Gespeichert: {p} ({len(content)} Zeichen)"


def list_directory(path: str = ".", pattern: str = "*"):
    p = resolve(path)
    if not p.is_dir():
        return f"Kein Ordner: {p}"
    items = sorted(p.glob(pattern))[:300]
    lines = [f"{'[DIR] ' if i.is_dir() else '      '}{i.name}  {'' if i.is_dir() else str(i.stat().st_size) + ' B'}" for i in items]
    return f"{p}\n" + "\n".join(lines) if lines else f"{p} ist leer / keine Treffer."


def open_target(target: str):
    if not confirm(f"Öffnen → {target}"):
        return "Vom Benutzer abgelehnt."
    if target.startswith(("http://", "https://")):
        webbrowser.open(target)
        return f"Browser geöffnet: {target}"
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(target) if Path(target).exists() else subprocess.Popen(["cmd", "/c", "start", "", target])
        elif system == "Darwin":
            subprocess.Popen(["open", target] if Path(target).exists() else ["open", "-a", target])
        else:
            subprocess.Popen(["xdg-open", target])
        return f"Geöffnet: {target}"
    except Exception as e:
        return f"Fehler beim Öffnen: {e}"


def fetch_url(url: str):
    import requests
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0 Jarvis"})
        text = re.sub(r"(?is)<(script|style).*?</\1>", "", r.text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return cut(text.strip())
    except Exception as e:
        return f"Fehler: {e}"


def system_info():
    return json.dumps({
        "os": f"{platform.system()} {platform.release()}",
        "python": sys.version.split()[0],
        "zeit": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
        "workspace": str(WORKSPACE),
        "home": str(Path.home()),
    }, ensure_ascii=False)


TOOL_FUNCS = {
    "run_command": run_command, "read_file": read_file, "write_file": write_file,
    "list_directory": list_directory, "open_target": open_target,
    "fetch_url": fetch_url, "system_info": system_info,
}

TOOLS = [
    {"name": "run_command", "description": "Führt einen Shell-Befehl aus (PowerShell unter Windows, bash sonst). Für Python-Skripte, Analysen, Dateioperationen, Systemabfragen.",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}, "timeout": {"type": "integer"}}, "required": ["command"]}},
    {"name": "read_file", "description": "Liest eine Datei (Text, Code, PDF, CSV, Excel). Relative Pfade beziehen sich auf den Workspace.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Erstellt oder überschreibt eine Datei (Texte, Code, Berichte, Skripte).",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"name": "list_directory", "description": "Listet Ordnerinhalt, optional mit Glob-Muster wie '*.pdf' oder '**/*.py'.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "pattern": {"type": "string"}}}},
    {"name": "open_target", "description": "Öffnet eine Webseite, Datei oder Anwendung (z.B. 'notepad', 'excel', 'https://...').",
     "input_schema": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}},
    {"name": "fetch_url", "description": "Lädt den Textinhalt einer Webseite.",
     "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
    {"name": "system_info", "description": "Betriebssystem, Uhrzeit, Workspace-Pfad.",
     "input_schema": {"type": "object", "properties": {}}},
    # serverseitige Websuche (mit dynamischer Filterung; ältere Modelle: web_search_20250305)
    {"type": "web_search_20260209", "name": "web_search", "max_uses": 5},
]

SYSTEM = f"""Du bist JARVIS, ein persönlicher KI-Assistent auf dem PC des Benutzers.
Du handelst selbstständig: plane kurz, nutze deine Tools, prüfe Ergebnisse, korrigiere Fehler und
arbeite weiter, bis die Aufgabe erledigt ist. Erstelle Dateien standardmäßig im Workspace: {WORKSPACE}
Für Analysen schreibst du bei Bedarf Python-Skripte und führst sie aus.
Antworte auf Deutsch, knapp und präzise, im Stil eines souveränen Butlers. Fasse am Ende zusammen, was du getan hast.
Führe nie destruktive Aktionen (Löschen, Formatieren, Registry) ohne ausdrücklichen Auftrag aus."""


# ---------------------------------------------------------------- Sprache (optional)
class Voice:
    def __init__(self):
        import speech_recognition as sr
        import pyttsx3
        self.sr = sr
        self.rec = sr.Recognizer()
        self.tts = pyttsx3.init()
        for v in self.tts.getProperty("voices"):
            if "german" in v.name.lower() or "de" in (v.id or "").lower():
                self.tts.setProperty("voice", v.id)
                break

    def listen(self):
        with self.sr.Microphone() as src:
            say("🎙  Ich höre zu …", "g")
            self.rec.adjust_for_ambient_noise(src, duration=0.5)
            audio = self.rec.listen(src, phrase_time_limit=20)
        try:
            return self.rec.recognize_google(audio, language="de-DE")
        except Exception:
            return ""

    def speak(self, text):
        self.tts.say(re.sub(r"[`*#_>]", "", text)[:600])
        self.tts.runAndWait()


# ---------------------------------------------------------------- Agent-Loop
def call_model(history: list):
    kwargs = dict(
        model=MODEL, max_tokens=16000, system=SYSTEM, tools=TOOLS, messages=history,
        cache_control={"type": "ephemeral"},  # Prompt-Caching: Verlauf wird nicht jedes Mal voll berechnet
    )
    if USE_FALLBACK:
        return client.beta.messages.create(**kwargs, betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    return client.messages.create(**kwargs)


def add_user_text(history: list, text: str):
    # Endete der letzte Auftrag am Schrittlimit, steht am Ende schon eine User-Nachricht
    # (Tool-Ergebnisse) – dann den Text dort anhängen statt zwei User-Nachrichten hintereinander.
    if history and history[-1]["role"] == "user" and isinstance(history[-1]["content"], list):
        history[-1]["content"].append({"type": "text", "text": text})
    else:
        history.append({"role": "user", "content": text})


def ask_jarvis(history: list, user_text: str) -> str:
    start = len(history)
    try:
        return _agent_loop(history, user_text)
    except BaseException:
        # Abbruch (Strg+C, API-Fehler) mitten im Auftrag: Verlauf auf den Stand davor zurücksetzen,
        # sonst bleibt ein tool_use ohne tool_result stehen und jede weitere Anfrage scheitert.
        del history[start:]
        if history and history[-1]["role"] == "user" and isinstance(history[-1]["content"], list):
            history[-1]["content"] = [b for b in history[-1]["content"] if b.get("type") == "tool_result"]
        raise


def _agent_loop(history: list, user_text: str) -> str:
    add_user_text(history, user_text)
    final_text = ""
    for _ in range(MAX_STEPS):
        resp = call_model(history)

        if resp.stop_reason == "refusal":
            say("Diese Anfrage wurde vom Modell abgelehnt.", "w")
            raise RefusalError()

        history.append({"role": "assistant", "content": resp.content})

        tool_results = []
        for block in resp.content:
            if block.type == "text" and block.text.strip():
                final_text = block.text
                say(f"\nJARVIS: {block.text}")
            elif block.type == "server_tool_use":
                say(f"  🌐 Websuche: {block.input.get('query', '')}", "g")
            elif block.type == "tool_use":
                say(f"  ⚙  {block.name}({json.dumps(block.input, ensure_ascii=False)[:150]})", "t")
                is_error = False
                try:
                    result = TOOL_FUNCS[block.name](**block.input)
                except Exception as e:
                    result, is_error = f"Fehler: {e}", True
                tool_results.append({"type": "tool_result", "tool_use_id": block.id,
                                     "content": str(result), "is_error": is_error})

        if resp.stop_reason == "max_tokens":
            say("  (Antwort wurde wegen Längenlimit abgeschnitten)", "g")

        if tool_results:
            history.append({"role": "user", "content": tool_results})
        elif resp.stop_reason != "pause_turn":  # pause_turn: Websuche läuft noch → gleiche Anfrage fortsetzen
            break
    else:
        say(f"  (Schrittlimit von {MAX_STEPS} erreicht – sag 'weiter', um fortzufahren)", "g")
    return final_text


class RefusalError(Exception):
    pass


def main():
    use_voice = "--voice" in sys.argv
    voice = Voice() if use_voice else None
    history = []
    say("=" * 55)
    say(f"  J.A.R.V.I.S. online  ·  Modell: {MODEL}")
    say(f"  Workspace: {WORKSPACE}")
    say("  'exit' beenden · 'reset' neues Gespräch · Strg+C bricht Auftrag ab")
    say("=" * 55)
    if voice:
        voice.speak("Jarvis ist online. Wie kann ich helfen?")

    while True:
        try:
            text = voice.listen() if voice else input(f"\n{C['g']}Du:{C['x']} ")
            if voice:
                say(f"Du: {text}", "g")
        except (KeyboardInterrupt, EOFError):
            break
        text = (text or "").strip()
        if not text:
            continue
        if text.lower() in ("exit", "quit", "beenden"):
            break
        if text.lower() == "reset":
            history.clear()
            say("Gespräch zurückgesetzt.")
            continue
        try:
            answer = ask_jarvis(history, text)
            if voice and answer:
                voice.speak(answer)
        except KeyboardInterrupt:
            say("\nAuftrag abgebrochen.", "w")
        except RefusalError:
            pass
        except anthropic.RateLimitError:
            say("Rate-Limit erreicht – bitte kurz warten und erneut versuchen.", "w")
        except anthropic.APIConnectionError as e:
            say(f"Keine Verbindung zur API: {e}", "w")
        except anthropic.APIStatusError as e:
            say(f"API-Fehler {e.status_code}: {e.message}", "w")
    say("Jarvis fährt herunter. Bis bald.")


if __name__ == "__main__":
    main()
