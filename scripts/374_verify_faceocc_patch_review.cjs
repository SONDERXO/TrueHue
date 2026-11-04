// Isolated synthetic DOM harness; never writes a review decision file.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const folder='outputs/faceocc_broader_annotation_v1/';
const manifest=JSON.parse(fs.readFileSync(folder+'manifest.json','utf8'));
const crypto=require('crypto');
const identity=crypto.createHash('sha256').update(fs.readFileSync(folder+'manifest.json')).digest('hex');
const data={manifest_sha256:identity,rows:manifest.rows,technical_failures:manifest.technical_failures};
const elements=new Map(),storage=new Map();let exported;
const get=id=>{if(!elements.has(id))elements.set(id,{value:'',textContent:'',innerHTML:'',events:{},
 addEventListener(k,f){this.events[k]=f;},getBoundingClientRect(){return {left:0,top:0,width:512,height:512};},
 getContext(){return {clearRect(){},drawImage(){},beginPath(){},moveTo(){},lineTo(){},closePath(){},stroke(){},fillRect(){}};},click(){if(this.onclick)this.onclick();}});return elements.get(id);};
get('data').textContent=JSON.stringify(data);get('label').value='skin';
class FakeImage{constructor(){this.complete=true;this.naturalWidth=256;}set src(v){this.path=v;if(this.onload)this.onload();}}
const context={document:{getElementById:get,createElement:()=>({click(){}})},Image:FakeImage,Blob,
 URL:{createObjectURL(b){exported=b;return 'fixture';},revokeObjectURL(){}},setTimeout:f=>f(),
 localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)}};
vm.createContext(context);vm.runInContext(fs.readFileSync(folder+'review.js','utf8'),context);
get('export').click();assert(!exported,'Incomplete work must not export');
get('annotator').value='SYNTHETIC TEST — NOT USER DECISIONS';get('annotator').events.input();
function polygon(label,points){get('label').value=label;for(const [x,y] of points)get('canvas').events.pointerdown({clientX:2*x,clientY:2*y});get('finish').click();}
polygon('skin',[[10,10],[30,10],[30,30],[10,30]]);
polygon('outside',[[40,40],[60,40],[60,60],[40,60]]);
get('status').value='gradable';get('status').events.input();
for(let i=1;i<data.rows.length;i++){get('next').click();get('status').value='ungradable';get('notes').value='Synthetic harness only';get('notes').events.input();}
get('export').click();assert(exported);
exported.text().then(text=>{const value=JSON.parse(text);assert.equal(value.rows.length,23);
 assert.equal(value.manifest_sha256,identity);assert.equal(value.rows[0].polygons.length,2);
 assert.deepEqual(value.rows[0].polygons[0].points,[[10,10],[30,10],[30,30],[10,30]]);
 assert.equal(value.technical_failures.length,1);assert(storage.size===1);
 console.log('Synthetic-only UI harness passed: incomplete export, drawing coordinates, navigation, persistence and exact export membership. No decisions saved.');
}).catch(e=>{console.error(e);process.exitCode=1;});
