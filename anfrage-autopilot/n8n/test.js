// Testet die Code-Nodes offline mit simulierten E-Mails und simulierten KI-Antworten.
// Aufruf: node test.js
const fs = require('fs');
const path = require('path');
const assert = require('assert');

function run(file, items, refs = {}) {
  const src = fs.readFileSync(path.join(__dirname, 'src', file), 'utf8');
  const $input = { all: () => items.map(json => ({ json })) };
  const $ = name => {
    if (!refs[name]) throw new Error('Unbekannte Node-Referenz: ' + name);
    return { all: () => refs[name] };
  };
  return new Function('$input', '$', src)($input, $).map(i => i.json);
}

const claude = obj => ({ stop_reason: 'end_turn', content: [{ type: 'thinking', thinking: '' }, { type: 'text', text: typeof obj === 'string' ? obj : JSON.stringify(obj) }] });

// 1) E-Mail normalisieren
const mails = run('01-mail-normalisieren.js', [
  { from: 'Anna Huber <Anna.Huber@web.de>', subject: 'Bad renovieren', textPlain: 'Hallo, wir möchten unser Bad renovieren. Wann hätten Sie Zeit?' },
  { from: 'newsletter@baumarkt.de', subject: 'Angebote', textPlain: 'Nur heute 20%' },
  { from: 'info@mustermann-haustechnik.de', subject: '[Autopilot] Rückfrage', textPlain: 'Schleife?' },
  { from: 'x@y.de', subject: 'HTML only', textHtml: '<p>Heizung <b>kaputt</b></p>' },
]);
assert.strictEqual(mails[0].absenderEmail, 'anna.huber@web.de');
assert.strictEqual(mails[0].absenderName, 'Anna Huber');
assert.ok(mails[3].text.includes('Heizung'), 'HTML wird zu Text');

// 2) Formular normalisieren (inkl. Honeypot)
const form = run('02-formular-normalisieren.js', [
  { body: { name: 'Besnik Krasniqi', email: 'besnik@example.com', telefon: '0151 123', plz: '94032', ort: 'Passau', leistung: 'Heizungstausch', nachricht: 'Unsere Heizung ist 25 Jahre alt.' } },
  { body: { name: 'Bot', website: 'http://spam', nachricht: 'buy now' } },
]);
assert.strictEqual(form.length, 1, 'Honeypot filtert Bots');
assert.ok(form[0].text.includes('Telefon: 0151 123'));

// 3) Konfiguration: filtert eigene/ignorierte Absender
const konf = run('03-konfiguration.js', [...mails, ...form]);
assert.strictEqual(konf.length, 3, 'Newsletter und eigene Autopilot-Mail werden gefiltert');
const body = konf[0].analyseBody;
assert.strictEqual(body.output_config.format.type, 'json_schema');
assert.strictEqual(body.fallbacks, 'default');
assert.ok(body.messages[0].content.includes('Bad renovieren'));

// 4) Analyse auswerten: drei Fälle + Spam
const analysen = [
  { kategorie: 'anfrage', sprache: 'Deutsch', name: 'Anna Huber', telefon: '', plz: '', ort: '', leistung: 'Badsanierung', dringend: false, zeitraum: '', fotos_vorhanden: false, fehlende_infos: ['Fotos', 'PLZ und Ort', 'Telefonnummer'], zusammenfassung_inhaber: 'Frau Huber will ihr Bad renovieren.' },
  { kategorie: 'spam', sprache: 'Deutsch', name: '', telefon: '', plz: '', ort: '', leistung: '', dringend: false, zeitraum: '', fotos_vorhanden: false, fehlende_infos: [], zusammenfassung_inhaber: '' },
  { kategorie: 'anfrage', sprache: 'Deutsch', name: 'Besnik Krasniqi', telefon: '0151 123', plz: '94032', ort: 'Passau', leistung: 'Heizungstausch', dringend: false, zeitraum: '', fotos_vorhanden: false, fehlende_infos: [], zusammenfassung_inhaber: 'Heizung 25 Jahre alt, Tausch gewünscht.' },
];
const ausw = run('04-analyse-auswerten.js', analysen.map(claude), { Konfiguration: konf.map(json => ({ json })) });
assert.strictEqual(ausw.length, 2, 'Spam wird verworfen');
assert.strictEqual(ausw[0].fall, 'rueckfrage');
assert.strictEqual(ausw[1].fall, 'bestaetigung');

// Außerhalb des Einzugsgebiets
const ausserhalb = run('04-analyse-auswerten.js', [claude({ ...analysen[2], plz: '80331', ort: 'München' })], { Konfiguration: [{ json: konf[2] }] });
assert.strictEqual(ausserhalb[0].fall, 'ausserhalb');

// 5) Antwort fertigstellen – Entwurfsmodus
const antworten = [claude('Guten Tag Frau Huber,\n\nvielen Dank <script>!\n\nViele Grüße'), claude('Guten Tag Herr Krasniqi,\n\ndanke.\n\nViele Grüße')];
const fertig = run('05-antwort-fertigstellen.js', antworten, { 'Analyse auswerten': ausw.map(json => ({ json })) });
assert.strictEqual(fertig[0].mailAn, 'max.mustermann@example.com', 'Entwurf geht an Inhaber');
assert.ok(fertig[0].betreff.startsWith('[Autopilot]'), 'Marker verhindert Schleifen');
assert.ok(fertig[0].html.includes('mailto:anna.huber%40web.de'));
assert.ok(!fertig[0].html.includes('<script>'), 'HTML wird escaped');
assert.ok(fertig[0].telegram.includes('Badsanierung'));

// Automatik-Modus
const autoAusw = ausw.map(a => ({ json: { ...a, config: { ...a.config, modus: 'automatisch' } } }));
const auto = run('05-antwort-fertigstellen.js', antworten, { 'Analyse auswerten': autoAusw });
assert.strictEqual(auto[1].mailAn, 'besnik@example.com', 'Automatik schreibt direkt an Kunden');
assert.ok(auto[1].html.includes('Tel. 0871'), 'Signatur angehängt');

// Workflow-JSON passt zu den Quelldateien
const wf = JSON.parse(fs.readFileSync(path.join(__dirname, 'anfrage-autopilot.json'), 'utf8'));
const names = new Set(wf.nodes.map(n => n.name));
for (const [from, c] of Object.entries(wf.connections)) {
  assert.ok(names.has(from), 'Verbindung von unbekanntem Node ' + from);
  c.main.flat().forEach(t => assert.ok(names.has(t.node), 'Verbindung zu unbekanntem Node ' + t.node));
}
for (const n of wf.nodes.filter(n => n.type === 'n8n-nodes-base.code')) {
  new Function('$input', '$', n.parameters.jsCode); // Syntaxcheck
}

console.log('Alle Tests bestanden ✔');
