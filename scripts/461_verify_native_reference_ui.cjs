// Synthetic DOM actions only; never writes actual reviewer response files.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const folder='outputs/stellenbosch_reference_points_v1/';
const manifest=JSON.parse(fs.readFileSync(folder+'manifest.json','utf8'));
const identity=crypto.createHash('sha256').update(fs.readFileSync(folder+'manifest.json')).digest('hex');
const data={manifest_sha256:identity,rows:manifest.rows},storage=new Map();let exported;
function launch(){
  const elements=new Map();
  const get=id=>{if(!elements.has(id))elements.set(id,{value:'',textContent:'',events:{},width:512,height:512,
    addEventListener(k,f){this.events[k]=f;},getBoundingClientRect(){return {left:0,top:0,width:512,height:512};},
    getContext(){return {clearRect(){},drawImage(){},beginPath(){},arc(){},stroke(){}};},click(){if(this.onclick)this.onclick();}});return elements.get(id);};
  get('data').textContent=JSON.stringify(data);get('label').value='skin';
  class FakeImage{constructor(){this.complete=true;}set src(v){this.path=v;if(this.onload)this.onload();}}
  const context={document:{getElementById:get,createElement:()=>({click(){}})},Image:FakeImage,Blob,
    URL:{createObjectURL(b){exported=b;return 'fixture';},revokeObjectURL(){}},setTimeout:f=>f(),
    localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)}};
  vm.createContext(context);vm.runInContext(fs.readFileSync(folder+'review.js','utf8'),context);return get;
}
(async()=>{
  let get=launch();get('export').click();assert(!exported,'Incomplete review must not export');
  get('reviewer').value='SYNTHETIC HARNESS ONLY';get('reviewer').events.input();
  function click(x,y){get('canvas').events.pointerdown({clientX:x,clientY:y});}
  click(80,96);get('label').value='hair_or_beard';click(80,96); // replaces same pixel
  get('label').value='skin';click(200,200);get('undo').click(); // removes second point
  click(-1,100); // outside does not clamp to border pixel
  get('status').value='marked';get('status').events.input();
  get('next').click();get('prev').click();assert(get('status').value==='marked');
  get=launch();assert(get('reviewer').value==='SYNTHETIC HARNESS ONLY'); // draft survives reload
  for(let i=1;i<6;i++){get('next').click();get('status').value='cannot_judge';get('notes').value='Synthetic fixture only';get('notes').events.input();}
  get('export').click();assert(exported);const value=JSON.parse(await exported.text());
  assert.equal(value.rows.length,6);assert.equal(value.manifest_sha256,identity);assert.equal(value.rows[0].points.length,1);
  assert.deepEqual(value.rows[0].points[0],{x:Math.floor(80*manifest.rows[0].width/512),y:Math.floor(96*manifest.rows[0].height/512),label:'hair_or_beard'});
  assert(value.rows.slice(1).every(r=>r.status==='cannot_judge'&&r.points.length===0));
  assert.equal(storage.size,1);console.log('Synthetic UI harness passed: native mapping, replacement, undo, outside rejection, navigation, persistence, completeness and export. No actual responses written.');
})().catch(e=>{console.error(e);process.exitCode=1;});
