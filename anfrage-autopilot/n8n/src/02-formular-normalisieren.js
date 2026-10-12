// Bringt Anfragen aus dem Website-Formular (Webhook) in dasselbe Format wie E-Mails.
const out = [];
for (const item of $input.all()) {
  const b = item.json.body || item.json;
  // Honeypot: Bots füllen das versteckte Feld "website" aus -> verwerfen.
  if (b.website) continue;
  const zeilen = [
    b.nachricht || '',
    '',
    b.leistung ? `Gewünschte Leistung: ${b.leistung}` : '',
    b.plz || b.ort ? `Ort: ${b.plz || ''} ${b.ort || ''}`.trim() : '',
    b.telefon ? `Telefon: ${b.telefon}` : '',
    b.zeitraum ? `Wunschzeitraum: ${b.zeitraum}` : '',
    b.fotos_link ? `Fotos: ${b.fotos_link}` : '',
  ].filter((z, i) => i < 2 || z);
  out.push({
    json: {
      quelle: 'Formular',
      absenderName: String(b.name || '').trim().slice(0, 200),
      absenderEmail: String(b.email || '').trim().toLowerCase().slice(0, 200),
      betreff: 'Anfrage über das Kontaktformular',
      text: zeilen.join('\n').trim().slice(0, 8000),
      autoSubmitted: '',
    },
  });
}
return out;
