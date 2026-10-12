# JARVIS – lokaler KI-Assistent

Ein Konsolen-Agent auf Basis der Claude API, der auf deinem PC Dateien liest/schreibt,
Befehle ausführt (mit Rückfrage), Apps und Webseiten öffnet, im Web sucht und Daten analysiert.

## Einrichtung

```bash
cd jarvis
pip install -r requirements.txt
cp .env.example .env      # dann ANTHROPIC_API_KEY eintragen
python jarvis.py          # Textmodus
python jarvis.py --voice  # Sprachmodus (SpeechRecognition, pyttsx3, pyaudio installieren)
```

## Mit Stimme und animierter Oberfläche

```bash
py jarvis_ui.py
```

Öffnet Jarvis im Browser (am besten **Microsoft Edge** – dort gibt es die natürlichen deutschen Stimmen,
z. B. „Conrad“). Kugel anklicken oder Leertaste drücken und sprechen; Jarvis antwortet mit Stimme,
die Kugel reagiert auf Zuhören (grün), Nachdenken (orange) und Sprechen (blau).
„Gespräch“ anhaken = nach jeder Antwort automatisch weiter zuhören. Bestätigungen erscheinen als Fenster.
Die Oberfläche ist nur auf diesem PC erreichbar (127.0.0.1).

Befehle im Chat: `exit` beendet, `reset` startet ein neues Gespräch, Strg+C bricht den laufenden Auftrag ab.

## Sicherheit

- Shell-Befehle, das Öffnen von Programmen, das Überschreiben von Dateien und Schreiben
  außerhalb des Workspace erfordern eine Bestätigung – außer `JARVIS_AUTO_APPROVE=true`.
- Webseiten-Inhalte, die Jarvis liest, könnten versuchen, ihm Anweisungen unterzuschieben.
  Lass die Bestätigungen deshalb eingeschaltet.
