"""Genera una hoja humana local: ningún rótulo se convierte automáticamente en etiqueta."""
import hashlib, json, os, random, shutil
from pathlib import Path
from urllib.parse import quote
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'modelos/imagenes_v02'; DEST=ROOT/'producto/imagenes_recortes'
SEED=20261024
df=pd.read_csv(OUT/'recortes_v02.csv',dtype=str,keep_default_na=False).sort_values('archivo_recorte')
manifest=OUT/'muestra_etiquetado_300.json'
if manifest.exists():
 selected=json.loads(manifest.read_text(encoding='utf-8'))
 if not all((ROOT/r['archivo_recorte']).exists() and (ROOT/r['ruta_original']).exists() for r in selected): raise RuntimeError('Muestra humana existente perdió archivos; no se cambia silenciosamente.')
 current=df.set_index('archivo_recorte').to_dict('index')
 for r in selected:
  r['tipo_estimado']=current.get(r['archivo_recorte'],{}).get('tipo_estimado','mixto_o_dudoso')
 manifest.write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
else:
 rng=random.Random(SEED); selected=[]
 for kind in ['micrografia_probable','grafica_probable','ilustracion_probable','mixto_o_dudoso']:
  pool=df[df.tipo_estimado==kind].to_dict('records'); rng.shuffle(pool); selected.extend(pool[:75])
 picked={r['archivo_recorte'] for r in selected}; rest=[r for r in df.to_dict('records') if r['archivo_recorte'] not in picked]; rng.shuffle(rest); selected.extend(rest[:300-len(selected)])
 if len(selected)!=300: raise RuntimeError(f'Solo {len(selected)} recortes: hacen falta 300 para crear la hoja.')
 rng.shuffle(selected); manifest.write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
items=[]
for r in selected:
 if not r.get('ruta_original_etiquetado'):
  source=ROOT/r['ruta_original'];digest=hashlib.sha256(source.read_bytes()).hexdigest()
  snapshot=DEST/'_originales_etiquetado'/r['pmcid']/f'{source.stem}__{digest[:16]}{source.suffix}';snapshot.parent.mkdir(parents=True,exist_ok=True)
  if not snapshot.exists():shutil.copy2(source,snapshot)
  r['ruta_original_etiquetado']=snapshot.relative_to(ROOT).as_posix();r['sha256_original_etiquetado']=digest
 items.append({'archivo_recorte':r['archivo_recorte'],'pmcid':r['pmcid'],'figura':r['figura'],'tipo_provisional':r['tipo_estimado'],
  'crop':quote(os.path.relpath(ROOT/r['archivo_recorte'],DEST).replace('\\','/'),safe='/.'),
  'original':quote(os.path.relpath(ROOT/r['ruta_original_etiquetado'],DEST).replace('\\','/'),safe='/.')})
manifest.write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
sample_hash=hashlib.sha256(json.dumps([r['archivo_recorte'] for r in items]).encode()).hexdigest()[:16]
template='''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Etiquetado humano de 300 paneles</title>
<style>body{font:16px system-ui,sans-serif;color:#17232d;background:#f3f6f6;margin:0;padding:20px}main{max-width:1600px;margin:auto}header{display:flex;gap:16px;align-items:center;flex-wrap:wrap}h1{font-size:23px;margin:0}button{font:inherit;cursor:pointer;padding:13px 16px;border:1px solid #718096;border-radius:7px;background:white;color:#17232d}button:focus-visible{outline:3px solid #0072b2}.choices{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0}.choices button{flex:1;min-width:180px}.chosen{background:#d0ede8;border:2px solid #087e78}.images{display:grid;grid-template-columns:1fr 1fr;gap:18px}.frame{background:white;border:1px solid #d3dddd;padding:12px;min-width:0}.frame img{object-fit:contain;width:100%;height:62vh}h2{font-size:17px;margin:2px 0 8px}.hint{color:#485763}#notice{color:#9b241c}#progress{font-variant-numeric:tabular-nums}a{color:#07599c}details{margin:12px 0}.footer{display:flex;gap:10px;align-items:center;flex-wrap:wrap}@media(max-width:850px){.images{grid-template-columns:1fr}.frame img{height:45vh}}</style>
<main><header><h1>Etiquetado humano de paneles</h1><span id="progress"></span><button id="download">Descargar CSV</button></header>
<p class="hint">Elige lo que realmente ves en el recorte. Teclas 1–4 para etiquetar; ← anterior; → siguiente. La decisión se guarda en este navegador y avanza al siguiente panel. Abre las imágenes a tamaño completo si lo necesitas.</p><p id="notice" role="status"></p>
<p id="identity"></p><div class="images"><section class="frame"><h2>Recorte a etiquetar</h2><a id="cropLink" target="_blank"><img id="crop" alt="Recorte a etiquetar"></a></section><section class="frame"><h2>Figura original</h2><a id="originalLink" target="_blank"><img id="original" alt="Figura original de referencia"></a></section></div>
<div class="choices" aria-label="Etiqueta humana"><button data-label="micrografia">1 · Micrografía</button><button data-label="grafica_espectro">2 · Gráfica o espectro</button><button data-label="ilustracion">3 · Ilustración</button><button data-label="mixto_no_sirve">4 · Mixto o no sirve</button></div>
<div class="footer"><button id="previous">← Anterior</button><button id="next">Siguiente →</button><span id="currentLabel" role="status"></span></div><details><summary>Ver etiqueta provisional del programa</summary><p id="prediction"></p><p>Es una estimación estadística; no cuenta como etiqueta humana. La clasificación final la eliges tú.</p></details></main>
<script id="sample-data" type="application/json">__DATA__</script><script>
"use strict";const items=JSON.parse(document.getElementById('sample-data').textContent),storageKey='nanotech_paneles___HASH__';let state={index:0,labels:{}},persistent=true;
try{const saved=localStorage.getItem(storageKey);if(saved)state=JSON.parse(saved)}catch(e){persistent=false;document.getElementById('notice').textContent='Este navegador no permite guardar avance local. Descarga el CSV antes de cerrar.'}
if(!Number.isInteger(state.index)||state.index<0||state.index>=items.length)state.index=0;if(!state.labels||typeof state.labels!=='object')state.labels={};
function save(){if(persistent)try{localStorage.setItem(storageKey,JSON.stringify(state))}catch(e){persistent=false;document.getElementById('notice').textContent='No se pudo guardar el avance. Descarga el CSV antes de cerrar.'}}
function show(){const r=items[state.index],v=state.labels[r.archivo_recorte];document.getElementById('identity').textContent=`${r.pmcid} · ${r.figura} · Panel ${state.index+1} de ${items.length}`;document.getElementById('progress').textContent=`${Object.keys(state.labels).length} / ${items.length} etiquetados`;
for(const k of ['crop','original']){const im=document.getElementById(k);im.src=r[k];im.onerror=()=>{document.getElementById('notice').textContent='No se pudo abrir una imagen. Conserva la estructura de carpetas y abre ETIQUETADO.html con doble clic.'};document.getElementById(k+'Link').href=r[k]}
document.getElementById('prediction').textContent=r.tipo_provisional;document.getElementById('currentLabel').textContent=v?'Etiqueta guardada: '+v.etiqueta:'Sin etiqueta humana';for(const b of document.querySelectorAll('[data-label]'))b.classList.toggle('chosen',Boolean(v&&v.etiqueta===b.dataset.label));save()}
function choose(label){const r=items[state.index];state.labels[r.archivo_recorte]={etiqueta:label,hora:new Date().toISOString()};if(state.index<items.length-1)state.index++;show()}
function move(delta){state.index=Math.max(0,Math.min(items.length-1,state.index+delta));show()}
for(const b of document.querySelectorAll('[data-label]'))b.addEventListener('click',()=>choose(b.dataset.label));document.getElementById('previous').onclick=()=>move(-1);document.getElementById('next').onclick=()=>move(1);
document.addEventListener('keydown',e=>{if(e.ctrlKey||e.metaKey||e.altKey)return;const labels=['micrografia','grafica_espectro','ilustracion','mixto_no_sirve'];if(/^[1-4]$/.test(e.key)){e.preventDefault();choose(labels[Number(e.key)-1])}else if(e.key==='ArrowLeft'){e.preventDefault();move(-1)}else if(e.key==='ArrowRight'){e.preventDefault();move(1)}});
function csvCell(x){return '"'+String(x).replaceAll('"','""')+'"'}
document.getElementById('download').onclick=()=>{const rows=[['archivo_recorte','etiqueta','hora']];for(const r of items){const v=state.labels[r.archivo_recorte];if(v)rows.push([r.archivo_recorte,v.etiqueta,v.hora])}const blob=new Blob(['\\ufeff'+rows.map(r=>r.map(csvCell).join(',')).join('\\r\\n')],{type:'text/csv;charset=utf-8'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='etiquetas_humanas.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};show();
</script></html>'''
page=template.replace('__DATA__',json.dumps(items,ensure_ascii=False).replace('</','<\\/')).replace('__HASH__',sample_hash)
(DEST/'ETIQUETADO.html').write_text(page,encoding='utf-8')
counts=pd.Series([r['tipo_provisional'] for r in items]).value_counts().to_dict()
(OUT/'validacion_etiquetado.json').write_text(json.dumps({'n':len(items),'semilla':SEED,'hash_muestra':sample_hash,'mezcla':counts,'paths_relativos':all(not Path(r['crop']).is_absolute() and not Path(r['original']).is_absolute() for r in items),'sin_etiquetas_humanas_precargadas':True,'prueba_navegador':'pendiente'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'html':str(DEST/'ETIQUETADO.html'),'n':len(items),'mezcla':counts},ensure_ascii=False))
