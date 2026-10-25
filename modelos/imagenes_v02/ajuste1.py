"""Inventario y segmentación local reproducible. No realiza peticiones de red."""
from __future__ import annotations
import argparse, csv, hashlib, html, json, math, os, random, re, shutil, time
from pathlib import Path
from xml.etree import ElementTree as ET
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy import ndimage as ndi

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'modelos/imagenes_v02'; CROPS=ROOT/'producto/imagenes_recortes'
OLD=ROOT/'producto/imagenes'; NEW=ROOT/'producto/imagenes_v02'
EXT={'.jpg','.jpeg','.png','.tif','.tiff','.gif','.webp'}
CONFIG={'version':'ajuste1-4','ejes_fraccion_lineas_max':.08,'seed':20261023,'max_dim_analisis':1400,'blanco':245,'mixta_area_sin_tecnica':.42,
 'dilatacion_px':3,'fusion_cajas_px':5,'adjuntar_texto_px':22,'area_min':.03,
 'tinta_min':.02,'pixeles_tinta_min':120,'aspecto_max':8,'franja_tinta_max':.012,
 'franja_ancho_min':2,'padding_px':4}
CH=hashlib.sha256(json.dumps(CONFIG,sort_keys=True).encode()).hexdigest()[:12]
TECNICA_CONFIG={'version':'solo_etiquetas_prefijo_2','herencia_figura':False,
 'pies_no_fiables':{'7310a3b9204e1d2f526721022214a7c8315a4ce6d9dd7584fd7642d161a81f6e':
 'PMC10605403, Figure 3: el pie intercambia las técnicas de a/b/c respecto de la imagen. Detectado visualmente en lote 17; abstención de toda asignación, sin reinterpretar el pie.'}}
TH=hashlib.sha256(json.dumps(TECNICA_CONFIG,sort_keys=True).encode()).hexdigest()[:12]
TECH_PAT={
 'cryo-EM':r'cryo[-\s]?(?:TEM|EM|electron)', 'HRTEM':r'\bHR[-\s]?TEM\b',
 'STEM':r'\bSTEM\b|scanning transmission electron', 'TEM':r'\bTEM\b|transmission electron',
 'SEM':r'\bSEM\b|scanning electron', 'AFM':r'\bAFM\b|atomic force microscop',
 'XRD':r'\bXRD\b|diffract(?:ion|ogram)', 'FTIR':r'FT[-\s]?IR|infrared|Fourier.transform',
 'UVVis':r'UV[-\s]?(?:vis|visible)|ultraviolet|absorbance|absorption spectr',
 'SAXS':r'\bSAXS\b|small.angle X.ray', 'EDS':r'\bEDS\b|\bEDX\b|energy.dispersive',
 'Raman':r'Raman|\bSERS\b','DLS':r'\bDLS\b|dynamic light scattering|size distribution',
 'zeta':r'zeta(?: potential)?(?: distribution)?'}
RX={k:re.compile(v,re.I) for k,v in TECH_PAT.items()}
MIC={'TEM','SEM','STEM','HRTEM','cryo-EM','AFM'}; SPEC=set(RX)-MIC

def load(p): return pd.read_csv(p,dtype=str,keep_default_na=False,encoding='utf-8-sig')
def dump(p,x):
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp')
 t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8'); t.replace(p)
def csvout(p,rows,columns=None):
 df=pd.DataFrame(rows,columns=columns); t=p.with_suffix('.csv.tmp'); df.to_csv(t,index=False,encoding='utf-8-sig'); t.replace(p)
def clean(s):
 s=str(s or '').translate(str.maketrans({'\u2212':'-','\u2013':'-','\u2014':'-','\u00ad':'','\u200b':''}))
 return re.sub(r'\s+',' ',''.join(c for c in s if c.isprintable() or c.isspace())).strip()
def tech(s):
 found=[k for k,rx in RX.items() if rx.search(clean(s))]
 if 'SEM' in found and re.search(r'(?:mean|means|average).{0,30}(?:SEM|standard error)|standard error (?:of (?:the )?mean|mean)',s,re.I) and not re.search(r'scanning electron|micrograph|SEM (?:image|micro|analysis)',s,re.I): found.remove('SEM')
 if 'DLS' in found and not re.search(r'\bDLS\b|dynamic light scattering',s,re.I): found.remove('DLS')
 if 'STEM' in found and 'scanning transmission' in s.lower(): found=[x for x in found if x not in {'SEM','TEM'}]
 return found
def fk(s):
 m=re.search(r'\d+',s); return m.group(0) if m else clean(s).lower()
def figure_type(caption,techniques):
 ts=set(techniques); m=bool(ts&MIC) or bool(re.search('micrograph',caption,re.I))
 s=bool(ts&SPEC) or bool(re.search(r'histogram|(?:size|diameter) distribution|elemental map',caption,re.I))
 return 'mixta' if m and s else 'micrografia' if m else 'espectro' if s else 'otra'
def ordered_articles():
 a=load(ROOT/'curation/ext_articulos.csv'); a=a[a.tier.isin(['E1','E2'])].copy()
 a['_tier']=a.tier.map({'E1':0,'E2':1}); return a.sort_values('_tier',kind='stable').reset_index(drop=True)
def archive():
 d=OUT/'historial_pre_ajuste1'
 if d.exists(): return
 d.mkdir()
 for n in ['progreso.json','recortes_v02.csv','inventario_figuras.csv','CHECKPOINTS.md','revision_muestras.csv','INFORME_IMAGENES_V02.md','tabla_modelo_v02.csv','tabla_espectros_v02.csv']:
  if (OUT/n).exists(): shutil.copy2(OUT/n,d/n)
 if (OUT/'muestras').exists(): shutil.copytree(OUT/'muestras',d/'muestras')
def full_figs(pm):
 root=ET.parse(ROOT/'data/cache/fulltext'/f'{pm}.xml').getroot(); out=[]
 for f in root.iter('fig'):
  label=f.find('label'); cap=f.find('caption')
  label=clean(''.join(label.itertext())) if label is not None else f.get('id','figura')
  caption=clean(''.join(cap.itertext())) if cap is not None else ''
  names=[]
  for g in f.iter('graphic'):
   v=g.get('{http://www.w3.org/1999/xlink}href','').replace('\\','/').split('/')[-1]
   if v and Path(v).suffix.lower() in EXT and v not in names: names.append(v)
  techniques=tech(caption)
  out.append({'figura':label,'figkey':fk(label),'pie_completo':caption,'archivos':names,'tecnicas':techniques,'tipo_figura':figure_type(caption,techniques)})
 return out
def inventory():
 archive(); a=ordered_articles(); model=load(ROOT/'curation/v0.1/tabla_modelo.csv')
 assert model.groupby('pmcid').fold.nunique().le(1).all()
 meta=model.drop_duplicates('pmcid').set_index('pmcid')[['fold','clase_modelo']].to_dict('index')
 base=set()
 for name in ['ext_paneles.csv','ext_espectros.csv']:
  d=load(ROOT/'curation'/name); base.update((r.pmcid,fk(r.fig)) for r in d.itertuples())
 rows=[]; figures={}; errors=[]
 for i,r in enumerate(a.itertuples()):
  try: figs=full_figs(r.pmcid); figures[r.pmcid]=figs
  except Exception as e: errors.append({'pmcid':r.pmcid,'error':str(e)}); figures[r.pmcid]=[]; continue
  for f in figs:
   kind=f['tipo_figura']
   if kind=='otra': continue
   for n in f['archivos'] or ['']:
    rows.append({'pmcid':r.pmcid,'figura':f['figura'],'archivo_grafico':n,'pie':f['pie_completo'][:300],
     'tipo_figura':kind,'tecnicas_en_pie':'|'.join(f['tecnicas']),'ya_en_base':int((r.pmcid,f['figkey']) in base),
     'clase_modelo':meta.get(r.pmcid,{}).get('clase_modelo',''),'fold':meta.get(r.pmcid,{}).get('fold',''),
     'lote':i//100+1,'tier':r.tier})
  if (i+1)%100==0: print(f'inventario {i+1}/{len(a)}',flush=True)
 df=pd.DataFrame(rows); assert not df.duplicated(['pmcid','figura','archivo_grafico']).any()
 assert df.groupby('pmcid').fold.nunique(dropna=False).le(1).all()
 csvout(OUT/'inventario_figuras.csv',rows); dump(OUT/'pies_ajuste1.json',figures)
 csvout(OUT/'orden_articulos.csv',[{'orden':i,'pmcid':r.pmcid,'tier':r.tier,'lote':i//100+1,**meta.get(r.pmcid,{'clase_modelo':'','fold':''})} for i,r in enumerate(a.itertuples())])
 dump(OUT/'validacion_inventario_ajuste1.json',{'articulos':len(a),'articulos_jats_ok':len(a)-len(errors),'figuras_graficos_candidatos':len(rows),'figuras_logicas':len(df.drop_duplicates(['pmcid','figura'])),'errores':errors,'F1':'PASS' if not errors else 'PARCIAL','red':'no utilizada'})
 dump(OUT/'config_ajuste1.json',CONFIG)
 p=json.loads((OUT/'progreso.json').read_text(encoding='utf-8')); p['inventario_ajuste1']={'articulos':len(a),'completo':not errors,'figuras_graficos':len(rows)}; dump(OUT/'progreso.json',p)
 checkpoint(f'Inventario ajuste 1: {len(a)} artículos E1/E2; {len(rows)} registros figura/archivo; JATS errores={len(errors)}. Descargas delegadas a Claude.')
 print(json.dumps({'inventario':len(rows),'articulos':len(a),'errores':len(errors)}))
def checkpoint(s):
 with (OUT/'CHECKPOINTS.md').open('a',encoding='utf-8') as f: f.write(f'\n## {time.strftime("%Y-%m-%d %H:%M:%S")} · Ajuste 1\n{s}\n')
def overlap(a,b): return min(a[2],b[2])>max(a[0],b[0]) and min(a[3],b[3])>max(a[1],b[1])
def distance(a,b): return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
def union(a,b): return (min(a[0],b[0]),min(a[1],b[1]),max(a[2],b[2]),max(a[3],b[3]))
def merge(boxes,gap=0):
 boxes=list(boxes); changed=True
 while changed:
  changed=False
  for i in range(len(boxes)):
   for j in range(i+1,len(boxes)):
    if overlap(boxes[i],boxes[j]) or distance(boxes[i],boxes[j])<=gap:
     boxes[i]=union(boxes[i],boxes[j]); boxes.pop(j); changed=True; break
   if changed: break
 return boxes
def bands(mask,box,depth=0):
 x0,y0,x1,y1=box; sub=mask[y0:y1,x0:x1]; h,w=sub.shape
 if depth>=5 or min(h,w)<100: return [box]
 candidates=[]
 for axis,p in [(0,sub.mean(axis=1)),(1,sub.mean(axis=0))]:
  length=len(p); ok=p<=CONFIG['franja_tinta_max']; labs,n=ndi.label(ok)
  for sl in ndi.find_objects(labs):
   if sl is None: continue
   st,en=sl[0].start,sl[0].stop
   if en-st<CONFIG['franja_ancho_min'] or st<.14*length or en>.86*length: continue
   candidates.append(((en-st)/length,axis,(st+en)//2))
 if not candidates: return [box]
 _,axis,k=max(candidates)
 if axis==0: children=[(x0,y0,x1,y0+k),(x0,y0+k,x1,y1)]
 else: children=[(x0,y0,x0+k,y1),(x0+k,y0,x1,y1)]
 return sum((bands(mask,b,depth+1) for b in children),[])
def segment(im,diagnostics=None):
 w,h=im.size; scale=min(1.,CONFIG['max_dim_analisis']/max(w,h)); W,H=max(1,round(w*scale)),max(1,round(h*scale))
 a=np.asarray(im.resize((W,H)).convert('RGB')); ink=a.min(axis=2)<CONFIG['blanco']
 regions=bands(ink,(0,0,W,H)); boxes=[]; tiny=[]
 for region in regions:
  x0,y0,x1,y1=region; mask=ink[y0:y1,x0:x1]
  dil=ndi.binary_dilation(mask,structure=np.ones((CONFIG['dilatacion_px'],)*2))
  labels,n=ndi.label(dil)
  for sl in ndi.find_objects(labels):
   if sl is None: continue
   ys,xs=sl; b=(x0+xs.start,y0+ys.start,x0+xs.stop,y0+ys.stop)
   area=(b[2]-b[0])*(b[3]-b[1]); ticks=int(ink[b[1]:b[3],b[0]:b[2]].sum())
   (boxes if area>=CONFIG['area_min']*W*H and ticks>=CONFIG['pixeles_tinta_min'] else tiny).append(b)
 boxes=merge(boxes,CONFIG['fusion_cajas_px'])
 # Attach panel labels, ticks, scale bars to the nearest large panel without joining separate panels.
 unattached=[]
 for b in tiny:
  if boxes:
   ds=[distance(b,c) for c in boxes]; i=int(np.argmin(ds))
   if ds[i]<=CONFIG['adjuntar_texto_px']: boxes[i]=union(boxes[i],b)
   else: unattached.append(b)
 boxes=merge(boxes,0)
 if len(boxes)<2: return [(0,0,w,h)],'compuesta_sin_separar'
 result=[]
 pad=CONFIG['padding_px']
 for x0,y0,x1,y1 in boxes:
  result.append((max(0,int((x0-pad)/scale)),max(0,int((y0-pad)/scale)),min(w,math.ceil((x1+pad)/scale)),min(h,math.ceil((y1+pad)/scale))))
 # Padding must not create overlapping crops; fall back rather than claim safe separation.
 if any(overlap(a,b) for i,a in enumerate(result) for b in result[i+1:]): return [(0,0,w,h)],'compuesta_sin_separar'
 # Group comparable top edges into reading-order rows.
 result.sort(key=lambda b:(b[1],b[0])); ordered=[]
 while result:
  first=result.pop(0); tol=.25*(first[3]-first[1]); row=[first]; rest=[]
  for b in result:
   (row if abs(b[1]-first[1])<=tol else rest).append(b)
  ordered.extend(sorted(row,key=lambda b:b[0])); result=rest
 if diagnostics is not None:
  for x0,y0,x1,y1 in unattached:
   diagnostics.append({'bbox':[int(x0/scale),int(y0/scale),math.ceil(x1/scale),math.ceil(y1/scale)],'motivo':'componente_menor_3pct_o_poca_tinta_no_asociado_a_panel','etapa':'componentes_previos_al_recorte'})
 return ordered,'componentes_y_franjas'
def statistics(im):
 a=np.asarray(im.resize((min(420,im.width),min(420,im.height))).convert('RGB')).astype(float)
 gray=a.mean(2); ink=a.min(2)<245; fraction=float(ink.mean()); sat=(a.max(2)-a.min(2))/255
 quant=(a//16).astype(int); fg=quant[ink]; flat=np.ravel_multi_index(fg.T,(16,16,16)) if len(fg) else np.array([],int)
 hist=np.bincount(flat,minlength=4096); dominant=float(np.sort(hist)[-12:].sum()/max(1,hist.sum()))
 histgray=np.histogram(gray,bins=32,range=(0,256))[0]; pp=histgray[histgray>0]/gray.size; entropy=float(-(pp*np.log2(pp)).sum())
 dark=gray<150; hor=ndi.binary_opening(dark,structure=np.ones((1,max(15,round(a.shape[1]*.30)))))
 ver=ndi.binary_opening(dark,structure=np.ones((max(15,round(a.shape[0]*.30)),1)))
 axes=bool(hor.any() and ver.any() and (hor.any(axis=1).mean()<=CONFIG['ejes_fraccion_lineas_max']) and (ver.any(axis=0).mean()<=CONFIG['ejes_fraccion_lineas_max']))
 edge=float((np.hypot(ndi.sobel(gray,0),ndi.sobel(gray,1))>80).mean())
 fgstd=float(gray[ink].std()) if ink.any() else 0.
 aspect=max(im.width/im.height,im.height/im.width)
 reasons=[]
 if fraction<.02: reasons.append('tinta_menor_2pct')
 if aspect>8: reasons.append('proporcion_mayor_8_a_1')
 if int(ink.sum())<CONFIG['pixeles_tinta_min']: reasons.append('pocos_pixeles_tinta')
 if fraction<.15 and fgstd<12 and entropy<1.3 and not axes: reasons.append('texto_o_lineas_sin_variacion')
 p_micro=float(np.clip(.45*(1-sat.mean())+.35*min(entropy/5,1)+.20*fraction,0,1))
 p_graph=float(np.clip(.50*(1-fraction)+.35*axes+.15*min(edge/.12,1),0,1))
 drawing=dominant>.78 and float(sat[ink].mean() if ink.any() else 0)>.12 and not axes
 if drawing: kind='ilustracion_probable'
 elif axes and fraction<.65: kind='grafica_probable'
 elif entropy>3.5 and fraction>.45 and sat.mean()<.10: kind='micrografia_probable'
 else: kind='mixto_o_dudoso'
 return {'tipo_estimado':kind,'p_micrografia':round(p_micro,4),'p_grafica':round(p_graph,4),
  'fraccion_tinta':round(fraction,4),'saturacion_media':round(float(sat.mean()),4),'densidad_bordes':round(edge,4),
  'relacion_aspecto':round(im.width/im.height,4),'entropia_gris':round(entropy,4),'colores_cuantizados':int((hist>0).sum()),
  'fraccion_12_colores_dominantes':round(dominant,4),'ejes_detectados':int(axes)},reasons
def panel_tech(caption,n):
 matches=list(re.finditer(r'\(([a-zA-Z])\)\s*',caption)); labels=[x.group(1).lower() for x in matches]
 if hashlib.sha256(clean(caption).encode()).hexdigest() in TECNICA_CONFIG['pies_no_fiables']: return ['']*n,labels
 if len(matches)!=n or labels!=[chr(97+i) for i in range(n)]: return ['']*n,labels
 # “DLS (A), SEM (B)” is suffix notation; following text belongs to the next label.
 # Abstain rather than shift techniques by one panel.
 if tech(caption[:matches[0].start()]): return ['']*n,labels
 result=[]
 for i,m in enumerate(matches):
  phrase=caption[m.end():matches[i+1].start() if i+1<n else len(caption)].split(';')[0]
  ts=tech(phrase[:130])
  if re.search(r'histogram|distribution derived|size distribution',phrase,re.I): ts=[t for t in ts if t not in MIC]
  result.append('|'.join(ts))
 return result,labels
def sources(pm,figures):
 mapping={Path(n).stem:f for f in figures for n in f['archivos']}
 inventory_names={Path(n).stem for f in figures if f.get('tipo_figura',figure_type(f['pie_completo'],f['tecnicas']))!='otra' for n in f['archivos']}
 grouped={}
 for base in [OLD,NEW]:
  for p in (base/pm).glob('*'):
   if p.suffix.lower() not in EXT: continue
   if base==NEW and p.stem not in inventory_names: continue
   grouped.setdefault(p.stem,[]).append(p)
 result=[]
 for stem,paths in sorted(grouped.items()):
  good=[]
  for p in paths:
   try:
    with Image.open(p) as im: wh=im.size
    good.append((p.suffix.lower()!='.gif',wh[0]*wh[1],str(p),p))
   except Exception: continue
  if good: result.append((max(good)[-1],mapping.get(stem,{'figura':'sin_figura_en_JATS','pie_completo':'','tecnicas':[]})))
 return result
def process_batch(batch):
 prog=json.loads((OUT/'progreso.json').read_text(encoding='utf-8'))
 if batch>2 and batch not in prog.get('ajuste1',{}).get('lotes_extraidos',[]):
  assert not prog.get('pausa_por_calidad_visual',True),'Pausa visual: revalidar los lotes 1–2 o resolver dos fallos consecutivos.'
  assert str(batch-1) in prog.get('revision_ajuste1',{}),'Inspeccionar la muestra del lote anterior antes de avanzar.'
  assert json.loads((OUT/f'validacion_ajuste1_lote_{batch-1:02d}.json').read_text(encoding='utf-8'))['F3']=='PASS','La validación técnica anterior debe estar terminada.'
 a=load(OUT/'orden_articulos.csv'); subset=a[a.lote.astype(int)==batch]
 if subset.empty: raise SystemExit('lote inexistente')
 figs=json.loads((OUT/'pies_ajuste1.json').read_text(encoding='utf-8')); results=OUT/'resultados_ajuste1'; results.mkdir(exist_ok=True); changed=False
 for k,r in enumerate(subset.to_dict('records')):
  pm=r['pmcid']; src=sources(pm,figs.get(pm,[])); signature=[(str(p),p.stat().st_size,p.stat().st_mtime_ns) for p,_ in src]
  cache=results/f'{pm}.json'
  if cache.exists():
   prior=json.loads(cache.read_text(encoding='utf-8'))
   if prior.get('config_hash')==CH and prior.get('tecnica_config_hash')==TH and prior.get('signature')==[list(x) for x in signature]: continue
  changed=True; rows=[]; discards=[]; err=[]
  for path,f in src:
   try:
    source_hash=hashlib.sha256(path.read_bytes()).hexdigest()
    with Image.open(path) as raw: im=ImageOps.exif_transpose(raw).convert('RGB'); im.load()
    boxes,status=segment(im); assigned,labels=panel_tech(f['pie_completo'],len(boxes)); accepted=[]
    for i,b in enumerate(boxes):
     crop=im.crop(b); stats,reasons=statistics(crop)
     if reasons: discards.append({'pmcid':pm,'figura':f['figura'],'archivo_original':str(path.relative_to(ROOT)),'bbox':b,'motivo':'|'.join(reasons)}); continue
     mixed=f.get('tipo_figura')=='mixta'
     area_fraction=((b[2]-b[0])*(b[3]-b[1]))/(im.width*im.height)
     if (status=='compuesta_sin_separar' and (len(labels)>1 or mixed)) or (mixed and not assigned[i] and area_fraction>CONFIG['mixta_area_sin_tecnica']): stats['tipo_estimado']='mixto_o_dudoso'
     accepted.append((i,b,crop,stats))
    # A rejected panel invalidates the one-to-one assignment for the remaining panels.
    if len(accepted)!=len(boxes): assigned=['']*len(boxes)
    for idx,(i,b,crop,stats) in enumerate(accepted,1):
     dest=CROPS/'ajuste1'/pm/f'{path.stem}__{CH}__{source_hash[:12]}_p{idx}.png'; dest.parent.mkdir(parents=True,exist_ok=True)
     crop.save(dest)
     rows.append({'pmcid':pm,'figura':f['figura'],'archivo_original':path.name,'ruta_original':path.relative_to(ROOT).as_posix(),
      'archivo_recorte':dest.relative_to(ROOT).as_posix(),'n_recortes_figura':len(accepted),**stats,
      'tecnica_asignada':assigned[i],'tecnicas_en_pie':'|'.join(f['tecnicas']),'etiqueta_subpanel':labels[i] if len(labels)==len(boxes) else '',
      'clase_modelo':r['clase_modelo'],'fold':r['fold'],'origen':'v0.1' if OLD in path.parents else 'nuevo',
      'x0':b[0],'y0':b[1],'x1':b[2],'y1':b[3],'estado_segmentacion':status,'lote':batch,'config_hash':CH,'tecnica_config_hash':TH,
      'sha256_pixeles':hashlib.sha256(crop.tobytes()).hexdigest(),'sha256_original':source_hash})
   except Exception as e: err.append({'archivo':str(path),'error':str(e)})
  dump(cache,{'pmcid':pm,'lote':batch,'config_hash':CH,'tecnica_config_hash':TH,'signature':signature,'recortes':rows,'descartes':discards,'errores':err})
  if (k+1)%20==0: print(f'lote {batch}: {k+1}/{len(subset)} artículos',flush=True)
 if changed:
  prog=json.loads((OUT/'progreso.json').read_text(encoding='utf-8'))
  if str(batch) in prog.get('revision_ajuste1',{}):
   for ext in ['json','png']:
    old=OUT/'muestras/ajuste1'/f'muestra_lote_{batch:02d}.{ext}'
    if old.exists(): shutil.copy2(old,old.with_name(f'{old.stem}_anterior_{time.time_ns()}.{ext}'))
   prog['revision_ajuste1'].pop(str(batch)); prog['ajuste1']['lotes_validados']=[int(k) for k,v in prog['revision_ajuste1'].items() if v['aprobado']]
   prog['articulos_hechos']=int(load(OUT/'orden_articulos.csv').lote.astype(int).isin(prog['ajuste1']['lotes_validados']).sum())
   if batch in [1,2]: prog['pausa_por_calidad_visual']=True
   dump(OUT/'progreso.json',prog)
  dump(OUT/f'validacion_ajuste1_lote_{batch:02d}.json',{'F3':'PENDIENTE','motivo':'Imágenes/configuración cambiaron o primera extracción; repetir validación técnica y visual.'})
 rebuild(); sample(batch)
 checkpoint(f'Lote {batch:02d}, ajuste 1: extracción guardada por artículo, CSV regenerados y muestra fija preparada. Pendiente de inspección visual; no cerrado.')
def rebuild():
 data=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((OUT/'resultados_ajuste1').glob('*.json'))]
 data=[d for d in data if d['config_hash']==CH]
 rows=[r for d in data if d['config_hash']==CH for r in d['recortes']]; ds=[r for d in data if d['config_hash']==CH for r in d['descartes']]
 csvout(OUT/'recortes_v02.csv',rows); csvout(OUT/'descartes_ajuste1.csv',ds)
 df=pd.DataFrame(rows)
 p=json.loads((OUT/'progreso.json').read_text(encoding='utf-8'))
 approved=[int(k) for k,v in p.get('revision_ajuste1',{}).items() if v['aprobado'] and (OUT/f'validacion_ajuste1_lote_{int(k):02d}.json').exists() and json.loads((OUT/f'validacion_ajuste1_lote_{int(k):02d}.json').read_text(encoding='utf-8'))['F3']=='PASS']
 if len(df):
  safe=df[df.lote.astype(int).isin(approved)]
  csvout(OUT/'tabla_modelo_v02.csv',safe[safe.tipo_estimado=='micrografia_probable'].to_dict('records'),columns=df.columns)
  csvout(OUT/'tabla_espectros_v02.csv',safe[(safe.tipo_estimado=='grafica_probable') & safe.tecnica_asignada.map(lambda x:bool(set(x.split('|'))&SPEC))].to_dict('records'),columns=df.columns)
 p['ajuste1']={**p.get('ajuste1',{}),'config_hash':CH,'articulos_extraidos':len(data),'recortes':len(rows),'descartes':len(ds),'lotes_extraidos':sorted(set(d['lote'] for d in data)),'lotes_validados':sorted(approved)}; dump(OUT/'progreso.json',p)
 print(json.dumps(p['ajuste1']))
def sample(batch,preserve=False):
 df=load(OUT/'recortes_v02.csv'); df=df[df.lote.astype(int)==batch].sort_values('archivo_recorte')
 rng=random.Random(CONFIG['seed']+batch); selected=[]
 micro=df[df.tipo_estimado=='micrografia_probable'].to_dict('records')
 graph=df[(df.tipo_estimado=='grafica_probable')&df.tecnicas_en_pie.map(lambda x:bool(set(x.split('|'))&SPEC))].to_dict('records')
 for pool in [micro,graph]: rng.shuffle(pool); selected.extend(pool[:2])
 chosen={r['archivo_recorte'] for r in selected}; rest=[r for r in df.to_dict('records') if r['archivo_recorte'] not in chosen]; rng.shuffle(rest); selected.extend(rest[:5-len(selected)])
 d=OUT/'muestras/ajuste1'; d.mkdir(parents=True,exist_ok=True)
 if preserve and (d/f'muestra_lote_{batch:02d}.json').exists():
  old=json.loads((d/f'muestra_lote_{batch:02d}.json').read_text(encoding='utf-8')); current=df.set_index('archivo_recorte').to_dict('index')
  selected=[dict(archivo_recorte=r['archivo_recorte'],**current[r['archivo_recorte']],**{k:r[k] for k in ['bien_extraida','veredicto'] if k in r}) for r in old]
 dump(d/f'muestra_lote_{batch:02d}.json',selected)
 micro_n=sum(r['tipo_estimado']=='micrografia_probable' for r in selected)
 graph_n=sum(r['tipo_estimado']=='grafica_probable' and bool(set(r['tecnicas_en_pie'].split('|'))&SPEC) for r in selected)
 dump(OUT/f'validacion_muestra_ajuste1_lote_{batch:02d}.json',{'n':len(selected),'micrografias_probables':micro_n,'graficas_con_tecnica_en_pie':graph_n,'mezcla_requerida':len(selected)==5 and micro_n>=2 and graph_n>=2,'semilla':CONFIG['seed']+batch})
 sheet=Image.new('RGB',(1800,5*450),'#f6f6f6'); draw=ImageDraw.Draw(sheet); font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21)
 for i,r in enumerate(selected):
  y=i*450; title=f"{i+1}. {r['pmcid']} · {r['figura']} · {r['tipo_estimado']}"
  draw.text((12,y+5),title,fill='black',font=font)
  draw.text((12,y+32),f"Panel: {r['tecnica_asignada'] or 'sin asignar'} | En pie: {r['tecnicas_en_pie']} | {r['estado_segmentacion']}",fill='#444',font=font)
  for x,col in [(12,'archivo_recorte'),(910,'ruta_original')]:
   with Image.open(ROOT/r[col]) as im: im=im.convert('RGB'); im.thumbnail((870,360)); sheet.paste(im,(x,y+65))
  draw.text((12,y+420),'Recorte',fill='black',font=font); draw.text((910,y+420),'Figura original',fill='black',font=font)
 sheet.save(d/f'muestra_lote_{batch:02d}.png')
 print(f'muestra {batch}: {len(selected)}; pool micro={len(micro)}, gráfica con técnica en pie={len(graph)}')
def validate(batch):
 dump(OUT/f'validacion_ajuste1_lote_{batch:02d}.json',{'F3':'EN_CURSO','visual':'no cerrar hasta finalizar las comprobaciones'})
 df=load(OUT/'recortes_v02.csv'); df=df[df.lote.astype(int)==batch]; errors=[]; reproducible={}; discarded_components=[]
 for r in df.to_dict('records'):
  try:
   if r.get('sha256_original'): assert hashlib.sha256((ROOT/r['ruta_original']).read_bytes()).hexdigest()==r['sha256_original'],'fuente cambió tras extraer'
   with Image.open(ROOT/r['ruta_original']) as raw: im=ImageOps.exif_transpose(raw).convert('RGB'); b=tuple(int(r[k]) for k in ['x0','y0','x1','y1']); rec=im.crop(b)
   with Image.open(ROOT/r['archivo_recorte']) as saved: assert saved.size==rec.size and hashlib.sha256(saved.convert('RGB').tobytes()).hexdigest()==hashlib.sha256(rec.tobytes()).hexdigest()==r['sha256_pixeles']
   assert 0<=b[0]<b[2]<=im.width and 0<=b[1]<b[3]<=im.height
   if r['ruta_original'] not in reproducible:
    diagnostics=[]; reproducible[r['ruta_original']]=segment(im,diagnostics)
    discarded_components.extend(dict(pmcid=r['pmcid'],figura=r['figura'],archivo_original=r['ruta_original'],lote=batch,**d) for d in diagnostics)
   checkboxes,checkstatus=reproducible[r['ruta_original']]
   assert b in checkboxes and checkstatus==r['estado_segmentacion'],'la caja no se reproduce con la configuración'
  except Exception as e: errors.append({'archivo_recorte':r['archivo_recorte'],'error':str(e)})
 official=load(ROOT/'curation/v0.1/tabla_modelo.csv').drop_duplicates('pmcid').set_index('pmcid').fold.to_dict()
 assert not df.archivo_recorte.duplicated().any(); assert df.groupby('pmcid').fold.nunique(dropna=False).le(1).all()
 assert all(r.fold==official.get(r.pmcid,'') for r in df.itertuples())
 figs=json.loads((OUT/'pies_ajuste1.json').read_text(encoding='utf-8'))
 for _,g in df.groupby('ruta_original',sort=False):
  rows=g.to_dict('records');f=next((f for f in figs[rows[0]['pmcid']] if f['figura']==rows[0]['figura']),{'pie_completo':''})
  expected,_=panel_tech(f['pie_completo'],len(rows))
  for r,t in zip(rows,expected): assert not r['tecnica_asignada'] or r['tecnica_asignada']==t,'técnica de panel no reproducible'
 csvout(OUT/f'descartes_componentes_lote_{batch:02d}.csv',discarded_components,columns=['pmcid','figura','archivo_original','lote','bbox','motivo','etapa'])
 prog=json.loads((OUT/'progreso.json').read_text(encoding='utf-8')); prior_visual=prog.get('revision_ajuste1',{}).get(str(batch)) if not errors else None
 dump(OUT/f'validacion_ajuste1_lote_{batch:02d}.json',{'F3':'PASS' if not errors else 'FAIL','recortes':len(df),'errores':errors,'bbox_pixeles_y_hash':'comparación completa con figura original','visual':prior_visual or 'pendiente de veredicto explícito'})
 print(f'F3 lote {batch}: recortes={len(df)}, errores={len(errors)}')
def review(batch,decisions):
 # Called only after the five contact-sheet samples have been inspected in this session.
 validation=json.loads((OUT/f'validacion_ajuste1_lote_{batch:02d}.json').read_text(encoding='utf-8'))
 assert validation['F3']=='PASS','La validación técnica debe pasar antes del cierre visual.'
 mix_path=OUT/f'validacion_muestra_ajuste1_lote_{batch:02d}.json'
 mix_ok=mix_path.exists() and json.loads(mix_path.read_text(encoding='utf-8'))['mezcla_requerida']
 p=OUT/'muestras/ajuste1'/f'muestra_lote_{batch:02d}.json'; selected=json.loads(p.read_text(encoding='utf-8'))
 assert len(decisions)==len(selected)==5
 for r,d in zip(selected,decisions): r.update({'bien_extraida':bool(d['ok']),'veredicto':d['veredicto']})
 dump(p,selected); score=sum(x['bien_extraida'] for x in selected)
 approved=score>=3 and mix_ok
 visual_status='PENDIENTE_MEZCLA' if not mix_ok else 'PASS' if approved else 'FAIL'
 prog=json.loads((OUT/'progreso.json').read_text(encoding='utf-8')); prog.setdefault('revision_ajuste1',{})[str(batch)]={'bien':score,'n':5,'aprobado':approved,'mezcla_requerida':mix_ok,'estado':visual_status,'muestra':str(p.relative_to(ROOT))}
 reviews=prog['revision_ajuste1']; ready=all(reviews.get(str(i),{}).get('aprobado',False) for i in [1,2])
 streak=0
 for k in sorted(map(int,reviews)):
  streak=streak+1 if reviews[str(k)]['bien']<3 else 0
 prog['pausa_por_calidad_visual']=not ready or streak>=2; prog['ajuste1']['lotes_validados']=sorted(int(i) for i,v in reviews.items() if v['aprobado'])
 order=load(OUT/'orden_articulos.csv'); prog['articulos_hechos']=int(order.lote.astype(int).isin(prog['ajuste1']['lotes_validados']).sum()); prog['lote_actual']=batch
 batchrows=load(OUT/'recortes_v02.csv');batchrows=batchrows[batchrows.lote.astype(int)==batch]
 prog['ultimo_lote']={'lote':batch,'metodo':'ajuste1','recortes':len(batchrows),'articulos_con_recorte':batchrows.pmcid.nunique(),'muestra_n':5,'bien_extraidas_muestra':score,'validacion_tecnica':'PASS','validacion_visual':visual_status,'siguiente_paso':'pausa de calidad' if prog['pausa_por_calidad_visual'] else f'lote {batch+1} / pendientes de imágenes y validación'}
 prog['lotes']=[{'lote':int(k),'inicio_indice':(int(k)-1)*100,'fin_indice':min(int(k)*100,len(order)),'metodo':'ajuste1',**v} for k,v in sorted(reviews.items(),key=lambda x:int(x[0]))]
 validation['visual']={'bien':score,'n':5,'aprobado':approved,'mezcla_requerida':mix_ok,'estado':visual_status}; dump(OUT/f'validacion_ajuste1_lote_{batch:02d}.json',validation)
 dump(OUT/'progreso.json',prog); checkpoint(f'Lote {batch:02d} ajuste 1: muestra inspeccionada {score}/5; {visual_status}. Pausa={prog["pausa_por_calidad_visual"]}. Veredictos individuales en {p.relative_to(OUT)}.')
 print(f'revisión lote {batch}: {score}/5; estado={visual_status}; pausa={prog["pausa_por_calidad_visual"]}')

def resume_batch():
 prog=json.loads((OUT/'progreso.json').read_text(encoding='utf-8'));reviews=prog.get('revision_ajuste1',{});extracted=prog.get('ajuste1',{}).get('lotes_extraidos',[])
 if prog.get('pausa_por_calidad_visual') and all(str(k) in reviews for k in [1,2]): raise SystemExit('Pausa por control visual: ajuste pendiente, no avanzar.')
 pending=sorted(set(extracted)-set(map(int,reviews)))
 if pending: print(f'Retomando lote {pending[0]} pendiente de control visual; se reutilizan artículos sin cambios.');return pending[0]
 total=math.ceil(len(load(OUT/'orden_articulos.csv'))/100)
 unprocessed=sorted(set(range(1,total+1))-set(extracted))
 if unprocessed:return unprocessed[0]
 figures=json.loads((OUT/'pies_ajuste1.json').read_text(encoding='utf-8'));changed=[]
 for path in (OUT/'resultados_ajuste1').glob('*.json'):
  d=json.loads(path.read_text(encoding='utf-8'));now=[[str(src),src.stat().st_size,src.stat().st_mtime_ns] for src,_ in sources(d['pmcid'],figures.get(d['pmcid'],[]))]
  if now!=d['signature'] or d.get('config_hash')!=CH or d.get('tecnica_config_hash')!=TH:changed.append(d['lote'])
 if changed:return min(changed)
 print('Primera pasada local terminada; no hay archivos nuevos. Consultar pendientes de imágenes y lotes no aprobados.');return None

if __name__=='__main__':
 parser=argparse.ArgumentParser(); parser.add_argument('accion',choices=['inventario','lote','validar','rebuild']); parser.add_argument('--lote',type=int); args=parser.parse_args()
 if args.accion=='inventario': inventory()
 elif args.accion=='lote':
  batch=args.lote if args.lote is not None else resume_batch()
  if batch is not None:process_batch(batch)
 elif args.accion=='validar': validate(args.lote)
 else: rebuild()
