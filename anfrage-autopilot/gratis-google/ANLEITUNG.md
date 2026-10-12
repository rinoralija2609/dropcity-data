# Gratis-Version: läuft in deinem Google-Konto (kein n8n nötig)

Diese Version macht genau dasselbe wie die n8n-Version, läuft aber **kostenlos bei Google** („Google Apps Script“).
Du brauchst nur ein Gmail-Konto und musst nichts installieren.

**Einzige Kosten:** das KI-Guthaben bei Anthropic (mindestens 5 $, ca. 4,60 €).
- Mit `claude-opus-5-5` reicht das für ca. 150 Anfragen.
- Mit `claude-haiku-5-5` reicht es für über 1.000 Anfragen. Dafür in der Konfiguration `modell: 'claude-haiku-5-5'` eintragen.

**Unterschied zu n8n:** Das Postfach wird alle **5 Minuten** geprüft statt sofort. Im Verkaufsgespräch sagst du dann „innerhalb von 5 Minuten“ statt „in 2 Minuten“.

---

## Einrichtung (ca. 20 Minuten)

### 1. Gmail-Konto anlegen
Lege ein neues Gmail-Konto für deine Demo an, z. B. `anfragen.demo.niederbayern@gmail.com`, und melde dich damit im Browser an.

### 2. Anthropic-API-Key holen
1. Auf <https://console.anthropic.com> registrieren.
2. Unter **Billing** 5 $ aufladen.
3. Unter **API Keys** auf **Create Key** klicken und den Schlüssel kopieren (beginnt mit `sk-ant-`).

### 3. Skript anlegen
1. Öffne <https://script.google.com> (mit dem Gmail-Konto aus Schritt 1) und klicke auf **Neues Projekt**.
2. Oben links auf „Unbenanntes Projekt“ klicken und es in **Anfrage-Autopilot** umbenennen.
3. Im Editor **den gesamten Inhalt löschen**.
4. Den Inhalt der Datei **`Code.gs`** aus diesem Ordner hineinkopieren:
   - Auf GitHub die Datei `Code.gs` öffnen.
   - Rechts oben auf das **Kopieren-Symbol** („Copy raw file“) klicken.
   - Im Editor einfügen.
5. Speichern (💾 oder Strg+S).

### 4. Konfiguration ausfüllen
Ganz oben im Code steht der Block `CONFIG`. Für deine **Demo** reicht:
- `inhaberEmail`: **deine private E-Mail-Adresse**, die du auf dem Handy liest. Dorthin kommen die Entwürfe.
- Alles andere kann für die Demo so bleiben.

Für einen **echten Kunden** trägst du dort Firmenname, Leistungen, PLZ-Gebiet, Signatur usw. ein.

### 5. API-Key sicher speichern
1. Links auf das **Zahnrad ⚙️ (Projekteinstellungen)** klicken und ganz nach unten zu **Skripteigenschaften** scrollen.
2. **Skripteigenschaft hinzufügen**:
   - Eigenschaft: `ANTHROPIC_API_KEY`
   - Wert: dein `sk-ant-…`-Schlüssel
3. Optional für die Handy-Benachrichtigung eine zweite Eigenschaft anlegen: `TELEGRAM_BOT_TOKEN` mit dem Bot-Token. Im CONFIG-Block dann `telegramChatId` eintragen. Wie du beides bekommst, steht in `../01-EINRICHTUNG.md` unter Schritt 3.
4. **Skripteigenschaften speichern** klicken.

### 6. Testen
1. Zurück zum Editor (links auf **<>** klicken).
2. Oben in der Auswahlliste neben „▷ Ausführen“ die Funktion **`testAnfrage`** wählen und auf **▷ Ausführen** klicken.
3. Beim ersten Mal fragt Google nach Berechtigungen:
   - **Berechtigungen überprüfen**, dann dein Konto wählen.
   - Es erscheint „Google hat diese App nicht überprüft“. Das ist normal, weil es **dein eigenes Skript** ist.
   - **Erweitert** und dann **Zu Anfrage-Autopilot wechseln (unsicher)** klicken.
   - **Zulassen** klicken.
4. Nach ca. 20 Sekunden sollte in deinem privaten Postfach eine Mail **„[Autopilot] Rückfrage …“** mit dem fertigen Antwort-Entwurf liegen. 🎉

### 7. Dauerbetrieb einschalten
Die Funktion **`installieren`** wählen und auf **▷ Ausführen** klicken.
Ab jetzt prüft das Skript **alle 5 Minuten** das Gmail-Postfach, auch wenn dein Computer aus ist.

**Ausprobieren:** Schick von deinem Handy eine der Anfragen aus `../demo/demo-anfragen.md` an das Demo-Gmail. Spätestens nach 5 Minuten kommt der Entwurf.

**Stoppen:** Die Funktion `deinstallieren` ausführen.

---

## Kontaktformular (optional, auch gratis)
1. Im Skript-Editor oben rechts auf **Bereitstellen** und dann **Neue Bereitstellung** klicken.
2. Beim Zahnrad den Typ **Web-App** wählen.
3. Einstellen:
   - Ausführen als: **Ich**
   - Zugriff: **Jeder**
4. Auf **Bereitstellen** klicken und die **Web-App-URL** kopieren (`https://script.google.com/macros/s/…/exec`).
5. In `../formular/kontaktformular.html` diese URL bei `WEBHOOK_URL` eintragen.
6. Die Datei gratis hosten, z. B. per Drag & Drop auf <https://app.netlify.com/drop>.

---

## Bei echten Kunden: 2 Möglichkeiten

**A) Der Kunde nutzt selbst Gmail**
Richte das Skript direkt in **seinem** Google-Konto ein, er meldet sich dafür kurz an. Fertig.

**B) Der Kunde hat IONOS, T-Online, Strato o. Ä. (der häufigste Fall)**
1. Lege ein neues Gmail-Konto **für diesen Kunden** an, z. B. `autopilot.mustermann@gmail.com`, und richte dort das Skript ein.
2. Im Postfach des Kunden (z. B. IONOS Webmail → Einstellungen → **Weiterleitung**) eine Weiterleitung an dieses Gmail einrichten. Dabei unbedingt **„Kopie im Postfach behalten“** aktivieren.
3. In der Konfiguration `inhaberEmail` auf die Adresse des Chefs setzen und `modus: 'entwurf'` lassen.
4. Der Chef bekommt jeden Entwurf mit dem Button **„Mit einem Klick senden“**. Die Antwort geht dann ganz normal **aus seinem eigenen Mailprogramm** an den Kunden.

---

## Gratis-Grenzen von Google (reichen locker)
- ca. 100 gesendete E-Mails pro Tag. Das entspricht ca. 100 Anfragen pro Tag und Kunde.
- 90 Minuten Skript-Laufzeit pro Tag. Die Prüfung alle 5 Minuten braucht davon nur einen Bruchteil.

## Wenn etwas nicht klappt
- Links auf **Ausführungen** (☰-Symbol) klicken. Dort siehst du jeden Lauf und eventuelle Fehlermeldungen.
- `Claude-API 401`: Der API-Key ist falsch oder es fehlt Guthaben.
- `Claude-API 400`: In der Konfiguration `modell: 'claude-haiku-5-5'` probieren. Hilft das nicht, die Fehlermeldung an mich schicken.
- Es kommt nichts an: Ist die Mail **ungelesen** im **Posteingang**? Das Skript bearbeitet nur ungelesene Mails der letzten 3 Tage. Bearbeitete Mails bekommen das Label `Autopilot-erledigt`.

## Für Entwickler
`node test.js` testet das Skript offline mit simuliertem Gmail, Telegram und Claude.
