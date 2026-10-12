// Bringt eingehende E-Mails (IMAP) in ein einheitliches Format.
const out = [];
for (const item of $input.all()) {
  const j = item.json;
  const fromRaw = String(j.from || (j.metadata && j.metadata.from) || '');
  const match = fromRaw.match(/<([^>]+)>/) || fromRaw.match(/([^\s"<>]+@[^\s"<>]+)/);
  const email = match ? match[1].trim().toLowerCase() : '';
  const name = fromRaw.replace(/<[^>]*>/, '').replace(/"/g, '').trim();
  let text = String(j.textPlain || j.text || '');
  if (!text && j.textHtml) {
    text = String(j.textHtml).replace(/<style[\s\S]*?<\/style>/gi, '').replace(/<[^>]+>/g, ' ');
  }
  text = text.replace(/\n{3,}/g, '\n\n').trim().slice(0, 8000);
  out.push({
    json: {
      quelle: 'E-Mail',
      absenderName: name && name !== email ? name : '',
      absenderEmail: email,
      betreff: String(j.subject || '').trim(),
      text,
      autoSubmitted: String((j.headers && (j.headers['auto-submitted'] || j.headers['Auto-Submitted'])) || ''),
    },
  });
}
return out;
