// Baut anfrage-autopilot.json (n8n-Workflow) aus den Code-Dateien in src/.
// Aufruf: node build.js
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const code = f => fs.readFileSync(path.join(__dirname, 'src', f), 'utf8');
const id = name => crypto.createHash('md5').update(name).digest('hex').replace(/^(.{8})(.{4})(.{4})(.{4})(.{12})$/, '$1-$2-$3-$4-$5');

const codeNode = (name, file, pos) => ({
  id: id(name), name, type: 'n8n-nodes-base.code', typeVersion: 2, position: pos,
  parameters: { jsCode: code(file) },
});

const claudeNode = (name, bodyField, pos) => ({
  id: id(name), name, type: 'n8n-nodes-base.httpRequest', typeVersion: 4.2, position: pos,
  retryOnFail: true, maxTries: 3, waitBetweenTries: 5000,
  parameters: {
    method: 'POST',
    url: 'https://api.anthropic.com/v1/messages',
    authentication: 'genericCredentialType',
    genericAuthType: 'httpHeaderAuth',
    sendHeaders: true,
    headerParameters: {
      parameters: [
        { name: 'anthropic-version', value: '2023-06-01' },
        { name: 'anthropic-beta', value: 'server-side-fallback-2026-07-01' },
      ],
    },
    sendBody: true,
    specifyBody: 'json',
    jsonBody: `={{ JSON.stringify($json.${bodyField}) }}`,
    options: { timeout: 120000 },
  },
});

const nodes = [
  {
    id: id('Hinweis'), name: 'Hinweis', type: 'n8n-nodes-base.stickyNote', typeVersion: 1, position: [-80, -360],
    parameters: {
      width: 720, height: 300,
      content: '## Anfrage-Autopilot\n**Pro Kunde nur 4 Dinge tun:**\n1. Node **Konfiguration** öffnen → Block oben ausfüllen\n2. **E-Mail-Eingang**: IMAP-Zugang des Kunden wählen\n3. **E-Mail senden**: SMTP-Zugang des Kunden wählen\n4. **KI**-Nodes: Header-Auth `x-api-key` (dein Anthropic-Key) · **Telegram**: Bot-Token\n\nDann oben rechts **Active** einschalten. Details: `01-EINRICHTUNG.md`',
    },
  },
  {
    id: id('E-Mail-Eingang'), name: 'E-Mail-Eingang', type: 'n8n-nodes-base.emailReadImap', typeVersion: 2, position: [0, 0],
    parameters: { mailbox: 'INBOX', postProcessAction: 'nothing', format: 'simple', options: { customEmailConfig: '["UNSEEN"]' } },
  },
  {
    id: id('Formular-Eingang'), name: 'Formular-Eingang', type: 'n8n-nodes-base.webhook', typeVersion: 2, position: [0, 220],
    webhookId: id('webhook-anfrage-autopilot'),
    parameters: { httpMethod: 'POST', path: 'anfrage-autopilot', responseMode: 'onReceived', options: { allowedOrigins: '*' } },
  },
  codeNode('Mail normalisieren', '01-mail-normalisieren.js', [220, 0]),
  codeNode('Formular normalisieren', '02-formular-normalisieren.js', [220, 220]),
  codeNode('Konfiguration', '03-konfiguration.js', [460, 110]),
  claudeNode('KI: Anfrage analysieren', 'analyseBody', [680, 110]),
  codeNode('Analyse auswerten', '04-analyse-auswerten.js', [900, 110]),
  claudeNode('KI: Antwort schreiben', 'antwortBody', [1120, 110]),
  codeNode('Antwort fertigstellen', '05-antwort-fertigstellen.js', [1340, 110]),
  {
    id: id('E-Mail senden'), name: 'E-Mail senden', type: 'n8n-nodes-base.emailSend', typeVersion: 2.1, position: [1580, 0],
    parameters: {
      fromEmail: '={{ $json.mailVon }}',
      toEmail: '={{ $json.mailAn }}',
      subject: '={{ $json.betreff }}',
      emailFormat: 'html',
      html: '={{ $json.html }}',
      options: { replyTo: '={{ $json.replyTo }}', appendAttribution: false },
    },
  },
  {
    id: id('Telegram an Chef'), name: 'Telegram an Chef', type: 'n8n-nodes-base.telegram', typeVersion: 1.2, position: [1580, 220],
    onError: 'continueRegularOutput',
    parameters: {
      chatId: '={{ $json.telegramChatId }}',
      text: '={{ $json.telegram }}',
      additionalFields: { appendAttribution: false, parse_mode: 'HTML' },
    },
  },
];

const link = to => ({ main: [[{ node: to, type: 'main', index: 0 }]] });
const connections = {
  'E-Mail-Eingang': link('Mail normalisieren'),
  'Formular-Eingang': link('Formular normalisieren'),
  'Mail normalisieren': link('Konfiguration'),
  'Formular normalisieren': link('Konfiguration'),
  'Konfiguration': link('KI: Anfrage analysieren'),
  'KI: Anfrage analysieren': link('Analyse auswerten'),
  'Analyse auswerten': link('KI: Antwort schreiben'),
  'KI: Antwort schreiben': link('Antwort fertigstellen'),
  'Antwort fertigstellen': {
    main: [[
      { node: 'E-Mail senden', type: 'main', index: 0 },
      { node: 'Telegram an Chef', type: 'main', index: 0 },
    ]],
  },
};

const workflow = {
  name: 'Anfrage-Autopilot',
  nodes,
  connections,
  settings: { executionOrder: 'v1', saveDataSuccessExecution: 'all', saveDataErrorExecution: 'all' },
  pinData: {},
};

fs.writeFileSync(path.join(__dirname, 'anfrage-autopilot.json'), JSON.stringify(workflow, null, 2) + '\n');
console.log('anfrage-autopilot.json geschrieben (' + nodes.length + ' Nodes)');
