"""
Outlook-Anbindung für JARVIS über Microsoft Graph (E-Mails + Kalender).
Anmeldung einmalig per Code im Browser (Device-Code-Flow); danach bleibt Jarvis angemeldet.
"""

import json
import os
import datetime
import webbrowser
from pathlib import Path

import requests

GRAPH = "https://graph.microsoft.com/v1.0"
SCOPES = ["User.Read", "Mail.ReadWrite", "Mail.Send", "Calendars.ReadWrite"]
CACHE_FILE = Path.home() / ".jarvis_outlook_token.json"  # Anmelde-Token, bleibt nur auf diesem PC
TIMEZONE = os.getenv("JARVIS_TIMEZONE", "W. Europe Standard Time")

_say = print
_confirm = lambda action, always=False: False
_cut = lambda t: t
_app = None
_cache = None


def setup(client_id: str, say, confirm, cut):
    """Wird von jarvis.py aufgerufen; gibt False zurück, wenn msal fehlt."""
    global _app, _cache, _say, _confirm, _cut
    try:
        import msal
    except ImportError:
        say("Für Outlook bitte 'py -m pip install msal' ausführen – Outlook-Funktionen sind aus.", "w")
        return False
    _say, _confirm, _cut = say, confirm, cut
    _cache = msal.SerializableTokenCache()
    if CACHE_FILE.exists():
        _cache.deserialize(CACHE_FILE.read_text(encoding="utf-8"))
    _app = msal.PublicClientApplication(client_id, authority="https://login.microsoftonline.com/common",
                                        token_cache=_cache)
    return True


def _token() -> str:
    accounts = _app.get_accounts()
    result = _app.acquire_token_silent(SCOPES, account=accounts[0]) if accounts else None
    if not result:
        flow = _app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            raise RuntimeError(f"Outlook-Anmeldung fehlgeschlagen: {flow.get('error_description', flow)}")
        _say(f"🔑 Outlook-Anmeldung: Öffne {flow['verification_uri']} und gib den Code {flow['user_code']} ein.", "w")
        webbrowser.open(flow["verification_uri"])
        result = _app.acquire_token_by_device_flow(flow)  # wartet, bis du dich angemeldet hast
    if "access_token" not in result:
        raise RuntimeError(f"Outlook-Anmeldung fehlgeschlagen: {result.get('error_description', result)}")
    if _cache.has_state_changed:
        CACHE_FILE.write_text(_cache.serialize(), encoding="utf-8")
    return result["access_token"]


def _graph(method: str, path: str, body=None, params=None, headers=None):
    h = {"Authorization": f"Bearer {_token()}", **(headers or {})}
    r = requests.request(method, GRAPH + path, json=body, params=params, headers=h, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Outlook-Fehler {r.status_code}: {r.text[:300]}")
    return r.json() if r.content else {}


def _sender(m) -> str:
    a = (m.get("from") or {}).get("emailAddress", {})
    return f"{a.get('name', '')} <{a.get('address', '')}>"


# ---------------------------------------------------------------- E-Mail
def mail_list(folder: str = "inbox", search: str = "", unread_only: bool = False, count: int = 15):
    params = {"$top": min(int(count), 50), "$select": "id,subject,from,receivedDateTime,isRead,bodyPreview"}
    if search:
        params["$search"] = f'"{search}"'  # $search lässt keine Sortierung zu – Graph sortiert nach Relevanz/Datum
    elif unread_only:
        params["$filter"] = "receivedDateTime ge 1900-01-01T00:00:00Z and isRead eq false"
        params["$orderby"] = "receivedDateTime desc"
    else:
        params["$orderby"] = "receivedDateTime desc"
    msgs = _graph("GET", f"/me/mailFolders/{folder}/messages", params=params).get("value", [])
    if not msgs:
        return "Keine E-Mails gefunden."
    lines = [f"{'●' if not m['isRead'] else ' '} {m['receivedDateTime'][:16].replace('T', ' ')} | {_sender(m)} | "
             f"{m.get('subject') or '(kein Betreff)'}\n    {(m.get('bodyPreview') or '')[:140]}\n    id: {m['id']}"
             for m in msgs]
    return _cut("● = ungelesen\n" + "\n".join(lines))


def mail_read(message_id: str):
    m = _graph("GET", f"/me/messages/{message_id}",
               params={"$select": "subject,from,toRecipients,ccRecipients,receivedDateTime,body"},
               headers={"Prefer": 'outlook.body-content-type="text"'})
    to = ", ".join(r["emailAddress"]["address"] for r in m.get("toRecipients", []))
    return _cut(f"Von: {_sender(m)}\nAn: {to}\nDatum: {m['receivedDateTime']}\nBetreff: {m.get('subject')}\n\n"
                f"{m.get('body', {}).get('content', '')}")


def mail_draft(body: str, to: str = "", subject: str = "", reply_to_id: str = ""):
    if reply_to_id:
        d = _graph("POST", f"/me/messages/{reply_to_id}/createReply", body={"comment": body})
    else:
        recipients = [{"emailAddress": {"address": a.strip()}} for a in to.split(",") if a.strip()]
        d = _graph("POST", "/me/messages", body={"subject": subject, "toRecipients": recipients,
                                                 "body": {"contentType": "Text", "content": body}})
    return f"Entwurf gespeichert (Outlook → Entwürfe). draft_id: {d['id']}"


def mail_send(draft_id: str):
    d = _graph("GET", f"/me/messages/{draft_id}", params={"$select": "subject,toRecipients,isDraft"})
    if not d.get("isDraft"):
        return "Das ist kein Entwurf – gesendet werden nur Entwürfe."
    to = ", ".join(r["emailAddress"]["address"] for r in d.get("toRecipients", [])) or "(kein Empfänger)"
    # Senden immer bestätigen lassen – auch mit JARVIS_AUTO_APPROVE (E-Mails können Anweisungen enthalten)
    if not _confirm(f"E-Mail SENDEN an {to} – Betreff: {d.get('subject')}", always=True):
        return "Vom Benutzer abgelehnt – der Entwurf bleibt in Outlook gespeichert."
    _graph("POST", f"/me/messages/{draft_id}/send")
    return f"Gesendet an {to}."


# ---------------------------------------------------------------- Kalender
def calendar_list(days: int = 7, start: str = ""):
    begin = datetime.datetime.fromisoformat(start) if start else datetime.datetime.now()
    begin = begin.astimezone()
    end = begin + datetime.timedelta(days=int(days))
    events = _graph("GET", "/me/calendarView",
                    params={"startDateTime": begin.isoformat(), "endDateTime": end.isoformat(),
                            "$orderby": "start/dateTime", "$top": 100,
                            "$select": "subject,start,end,location,isAllDay"},
                    headers={"Prefer": f'outlook.timezone="{TIMEZONE}"'}).get("value", [])
    if not events:
        return f"Keine Termine zwischen {begin:%d.%m.} und {end:%d.%m.%Y}."
    lines = []
    for e in events:
        s, t = e["start"]["dateTime"][:16].replace("T", " "), e["end"]["dateTime"][11:16]
        when = f"{s[:10]} ganztägig" if e.get("isAllDay") else f"{s}–{t}"
        loc = (e.get("location") or {}).get("displayName")
        lines.append(f"{when} | {e.get('subject')}" + (f" | 📍 {loc}" if loc else ""))
    return "\n".join(lines)


def calendar_create(subject: str, start: str, end: str, location: str = "", notes: str = ""):
    if not _confirm(f"Termin eintragen → {subject} ({start} bis {end})"):
        return "Vom Benutzer abgelehnt."
    ev = {"subject": subject, "start": {"dateTime": start, "timeZone": TIMEZONE},
          "end": {"dateTime": end, "timeZone": TIMEZONE}}
    if location:
        ev["location"] = {"displayName": location}
    if notes:
        ev["body"] = {"contentType": "Text", "content": notes}
    _graph("POST", "/me/events", body=ev)
    return f"Termin eingetragen: {subject}, {start}"


FUNCS = {"mail_list": mail_list, "mail_read": mail_read, "mail_draft": mail_draft, "mail_send": mail_send,
         "calendar_list": calendar_list, "calendar_create": calendar_create}

TOOLS = [
    {"name": "mail_list", "description": "Listet E-Mails aus Outlook (neueste zuerst). folder: 'inbox', 'sentitems', 'drafts', 'archive'. search: Suchbegriff (Absender, Betreff, Inhalt). unread_only: nur ungelesene.",
     "input_schema": {"type": "object", "properties": {"folder": {"type": "string"}, "search": {"type": "string"},
                      "unread_only": {"type": "boolean"}, "count": {"type": "integer"}}}},
    {"name": "mail_read", "description": "Liest eine E-Mail vollständig (id aus mail_list).",
     "input_schema": {"type": "object", "properties": {"message_id": {"type": "string"}}, "required": ["message_id"]}},
    {"name": "mail_draft", "description": "Speichert einen E-Mail-Entwurf in Outlook (sendet NICHT). Für Antworten reply_to_id setzen, sonst to (Komma-getrennt) und subject.",
     "input_schema": {"type": "object", "properties": {"body": {"type": "string"}, "to": {"type": "string"},
                      "subject": {"type": "string"}, "reply_to_id": {"type": "string"}}, "required": ["body"]}},
    {"name": "mail_send", "description": "Sendet einen zuvor erstellten Entwurf. Nur verwenden, wenn der Benutzer ausdrücklich senden möchte; er muss zusätzlich bestätigen.",
     "input_schema": {"type": "object", "properties": {"draft_id": {"type": "string"}}, "required": ["draft_id"]}},
    {"name": "calendar_list", "description": "Zeigt Outlook-Termine ab start (ISO-Datum, Standard: jetzt) für days Tage.",
     "input_schema": {"type": "object", "properties": {"days": {"type": "integer"}, "start": {"type": "string"}}}},
    {"name": "calendar_create", "description": "Trägt einen Termin in den Outlook-Kalender ein. start/end als lokale Zeit 'JJJJ-MM-TTTHH:MM'.",
     "input_schema": {"type": "object", "properties": {"subject": {"type": "string"}, "start": {"type": "string"},
                      "end": {"type": "string"}, "location": {"type": "string"}, "notes": {"type": "string"}},
                      "required": ["subject", "start", "end"]}},
]
