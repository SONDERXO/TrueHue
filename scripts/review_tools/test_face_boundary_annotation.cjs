// Node logic checks with a mock DOM/canvas; not an interactive browser test.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');

class Element {
  constructor() { this.events={}; this.children=[]; this.style={}; this.value=''; this.checked=false; this.textContent=''; this.dataset={}; this.files=[]; }
  addEventListener(name,fn){this.events[name]=fn;}
  append(...elements){this.children.push(...elements);}
  replaceChildren(){this.children=[];}
  setAttribute(name,value){this[name]=value;}
  click(){this.clicked=true;}
  getBoundingClientRect(){return {left:0,top:0,width:parseFloat(this.style.width),height:parseFloat(this.style.height)};}
  getContext(){return new Proxy({}, {get:(_,key)=>()=>{},set:()=>true});}
}

async function main(){
  const ids=['review-data','drawing','message','storage-status','progress','show-polygons','polygon-count','polygon-list','notes','complete','image-select','image-title','image-hint','image-size','previous','next','finish','undo-point','cancel','zoom','download','import'];
  const els=Object.fromEntries(ids.map(id=>[id,new Element()]));els['show-polygons'].checked=true;
  const spec={version:'unit_test_only',manifest_sha256:'dummy',images:[1,2,3].map(i=>({image_id:'test'+i,title:'Test'+i,hint:'Test',width:100,height:100,image_sha256:'sha'+i,data_url:'dummy'}))};
  els['review-data'].textContent=JSON.stringify(spec);
  const buttons=['skin','exclude','uncertain'].map(label=>{const b=new Element();b.dataset.label=label;return b;});
  const blobs=[],storage={};let storageFails=false;
  const sandbox={console,Blob,document:{getElementById:id=>els[id],querySelectorAll:()=>buttons,createElement:()=>new Element()},
    localStorage:{getItem:k=>storage[k]??null,setItem:(k,v)=>{if(storageFails)throw Error('unavailable');storage[k]=v;}},
    Image:class {set src(value){this.onload();}},URL:{createObjectURL:b=>{blobs.push(b);return 'blob:test';},revokeObjectURL:()=>{}},setTimeout:fn=>fn()};
  const context=vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(path.join(__dirname,'face_boundary_annotation.js'),'utf8'),context);
  const run=code=>vm.runInContext(code,context);
  assert.equal(run('Object.values(state).every(r=>r.polygons.length===0 && !r.complete)'),true);
  assert.equal(els['progress'].textContent,'0 / 3 marked complete');
  function click(x,y){els.drawing.events.click({clientX:x,clientY:y});}
  // Zoom changes display, not saved original-image coordinates.
  els.zoom.events.change({target:{value:'4'}});click(40,40);click(240,40);click(240,240);els.finish.events.click();
  assert.equal(run('JSON.stringify(annotations().polygons[0].points)'),'[[10,10],[60,10],[60,60]]');
  // A face polygon alone cannot certify complete exclusion review.
  const checkbox={checked:true};els.complete.events.change({target:checkbox});assert.equal(checkbox.checked,false);
  buttons[1].events.click();click(80,80);click(120,80);click(120,120);els.finish.events.click();
  els.complete.events.change({target:{checked:true}});assert.equal(run('annotations().complete'),true);
  // Unfinished polygons block export and image switching, and can be canceled.
  click(140,140);els.download.events.click();assert.equal(blobs.length,0);
  els.next.events.click();assert.equal(run('index'),0);els.cancel.events.click();
  els.download.events.click();assert.equal(blobs.length,1);
  const exported=JSON.parse(await blobs[0].text());assert.equal(exported.draft,true);assert.equal(exported.images.length,3);assert.equal(exported.images[0].complete,true);
  assert.deepEqual(exported.label_priority,['exclude','uncertain','skin']);assert.equal(exported.outside_polygons,'unlabeled, not automatically background');
  // Deleting a saved polygon clears completion without inventing a replacement.
  els['polygon-list'].children[1].children[0].events.click();assert.equal(run('annotations().complete'),false);
  assert.equal(run('annotations().polygons.length'),1);
  // Self-crossing input must not be saved.
  els.next.events.click();buttons[0].events.click();click(40,40);click(120,120);click(40,120);click(120,40);els.finish.events.click();
  assert.equal(run('annotations().polygons.length'),0);assert.match(els.message.textContent,/crosses itself/);els.cancel.events.click();
  // Clicking near the first vertex closes and saves rather than adding a
  // slightly offset final point that crosses the outline.
  click(40,40);click(240,40);click(240,240);click(40,240);click(42,42);
  assert.equal(run('annotations().polygons.length'),1);
  assert.equal(run('annotations().polygons[0].points.length'),4);
  assert.equal(run('draft.length'),0);
  // Finish also accepts an explicitly repeated starting vertex.
  run('draft=[[20,20],[40,20],[40,40],[20,40],[20,20]]');els.finish.events.click();
  assert.equal(run('annotations().polygons.length'),2);
  assert.equal(run('annotations().polygons[1].points.length'),4);
  // Imports enforce manifest identity and coordinate bounds.
  const before=run('JSON.stringify(state)');const invalid={...exported,manifest_sha256:'wrong'};
  els.import.files=[{text:async()=>JSON.stringify(invalid)}];await els.import.events.change({target:els.import});assert.equal(run('JSON.stringify(state)'),before);
  exported.images[0].polygons[0].points[0]=[500,500];els.import.files=[{text:async()=>JSON.stringify(exported)}];await els.import.events.change({target:els.import});assert.equal(run('JSON.stringify(state)'),before);
  // Storage failure leaves export usable and is visible to the user.
  storageFails=true;els.notes.events.input({target:{value:'unit test note'}});assert.match(els['storage-status'].textContent,/unavailable/);
  els.download.events.click();assert.equal(blobs.length,2);
  console.log('Annotation logic checks passed: blank start, native coordinates, completion gates, draft protection, export, deletion, crossing rejection, import validation and storage failure.');
}
main().catch(error=>{console.error(error);process.exitCode=1;});
