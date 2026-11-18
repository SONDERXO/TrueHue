// Synthetic DOM only. Never writes an actual reviewer response.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const folder='outputs/stellenbosch_skin_patch_review_v2/';
const raw=fs.readFileSync(folder+'manifest.json'),spec={manifest_sha256:crypto.createHash('sha256').update(raw).digest('hex'),rows:JSON.parse(raw).rows};
const storage=new Map();let exported;
function launch(){
 const nodes=new Map(),get=id=>{if(!nodes.has(id))nodes.set(id,{value:'',checked:true,textContent:'',events:{},
  addEventListener(k,f){this.events[k]=f;},getBoundingClientRect(){return {left:0,top:0,width:512,height:512};},
  getContext(){return {clearRect(){},drawImage(){},beginPath(){},lineTo(){},moveTo(){},closePath(){},fill(){},stroke(){}};}});return nodes.get(id);};
 get('data').textContent=JSON.stringify(spec);get('mode').value='polygon';get('canvas').setPointerCapture=()=>{};
 class Picture{set src(v){this.path=v;if(this.onload)this.onload();}}
 const context={document:{getElementById:get,createElement:()=>({click(){}})},Image:Picture,Blob,
  URL:{createObjectURL(b){exported=b;return 'fixture';},revokeObjectURL(){}},setTimeout:f=>f(),
  localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)}};
 vm.createContext(context);vm.runInContext(fs.readFileSync(folder+'review.js','utf8'),context);return {get,context};
}
(async()=>{
 let {get,context}=launch();get('export').onclick();assert(!exported);
 get('reviewer').value='SYNTHETIC ONLY';get('reviewer').oninput();
 const click=(x,y)=>get('canvas').events.pointerdown({clientX:x,clientY:y});
 click(-1,50);assert(get('count').textContent.includes('0 draft'));
 click(80,80);click(240,80);click(240,240);click(80,240);
 get('finish').onclick();assert(get('count').textContent.startsWith('1 saved'));
 get('status').value='unavailable';get('status').onchange();assert.equal(get('status').value,'marked');
 get('next').onclick();get('prev').onclick();assert.equal(get('status').value,'marked');
 ({get,context}=launch());assert.equal(get('reviewer').value,'SYNTHETIC ONLY');
 assert.equal(get('status').value,'marked');
 assert.equal(vm.runInContext('validPolygon([[1,1],[8,8],[1,8],[8,1]],20,20)',context),false);
 assert.equal(vm.runInContext('validPolygon([[1,1],[2,2],[3,3]],20,20)',context),false);
 assert.equal(vm.runInContext('validPolygon([[1,1],[8,1],[8,8],[1,8]],20,20)',context),true);
 for(let i=1;i<6;i++){get('next').onclick();get('status').value='unavailable';get('status').onchange();get('notes').value='Synthetic unavailable fixture';get('notes').oninput();}
 get('export').onclick();assert(exported);const value=JSON.parse(await exported.text());
 assert(!value.draft);assert.equal(value.rows.length,6);assert.equal(value.manifest_sha256,spec.manifest_sha256);
 const w=spec.rows[0].width,h=spec.rows[0].height;
 assert.deepEqual(value.rows[0].polygons[0],[[80,80],[240,80],[240,240],[80,240]].map(([x,y])=>[Math.floor(x*w/512),Math.floor(y*h/512)]));
 assert(value.rows.slice(1).every(r=>r.status==='unavailable'&&r.polygons.length===0&&r.notes));
 get('draft').onclick();assert(JSON.parse(await exported.text()).draft);
 get('prev').onclick();get('prev').onclick();get('prev').onclick();get('prev').onclick();get('prev').onclick();
 get('mode').value='rectangle';get('mode').onchange();
 get('canvas').events.pointerdown({clientX:300,clientY:300,pointerId:1});
 get('canvas').events.pointermove({clientX:420,clientY:420});
 get('canvas').events.pointerup({clientX:420,clientY:420});get('finish').onclick();
 assert(get('count').textContent.startsWith('2 saved'));
 
 // Import a saved synthetic draft back into browser-memory state.
 get('import').files=[{text:async()=>JSON.stringify(value)}];await get('import').onchange({target:get('import')});
 assert(get('message').textContent.includes('Draft imported'));
 console.log('PASS synthetic native coordinates, outside rejection, polygons, status protection, navigation, persistence, completeness, draft/final export and import. No actual responses written.');
})().catch(e=>{console.error(e);process.exitCode=1;});
