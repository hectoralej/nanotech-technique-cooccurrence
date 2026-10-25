"""Retira asignaciones ambiguas de pies con etiquetas en sufijo; no cambia píxeles/cajas."""
import json,shutil
from PIL import Image
import ajuste1 as a
figs=json.loads((a.OUT/'pies_ajuste1.json').read_text(encoding='utf-8'));backup=a.OUT/'historial_tecnicas_antes_prefijo';backup.mkdir(exist_ok=True)
if not (backup/'muestras').exists():shutil.copytree(a.OUT/'muestras/ajuste1',backup/'muestras')
changed=0; lots=set()
for p in (a.OUT/'resultados_ajuste1').glob('*.json'):
 d=json.loads(p.read_text(encoding='utf-8'));groups={}
 for r in d['recortes']:groups.setdefault(r['ruta_original'],[]).append(r)
 for rows in groups.values():
  f=next((f for f in figs[d['pmcid']] if f['figura']==rows[0]['figura']),{'pie_completo':'','tipo_figura':'otra'})
  ts,labels=a.panel_tech(f['pie_completo'],len(rows))
  with Image.open(a.ROOT/rows[0]['ruta_original']) as im: area_original=im.width*im.height
  for i,r in enumerate(rows):
   changed+=r['tecnica_asignada']!=ts[i];r['tecnica_asignada']=ts[i];r['tecnica_config_hash']=a.TH
   r['etiqueta_subpanel']=labels[i] if len(labels)==len(rows) else ''
   if not ts[i] and f.get('tipo_figura')=='mixta' and (r['x1']-r['x0'])*(r['y1']-r['y0'])/area_original>a.CONFIG['mixta_area_sin_tecnica']:r['tipo_estimado']='mixto_o_dudoso'
 d['tecnica_config_hash']=a.TH;a.dump(p,d);lots.add(d['lote'])
a.dump(a.OUT/'reglas_tecnica_ajuste1.json',a.TECNICA_CONFIG);a.rebuild()
for lot in sorted(lots):a.sample(lot,preserve=True)
previous=json.loads((a.OUT/'MIGRACION_TECNICAS.json').read_text(encoding='utf-8')).get('asignaciones_cambiadas',0) if (a.OUT/'MIGRACION_TECNICAS.json').exists() else 0
a.dump(a.OUT/'MIGRACION_TECNICAS.json',{'asignaciones_cambiadas':previous+changed,'pixeles_y_cajas_modificados':False,'muestras_aleatorias_conservadas':True,'regla':a.TECNICA_CONFIG})
a.checkpoint(f'Revisión estricta de técnicas: se retiraron/corrigieron {changed} asignaciones ambiguas en pies de sufijo. Misma muestra aleatoria, mismas cajas y píxeles; metadatos actualizados.');print('asignaciones cambiadas',changed)
