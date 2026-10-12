# Auftragsverarbeitungsvertrag (AVV) – Muster

> ⚠️ **Muster ohne Gewähr, keine Rechtsberatung.** Es deckt die Pflichtinhalte nach Art. 28 Abs. 3 DSGVO in Kurzform ab.
> Für mehr Sicherheit kannst du stattdessen die kostenlosen, ausführlichen Muster nutzen, z. B. das **AVV-Muster der GDD** oder **des Bitkom** (beide per Suchmaschine zu finden), und die Anlage unten übernehmen.

---

**zwischen**
[Firma des Kunden], [Adresse], vertreten durch [Inhaber]
– *Verantwortlicher* –

**und**
[Dein Name], [Adresse]
– *Auftragsverarbeiter* –

### § 1 Gegenstand und Dauer
(1) Der Auftragsverarbeiter betreibt für den Verantwortlichen einen automatisierten Anfrage-Assistenten gemäß Angebot Nr. [..] vom [Datum]: Eingehende Kundenanfragen werden ausgelesen, mit KI-Unterstützung analysiert, Antwortentwürfe werden erstellt und der Verantwortliche wird benachrichtigt.
(2) Der Vertrag gilt für die Dauer des Hauptvertrags.

### § 2 Art der Daten und betroffene Personen
- **Betroffene:** Interessenten und Kunden des Verantwortlichen, die Anfragen senden.
- **Daten:** Name, E-Mail-Adresse, Telefonnummer, Anschrift bzw. PLZ/Ort, Inhalt der Anfrage, gegebenenfalls Hinweise auf Fotos.
- Besondere Kategorien von Daten (Art. 9 DSGVO) sind nicht Gegenstand der Verarbeitung.

### § 3 Pflichten des Auftragsverarbeiters
(1) Der Auftragsverarbeiter verarbeitet die Daten nur auf dokumentierte Weisung des Verantwortlichen.
(2) Er gewährleistet die Vertraulichkeit; Personen mit Zugriff sind zur Vertraulichkeit verpflichtet.
(3) Er trifft die technischen und organisatorischen Maßnahmen nach Anlage 2 (Art. 32 DSGVO).
(4) Er unterstützt den Verantwortlichen bei der Erfüllung von Betroffenenrechten und bei Meldepflichten (Art. 32–36 DSGVO).
(5) Er meldet Datenschutzverletzungen unverzüglich, spätestens innerhalb von 24 Stunden nach Kenntnis.
(6) Nach Vertragsende löscht er alle Daten und Zugangsdaten bzw. gibt sie zurück, soweit keine Aufbewahrungspflicht besteht.
(7) Er stellt alle Informationen zum Nachweis der Pflichten zur Verfügung und ermöglicht Überprüfungen.

### § 4 Unterauftragsverarbeiter
(1) Der Verantwortliche genehmigt die in Anlage 1 genannten Unterauftragsverarbeiter.
(2) Änderungen teilt der Auftragsverarbeiter vorab mit; der Verantwortliche kann aus wichtigem Grund widersprechen.
(3) Für Übermittlungen in Drittländer stellt der Auftragsverarbeiter geeignete Garantien sicher (z. B. EU-Standardvertragsklauseln oder einen Angemessenheitsbeschluss).

### § 5 Speicherdauer
Protokolle der Verarbeitungsläufe werden höchstens [30] Tage gespeichert und dann gelöscht.

### § 6 Schlussbestimmungen
Änderungen bedürfen der Textform. Es gilt deutsches Recht.

______________________________   ______________________________
Ort, Datum, Verantwortlicher            Ort, Datum, Auftragsverarbeiter

---

## Anlage 1: Unterauftragsverarbeiter
*(an dein tatsächliches Setup anpassen)*

| Dienstleister | Zweck | Sitz / Datenstandort | Grundlage |
|---|---|---|---|
| n8n GmbH (n8n Cloud) **oder** Hetzner Online GmbH (eigener Server) | Betrieb der Automatisierung | Deutschland / EU | AVV des Anbieters |
| Anthropic (Claude API) | KI-Analyse und Textentwurf | USA | Data Processing Addendum von Anthropic inkl. Standardvertragsklauseln; API-Daten werden laut Anbieter nicht zum Training verwendet |
| Telegram (optional) | Benachrichtigung des Verantwortlichen | außerhalb der EU | nur Kurz-Zusammenfassung; auf Wunsch abschaltbar (dann nur E-Mail) |
| E-Mail-Anbieter des Verantwortlichen | Empfang & Versand | lt. Vertrag des Verantwortlichen | – |

## Anlage 2: Technische und organisatorische Maßnahmen (Kurzfassung)
- Zugang zu n8n nur mit starkem Passwort und Zwei-Faktor-Authentifizierung
- Verschlüsselte Übertragung (TLS) bei allen Verbindungen (IMAP, SMTP, API)
- Zugangsdaten werden verschlüsselt in n8n gespeichert und nicht per E-Mail übermittelt
- Automatische Löschung der Ausführungsprotokolle nach [30] Tagen
- Getrennte Workflows und Zugangsdaten je Kunde
- Regelmäßige Updates der eingesetzten Software

---

## Für dich: DSGVO-Einstellungen in n8n
- **Settings → Two-factor authentication** aktivieren.
- Ausführungsprotokolle begrenzen: Auf eigenem Server die Umgebungsvariablen `EXECUTIONS_DATA_PRUNE=true` und `EXECUTIONS_DATA_MAX_AGE=720` (Stunden = 30 Tage) setzen. In n8n Cloud gilt die Aufbewahrungszeit des Tarifs.
- Anthropic: In der Console das Data Processing Addendum (DPA) akzeptieren bzw. prüfen. Es ist in den kommerziellen Bedingungen enthalten.
