// Offline-Test von Code.gs mit simuliertem Gmail, Telegram und Claude. Aufruf: node test.js
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

function umgebung({ mails = [], analyse, props = { ANTHROPIC_API_KEY: 'sk-test' } }) {
  const gesendet = [], api = [], antworten = [], labels = [];
  const msg = m => ({
    getFrom: () => m.from, getSubject: () => m.subject, getPlainBody: () => m.body,
    reply: (body, opt) => antworten.push({ to: m.from, body, opt }),
  });
  const threads = mails.map(m => ({ getMessages: () => [msg(m)], addLabel: () => labels.push(m.subject) }));
  const ctx = {
    Logger: { log: () => {} },
    LockService: { getScriptLock: () => ({ tryLock: () => true, releaseLock: () => {} }) },
    Session: { getEffectiveUser: () => ({ getEmail: () => 'demo@gmail.com' }) },
    PropertiesService: { getScriptProperties: () => ({ getProperty: k => props[k] || null }) },
    ScriptApp: { getProjectTriggers: () => [], deleteTrigger: () => {}, newTrigger: () => ({ timeBased: () => ({ everyMinutes: () => ({ create: () => {} }) }) }) },
    ContentService: { MimeType: { JSON: 'json' }, createTextOutput: t => ({ setMimeType: () => t }) },
    GmailApp: {
      search: () => threads,
      sendEmail: (to, subject, body, opt) => gesendet.push({ to, subject, body, opt }),
      getUserLabelByName: () => ({}), createLabel: () => ({}),
    },
    UrlFetchApp: {
      fetch: (url, opt) => {
        const body = JSON.parse(opt.payload);
        api.push({ url, headers: opt.headers, body });
        if (url.includes('telegram')) return { getResponseCode: () => 200, getContentText: () => '{}' };
        const text = body.output_config.format ? JSON.stringify(analyse) : 'Guten Tag,\n\ndanke für Ihre Anfrage.\n\nViele Grüße';
        return { getResponseCode: () => 200, getContentText: () => JSON.stringify({ stop_reason: 'end_turn', content: [{ type: 'thinking', thinking: '' }, { type: 'text', text }] }) };
      },
    },
  };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(__dirname + '/Code.gs', 'utf8') + '\nthis.CONFIG = CONFIG;', ctx);
  return { ctx, gesendet, api, antworten, labels };
}

const anfrage = { kategorie: 'anfrage', sprache: 'Deutsch', name: 'Anna Huber', telefon: '', plz: '', ort: '', leistung: 'Badsanierung', dringend: false, zeitraum: '', fotos_vorhanden: false, fehlende_infos: ['Fotos', 'PLZ'], zusammenfassung_inhaber: 'Bad <renovieren>.' };

// 1) Normale E-Mail im Entwurfsmodus + Filter
let u = umgebung({
  analyse: anfrage,
  mails: [
    { from: 'Anna Huber <anna@web.de>', subject: 'Bad', body: 'Wir wollen unser Bad renovieren.' },
    { from: 'newsletter@shop.de', subject: 'Rabatt', body: 'Nur heute!' },
    { from: 'demo@gmail.com', subject: '[Autopilot] Rückfrage', body: 'eigene Mail' },
  ],
});
u.ctx.pruefeNeueMails();
assert.strictEqual(u.labels.length, 3, 'alle Threads werden markiert');
assert.strictEqual(u.gesendet.length, 1, 'nur eine echte Anfrage');
assert.strictEqual(u.gesendet[0].to, 'max.mustermann@example.com');
assert.ok(u.gesendet[0].subject.startsWith('[Autopilot] Rückfrage'));
assert.ok(u.gesendet[0].opt.htmlBody.includes('mailto:anna%40web.de'));
assert.ok(!u.gesendet[0].opt.htmlBody.includes('<renovieren>'), 'HTML escaped');
assert.strictEqual(u.antworten.length, 0, 'Entwurfsmodus: nichts an Kunden');
assert.strictEqual(u.api[0].headers['anthropic-version'], '2023-06-01');
assert.strictEqual(u.api[0].body.output_config.format.type, 'json_schema');
assert.strictEqual(u.api[0].body.fallbacks, 'default');

// 2) Spam -> nichts senden
u = umgebung({ analyse: { ...anfrage, kategorie: 'spam' }, mails: [{ from: 'x@seo.de', subject: 'SEO', body: 'Platz 1 bei Google!' }] });
u.ctx.pruefeNeueMails();
assert.strictEqual(u.gesendet.length, 0);

// 3) Automatik-Modus + Telegram
u = umgebung({ analyse: { ...anfrage, fehlende_infos: [], plz: '84028' }, props: { ANTHROPIC_API_KEY: 'k', TELEGRAM_BOT_TOKEN: 't' }, mails: [{ from: 'anna@web.de', subject: 'Bad', body: 'Bad renovieren, 84028 Landshut' }] });
u.ctx.CONFIG.modus = 'automatisch';
u.ctx.CONFIG.telegramChatId = '42';
u.ctx.pruefeNeueMails();
assert.strictEqual(u.antworten.length, 1, 'Antwort direkt an Kunden');
assert.ok(u.antworten[0].body.includes('Tel. 0871'), 'Signatur');
assert.ok(u.gesendet[0].subject.includes('Eingangsbestätigung'));
assert.ok(u.api.some(c => c.url.includes('telegram') && c.body.chat_id === '42'));

// 4) Außerhalb des Gebiets
u = umgebung({ analyse: { ...anfrage, plz: '80331' }, mails: [{ from: 'b@web.de', subject: 'Bad München', body: 'Bad in 80331 München' }] });
u.ctx.pruefeNeueMails();
assert.ok(u.gesendet[0].subject.includes('Absage'));

// 5) Formular (doPost) inkl. Honeypot
u = umgebung({ analyse: anfrage });
u.ctx.doPost({ postData: { contents: JSON.stringify({ name: 'Bot', website: 'x', nachricht: 'spam' }) } });
assert.strictEqual(u.api.length, 0, 'Honeypot');
u.ctx.doPost({ postData: { contents: JSON.stringify({ name: 'Anna', email: 'anna@web.de', nachricht: 'Bad renovieren', plz: '84028' }) } });
assert.strictEqual(u.gesendet.length, 1);
assert.ok(u.api[0].body.messages[0].content.includes('Ort: 84028'));

// 6) Installieren ohne API-Key -> klare Fehlermeldung
u = umgebung({ analyse: anfrage, props: {} });
assert.throws(() => u.ctx.installieren(), /ANTHROPIC_API_KEY/);

console.log('Alle Tests bestanden ✔');
