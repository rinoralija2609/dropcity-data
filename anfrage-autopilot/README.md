# Anfrage-Autopilot: dein komplettes Paket 🇹🇭

> **„Ich sorge dafür, dass jede Kundenanfrage in 2 Minuten beantwortet wird, während Sie auf der Baustelle sind.“**

Hier liegt alles, was du für dein KI-Nebengeschäft brauchst: das fertige System, die Demo, die Verkaufsunterlagen, die Rechtsvorlagen und eine Liste mit 29 Betrieben zum Anrufen.

## Was das System macht
```
Kunde schreibt E-Mail / füllt Formular aus
        ↓
KI prüft: Anfrage? Spam? Was fehlt? Wie dringend? Im Einzugsgebiet?
        ↓
KI schreibt passende Antwort in Kundensprache
(Rückfrage nach Fotos/Maßen · Eingangsbestätigung · höfliche Absage)
        ↓
Chef bekommt: Telegram aufs Handy + E-Mail mit „Mit einem Klick senden“-Button
(oder im Automatik-Modus: Antwort geht direkt raus)
```

---

## ✅ Was nur du machen kannst (insgesamt ca. 3 Stunden + Gespräche)
Das kann ich nicht übernehmen, weil es deine Konten, deine Unterschrift und deine Stimme braucht:

| # | Aufgabe | Zeit | Anleitung |
|---|---|---|---|
| 1 | Konten anlegen: n8n, Anthropic (5–10 $ Guthaben), Telegram-Bot, Demo-Gmail | 30 Min. | [`01-EINRICHTUNG.md`](01-EINRICHTUNG.md) |
| 2 | Workflow importieren, Zugangsdaten eintragen, testen | 45 Min. | [`01-EINRICHTUNG.md`](01-EINRICHTUNG.md) |
| 3 | 90-Sekunden-Demo-Video aufnehmen | 45 Min. | [`demo/demo-skript.md`](demo/demo-skript.md) |
| 4 | Gewerbe anmelden | 30 Min. | [`recht/gewerbe-und-datenschutz.md`](recht/gewerbe-und-datenschutz.md) |
| 5 | Deine Kontaktdaten in Flyer & Angebot eintragen | 15 Min. | [`verkauf/`](verkauf/) |
| 6 | **Anrufen, Termine machen, verkaufen** | 6 Wochen à 8 Std. | [`akquise/akquise-plan.md`](akquise/akquise-plan.md) |

---

## 📁 Inhalt

| Ordner / Datei | Was drin ist |
|---|---|
| [`01-EINRICHTUNG.md`](01-EINRICHTUNG.md) | Klick-für-Klick-Anleitung inkl. IMAP/SMTP-Daten aller gängigen Mail-Anbieter |
| [`n8n/anfrage-autopilot.json`](n8n/anfrage-autopilot.json) | **Der fertige Workflow:** in n8n importieren, Zugangsdaten eintragen, fertig |
| `n8n/src/`, `build.js`, `test.js` | Quellcode der Workflow-Schritte und automatische Tests |
| [`formular/kontaktformular.html`](formular/kontaktformular.html) | Fertiges Anfrageformular für Website und Google-Profil (handytauglich, mit Spam-Schutz) |
| [`demo/demo-anfragen.md`](demo/demo-anfragen.md) | 7 Test-Anfragen (unvollständig, Notfall, Albanisch, Spam …) |
| [`demo/demo-skript.md`](demo/demo-skript.md) | Drehbuch fürs Video und Ablauf der Live-Demo im Termin |
| [`verkauf/pitch-und-telefonskript.md`](verkauf/pitch-und-telefonskript.md) | Pitch, Telefonleitfaden, Antworten auf 9 Einwände, albanischer Einstieg |
| [`verkauf/nachrichten-vorlagen.md`](verkauf/nachrichten-vorlagen.md) | E-Mail- und WhatsApp-Vorlagen für jeden Schritt (DE + AL) |
| [`verkauf/angebot-vorlage.md`](verkauf/angebot-vorlage.md) | Angebot und Rechnung (Kleinunternehmer) |
| [`verkauf/flyer.html`](verkauf/flyer.html) | Einseitiger Flyer, im Browser öffnen und als PDF drucken |
| [`recht/avv-muster.md`](recht/avv-muster.md) | Muster für den Auftragsverarbeitungsvertrag (DSGVO) |
| [`recht/gewerbe-und-datenschutz.md`](recht/gewerbe-und-datenschutz.md) | Checkliste Gewerbe, Steuer, Datenschutz und Textbaustein für Kunden |
| [`akquise/lead-liste.csv`](akquise/lead-liste.csv) | **29 Handwerksbetriebe** in Landshut, Straubing, Deggendorf, Passau, Dingolfing mit Telefonnummern |
| [`akquise/akquise-plan.md`](akquise/akquise-plan.md) | 6-Wochen-Plan mit Tagesaufgaben, Lead-Strategie und Einnahmen-Tracker |

## 💶 Preise (Empfehlung)
| | Einrichtung | Monatlich |
|---|---|---|
| Pilotkunden (die ersten 2) | 290 € (fällig nach der Testphase) | 39 € (1. Monat gratis) |
| Standard | 450 € | 49 € |
| Plus (inkl. Formular, Nachfassen, Bewertungen) | 650 € | 69 € |

## 💸 Deine Kosten
- **Start:** 0 € (n8n-Testphase) + 5–10 $ API-Guthaben + ca. 20–50 € Gewerbeanmeldung + ca. 10 € Flyerdruck
- **Laufend:** n8n ca. 20–25 €/Monat (oder eigener Server ca. 5 €) + KI ca. 3–4 Cent pro Anfrage
