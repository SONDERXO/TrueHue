// Unit-test review state/export with an in-memory DOM, not a live browser.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const crypto = require('node:crypto');
const folder = path.resolve(__dirname, '../outputs/primary_training_review_v1');
const source = fs.readFileSync(path.join(folder, 'review-script.js'), 'utf8');
const storage = new Map();
let downloaded;
function element(tag = 'div') {
  return { tag, children: [], value: '', attributes: {}, append(...items) { this.children.push(...items); },
    replaceChildren(...items) { this.children = items; }, setAttribute(k, v) { this.attributes[k] = v; }, click() {} };
}
function context() {
  const ids = new Map();
  const ctx = vm.createContext({ document: { getElementById(id) { if (!ids.has(id)) ids.set(id, element()); return ids.get(id); }, createElement: element },
    localStorage: { getItem: k => storage.get(k) || null, setItem: (k, v) => storage.set(k, v) },
    Blob, URL: { createObjectURL(blob) { downloaded = blob; return 'unit-test-only'; }, revokeObjectURL() {} },
    setTimeout() {}, window: { scrollTo() {} }, console });
  vm.runInContext(source, ctx);
  return { ctx, ids, evaluate: code => vm.runInContext(code, ctx) };
}
function findTag(node, tag) { if (node.tag === tag) return node; for (const child of node.children || []) { const found = findTag(child, tag); if (found) return found; } }
(async () => {
  const test = context();
  assert.equal(test.evaluate('groups.length'), 26);
  assert.equal(test.evaluate('Object.keys(decisions).length'), 0);
  const groupCount = test.evaluate('groups[0].rows.length');
  test.ids.get('acceptGroup').onclick();
  assert.equal(test.evaluate('Object.keys(decisions).length'), groupCount);
  assert.equal(test.evaluate("Object.values(decisions).every(d=>d.decision==='accept')"), true);
  test.ids.get('next').onclick();
  assert.equal(test.evaluate('index'), 1);
  assert.equal(test.evaluate('groups[1].rows.some(r=>decisions[r.pair_id])'), false);
  test.evaluate("choose(groups[index].rows[0].pair_id,'reject')");
  const note = findTag(test.ids.get('cards'), 'textarea');
  note.value = 'Unit test only: excluded from real decisions'; note.oninput();
  assert.equal(test.evaluate('decisions[groups[1].rows[0].pair_id].notes'), note.value);
  test.ids.get('download').onclick();
  const data = JSON.parse(await downloaded.text());
  const expectedHash = crypto.createHash('sha256').update(fs.readFileSync(path.join(folder, 'manifest.json'))).digest('hex');
  assert.equal(data.manifest_sha256, expectedHash);
  assert.equal(Object.keys(data.reviews).length, 61);
  assert.equal(Object.values(data.reviews).filter(d => d.decision === 'accept').length, groupCount);
  assert.equal(Object.values(data.reviews).filter(d => d.decision === 'reject').length, 1);
  assert.equal(Object.values(data.reviews).filter(d => d.decision === '').length, 60 - groupCount);
  const reloaded = context();
  assert.equal(reloaded.evaluate('Object.keys(decisions).length'), groupCount + 1);
  const sha = file => crypto.createHash('sha256').update(fs.readFileSync(path.join(folder, file))).digest('hex');
  fs.writeFileSync(path.join(folder, 'review-unit-verification.json'), JSON.stringify({ status: 'pass',
    checked: ['no preselected decisions', 'group acceptance restricted to current photo', 'individual rejection and notes', '61-row manifest-bound export', 'in-memory reload persistence'],
    live_browser_tested: false, real_user_decisions_created: false, html_sha256: sha('review.html'), script_sha256: sha('review-script.js') }, null, 2));
  console.log('PASS: review scope, notes, export and reload; in-memory test only, no user decisions written.');
})().catch(error => { console.error(error); process.exitCode = 1; });
