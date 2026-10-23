from __future__ import annotations
import os,json
from engine_v2 import *
os.environ.setdefault('MPLCONFIGDIR',str(OUT/'.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from control import checkpoint

def value(r,m):return r['metricas'][m]['valor']
def cell(r,m):
    x=r['metricas'][m];return f"{x['valor']:.3f} [{x['ic95'][0]:.3f}, {x['ic95'][1]:.3f}]"
def pred(r):return pd.read_csv(ROOT/r['predicciones'],encoding='utf-8-sig',keep_default_na=False)
def paired(new,old):
    p,q=pred(new),pred(old);assert p.pmcid.equals(q.pmcid) and np.allclose(p.y_real,q.y_real)
    codes,groups=pd.factorize(p.pmcid,sort=True);ng=len(groups);y=p.y_real.to_numpy(float)
    statistics=np.column_stack([np.ones(len(p)),y,y*y,(y-q.y_pred.to_numpy(float))**2-(y-p.y_pred.to_numpy(float))**2]);sums=np.zeros((ng,4));np.add.at(sums,codes,statistics)
    weights=np.random.default_rng(0).multinomial(ng,np.full(ng,1/ng),size=1000);s=weights@sums;d=s[:,3]/(s[:,2]-s[:,1]**2/s[:,0])
    return {'delta_r2':value(new,'r2')-value(old,'r2'),'ic95':[float(np.quantile(d,.025)),float(np.quantile(d,.975))]}

def main():
    guard();product_path=ROOT/'producto'/'modelo_tabular'/'metricas_tabular_v2.json';obj=json.loads(product_path.read_text(encoding='utf-8'));models={r['id']:r for r in obj['modelos']};assert len(models)==30
    pairs=[]
    for key in ['lineal','ridge','rf300','hgb']:
        pairs.append({'modelo':key,'comparacion':'AF-A',**paired(models[f'tamano_AF_{key}'],models[f'tamano_A_{key}'])})
        old=json.loads((ROOT/'modelos'/'tabular'/'resultados'/f'metricas_tamano_B_{key}.json').read_text(encoding='utf-8'))
        pairs.append({'modelo':key,'comparacion':'BF-B',**paired(models[f'tamano_BF_{key}'],old)})
    pd.DataFrame(pairs).to_csv(OUT/'mejoras_pareadas.csv',index=False,encoding='utf-8-sig');obj['mejoras_pareadas']=pairs;write_json(product_path,obj)
    metrics=[]
    for r in models.values():
        row={'id':r['id'],'tarea':r['tarea'],'variante':r['variante'],'n_filas':r['n_filas'],'n_articulos':r['n_articulos']}
        for m,v in r['metricas'].items():row[m]=v['valor'];row[m+'_ic_inf']=v['ic95'][0];row[m+'_ic_sup']=v['ic95'][1]
        metrics.append(row)
    pd.DataFrame(metrics).to_csv(OUT/'metricas_v2.csv',index=False,encoding='utf-8-sig')
    figs=OUT/'figuras';figs.mkdir(exist_ok=True)
    fig,ax=plt.subplots(figsize=(11,6));names=['lineal','ridge','rf300','hgb'];offsets=[-.20,0,.20]
    for variant,color,offset in zip(['A','AF','BF'],['#888888','#087e78','#0072B2'],offsets):
        rs=[models[f'tamano_{variant}_{k}'] for k in names];v=np.array([value(r,'r2') for r in rs]);lo=np.array([r['metricas']['r2']['ic95'][0] for r in rs]);hi=np.array([r['metricas']['r2']['ic95'][1] for r in rs]);ax.errorbar(v,np.arange(4)+offset,xerr=[v-lo,hi-v],fmt='o',capsize=3,label=variant,color=color)
    ax.set_yticks(range(4),['Lineal','Ridge','RF 300','Boosting']);ax.set_xlabel('R² log10(tamaño), OOF · IC95 por artículo');ax.set_title('¿Aportan las menciones textuales de formulación?');ax.legend();fig.tight_layout();fig.savefig(figs/'formulacion_r2.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(12,9))
    for ax,task in zip(axes.flat,['clase4','clase3','zeta','pdi']):
        rs=[models[f'{task}_{k}'] for k in ['mayoritaria','logistica','rf','hgb']];ax.barh(['Mayoritaria','Logística','RF','Boosting'],[value(r,'f1_macro') for r in rs],color='#087e78');ax.set_title(task);ax.set_xlabel('F1 macro OOF');ax.set_xlim(0,1)
    fig.tight_layout();fig.savefig(figs/'tareas_clasificacion.png',dpi=150);plt.close(fig)
    for variant in ['AF','BF']:
        importance=pd.read_csv(OUT/f'importancia_tamano_{variant}_ridge.csv',encoding='utf-8-sig');importance=importance[importance.variable.isin(FORM)].groupby('variable').importancia.mean().sort_values().tail(15)
        fig,ax=plt.subplots(figsize=(11,7));ax.barh(importance.index,importance,color=['#CC79A7' if x.startswith('mat_') else '#0072B2' if x.startswith('met_') else '#009E73' for x in importance.index]);ax.set_xlabel('Caída R² de test al permutar bandera');ax.set_title(f'Ridge {variant} · importancia de menciones textuales');fig.tight_layout();fig.savefig(figs/f'importancias_F_{variant}.png',dpi=150);plt.close(fig)

    # Automatic gates: predictions, probabilities, source hashes and explicit feature rejection.
    for task in ['clase4','zeta','pdi']:
        actual=next(r['entradas'] for r in models.values() if r['tarea']==task)
        for bad in [*MATERIAL,'carrier_type','clase_modelo','family','categoria_uso','sample','material_derivado']:
            try:safe_features([*actual,bad],task)
            except AssertionError:pass
            else:raise AssertionError(bad)
    official=base.load_dataset().drop_duplicates('pmcid').set_index('pmcid').fold.astype(int)
    for r in models.values():
        p=pred(r);assert len(p)==r['n_filas'] and p.pmcid.nunique()==r['n_articulos'];assert p.groupby('pmcid').fold.nunique().max()==1;assert np.array_equal(p.fold.astype(int),p.pmcid.map(official))
        reg=r['tarea']=='tamano'
        if not reg:
            safe_features(r['entradas'],r['tarea']);cols=['p_'+c for c in r['clases']];prob=p[cols].to_numpy(float);assert np.isfinite(prob).all() and (prob>=0).all() and (prob<=1).all() and np.allclose(prob.sum(axis=1),1)
            assert np.array_equal(np.asarray(r['clases'])[prob.argmax(axis=1)],p.y_pred.to_numpy());assert all(f['repeticion_identica'] for f in r['por_fold'])
            if r['id'].endswith('mayoritaria'):assert np.isclose(value(r,'exactitud'),p.y_real.value_counts(normalize=True).max())
        yy=p.y_real.to_numpy(float) if reg else p.y_real.to_numpy(str);yp=p.y_pred.to_numpy(float) if reg else p.y_pred.to_numpy(str)
        values=base.metric_values(yy,yp,'regresion' if reg else 'clasificacion',r.get('clases'))
        for m,v in values.items():assert np.isclose(v,value(r,m),rtol=1e-10,atol=1e-10)
        assert len(r['por_fold'])==5
    audit=json.loads((ROOT/'modelos'/'formulacion'/'validacion_B1.json').read_text(encoding='utf-8'));assert audit['revisados']==30 and audit['correctos']==21
    checks={'estado':'PASS','modelos':len(models),'clasificadores_con_probabilidades':sum(r['tarea']!='tamano' for r in models.values()),'articulos_en_folds_distintos':0,'materiales_excluidos_de_clasificacion':True,'predicciones_y_probabilidades_reproducibles':True,'fuentes_inalteradas':True}
    write_json(OUT/'VALIDACION_B.json',checks);guard()
    rows=['| Modelo | A (R1) | A+F | B+F |','|---|---:|---:|---:|']
    for k in names:rows.append('| '+k+' | '+' | '.join(cell(models[f'tamano_{v}_{k}'],'r2') for v in ['A','AF','BF'])+' |')
    classrows=['| Tarea | Modelo | Exactitud [IC95] | F1 macro [IC95] |','|---|---|---:|---:|']
    for task in ['clase4','clase3','zeta','pdi']:
        for k in ['mayoritaria','logistica','rf','hgb']:
            r=models[f'{task}_{k}'];classrows.append(f"| {task} | {k} | {cell(r,'exactitud')} | {cell(r,'f1_macro')} |")
    ridge_pair=next(x for x in pairs if x['modelo']=='ridge' and x['comparacion']=='AF-A');support='no demuestra una mejora clara' if ridge_pair['ic95'][0]<=0 else 'muestra una mejora interna positiva'
    report=f"""# Ronda 2: modelos tabulares y menciones de formulación

28 banderas léxicas, 1.707 artículos (1.691 métodos; 16 texto completo sin referencias). Ninguna bandera está por debajo de 10 artículos. Revisión asistida por IA de 30 pares positivos aleatorios: 21 correctos y 9 dudosos para atribuirlos a formulación (70 %); las 30 citas son literales y ≤200 caracteres. No es una estimación de precisión humana de toda la extracción. `met_*`, `mat_*` y `ctx_*` significan mención, no receta confirmada.

## Tamaño: R² [IC95]

Media por clase compartida: {cell(models['tamano_media_clase'],'r2')}. A conserva las entradas y predicciones R1; A+F añade 28 banderas, B+F también zeta/PDI. Se mantienen 2.749 filas/1.080 artículos y los mismos folds; Ridge usa GroupKFold interno. Random Forest: 300 árboles, hoja mínima 3; HGB 300 iteraciones, LR=0,05; sin tuning externo.

{chr(10).join(rows)}

## Qué aporta la formulación

La comparación primaria pareada Ridge A+F−A da ΔR²={ridge_pair['delta_r2']:+.4f}, IC95 [{ridge_pair['ic95'][0]:.4f}, {ridge_pair['ic95'][1]:.4f}]; {support}. Los cuatro modelos tienen comparaciones pareadas A+F−A y B+F−B en `resultados/mejoras_pareadas.csv`. Los IC usan 1.000 bootstrap por artículo sobre OOF, sin reentrenar. Importancias de las banderas: permutación en test, tres repeticiones por fold; CSV y PNG disponibles. La ganancia de una mención no demuestra un mecanismo de formulación.

## Clasificación y tareas nuevas

Para clase: medidas, medio/año/técnicas y únicamente métodos/contexto. Ninguna bandera de material entra a los clasificadores. Zeta: negativo/positivo, excluye zeta=0 y usa tamaño/PDI; PDI: umbral estricto <0,3, usa tamaño/zeta. Ninguna tarea recibe su medida objetivo. Cada clasificador/fold se entrena dos veces y debe producir idénticas probabilidades. Las probabilidades OOF por clase se guardan en todas las predicciones.

{chr(10).join(classrows)}

Para C se añade `clase4_mediciones_logistica`: solo log10(tamaño), zeta, PDI e indicadores de faltante. Evita llamar «solo mediciones» a un clasificador que también utiliza texto, año o técnicas.

## Limitaciones

Oro puede ser recubrimiento SEM; sílice puede ser TLC; sonicación o evaporación pueden preparar muestras para caracterización. El 70 % revisado apoya tratar las banderas como proxies textuales ruidosos. No hay proporciones ni condiciones de preparación verificadas; 74,6 % de filas no declara medio. Los artículos tienen varias filas y las métricas ponderan filas; los IC agrupan por artículo. Selección de banderas por prevalencia global sin usar objetivos; una selección estrictamente anidada sería una sensibilidad futura. Sin evaluación externa ni ajuste del clúster.

## Reproducción

`extraer_formulacion.py` usa Python con lxml y utilidades locales; la ejecución de esta ronda empleó el Python 3.12 incluido con la app (requests puro de Python 3.13). Entrenamiento: Python 3.13, `python modelos/tabular_v2/run_models.py`; informe/gates: `python modelos/tabular_v2/informe_v2.py`. Se importa tabular_common de R1 para preprocesamiento, coeficientes, métricas y bootstrap; ningún archivo de R1 se copia como código ni modifica. Las predicciones A se reutilizan verificando su identidad de filas/targets/folds.
"""
    (HERE/'REPORTE_TABULAR_V2.md').write_text(report,encoding='utf-8')
    (ROOT/'modelos'/'formulacion'/'REPORTE_FORMULACION.md').write_text('# Auditoría de menciones\n\nSe procesaron 1.707 artículos: 1.691 con métodos y 16 con texto completo sin referencias. 28 banderas retenidas (todas con ≥10 artículos); ninguna descartada. Las reglas y la prevalencia se documentan en reglas.json y tasas_banderas.csv.\n\nTreinta pares positivos elegidos uniformemente con semilla 0 se revisaron con sus frases literales: 21 correctos (70 %) y 9 dudosos. «Correcto» significa apoyo contextual razonable en el fragmento para el material o proceso; «dudoso» incluye recubrimiento SEM, cromatografía, preparación analítica y uso figurado de extrusión. La revisión es asistida por IA y no una auditoría humana. No se corrigieron selectivamente banderas con base en el desempeño de modelos.\n\nLa literalidad está verificada por código. La atribución a la formulación sigue siendo incierta; por ello no se deben presentar estas columnas como parámetros experimentales confirmados.\n',encoding='utf-8')
    checkpoint('B',f"PASS: 30 modelos (13 regresiones incluidas A importadas, 17 clasificadores), 28 banderas/1707 artículos, 30 ejemplos revisados (21 correctos/9 dudosos); IC por artículo, pruebas de fuga/materiales y repetición de probabilidades, fuentes intactas. Ridge AF-A={ridge_pair['delta_r2']:+.4f}, IC={ridge_pair['ic95']}.")

if __name__=='__main__':main()
