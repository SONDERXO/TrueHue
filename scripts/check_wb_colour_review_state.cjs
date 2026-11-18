// Generated DOM/state fixtures only; not browser-layout QA or scientific ratings.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'..','outputs','wb_feature_colour_review_v1');
const nodes={},buttons=[];let downloaded=null;
for(const field of ['preference','appearance'])for(const value of field==='preference'?['candidate','input','no_useful_difference','uncertain']:['acceptable','unwanted','uncertain']){
  buttons.push({dataset:{field,value},setAttribute(){}});
}
const element=id=>nodes[id]??(nodes[id]={value:'',disabled:false,hidden:true,textContent:'',files:[]});
const storage=new Map();
const context=vm.createContext({document:{getElementById:element,querySelectorAll:()=>buttons,
  createElement:()=>({download:'',click(){downloaded=this.download;}})},
  localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},
  Blob,URL:{createObjectURL:()=> 'blob:generated-qa-only',revokeObjectURL(){}},setTimeout:fn=>fn()});
vm.runInContext(fs.readFileSync(path.join(root,'qa_review.js'),'utf8'),context);
const payload=()=>JSON.parse(vm.runInContext('JSON.stringify(payload())',context));
const click=(field,value)=>buttons.find(b=>b.dataset.field===field&&b.dataset.value===value).onclick();
assert.equal(payload().status,'partial');assert.deepEqual(payload().answers,{});
click('preference','no_useful_difference');const partial=payload();
assert.equal(partial.answers.qa_01.appearance,null);assert.equal(element('next').disabled,true);
vm.runInContext('restore(valid('+JSON.stringify(partial)+'))',context);
assert.equal(payload().answers.qa_01.preference,'no_useful_difference');
assert.equal(payload().answers.qa_01.appearance,null);
click('appearance','uncertain');assert.equal(payload().status,'stopped_uncertain');assert.equal(element('next').disabled,true);
element('clear').onclick();assert.equal(payload().status,'partial');assert.deepEqual(payload().answers,{});
assert.throws(()=>vm.runInContext('valid('+JSON.stringify({...partial,manifest_sha256:'wrong'})+')',context));
assert.throws(()=>vm.runInContext('valid('+JSON.stringify({...partial,qa_fixture:false})+')',context));
for(let i=0;i<11;i++){click('preference','candidate');click('appearance','acceptable');if(i<10)element('next').onclick();}
assert.equal(payload().status,'complete_recorded');assert.equal(Object.keys(payload().answers).length,11);
element('save').onclick();assert.equal(downloaded,'colour-review-QA.json');
const result={passed:true,generated_fixture_only:true,initial_answers_empty:true,partial_restore_preserved:true,
  uncertain_appearance_stops:true,clear_preserved:true,wrong_manifest_rejected:true,scientific_fixture_mix_rejected:true,
  all11_recorded_status:true,qa_download_name:downloaded,interactive_browser_qa:false,scientific_ratings_generated:0};
const dest=path.join(root,'generated_state_verification_PRIVATE.json');if(fs.existsSync(dest))throw Error('Refuse overwrite');
fs.writeFileSync(dest,JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
