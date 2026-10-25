import json
from pathlib import Path
from collections import Counter
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'modelos/imagenes_v02'
def load(p): return pd.read_csv(p,dtype=str,keep_default_na=False,encoding='utf-8-sig')
p=json.loads((OUT/'progreso.json').read_text(encoding='utf-8')); inv=load(OUT/'inventario_figuras.csv'); crops=load(OUT/'recortes_v02.csv'); order=load(OUT/'orden_articulos.csv')
valid=[k for k in p.get('ajuste1',{}).get('lotes_validados',[]) if (OUT/f'validacion_ajuste1_lote_{k:02d}.json').exists() and json.loads((OUT/f'validacion_ajuste1_lote_{k:02d}.json').read_text(encoding='utf-8'))['F3']=='PASS']; p['ajuste1']['lotes_validados']=valid
approved=crops[crops.lote.astype(int).isin(valid)]
approved[approved.tipo_estimado=='micrografia_probable'].to_csv(OUT/'tabla_modelo_v02.csv',index=False,encoding='utf-8-sig')
spectral={'XRD','FTIR','UVVis','SAXS','EDS','Raman','DLS','zeta'}
espectros=approved[(approved.tipo_estimado=='grafica_probable')&approved.tecnica_asignada.map(lambda x:bool(set(x.split('|'))&spectral))]
espectros.to_csv(OUT/'tabla_espectros_v02.csv',index=False,encoding='utf-8-sig')
approved[(approved.tipo_estimado=='grafica_probable')&approved.tecnica_asignada.eq('')].to_csv(OUT/'graficas_sin_tecnica_asignada.csv',index=False,encoding='utf-8-sig')
inv['_figura_id']=inv.pmcid+'|'+inv.figura
inv.groupby(['lote','clase_modelo','tipo_figura','ya_en_base']).agg(referencias_archivo=('archivo_grafico','size'),figuras_logicas=('_figura_id','nunique')).reset_index().to_csv(OUT/'conteos_por_lote_clase.csv',index=False,encoding='utf-8-sig')
crops.groupby(['lote','clase_modelo','tipo_estimado']).size().rename('recortes').reset_index().to_csv(OUT/'recortes_por_lote_clase.csv',index=False,encoding='utf-8-sig')
figures=crops.drop_duplicates(['pmcid','ruta_original']); compound=int(figures.estado_segmentacion.eq('compuesta_sin_separar').sum()); pct=100*compound/max(len(figures),1)
caches=[json.loads(f.read_text(encoding='utf-8')) for f in (OUT/'resultados_ajuste1').glob('*.json')]
parts=[pd.DataFrame([r for d in caches for r in d.get('descartes',[])],columns=['pmcid','figura','archivo_original','bbox','motivo'])]
parts.extend(load(f) for f in sorted(OUT.glob('descartes_componentes_lote_*.csv')))
discards=pd.concat(parts,ignore_index=True);discards.to_csv(OUT/'descartes_ajuste1.csv',index=False,encoding='utf-8-sig')
reasons=Counter(t for s in discards.motivo for t in s.split('|'))
files=set()
for base in ['imagenes','imagenes_v02']:
 files.update((base,f.parent.name,f.name) for f in (ROOT/'producto'/base).glob('*/*') if f.is_file() and f.suffix.lower() in {'.jpg','.jpeg','.gif','.png','.webp','.tif','.tiff'})
availability=[]
for r in inv.to_dict('records'):
 name=r['archivo_grafico']; names=[str(Path(name).with_suffix('.jpg')),name] if name.lower().endswith('.gif') else [name]; path=''
 for n in names:
  for base in ['imagenes_v02','imagenes']:
   if (base,r['pmcid'],n) in files: path=f'producto/{base}/{r["pmcid"]}/{n}'; break
  if path: break
 availability.append({'pmcid':r['pmcid'],'figura':r['figura'],'archivo_inventario':name,'lote':r['lote'],'disponible':int(bool(path)),'ruta_disponible':path})
pd.DataFrame(availability).to_csv(OUT/'disponibilidad_ajuste1.csv',index=False,encoding='utf-8-sig')
unavailable=sum(not r['disponible'] for r in availability)
summary={'articulos_inventariados':len(order),'figuras_logicas':len(inv.drop_duplicates(['pmcid','figura'])),'referencias_archivo':len(inv),
 'lotes_extraidos':p.get('ajuste1',{}).get('lotes_extraidos',[]),'lotes_aprobados':valid,'articulos_lotes_aprobados':int(order.lote.astype(int).isin(valid).sum()),
 'recortes_extraidos':len(crops),'recortes_lotes_aprobados':len(approved),'figuras_procesadas':len(figures),'compuesta_sin_separar':compound,'porcentaje_compuesta_sin_separar':round(pct,2),
 'descartes':len(discards),'motivos_descarte':dict(reasons),'referencias_archivo_pendientes_imagen':unavailable,
 'componentes_previos_descartados':sum(len(x) for x in parts[1:]),'recortes_descartados_por_filtros':len(parts[0]),
 'micrografias_provisionales_aprobadas':int(approved.tipo_estimado.eq('micrografia_probable').sum()),'espectros_tecnica_panel_aprobados':len(espectros),
 'imagenes_originales':sum(base=='imagenes' for base,_,_ in files),'imagenes_en_destino_claude':sum(base=='imagenes_v02' for base,_,_ in files),
 'errores_por_archivo':sum(len(d.get('errores',[])) for d in caches),'articulos_sin_imagen_local':sum(not d.get('signature') for d in caches),
 'aviso':'Aprobación por muestreo, tipos provisionales; ninguna etiqueta humana fue inventada.'}
summary['articulos_con_recorte_en_lotes_aprobados']=approved.pmcid.nunique()
first400=set(order.iloc[:400].pmcid); actual=set(approved.pmcid); missing400=first400-actual
summary['primeros_400_con_recorte']=len(first400&actual);summary['primeros_400_pendientes_imagen_o_lote']=len(missing400)
old_stems={(pm,Path(name).stem) for base,pm,name in files if base=='imagenes'}
new_figs=figures[(figures.origen=='nuevo')&pd.Series([(pm,Path(name).stem) not in old_stems for pm,name in zip(figures.pmcid,figures.archivo_original)],index=figures.index)]
summary['articulos_que_ganaron_figuras_utilizadas']=new_figs.pmcid.nunique();summary['figuras_nuevas_utilizadas']=len(new_figs)
new_figs.groupby(['lote','clase_modelo']).agg(articulos_que_ganaron=('pmcid','nunique'),figuras_nuevas=('ruta_original','size')).reset_index().to_csv(OUT/'ganancias_imagenes_por_lote_clase.csv',index=False,encoding='utf-8-sig')
pending=[{'pmcid':d['pmcid'],'lote':d['lote'],'motivo':'sin_imagen_local_utilizable','archivo_candidato': '|'.join(inv.loc[inv.pmcid==d['pmcid'],'archivo_grafico'].unique())} for d in caches if not d.get('signature')]
pd.DataFrame(pending,columns=['pmcid','lote','motivo','archivo_candidato']).to_csv(OUT/'pendientes_imagen_articulos.csv',index=False,encoding='utf-8-sig')
order[order.pmcid.isin(missing400)].to_csv(OUT/'pendientes_primeros_400.csv',index=False,encoding='utf-8-sig')
p['cobertura_local']={'articulos_con_recorte_aprobado':summary['articulos_con_recorte_en_lotes_aprobados'],'primeros_400_con_recorte':summary['primeros_400_con_recorte'],'primeros_400_pendientes':sorted(missing400),'articulos_sin_imagen_utilizable':[r['pmcid'] for r in pending]}
p['errores']=[dict(pmcid=d['pmcid'],lote=d['lote'],**e) for d in caches for e in d.get('errores',[])]
(OUT/'progreso.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'RESUMEN_AJUSTE1.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
reviews=p.get('revision_ajuste1',{}); lines=[]
for lot in sorted(p.get('ajuste1',{}).get('lotes_extraidos',[])):
 d=crops[crops.lote.astype(int)==lot]; v=reviews.get(str(lot),{}); lines.append(f'| {lot:02d} | {len(order[order.lote.astype(int)==lot])} | {len(d)} | {v.get("bien","pendiente")}/5 | {"aprobado" if v.get("aprobado") else "pendiente/no aprobado"} |')
report=f'''# Imágenes y espectros v0.2 · ajuste 1

Inventario completo: {len(order)} artículos E1/E2, {summary['figuras_logicas']} figuras lógicas y {len(inv)} referencias gráficas. Las alternativas GIF/JPG se conservan como referencias para la descarga, pero cada figura se recorta una sola vez usando el JPG grande disponible. Claude gestiona las descargas; este flujo solo usa archivos locales.

| Lote | Artículos | Recortes | Muestra visual | Estado |
|---|---:|---:|---:|---|
{chr(10).join(lines)}

Las muestras son autoevaluaciones del asistente, no etiquetas humanas. Hay {summary['articulos_con_recorte_en_lotes_aprobados']} artículos con recorte en lotes aprobados. Primeros 400: {summary['primeros_400_con_recorte']} con recorte y {summary['primeros_400_pendientes_imagen_o_lote']} pendientes de imagen; meta no cumplida. Ver `pendientes_primeros_400.csv`. Los lotes 8 y 11 fallaron el muestreo. El 18 tiene 3/5 útiles, pero cero gráficas elegibles: queda `PENDIENTE_MEZCLA`, excluido aunque alcance 3/5. No se redujo la exigencia.

Las tablas para modelos contienen solo los lotes con validación técnica y muestra aprobadas: {summary['micrografias_provisionales_aprobadas']} micrografías probables y {len(espectros)} gráficas con técnica espectral asignada de forma inequívoca al panel. Las demás gráficas se conservan en `graficas_sin_tecnica_asignada.csv`. Las clases siguen siendo provisionales hasta revisión humana o clasificación del clúster.

Se procesaron {len(figures)} imágenes de figura; {compound} ({pct:.2f}%) quedaron con estado `compuesta_sin_separar`. Este estado significa que la segmentación conservó la figura completa, no prueba que todas ellas sean composiciones. El total disponible actualmente es {summary['imagenes_originales']} imágenes originales y {summary['imagenes_en_destino_claude']} archivos del destino nuevo; esa cifra incluye alternativas que se deduplican antes de recortar. Se utilizaron {summary['figuras_nuevas_utilizadas']} figuras que no estaban en la carpeta antigua, beneficiando a {summary['articulos_que_ganaron_figuras_utilizadas']} artículos; no se cuentan como ganancia los duplicados con el mismo nombre base.

## Método y límites

Se analiza la figura con dimensión máxima 1.400 px, manteniendo su proporción. La máscara no blanca usa mínimo RGB <245; dilatación 3×3, componentes conexas, unión de cajas a ≤5 px y anexión de texto/escala a ≤22 px. Los componentes principales ocupan ≥3% del área. Se combinan con franjas de tinta ≤1,2% y ancho ≥2 px. Todas las cajas finales se expresan en píxeles del original `(x0,y0,x1,y1)`, con extremo derecho/inferior exclusivo. Los recortes no solapan; ante ambigüedad se conserva la figura completa. Figuras mixtas o con subpaneles explícitos sin separar se marcan dudosas.

Se descartan fracción de tinta <2%, <120 píxeles de tinta en la imagen de análisis, proporción >8:1 y regiones de poca tinta/variación de gris compatibles con texto aislado. Descartes observados: {summary['componentes_previos_descartados']} componentes pequeños no asociados antes de formar recortes, y {summary['recortes_descartados_por_filtros']} candidatos por filtros de recorte; motivos: {dict(reasons) or 'ninguno activado en esta corrida'}. Se registran las cajas y motivos en `descartes_ajuste1.csv`. La prueba específica del antiguo recorte “drying” activa poca tinta y proporción extrema aunque ese candidato ya no se genera con el método nuevo.

Ilustración probable: >78% de la tinta concentrada en 12 colores RGB cuantizados (16 niveles/canal), saturación media de la tinta >0,12 y sin ejes ortogonales detectables. Los demás tipos usan entropía de gris, tinta, saturación y ejes; no son probabilidades calibradas. Un dibujo y una gráfica pueden compartir estadística: la hoja humana permite corregirlos.

`tecnicas_en_pie` contiene solo nombres canónicos extraídos del pie limpio. `tecnica_asignada` queda vacía salvo coincidencia del número de recortes con etiquetas de subpanel consecutivas y mención explícita de técnica en ese subpanel. Se aceptan etiquetas de prefijo; ante sufijos ambiguos como “DLS (A), SEM (B)” se abstiene. No se infiere DLS de “distribución de tamaño”; SEM estadístico se excluye. Cada figura conserva el fold oficial del artículo. La validación compara todos los recortes con su caja en el original orientado mediante EXIF y su hash de píxeles, y reproduce la segmentación.

Discrepancia comprobada visualmente: en PMC10605403, figura 3, el pie intercambia las técnicas de los subpaneles respecto de la imagen. Se retiraron todas las asignaciones de esa figura mediante una abstención por hash del pie, documentada en `reglas_tecnica_ajuste1.json`; no se corrigió ni reinterpretó el artículo. El caso no cuenta como positivo en la muestra del lote 17. Esta observación limita la expresión «inequívoca»: la regla textual no garantiza que el pie publicado sea correcto.

## Evidencia y entrega

`muestras/ajuste1/` guarda las hojas y los veredictos por elemento. `validacion_ajuste1_lote_NN.json`, `CHECKPOINTS.md` y `progreso.json` documentan cada cierre. `conteos_por_lote_clase.csv` y `recortes_por_lote_clase.csv` contienen los conteos detallados. El inventario completo no depende del control visual; {unavailable} referencias aún no tienen imagen local (pueden ser alternativas del mismo gráfico). No se atribuyen diferencias de calidad a revistas/editoriales sin una revisión específica.

`producto/imagenes_recortes/ETIQUETADO.html` presenta 300 casos fijos, con original al lado, teclas 1–4, anterior, guardado local y exportación `etiquetas_humanas.csv`. Las predicciones están ocultas inicialmente para reducir sesgo. Las etiquetas humanas comienzan vacías. Los originales de referencia se copian sin editar a una carpeta derivada para que la hoja no cambie durante descargas posteriores. Las funciones y 600 rutas se comprobaron en un DOM simulado; el navegador de la aplicación bloqueó `file://`, por lo que su apariencia en navegador no se pudo verificar. No se entrenó ningún modelo ni se ejecutó git.
'''
(OUT/'INFORME_IMAGENES_V02.md').write_text(report,encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
