// Baut die fertige E-Mail (Entwurf an Inhaber oder direkt an Kunden) und die Telegram-Nachricht.
const vorher = $('Analyse auswerten').all();
const esc = s => String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const nl2br = s => esc(s).replace(/\n/g, '<br>');
const out = [];
$input.all().forEach((item, i) => {
  const { config, anfrage, marker, analyse: an, fall } = vorher[i].json;
  const res = item.json;
  if (res.stop_reason === 'refusal') return;
  const antwort = (res.content || []).filter(b => b.type === 'text').map(b => b.text).join('\n').trim();
  if (!antwort) throw new Error('Leere KI-Antwort');

  const kundenBetreff = anfrage.betreff && !/^re:/i.test(anfrage.betreff) ? `Re: ${anfrage.betreff}` : (anfrage.betreff || 'Ihre Anfrage');
  const volltext = `${antwort}\n\n${config.signatur}`;
  const hatEmail = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(anfrage.absenderEmail);
  const fallText = { rueckfrage: 'Rückfrage (Infos fehlen)', bestaetigung: 'Eingangsbestätigung', ausserhalb: 'Absage (außerhalb Einzugsgebiet)' }[fall];

  const steckbrief = `
    <table cellpadding="4" style="border-collapse:collapse;font-family:Arial,sans-serif;font-size:14px">
      <tr><td><b>Kunde</b></td><td>${esc(an.name || anfrage.absenderName)} &lt;${esc(anfrage.absenderEmail)}&gt;</td></tr>
      <tr><td><b>Telefon</b></td><td>${esc(an.telefon) || '–'}</td></tr>
      <tr><td><b>Ort</b></td><td>${esc(an.plz)} ${esc(an.ort)}</td></tr>
      <tr><td><b>Leistung</b></td><td>${esc(an.leistung) || '–'}</td></tr>
      <tr><td><b>Zeitraum</b></td><td>${esc(an.zeitraum) || '–'}</td></tr>
      <tr><td><b>Dringend</b></td><td>${an.dringend ? 'JA' : 'nein'}</td></tr>
      <tr><td><b>Fotos</b></td><td>${an.fotos_vorhanden ? 'vorhanden' : 'keine'}</td></tr>
      <tr><td><b>Sprache</b></td><td>${esc(an.sprache)}</td></tr>
    </table>
    <p style="font-family:Arial,sans-serif"><b>Zusammenfassung:</b> ${esc(an.zusammenfassung_inhaber)}</p>`;

  let mailAn, betreff, html, replyTo;
  if (config.modus === 'automatisch' && hatEmail) {
    mailAn = anfrage.absenderEmail;
    betreff = kundenBetreff;
    html = `<div style="font-family:Arial,sans-serif;font-size:14px">${nl2br(volltext)}</div>`;
    replyTo = config.absenderEmail;
  } else {
    const mailto = hatEmail
      ? `mailto:${encodeURIComponent(anfrage.absenderEmail)}?subject=${encodeURIComponent(kundenBetreff)}&body=${encodeURIComponent(volltext)}`
      : '';
    mailAn = config.inhaberEmail;
    betreff = `${marker} ${fallText}: ${an.leistung || 'Anfrage'} – ${an.name || anfrage.absenderName || anfrage.absenderEmail}`;
    replyTo = hatEmail ? anfrage.absenderEmail : config.absenderEmail;
    html = `
      <div style="font-family:Arial,sans-serif;font-size:14px">
        <h2 style="margin:0 0 8px">Neue Anfrage – Antwort-Entwurf liegt bereit</h2>
        ${steckbrief}
        ${mailto ? `<p><a href="${esc(mailto)}" style="display:inline-block;background:#1d6f42;color:#fff;padding:12px 18px;border-radius:6px;text-decoration:none;font-weight:bold">Antwort mit einem Klick öffnen &amp; senden</a></p>
        <p style="color:#666;font-size:12px">Der Button öffnet Ihr Mailprogramm mit fertigem Text – prüfen, ggf. anpassen, senden.</p>`
        : '<p><b>Keine E-Mail-Adresse angegeben – bitte telefonisch melden.</b></p>'}
        <h3>Entwurf</h3>
        <div style="border-left:4px solid #1d6f42;padding:8px 12px;background:#f5f8f6">${nl2br(volltext)}</div>
        <h3>Ursprüngliche Nachricht</h3>
        <div style="color:#444">${nl2br(anfrage.text)}</div>
      </div>`;
  }

  const telegram = [
    `🔔 <b>Neue Anfrage</b> (${esc(anfrage.quelle)})`,
    `👤 ${esc(an.name || anfrage.absenderName || anfrage.absenderEmail)}${an.telefon ? ' · ' + esc(an.telefon) : ''}`,
    `🔧 ${esc(an.leistung) || '–'}`,
    `📍 ${esc(an.plz)} ${esc(an.ort)}`,
    `${an.dringend ? '🚨 DRINGEND' : '🕒 nicht dringend'} · 📷 ${an.fotos_vorhanden ? 'Fotos ✅' : 'keine Fotos'}`,
    '',
    esc(an.zusammenfassung_inhaber),
    '',
    config.modus === 'automatisch' && hatEmail
      ? `✅ ${fallText} wurde automatisch gesendet.`
      : `✉️ ${fallText} liegt als Entwurf in Ihrem Postfach.`,
  ].join('\n');

  out.push({ json: { mailVon: config.absenderEmail, mailAn, betreff, html, replyTo, telegramChatId: config.telegramChatId, telegram } });
});
return out;
