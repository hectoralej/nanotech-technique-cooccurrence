import hashlib,json
from pathlib import Path
import pandas as pd
import ajuste1 as a
def load(p):return pd.read_csv(p,dtype=str,keep_default_na=False,encoding='utf-8-sig')
p=json.loads((a.OUT/'progreso.json').read_text(encoding='utf-8'));order=load(a.OUT/'orden_articulos.csv');inv=load(a.OUT/'inventario_figuras.csv');r=load(a.OUT/'recortes_v02.csv')
official=load(a.ROOT/'curation/v0.1/tabla_modelo.csv').drop_duplicates('pmcid').set_index('pmcid')
checks={
 '1707_articulos_ordenados_sin_duplicados':len(order)==1707 and not order.pmcid.duplicated().any(),
 'E1_antes_de_E2':order.tier.tolist()==sorted(order.tier.tolist()),
 'inventario_sin_claves_duplicadas':not inv.duplicated(['pmcid','figura','archivo_grafico']).any(),
 'folds_inventario_oficiales':all(x.fold==official.fold.get(x.pmcid,'') for x in inv.itertuples()),
 'un_solo_fold_por_articulo':r.groupby('pmcid').fold.nunique(dropna=False).le(1).all(),
 'clases_y_folds_recortes_oficiales':all(x.fold==official.fold.get(x.pmcid,'') and x.clase_modelo==official.clase_modelo.get(x.pmcid,'') for x in r.itertuples()),
 'archivos_recorte_unicos':not r.archivo_recorte.duplicated().any(),
 'todos_los_recortes_existen':all((a.ROOT/f).exists() for f in r.archivo_recorte),
 'configuracion_actual':r.config_hash.eq(a.CH).all() and r.tecnica_config_hash.eq(a.TH).all(),
}
figmetadata=json.loads((a.OUT/'pies_ajuste1.json').read_text(encoding='utf-8'));tech_ok=True
for _,g in r.groupby('ruta_original',sort=False):
 rows=g.to_dict('records');f=next((f for f in figmetadata[rows[0]['pmcid']] if f['figura']==rows[0]['figura']),{'pie_completo':''});expected,_=a.panel_tech(f['pie_completo'],len(rows))
 tech_ok=tech_ok and all(not x['tecnica_asignada'] or x['tecnica_asignada']==t for x,t in zip(rows,expected))
checks['tecnicas_panel_regla_actual']=tech_ok
reviews=p.get('revision_ajuste1',{});accepted=p['ajuste1'].get('lotes_validados',[]);batchchecks={}
for batch in p['ajuste1']['lotes_extraidos']:
 v=json.loads((a.OUT/f'validacion_ajuste1_lote_{batch:02d}.json').read_text(encoding='utf-8'))
 selected=json.loads((a.OUT/'muestras/ajuste1'/f'muestra_lote_{batch:02d}.json').read_text(encoding='utf-8'))
 review=reviews.get(str(batch))
 assessed=all('bien_extraida' in x and 'veredicto' in x for x in selected)
 mix=(sum(x['tipo_estimado']=='micrografia_probable' for x in selected)>=2 and sum(x['tipo_estimado']=='grafica_probable' and bool(set(x['tecnicas_en_pie'].split('|'))&a.SPEC) for x in selected)>=2)
 batchchecks[str(batch)]={'F3':v['F3'],'muestra_n':len(selected),'mezcla_2_micros_2_graficas':mix,'veredictos_presentes':assessed,'bien':review.get('bien') if review else None,'aprobado':batch in accepted}
 if batch in accepted:checks[f'lote_{batch}_cierre_valido']=v['F3']=='PASS' and len(selected)==5 and assessed and mix and sum(x['bien_extraida'] for x in selected)>=3
 for x in selected:
  if review: assert x.get('bien_extraida') in [True,False]
for name,kind in [('tabla_modelo_v02.csv','micrografia_probable'),('tabla_espectros_v02.csv','grafica_probable')]:
 t=load(a.OUT/name);checks[name+'_solo_aprobados']=t.lote.astype(int).isin(accepted).all();checks[name+'_tipo']=t.tipo_estimado.eq(kind).all();checks[name+'_subconjunto_recortes']=set(t.archivo_recorte).issubset(set(r.archivo_recorte))
manifest=json.loads((a.OUT/'muestra_etiquetado_300.json').read_text(encoding='utf-8'));checks['muestra_humana_300_fija']=len(manifest)==300 and len({x['archivo_recorte'] for x in manifest})==300
checks['referencias_humanas_conservadas']=all((a.ROOT/x['ruta_original_etiquetado']).exists() and hashlib.sha256((a.ROOT/x['ruta_original_etiquetado']).read_bytes()).hexdigest()==x['sha256_original_etiquetado'] for x in manifest)
ui=json.loads((a.OUT/'validacion_etiquetado.json').read_text(encoding='utf-8'));checks['interfaz_pruebas_funcionales']=ui.get('prueba_funcional_js',{}).get('estado')=='PASS'
rules=json.loads((a.OUT/'REGRESIONES_AJUSTE1.json').read_text(encoding='utf-8'));checks['reglas_casos_regresion']=rules['estado']=='PASS'
checks['bloqueo_cierre_regresion']=json.loads((a.OUT/'REGRESION_CIERRES_AJUSTE1.json').read_text(encoding='utf-8'))['estado']=='PASS'
checks={k:bool(v) for k,v in checks.items()};failed=[k for k,v in checks.items() if not v]
pending=load(a.OUT/'pendientes_primeros_400.csv');rejected=[int(k) for k,v in reviews.items() if not v['aprobado']];done=set(r.pmcid)
stale=[];figs=json.loads((a.OUT/'pies_ajuste1.json').read_text(encoding='utf-8'))
for cache in (a.OUT/'resultados_ajuste1').glob('*.json'):
 d=json.loads(cache.read_text(encoding='utf-8'));now=[(str(src),src.stat().st_size,src.stat().st_mtime_ns) for src,_ in a.sources(d['pmcid'],figs.get(d['pmcid'],[]))]
 if [list(x) for x in now]!=d['signature']:stale.append({'pmcid':d['pmcid'],'lote':d['lote'],'motivo':'nuevas_imagenes_o_firma_cambiada; requiere reextraer y revalidar'})
pd.DataFrame(stale,columns=['pmcid','lote','motivo']).to_csv(a.OUT/'articulos_con_imagenes_nuevas_por_reprocesar.csv',index=False,encoding='utf-8-sig')
result={'validacion_artefactos':'PASS' if not failed else 'FAIL','comprobaciones':checks,'fallos':failed,'lotes':batchchecks,
 'lotes_no_aprobados':rejected,'lotes_pendientes_por_mezcla':[int(k) for k,v in reviews.items() if v.get('estado')=='PENDIENTE_MEZCLA'],'lotes_sin_procesar':sorted(set(order.lote.astype(int))-set(p['ajuste1']['lotes_extraidos'])),
 'primeros_400_pendientes':pending.pmcid.tolist(),'articulos_con_datos_nuevos_no_reprocesados':stale,
 'cobertura_total_satisfecha':not pending.pmcid.tolist() and not rejected and len(p['ajuste1']['lotes_extraidos'])==18 and not stale,
 'nota':'PASS verifica coherencia y restricciones de las tablas entregadas; no equivale a que todos los lotes o todas las imágenes pendientes estén completados.',
 'html_visual':ui.get('prueba_navegador')}
a.dump(a.OUT/'VALIDACION_GLOBAL_AJUSTE1.json',result);print(json.dumps({k:result[k] for k in ['validacion_artefactos','fallos','lotes_no_aprobados','lotes_sin_procesar','cobertura_total_satisfecha']},ensure_ascii=False));print('firmas nuevas por reprocesar',len(stale))
if failed:raise SystemExit(1)
