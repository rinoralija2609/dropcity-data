# Einrichtung: einmalig ca. 60–90 Minuten

Alles ist vorbereitet. Du klickst nur noch Konten zusammen und fügst Zugangsdaten ein.
Diese Konten kann ich nicht für dich anlegen, weil sie auf deinen Namen laufen und bezahlt werden müssen.

---

## Schritt 1: n8n-Konto (10 Min.)

**Option A: n8n Cloud (am einfachsten, für den Start empfohlen)**
1. Auf <https://n8n.io> „Get started free“ wählen. Die Testphase ist kostenlos.
2. Nach der Testphase kostet der Starter-Tarif ca. 20–25 €/Monat. Zahle erst, **wenn Kunde 1 unterschrieben hat**.

**Option B: eigener Server (ca. 5 €/Monat, sobald du 2+ Kunden hast)**
1. Bei Hetzner Cloud den kleinsten Server mit Ubuntu anlegen.
2. Per SSH einloggen und ausführen:
   ```bash
   curl -fsSL https://get.docker.com | sh
   docker volume create n8n_data
   docker run -d --restart unless-stopped --name n8n -p 5678:5678 \
     -e GENERIC_TIMEZONE=Europe/Berlin -e TZ=Europe/Berlin \
     -e N8N_SECURE_COOKIE=false \
     -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
   ```
3. Für den echten Betrieb mit Formular brauchst du HTTPS, z. B. eine Domain mit Caddy davor. Das richte ich dir gern ein, sobald es so weit ist.
4. Umzug von Cloud zu eigenem Server: Workflow exportieren und dort importieren, Zugangsdaten neu eintragen. Das dauert etwa 10 Minuten.

## Schritt 2: Anthropic-API-Key (5 Min.)
1. Auf <https://console.anthropic.com> registrieren.
2. Unter **Billing** 5–10 $ Guthaben aufladen. Das reicht für Hunderte Anfragen.
3. Unter **API Keys** auf **Create Key** klicken und den Schlüssel kopieren (beginnt mit `sk-ant-`).

**Kosten pro Anfrage:** Voreingestellt ist `claude-opus-5-5`, das kostet ca. 3–4 Cent pro Anfrage (beide KI-Schritte zusammen).
Günstiger geht es mit `claude-haiku-5-5` (unter 0,5 Cent). Dafür in der **Konfiguration** `modell: 'claude-haiku-5-5'` eintragen. Teste beide mit den Demo-Anfragen und entscheide dann.

## Schritt 3: Telegram-Bot für die Handy-Benachrichtigung (5 Min.)
1. In Telegram **@BotFather** öffnen, `/newbot` senden, einen Namen vergeben (z. B. „Anfragen Mustermann“) und den **Token** kopieren.
2. Den neuen Bot öffnen und **Start** drücken. Das muss später auch der Chef des Betriebs tun.
3. Im Browser diese Seite öffnen (Token einsetzen):
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Dort steht `"chat":{"id":123456789`. **Diese Zahl ist die `telegramChatId`.**

Ohne Telegram geht es auch: Die E-Mail an den Chef kommt trotzdem an.

## Schritt 4: Workflow importieren (5 Min.)
1. In n8n oben rechts auf **⋯** und dann auf **Import from File** klicken.
2. Die Datei `n8n/anfrage-autopilot.json` wählen.
3. Fertig. Du siehst den kompletten Ablauf:
   `E-Mail/Formular → Konfiguration → KI analysiert → KI schreibt Antwort → E-Mail + Telegram`

## Schritt 5: Zugangsdaten eintragen (15 Min.)

| Node | Was eintragen |
|---|---|
| **KI: Anfrage analysieren** | Authentication → *Header Auth* → **Create New** → Name: `x-api-key`, Value: dein `sk-ant-…`-Key |
| **KI: Antwort schreiben** | denselben Header-Auth-Zugang auswählen |
| **E-Mail-Eingang** | **Create New** IMAP-Zugang (siehe Tabelle unten) |
| **E-Mail senden** | **Create New** SMTP-Zugang (siehe Tabelle unten) |
| **Telegram an Chef** | **Create New** → Bot-Token einfügen |

**IMAP- und SMTP-Daten der gängigen Anbieter** (User = E-Mail-Adresse, Passwort = E-Mail-Passwort):

| Anbieter | IMAP (Port 993, SSL) | SMTP (Port 465, SSL) | Hinweis |
|---|---|---|---|
| IONOS (1&1) | `imap.ionos.de` | `smtp.ionos.de` | häufigster Anbieter bei Handwerkern |
| Strato | `imap.strato.de` | `smtp.strato.de` | |
| T-Online | `secureimap.t-online.de` | `securesmtp.t-online.de` | eigenes „E-Mail-Passwort“ im Kundencenter anlegen |
| Gmail | `imap.gmail.com` | `smtp.gmail.com` | 2-Faktor an + **App-Passwort** erzeugen |
| GMX | `imap.gmx.net` | `mail.gmx.net` | IMAP in den GMX-Einstellungen freischalten |
| WEB.DE | `imap.web.de` | `smtp.web.de` (Port 587, SSL aus/STARTTLS) | IMAP in den Einstellungen freischalten |
| Microsoft 365 / Outlook | – | – | IMAP ist meist gesperrt: in n8n stattdessen den Node „Microsoft Outlook Trigger“ verwenden |

**Für deine eigene Demo** nimmst du am besten ein neues, kostenloses Gmail-Konto (z. B. `demo.anfragen.niederbayern@gmail.com`).

## Schritt 6: Konfiguration ausfüllen (10 Min.)
Öffne den Node **Konfiguration** und fülle nur den Block zwischen den `=====`-Linien aus: Firmenname, Leistungen, Pflichtinfos, PLZ-Gebiet, Signatur, E-Mail-Adressen, Telegram-Chat-ID und Modus.
Die Felder sind kommentiert, und die Beispielwerte zeigen das Format.

> **Wichtig:** `inhaberEmail` sollte eine andere Adresse sein als das überwachte Postfach (z. B. die private Adresse des Chefs). Eine eingebaute Sperre verhindert Endlosschleifen zwar auch so, sauberer ist es trotzdem.

## Schritt 7: Testen (10 Min.)
1. Oben auf **Test workflow** klicken.
2. Von einer anderen Adresse eine Anfrage aus `demo/demo-anfragen.md` an das Postfach schicken.
3. Nach etwa 1 Minute sollten der Entwurf per E-Mail und die Telegram-Nachricht ankommen.
4. Wenn alles passt, oben rechts **Active** einschalten. Ab jetzt läuft es rund um die Uhr.

## Schritt 8 (optional): Kontaktformular
1. Im Node **Formular-Eingang** die **Production URL** kopieren.
2. In `formular/kontaktformular.html` die Werte für `WEBHOOK_URL`, `FIRMENNAME`, `LEISTUNGEN` und `DATENSCHUTZ_URL` eintragen.
3. Kostenlos hosten: <https://app.netlify.com/drop> öffnen, die Datei hineinziehen und den Link kopieren.
4. Den Link auf der Website und im Google-Unternehmensprofil des Kunden eintragen („Anfrage senden“).

---

## Neuen Kunden anlegen (danach jedes Mal ca. 20 Min.)
1. Workflow in n8n **duplizieren** und umbenennen in „Autopilot – Firmenname“.
2. Im Node **Formular-Eingang** den Path ändern auf `anfrage-firmenname`. Er muss pro Kunde eindeutig sein.
3. In **Konfiguration** die Kundendaten eintragen.
4. Neue IMAP-, SMTP- und Telegram-Zugänge des Kunden anlegen. Den Anthropic-Key nutzt du für alle Kunden.
5. Testen, dann **Active** einschalten. Die ersten 2 Wochen bleibt `modus: 'entwurf'`.

## Wenn etwas nicht klappt
- **Links auf „Executions“ klicken:** Jeder Durchlauf ist dort Schritt für Schritt einsehbar. Der rote Node zeigt den Fehler.
- `401` bei den KI-Nodes: Der API-Key ist falsch oder es fehlt Guthaben.
- `400` bei den KI-Nodes: In der Konfiguration probeweise `modell: 'claude-haiku-5-5'` eintragen. Bleibt der Fehler, die Meldung aus „Executions“ kopieren und mir schicken.
- Keine E-Mails kommen an: IMAP-Zugang prüfen (Passwort, IMAP freigeschaltet?). Prüfe auch, ob der Absender auf der `ignorieren`-Liste steht.
- Die Antwort klingt nicht passend: In `n8n/src/04-analyse-auswerten.js` den Stil ändern, `node build.js` ausführen und neu importieren. Oder direkt im Node bearbeiten.

## Für Entwickler: Workflow bearbeiten und testen
```bash
cd anfrage-autopilot/n8n
node build.js   # baut anfrage-autopilot.json aus src/*.js
node test.js    # Offline-Tests aller Code-Schritte mit Beispieldaten
```
