const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..'), file=path.join(root,'producto/imagenes_recortes/ETIQUETADO.html');
const html=fs.readFileSync(file,'utf8'),raw=html.match(/<script id="sample-data" type="application\/json">([\s\S]*?)<\/script>/)[1],items=JSON.parse(raw);
const js=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)[1];
assert.equal(items.length,300);assert.equal(new Set(items.map(x=>x.archivo_recorte)).size,300);
for(const r of items)for(const k of ['crop','original']){assert(!/^https?:|^file:|^[a-z]:/i.test(r[k]));assert(fs.existsSync(path.resolve(path.dirname(file),decodeURIComponent(r[k]))));}
const storage=new Map();let exported=null;
function browser(){const els={},handlers={};const labels=['micrografia','grafica_espectro','ilustracion','mixto_no_sirve'];
const button=label=>({dataset:{label},classList:{toggle(){}},addEventListener(event,fn){this[event]=fn}});
const buttons=labels.map(button);function el(id){return els[id]??=(id==='sample-data'?{textContent:raw}:{textContent:'',classList:{toggle(){}}})}
const doc={getElementById:el,querySelectorAll:()=>buttons,addEventListener:(k,f)=>handlers[k]=f,createElement:()=>({click(){exported.name=this.download}})};
const ctx=vm.createContext({document:doc,localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)},Blob,URL:{createObjectURL(blob){exported={blob};return 'blob:test'},revokeObjectURL(){}},setTimeout:fn=>fn(),Date,JSON,Number,Object,Math,Boolean,String});vm.runInContext(js,ctx);
return{ctx,els,handlers,buttons};}
(async()=>{let b=browser();assert(b.els.progress.textContent.startsWith('0 / 300'));for(const key of ['1','2','3','4'])b.handlers.keydown({key,preventDefault(){}});
assert(b.els.progress.textContent.startsWith('4 / 300'));b.handlers.keydown({key:'ArrowLeft',preventDefault(){}});assert(b.els.currentLabel.textContent.includes('mixto_no_sirve'));
const saved=[...storage.values()][0];b=browser();assert.equal([...storage.values()][0],saved);assert(b.els.currentLabel.textContent.includes('mixto_no_sirve'));b.els.download.onclick();
assert.equal(exported.name,'etiquetas_humanas.csv');const text=await exported.blob.text();assert(text.includes('"archivo_recorte","etiqueta","hora"'));assert.equal(text.trim().split('\r\n').length,5);
for(const label of ['micrografia','grafica_espectro','ilustracion','mixto_no_sirve'])assert(text.includes('"'+label+'"'));
assert(!/<script[^>]+src=|<link[^>]+href=/i.test(html));
// The application browser rejected file://. Do not circumvent it with a server or another browser.
const p=path.join(__dirname,'validacion_etiquetado.json'),r=JSON.parse(fs.readFileSync(p,'utf8'));r.prueba_navegador='No realizada: el navegador de la aplicación bloqueó el protocolo file://; no se intentó eludir la restricción.';r.prueba_funcional_js={estado:'PASS',teclas_1_a_4:true,anterior:true,restauracion_localStorage:true,descarga_csv_3_columnas:true,imagenes_relativas_existentes:600,nota:'Entorno DOM simulado aislado; etiquetas de prueba no se guardaron en la hoja real.'};fs.writeFileSync(p,JSON.stringify(r,null,2));console.log(JSON.stringify(r.prueba_funcional_js));})().catch(e=>{console.error(e);process.exitCode=1});
