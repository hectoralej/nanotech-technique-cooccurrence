(() => {
  const $ = id => document.getElementById(id); const status = $('demo-status'); let selectedSource = '';
  const classesFrom = data => Array.isArray(data) ? data : Array.isArray(data?.clases) ? data.clases : Object.keys(data || {});
  const labelOf = value => typeof value === 'string' ? value : String(value?.id || value?.clase || value?.nombre || 'Clase');
  const safeFile = file => file && /^image\//.test(file.type || '');
  const showImage = (src, alt) => { const preview = $('demo-preview'); preview.replaceChildren(); const image = document.createElement('img'); image.src = src; image.alt = alt || 'Micrografía seleccionada'; preview.append(image); };
  const probabilities = (values, classes) => {
    const root = $('demo-results'); root.replaceChildren();
    classes.forEach((className,index) => { const row=document.createElement('div'); row.className='probability-row'; const name=document.createElement('span'); name.textContent=className; const bar=document.createElement('span'); bar.className='probability-bar'; const fill=document.createElement('i'); fill.style.width=`${Math.max(0,Math.min(1,values[index]||0))*100}%`; bar.append(fill); const value=document.createElement('b'); value.textContent=`${((values[index]||0)*100).toLocaleString('es-CR',{maximumFractionDigits:1})}%`; row.append(name,bar,value); root.append(row); });
    const reference=document.createElement('p'); reference.className='prediction-reference'; reference.textContent='Validación cruzada por artículo: exactitud 0,561 · F1 macro 0,521. Línea base de clase mayoritaria: exactitud 0,442.'; root.append(reference);
  };
  function preprocess(image) {
    const width=image.naturalWidth||image.width, height=image.naturalHeight||image.height, side=Math.max(width,height); const source=document.createElement('canvas'); source.width=side; source.height=side;
    const ctx=source.getContext('2d',{willReadFrequently:true}); ctx.fillStyle='#fff'; ctx.fillRect(0,0,side,side); ctx.drawImage(image,(side-width)/2,(side-height)/2);
    const canvas=document.createElement('canvas'); canvas.width=256; canvas.height=256; const target=canvas.getContext('2d',{willReadFrequently:true}); target.imageSmoothingEnabled=true; target.imageSmoothingQuality='high'; target.drawImage(source,0,0,256,256);
    const rgba=target.getImageData(0,0,256,256).data, plane=256*256, data=new Float32Array(plane*3);
    for(let pixel=0;pixel<plane;pixel++){data[pixel]=rgba[pixel*4];data[plane+pixel]=rgba[pixel*4+1];data[plane*2+pixel]=rgba[pixel*4+2];} return data;
  }
  function csvRows(text) {
    const rows=[]; let row=[],field='',quoted=false;
    for(let i=0;i<text.length;i++){const c=text[i]; if(quoted){if(c==='"'&&text[i+1]==='"'){field+='"';i++;}else if(c==='"')quoted=false;else field+=c;}else if(c==='"')quoted=true;else if(c===','){row.push(field);field='';}else if(c==='\n'){row.push(field.replace(/\r$/,''));if(row.some(Boolean))rows.push(row);row=[];field='';}else field+=c;}
    if(field||row.length){row.push(field.replace(/\r$/,''));rows.push(row);} const headers=rows.shift()||[]; return rows.map(values=>Object.fromEntries(headers.map((key,index)=>[key,values[index]||''])));
  }
  const loadImage = src => new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=()=>reject(new Error(`No se pudo cargar la imagen local: ${src}`));image.src=src;});
  async function init() {
    try {
      const response=await fetch('data/demo-status.json'); if(!response.ok) throw new Error('No se pudo leer el estado local del paquete.'); const availability=await response.json();
      if(availability.available!==true){status.textContent='En preparación: falta el paquete local del modelo, la verificación o el runtime fijado. No se ejecuta ningún modelo; los controles permanecen desactivados.';$('demo-check-status').textContent=`Paquete incompleto: ${availability.reason||'faltan archivos requeridos'}.`;return;}
      await new Promise((resolve,reject)=>{const script=document.createElement('script');script.src='vendor/onnxruntime-web/ort.min.js';script.onload=resolve;script.onerror=()=>reject(new Error('No se pudo cargar ONNX Runtime Web local.'));document.head.append(script);});
      const [classesResponse,cardResponse,csvResponse,preprocessResponse]=await Promise.all([fetch('../modelo_onnx/02_onnx/clases.json'),fetch('../modelo_onnx/02_onnx/modelo_card.json'),fetch('../modelo_onnx/03_verificacion/verificacion_onnx.csv'),fetch('../modelo_onnx/02_onnx/preprocesado.json')]);
      if(!classesResponse.ok||!cardResponse.ok||!csvResponse.ok||!preprocessResponse.ok) throw new Error('Faltan clases.json, preprocesado.json, modelo_card.json o el CSV de verificación.');
      const classes=classesFrom(await classesResponse.json()).map(labelOf), card=await cardResponse.json(), preprocessing=await preprocessResponse.json(), tests=csvRows(await csvResponse.text());
      const inputName=preprocessing.entrada?.nombre||'imagen', outputName=preprocessing.salida?.nombre||'probabilidades';
      if(card.desempeno_de_referencia_validacion_cruzada?.exactitud!==0.561||Math.round(card.desempeno_de_referencia_validacion_cruzada?.f1_macro*1000)!==521) throw new Error('Las métricas de referencia del paquete no coinciden con la ficha aprobada.');
      window.ort.env.wasm.wasmPaths=new URL('vendor/onnxruntime-web/',document.baseURI).href; window.ort.env.wasm.numThreads=1;
      const loadStart=performance.now(), session=await window.ort.InferenceSession.create('../modelo_onnx/02_onnx/ensamble3_int8.onnx',{executionProviders:['wasm']}), loadTime=performance.now()-loadStart;
      status.textContent=`Modelo local cargado en ${loadTime.toLocaleString('es-CR',{maximumFractionDigits:0})} ms. Procesamiento solo en este navegador.`; status.dataset.loadMs=String(loadTime); $('demo-edition').textContent='Modelo local'; $('demo-check-status').textContent='Modelo listo. Ejecuta la comprobación de equivalencia para revisar las 20 imágenes.';
      $('demo-file').disabled=false; $('demo-run').disabled=false;
      const headers=Object.keys(tests[0]||{}); const canonical=value=>String(value).toLocaleLowerCase('en').replace(/[^a-z0-9]/g,'');
      const expectedColumns=classes.map(className=>headers.find(key=>key.startsWith('onnx_int8_')&&canonical(key.slice('onnx_int8_'.length))===canonical(className))).filter(Boolean);
      if(expectedColumns.length!==classes.length) throw new Error('Las columnas onnx_int8_* no corresponden al orden de clases.json.');
      const imageColumn=headers.find(key=>/imagen|image|archivo|png/i.test(key));
      const testRecords=tests.filter(row=>imageColumn&&row[imageColumn]&&expectedColumns.length&&expectedColumns.every(key=>Number.isFinite(Number(row[key])))).slice(0,20);
      if(testRecords.length!==20) throw new Error(`El CSV debe aportar 20 filas completas; se encontraron ${testRecords.length}.`);
      const examples=$('demo-examples'); examples.replaceChildren(); testRecords.slice(0,4).forEach((row,index)=>{const button=document.createElement('button');button.type='button';button.className='demo-example';button.textContent=`Ejemplo ${index+1} · ${row[imageColumn]}`;button.addEventListener('click',()=>{selectedSource=`../modelo_onnx/03_verificacion/entradas/${encodeURIComponent(row[imageColumn].split(/[\\/]/).pop())}`;showImage(selectedSource,`Imagen de verificación ${index+1}`);});examples.append(button);});
      const useFile=file=>{if(!safeFile(file))return;selectedSource=URL.createObjectURL(file);showImage(selectedSource,file.name);};
      $('demo-file').addEventListener('change',event=>useFile(event.target.files?.[0]));
      $('demo-preview').addEventListener('dragover',event=>event.preventDefault()); $('demo-preview').addEventListener('drop',event=>{event.preventDefault();useFile(event.dataTransfer?.files?.[0]);});
      $('demo-run').addEventListener('click',async()=>{if(!selectedSource)return;try{const image=await loadImage(selectedSource);const tensor=new window.ort.Tensor('float32',preprocess(image),[1,3,256,256]);const start=performance.now(),out=await session.run({[inputName]:tensor}),elapsed=performance.now()-start,values=out[outputName]?.data;if(!values||values.length!==classes.length)throw new Error('La salida del modelo no coincide con las cuatro clases esperadas.');const displayClasses=classes.map(value=>({'inorganico':'Inorgánico','lipidico':'Lipídico','nanomaterial':'Nanomaterial','polimerico':'Polimérico'}[value]||value));probabilities(Array.from(values),displayClasses);$('demo-check-status').textContent=`Inferencia local: ${elapsed.toLocaleString('es-CR',{maximumFractionDigits:0})} ms.`;}catch(error){$('demo-check-status').textContent=error.message;}});
      $('demo-check').disabled=false; $('demo-check').addEventListener('click',async()=>{const button=$('demo-check');button.disabled=true;$('demo-check-status').textContent='Ejecutando la comparación local de las 20 imágenes…';try{let max=0,sum=0,n=0;for(const row of testRecords){const filename=row[imageColumn].split(/[\\/]/).pop(),image=await loadImage(`../modelo_onnx/03_verificacion/entradas/${encodeURIComponent(filename)}`),input=new window.ort.Tensor('float32',preprocess(image),[1,3,256,256]),out=await session.run({[inputName]:input}),actual=Array.from(out[outputName]?.data||[]);const expected=expectedColumns.map(key=>Number(row[key]));if(expected.some(value=>!Number.isFinite(value))||actual.length!==expected.length)throw new Error('Columnas esperadas no coinciden con clases/salida del modelo.');actual.forEach((value,index)=>{const diff=Math.abs(value-expected[index]);max=Math.max(max,diff);sum+=diff;n++;});}const mean=n?sum/n:NaN;$('demo-check-status').textContent=`${testRecords.length} imágenes · diferencia absoluta media ${mean.toLocaleString('es-CR',{maximumFractionDigits:4})} · máxima ${max.toLocaleString('es-CR',{maximumFractionDigits:4})}${mean<0.03?' · OK: menor que 0,03.':mean===0.03?' · LÍMITE: no está por debajo de 0,03.':' · ALERTA: el preprocesado no coincide (media ≥ 0,03).'}`;}catch(error){$('demo-check-status').textContent=`No se pudo completar la equivalencia: ${error.message}`;}finally{button.disabled=false;}});
    }catch(error){status.textContent=`La demo permanece desactivada: ${error.message}`;}
  }
  init();
})();
