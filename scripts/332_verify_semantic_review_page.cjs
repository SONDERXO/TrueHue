// Isolated DOM harness only: never creates user decisions or trains a model.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');
const assert = require('assert/strict');
const folder = path.resolve(__dirname, '../outputs/semantic_reference_readiness_v1');
const manifestBytes = fs.readFileSync(path.join(folder, 'manifest.json'));
const manifest = JSON.parse(manifestBytes);
const script = fs.readFileSync(path.join(folder, 'review-script.js'), 'utf8');
const elements = new Map();
const element = id => {
  if (!elements.has(id)) elements.set(id, {value:'', textContent:'', handlers:{}, addEventListener(name, fn){this.handlers[name]=fn;}});
  return elements.get(id);
};
for (const row of manifest.rows) {
  element('decision_'+row.case_id).value = 'pending';
  element('notes_'+row.case_id);
  assert(fs.existsSync(path.join(folder, row.board_path)));
}
let exported;
const memory = new Map();
const context = vm.createContext({
  document: {
    getElementById: element,
    querySelectorAll: () => manifest.rows.flatMap(r=>[element('decision_'+r.case_id),element('notes_'+r.case_id)]),
    createElement: () => ({click(){}}),
  },
  localStorage: {getItem:k=>memory.get(k)||null,setItem:(k,v)=>memory.set(k,v)},
  Blob: class {constructor(parts){exported=JSON.parse(parts.join(''));}},
  URL: {createObjectURL:()=> 'mock:download',revokeObjectURL(){}},
  setTimeout:fn=>fn(),
});
vm.runInContext(script, context);
assert.equal(element('count').textContent,'0 / 6 decided');
element('export').handlers.click();
assert(exported.rows.every(r=>r.decision==='pending'));
for (const row of manifest.rows) {
  element('decision_'+row.case_id).value='uncertain';
  element('notes_'+row.case_id).value='Harness only — not a user decision';
}
vm.runInContext('update()',context);
element('export').handlers.click();
assert.equal(element('count').textContent,'6 / 6 decided');
assert.equal(exported.rows.length,6);
assert.equal(exported.manifest_sha256,crypto.createHash('sha256').update(manifestBytes).digest('hex'));
assert.equal(exported.measurement_contract_sha256,manifest.measurement_contract_sha256);
assert(exported.rows.every(r=>r.decision==='uncertain' && r.notes.includes('Harness only')));
// Only a verification record is written, never the simulated decisions.
const result={status:'pass',image_links:6,initial_pending:6,export_membership_and_hashes:true,
  notes_preserved:true,live_browser_tested:false,simulated_user_decisions_saved:false};
fs.writeFileSync(path.join(folder,'page_verification.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify(result));
