"""Migración de clasificación exclusivamente: conserva cajas, imágenes y hashes de píxeles."""
import json,shutil
from collections import Counter
from PIL import Image
import ajuste1 as a
old=json.loads((a.OUT/'config_ajuste1.json').read_text(encoding='utf-8'))
assert {k:v for k,v in old.items() if k!='version'}=={k:v for k,v in a.CONFIG.items() if k not in ['version','ejes_fraccion_lineas_max']},'La migración solo permite cambiar el detector de ejes.'
backup=a.OUT/'historial_ajuste1_antes_ejes_delgados';backup.mkdir(exist_ok=True)
for n in ['recortes_v02.csv','progreso.json','config_ajuste1.json','revision_ajuste1.py','INFORME_IMAGENES_V02.md']:
 shutil.copy2(a.OUT/n,backup/n)
if not (backup/'muestras').exists(): shutil.copytree(a.OUT/'muestras/ajuste1',backup/'muestras')
figs=json.loads((a.OUT/'pies_ajuste1.json').read_text(encoding='utf-8')); dropped=0; total=0; lots=set()
for path in (a.OUT/'resultados_ajuste1').glob('*.json'):
 data=json.loads(path.read_text(encoding='utf-8')); rows=[]
 for r in data['recortes']:
  with Image.open(a.ROOT/r['archivo_recorte']) as im: stats,reasons=a.statistics(im)
  if reasons:
   data['descartes'].append({'pmcid':r['pmcid'],'figura':r['figura'],'archivo_original':r['ruta_original'],'bbox':[r[k] for k in ['x0','y0','x1','y1']],'motivo':'|'.join(reasons)});dropped+=1;continue
  f=next((f for f in figs[r['pmcid']] if f['figura']==r['figura']),{'tipo_figura':'otra','pie_completo':''})
  _,labels=a.panel_tech(f['pie_completo'],int(r['n_recortes_figura']))
  with Image.open(a.ROOT/r['ruta_original']) as im: area=((r['x1']-r['x0'])*(r['y1']-r['y0']))/(im.width*im.height)
  mixed=f.get('tipo_figura')=='mixta'
  if (r['estado_segmentacion']=='compuesta_sin_separar' and (len(labels)>1 or mixed)) or (mixed and not r['tecnica_asignada'] and area>a.CONFIG['mixta_area_sin_tecnica']): stats['tipo_estimado']='mixto_o_dudoso'
  r.update(stats);r['config_hash']=a.CH;rows.append(r);total+=1
 counts=Counter(r['ruta_original'] for r in rows)
 for r in rows:
  if counts[r['ruta_original']]!=int(r['n_recortes_figura']):r['tecnica_asignada']='';r['etiqueta_subpanel']=''
  r['n_recortes_figura']=counts[r['ruta_original']]
 data['recortes']=rows;data['config_hash']=a.CH;data['clasificacion_migrada_sin_cambio_de_pixeles']=True;a.dump(path,data);lots.add(data['lote'])
a.dump(a.OUT/'config_ajuste1.json',a.CONFIG);a.rebuild()
for lot in sorted(lots):
 p=a.OUT/f'validacion_ajuste1_lote_{lot:02d}.json';v=json.loads(p.read_text(encoding='utf-8'));v['visual']='pendiente tras revisión de clasificación';v['recortes']=sum(1 for r in a.load(a.OUT/'recortes_v02.csv').to_dict('records') if int(r['lote'])==lot);v['clasificacion_revision']=a.CH;v['nota_migracion']='Cajas y hash de píxeles intactos; validación F3 previa conservada para las filas restantes.';a.dump(p,v);a.sample(lot)
prog=json.loads((a.OUT/'progreso.json').read_text(encoding='utf-8'));prog['revision_ajuste1']={};prog['ajuste1']['lotes_validados']=[];prog['pausa_por_calidad_visual']=True;prog['articulos_hechos']=0;a.dump(a.OUT/'progreso.json',prog)
a.dump(a.OUT/'MIGRACION_EJES.json',{'config_anterior':old,'config_actual':a.CONFIG,'pixeles_y_cajas_modificados':False,'recortes_reclasificados':total,'rechazados_por_filtro_actualizado':dropped,'veredictos_previos':'archivados; pendientes de nueva inspección'})
a.checkpoint(f'Revisión del detector de ejes: {total} recortes reclasificados sin cambiar cajas/píxeles; descartes nuevos={dropped}. Se invalidaron expresamente los cierres visuales para re-inspeccionar las muestras.');print('migración terminada',total,dropped)
