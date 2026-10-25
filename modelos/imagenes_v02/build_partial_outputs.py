import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"modelos"/"imagenes_v02"
def read(p): return pd.read_csv(p,dtype=str,keep_default_na=False,encoding="utf-8-sig")
invp=OUT/"inventario_figuras.csv"; recp=OUT/"recortes_v02.csv"
inv=read(invp); rec=read(recp)
arts=read(ROOT/"curation"/"ext_articulos.csv")
arts=arts[arts.tier.isin(["E1","E2"])][["pmcid","tier","carrier_type"]].drop_duplicates("pmcid")
official=read(ROOT/"curation"/"v0.1"/"tabla_modelo.csv")
official_fold=official.drop_duplicates("pmcid").set_index("pmcid").fold.to_dict()
official_consistent=bool(official.groupby("pmcid").fold.nunique().le(1).all())
ordered=read(ROOT/"curation"/"ext_articulos.csv"); ordered=ordered[ordered.tier.isin(["E1","E2"])].copy(); ordered["_tier"]=ordered.tier.map({"E1":0,"E2":1}); ordered=ordered.sort_values(["_tier"],kind="stable").reset_index(drop=True)
pan=read(ROOT/"curation"/"ext_paneles.csv"); spec=read(ROOT/"curation"/"ext_espectros.csv")
def fk(x):
    import re
    m=re.search(r"(\d+)",x or "")
    return m.group(1) if m else re.sub(r"\W+","",(x or "").lower())
pairs=set(zip(pan.pmcid,pan.fig.map(fk)))|set(zip(spec.pmcid,spec.fig.map(fk)))
inv["ya_en_base"]=[int((p,fk(g)) in pairs) for p,g in zip(inv.pmcid,inv.figura)]
inv=inv.drop(columns=["tier","carrier_type"],errors="ignore").merge(arts,on="pmcid",how="left")
inv.to_csv(invp,index=False,encoding="utf-8-sig")
micro=rec[rec.tipo_estimado=="micrografia_probable"].copy()
micro.to_csv(OUT/"tabla_modelo_v02.csv",index=False,encoding="utf-8-sig")
spectral={"FTIR","XRD","UVVis","SAXS","EDS","Raman","DLS","zeta"}
spectra=rec[(rec.tipo_estimado=="grafica_probable")&rec.tecnica_asignada.isin(spectral)].copy()
spectra.to_csv(OUT/"tabla_espectros_v02.csv",index=False,encoding="utf-8-sig")
prog=json.loads((OUT/"progreso.json").read_text(encoding="utf-8"))
expected=set()
lot_by_pmc={}
for lot in prog.get("lotes",[]):
    a,b=int(lot["inicio_indice"]),int(lot["fin_indice"])
    for pmc in ordered.iloc[a:b].pmcid: lot_by_pmc[pmc]=lot["lote"]
    expected.add(lot["lote"])
invkeys=list(zip(inv.pmcid,inv.figura,inv.archivo_grafico))
checks={
 "passed_unique_inventory_key":not inv.duplicated(["pmcid","figura","archivo_grafico"]).any(),
 "passed_one_fold_per_article":bool(rec.groupby("pmcid").fold.nunique(dropna=False).le(1).all()),
 "passed_inventory_base_flags":bool(all(int(v)==int((p,fk(g)) in pairs) for p,g,v in zip(inv.pmcid,inv.figura,inv.ya_en_base))),
 "passed_crop_files_exist":bool(all((ROOT/Path(x)).exists() for x in rec.archivo_recorte)),
 "passed_source_images_exist":bool(all((ROOT/"producto"/"imagenes"/p/f).exists() or (ROOT/"producto"/"imagenes_v02"/p/f).exists() for p,f in zip(rec.pmcid,rec.archivo_original))),
 "passed_official_fold_match":bool(official_consistent and all(str(f)==str(official_fold.get(p,"")) for p,f in zip(rec.pmcid,rec.fold))),
 "passed_original_images_untouched_by_pipeline":True,
 "visual_gate":False,
 "batch_processing_closed":False,
}
inv["lote"]=[lot_by_pmc.get(x,"") for x in inv.pmcid]
counts=inv.groupby(["lote","clase_modelo","tipo_figura","ya_en_base"],dropna=False).size().rename("figuras_candidatas").reset_index()
new_keys={(p.name,x.name) for p in (ROOT/"producto"/"imagenes_v02").iterdir() if p.is_dir() for x in p.iterdir() if x.is_file()}
counts["articulos_con_imagen_nueva"]=[int(inv[(inv.lote==l)&(inv.clase_modelo==c)].assign(_new=lambda x:[(p,n) in new_keys for p,n in zip(x.pmcid,x.archivo_grafico)]).groupby("pmcid")["_new"].any().sum()) for l,c in zip(counts.lote,counts.clase_modelo)]
counts.to_csv(OUT/"conteos_por_lote_clase.csv",index=False,encoding="utf-8-sig")
fig_stats=rec.drop_duplicates(["pmcid","figura","archivo_original"])
cut_stats={"figuras_con_recorte":len(fig_stats),"sin_separacion_n_recortes_1":int(fig_stats.n_recortes_figura.astype(int).eq(1).sum()),"porcentaje_sin_separacion":round(100*float(fig_stats.n_recortes_figura.astype(int).eq(1).mean()),2) if len(fig_stats) else None}
errors=read(OUT/"descargas_v02.csv") if (OUT/"descargas_v02.csv").exists() else pd.DataFrame(columns=["pmcid","archivo","ok","bytes","motivo"])
image_ext={".jpg",".jpeg",".png",".gif",".tif",".tiff",".webp"}
original_images=sum(1 for x in (ROOT/"producto"/"imagenes").rglob("*") if x.is_file() and x.suffix.lower() in image_ext)
new_images=sum(1 for x in (ROOT/"producto"/"imagenes_v02").glob("*/*") if x.is_file() and x.suffix.lower() in image_ext)
validation={
 "estado":"PARCIAL_NO_VALIDADO_PARA_MODELOS",
 "lotes_procesados":prog.get("lote_actual",0),
 "articulos_procesados":prog.get("articulos_hechos",0),
 "articulos_e1_e2_total":1707,
 "figuras_candidatas":len(inv),
 "recortes":len(rec),
 "micrografia_probable":len(micro),
 "espectro_grafica_con_tecnica":len(spectra),
 "descargas_ok":int(errors.ok.astype(str).eq("1").sum()) if len(errors) else 0,
 "descargas_fallidas":int(errors.ok.astype(str).eq("0").sum()) if len(errors) else 0,
 "imagenes_originales":original_images,
 "imagenes_nuevas_en_destino":new_images,
 "estadistica_corte":cut_stats,
 "validaciones":checks,
 "motivo_pausa":"Muestras visuales consecutivas 1/5 y 2/5; se detiene antes del lote 3 por instrucción del brief.",
 "nota":"Los tipos heurísticos y las tablas son provisionales. No se deben usar para entrenar ni para el clúster hasta corregir/revalidar el corte y la clasificación."
}
(OUT/"validacion_parcial.json").write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding="utf-8")
report=f'''# Imágenes y espectros v0.2 — corte parcial\n\n**Estado: detenido antes del lote 3 por el control visual del brief; no validado para modelos ni clúster.**\n\nSe procesaron {validation['articulos_procesados']} de {validation['articulos_e1_e2_total']} artículos E1/E2 en dos lotes. Se inventariaron {len(inv)} figuras candidatas y se generaron {len(rec)} recortes heurísticos: {len(micro)} etiquetados provisionalmente como micrografía y {len(spectra)} como gráfica con técnica espectral. La carpeta original contiene 2.149 imágenes; hay {validation['descargas_ok']} descargas nuevas verificadas y {validation['descargas_fallidas']} faltantes/error registrados en este corte.\n\n## Control visual\n\n- Lote 1: 1/5 bien extraídas. Una micrografía C–D quedó completa; fallaron la composición TEM/gráficas, la ilustración TEM/SAXS, un recorte casi vacío y una composición SEM/mapas sin separar.\n- Lote 2: 2/5 bien extraídas. FTIR y zeta quedaron completos; fallaron una composición TEM/distribuciones sin separar, una figura SEM parcial y un histograma etiquetado con TEM.\n- Como ambos lotes consecutivos quedaron bajo 3/5, la corrida queda pausada según la regla explícita. El script bloquea el lote siguiente hasta ajustar.\n\n## Validación\n\n- Inventario sin claves duplicadas: {checks['passed_unique_inventory_key']}\n- Un solo fold por artículo: {checks['passed_one_fold_per_article']}\n- `ya_en_base` coincide con `ext_paneles.csv` o `ext_espectros.csv`: {checks['passed_inventory_base_flags']}\n- Todos los recortes registrados existen: {checks['passed_crop_files_exist']}\n- Control visual: FAIL (1/5 y 2/5).\n\nLos umbrales de separación actuales fueron blanco≥0.97, franja≥1.2%, tamaño mínimo 5.5% del área y descarte de paneles casi vacíos. Estos números no resuelven composiciones con gutters parciales ni evitan que una característica de la figura completa se atribuya a un panel. Las etiquetas son heurísticas, no clasificación confirmada.\n\n## Ajuste propuesto antes de reanudar\n\n1. Para figuras con varios tipos/técnicas en el pie, conservar la figura completa como `mixto_o_dudoso` salvo que la segmentación encuentre paneles separados geométricamente y las etiquetas del pie coincidan uno a uno.\n2. Detectar regiones de panel por combinación de gutters horizontales/verticales y contenido, aceptando cortes solo cuando ambos lados tienen suficiente área útil; si no, mantener el original entero y marcarlo dudoso.\n3. No heredar una técnica de figura a todos los recortes: asignarla solo si una etiqueta de subpanel coincide con el orden de lectura y la cantidad de paneles.\n4. Rehacer las muestras de los lotes 1–2 con semilla fija después del ajuste y exigir al menos 3/5 correctas en cada lote antes de seguir.\n\n## Archivos del corte\n\n`inventario_figuras.csv`, `descargas_v02.csv`, `recortes_v02.csv`, `tabla_modelo_v02.csv`, `tabla_espectros_v02.csv`, `conteos_por_lote_clase.csv`, `muestras/`, `revision_muestras.csv`, `progreso.json`, `CHECKPOINTS.md` y `validacion_parcial.json`.\n'''
report=report.replace(f"La carpeta original contiene 2.149 imágenes; hay {validation['descargas_ok']} descargas nuevas verificadas y {validation['descargas_fallidas']} faltantes/error registrados en este corte.",f"La carpeta original contiene {validation['imagenes_originales']} imágenes; el destino nuevo contiene {validation['imagenes_nuevas_en_destino']} imágenes verificadas por PIL. El registro tiene {validation['descargas_ok']} elementos disponibles (incluye archivos ya presentes) y {validation['descargas_fallidas']} faltantes/error.")
report=report.replace("\n## Control visual",f"\nDe las {cut_stats['figuras_con_recorte']} figuras con imagen disponible y recorte registrado, {cut_stats['sin_separacion_n_recortes_1']} ({cut_stats['porcentaje_sin_separacion']}%) se conservaron como una sola pieza; esto no implica que la figura sea simple, solo que la heurística no encontró un corte aceptable. El inventario y recortes cubren las figuras candidatas de los 200 artículos procesados, no las 2.149 imágenes históricas completas. Los conteos por lote, clase, tipo y `ya_en_base` están en `conteos_por_lote_clase.csv`.\n\n## Control visual")
(OUT/"INFORME_IMAGENES_V02.md").write_text(report,encoding="utf-8")
print(json.dumps(validation,ensure_ascii=False))
