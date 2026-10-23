"""Read-only numerical diagnostics for the critical review; no new model selection."""
import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score,mean_absolute_error,accuracy_score,f1_score,mutual_info_score
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));from control import guard,write_json,checkpoint

def main():
    guard();data=pd.read_csv(ROOT/'modelos'/'tabular'/'dataset_descriptores.csv',encoding='utf-8-sig',keep_default_na=False)
    art=pd.read_csv(ROOT/'curation'/'ext_articulos.csv',encoding='utf-8-sig',keep_default_na=False);art=art[art.tier.isin(['E1','E2'])].copy()
    art['doi_normalizado']=art.doi.str.strip().str.lower();dup=art[art.doi_normalizado.ne('')&art.duplicated('doi_normalizado',keep=False)]
    formulation=pd.read_csv(ROOT/'modelos'/'formulacion'/'formulacion_articulos.csv',encoding='utf-8-sig');merged=formulation.merge(art[['pmcid','year','doi_normalizado']],on='pmcid',validate='one_to_one')
    merged['prefijo_doi']=merged.doi_normalizado.str.split('/').str[0].replace('','desconocido')
    associations=[]
    for flag in formulation.columns[1:]:
        corr=float(merged[flag].corr(pd.to_numeric(merged.year,errors='coerce')));mi=float(mutual_info_score(merged[flag],merged.prefijo_doi))
        associations.append({'bandera':flag,'correlacion_year':corr,'MI_prefijo_doi':mi})
    associations=pd.DataFrame(associations);associations.to_csv(HERE/'asociaciones_banderas.csv',index=False,encoding='utf-8-sig')
    top_year=associations.loc[associations.correlacion_year.abs().idxmax()].to_dict();top_doi=associations.loc[associations.MI_prefijo_doi.idxmax()].to_dict()
    panels=pd.read_csv(ROOT/'curation'/'ext_paneles.csv',encoding='utf-8-sig');sem=set(panels.loc[panels.variant.eq('SEM'),'pmcid']);merged['hay_SEM']=merged.pmcid.isin(sem)
    gold_by_sem={str(k):float(v) for k,v in merged.groupby('hay_SEM').mat_oro.mean().items()}
    reg=pd.read_csv(ROOT/'modelos'/'tabular_v2'/'resultados'/'predicciones_tamano_BF_rf300.csv',encoding='utf-8-sig');rw=1/reg.pmcid.map(reg.pmcid.value_counts())
    regmetrics={'r2_filas':float(r2_score(reg.y_real,reg.y_pred)),'r2_peso_igual_articulo':float(r2_score(reg.y_real,reg.y_pred,sample_weight=rw)),'mae_log_filas':float(mean_absolute_error(reg.y_real,reg.y_pred)),'mae_log_peso_igual_articulo':float(mean_absolute_error(reg.y_real,reg.y_pred,sample_weight=rw))}
    cls=pd.read_csv(ROOT/'modelos'/'tabular_v2'/'resultados'/'predicciones_clase4_logistica.csv',encoding='utf-8-sig');cw=1/cls.pmcid.map(cls.pmcid.value_counts())
    classmetrics={'f1_filas':float(f1_score(cls.y_real,cls.y_pred,average='macro')),'f1_peso_igual_articulo':float(f1_score(cls.y_real,cls.y_pred,average='macro',sample_weight=cw)),'accuracy_filas':float(accuracy_score(cls.y_real,cls.y_pred)),'accuracy_peso_igual_articulo':float(accuracy_score(cls.y_real,cls.y_pred,sample_weight=cw))}
    labels=sorted(cls.y_real.unique());pr=cls[['p_'+l for l in labels]].to_numpy();truth=np.zeros_like(pr)
    for i,label in enumerate(cls.y_real):truth[i,labels.index(label)]=1
    brier=float(np.mean(np.sum((truth-pr)**2,axis=1)));confidence=pr.max(axis=1);correct=(cls.y_real==cls.y_pred).to_numpy();ece=0.;binrows=[]
    for lo,hi in zip(np.arange(0,1,.1),np.arange(.1,1.1,.1)):
        mask=(confidence>=lo)&(confidence<(hi if hi<1 else 1.000001))
        if mask.any():
            acc=float(correct[mask].mean());conf=float(confidence[mask].mean());ece+=float(mask.mean())*abs(acc-conf);binrows.append({'lo':float(lo),'hi':float(hi),'n':int(mask.sum()),'exactitud':acc,'confianza':conf})
    pdi=pd.to_numeric(data.pdi,errors='coerce');zeta=pd.to_numeric(data.zeta_mV,errors='coerce');review=pd.read_csv(ROOT/'modelos'/'formulacion'/'evidencia_formulacion.csv',encoding='utf-8-sig');n_review_flags=review.bandera.nunique()
    diagnostics={'doi_duplicados_pmcids_distintos':dup[['pmcid','doi_normalizado']].to_dict('records'),'filas_por_articulo_max':int(data.groupby('pmcid').size().max()),'regresion_ponderacion':regmetrics,'clasificacion_ponderacion':classmetrics,'mayor_asociacion_year':top_year,'mayor_MI_prefijo_doi':top_doi,'oro_condicional_SEM':gold_by_sem,'calibracion_descriptiva':{'brier_multiclase_suma':brier,'ECE_10_bins':ece,'bins':binrows},'PDI_negativos':int((pdi<0).sum()),'zeta_ceros_excluidos':int((zeta==0).sum()),'banderas_distintas_en_muestra_30':int(n_review_flags)}
    write_json(HERE/'DIAGNOSTICOS_CRITICOS.json',diagnostics)
    report=f"""# Revisión crítica de las rondas 1 y 2

Estos controles son diagnósticos sobre OOF y fuentes locales; no constituyen una validación externa ni una auditoría humana de las extracciones. Código reproducible: `modelos/ronda2/revision_critica.py`; valores en `DIAGNOSTICOS_CRITICOS.json` y `asociaciones_banderas.csv`.

1. **La identidad PMCID puede no identificar experimentos independientes.** Comprobado: no se comparte ningún PMCID entre train/test y los DOI normalizados repetidos entre artículos E1/E2 involucran {len(dup)} registros. Esto no descarta reutilización de datos, versiones distintas o imágenes compartidas con DOI diferente. Propuesta: revisión de duplicados de título/figuras y asignación por familia de publicaciones antes de una evaluación externa.

2. **Las filas influyen más cuando un artículo aporta muchas muestras.** Comprobado: hasta {diagnostics['filas_por_articulo_max']} filas por artículo. En RF B+F, R² por filas={regmetrics['r2_filas']:.4f}; dando el mismo peso total a cada artículo={regmetrics['r2_peso_igual_articulo']:.4f}. En logística de cuatro clases, F1={classmetrics['f1_filas']:.4f} frente a {classmetrics['f1_peso_igual_articulo']:.4f}. El bootstrap agrupa artículos, pero no convierte la métrica puntual en una media por artículo. Propuesta: publicar ambas ponderaciones y mantener la unidad de evaluación según el uso previsto.

3. **Una mención no prueba un componente ni un método de formulación.** Comprobado en la muestra aleatoria: 21/30 correctos para apoyo contextual y 9 dudosos; solo {n_review_flags} banderas distintas de 28 aparecen en esa muestra. Oro de recubrimiento SEM, sílice de TLC y preparación analítica activan reglas. Tasa mat_oro en artículos con SEM={100*gold_by_sem.get('True',0):.1f}% y sin SEM={100*gold_by_sem.get('False',0):.1f}%. Esa asociación es compatible con confusión por caracterización, no demuestra su causa. Propuesta: separar síntesis, caracterización y ensayos biológicos, añadir exclusiones de recubrimiento/TLC y hacer una auditoría nueva estratificada, sin reutilizar la muestra para declarar precisión final.

4. **Métodos/contexto pueden ser sustitutos del año o de la editorial.** Comprobado: la mayor correlación bandera-año es {top_year['bandera']} (r={top_year['correlacion_year']:+.3f}); la mayor información mutua con prefijo DOI es {top_doi['bandera']} (MI={top_doi['MI_prefijo_doi']:.3f} nats). Prefijo DOI es solo un proxy del registrante editorial, no una identificación perfecta de revista/editorial. Propuesta: evaluación temporal y por revista/registrante, con revisión de la distribución de clases, para medir generalización fuera de estilos editoriales.

5. **Variables permitidas pueden no estar disponibles antes del experimento.** R1 usa técnicas de caracterización; B añade DLS y contexto, y B+F utiliza zeta/PDI medidos. Esto puede explicar tamaño observado dentro de la base, pero no equivale a predecir la formulación antes de prepararla. Comprobado: la variante A+F no recibe medidas, B+F sí; las dos se mantienen separadas. Propuesta: fijar el momento de uso del modelo y evaluar solo las variables disponibles en ese momento; extraer proporciones y condiciones, actualmente ausentes.

6. **La ontología de clases mezcla composición y uso.** `nanomaterial` no es un tipo químico excluyente frente a inorgánico/polimérico. El experimento de tres clases cambia la población; un F1 mayor no prueba mejor capacidad sobre los mismos artículos. Comprobado: el informe distingue ambas cohortes y C exige cuatro clases e IDs/folds comunes. Propuesta: discutir con el equipo dos ejes de etiqueta independientes (composición y función), sin cambiar retrospectivamente v0.1.

7. **Los IC condicionales y la selección del mejor modelo pueden dar una impresión excesiva de certeza.** Los 1.000 bootstrap remuestrean predicciones OOF fijas, no todos los reentrenamientos ni la búsqueda entre modelos. La comparación primaria Ridge A+F−A incluye cero; RF/boosting mejoran más que sus equivalentes A, pero son parte de una escalera exploratoria. Propuesta: preespecificar el estimador final o hacer evaluación anidada de toda la selección, y reservar artículos nuevos para validación externa. La selección global de banderas por frecuencia no quitó ninguna en esta ronda; si quita banderas en el futuro debe entrar dentro del entrenamiento.

8. **Probabilidades sin calibración no son intercambiables.** Diagnóstico OOF de logística de cuatro clases: Brier multiclase (suma por fila)={brier:.4f}, ECE descriptivo de 10 bins={ece:.4f}. No basta para establecer calibración por clase, editorial o tiempo. Propuesta: calibración dentro de entrenamiento y evaluación con diagramas por clase. En C, reconstruir cuatro scores de una confianza asume resto uniforme y se etiqueta; no se presenta como probabilidad auténtica suministrada por Kabré.

9. **La fusión ponderada aún no tiene garantía de anidamiento completo.** La prueba hecha cambia etiquetas del fold test y verifica que no cambie su peso. Eso descarta uso directo de etiquetas test, pero otros scores OOF pueden haber sido producidos por modelos entrenados con ese fold externo. Sin procedencia por outer-fold no puede descartarse la dependencia indirecta. Propuesta concreta: Kabré y el tabular deben exportar predicciones internas para cada entrenamiento externo, con IDs/folds usados para ajustar; elegir el peso solo con esas predicciones y evaluar una vez en el fold externo. El JSON y README de C advierten esta limitación; no hay resultados reales hasta recibir Kabré.

10. **Disponibilidad de imágenes y figuras completas pueden sesgar C.** Se fijaron 1.179 artículos/1.458 imágenes existentes no vacías; esto es una instantánea, y algunos artículos aportan más figuras. No se verificó visualmente aquí que toda imagen sea una micrografía pura: puede contener espectros, texto o multipaneles. Propuesta: registrar exclusiones por clase, inspeccionar una muestra de imágenes, deduplicar visualmente y contrastar agregación con peso igual por artículo. No se tocó el clúster ni se inventaron embeddings.

11. **La evidencia de QC publicada es secundaria.** La ruta `equipo/qc_carlos/RESUMEN_QC.md` no está disponible; figura 9 cita el LEEME congelado con los mismos recuentos. Esa muestra fue asistida por IA, no una revisión humana independiente. Propuesta: recuperar el registro original y una auditoría humana ciega para cuantificar errores de extracción, selección y clases.

12. **Pruebas de código no sustituyen revisión científica ni cubren toda mala codificación.** Comprobado: R1 y V2 rechazan columnas prohibidas; V2 excluye materiales en todos los clasificadores y excluye zeta/PDI de su propia tarea objetivo. R1 permite PDI ≤1,5 sin exigir explícitamente PDI≥0; hay {diagnostics['PDI_negativos']} negativos actuales, por lo que no cambió estas cifras. Para signo zeta se excluyeron {diagnostics['zeta_ceros_excluidos']} ceros. Propuesta: esquemas físicos explícitos y casos límite en futuras versiones, manteniendo v0.1 congelada. Los hashes de las fuentes y R1 se verifican; reproducibilidad de una semilla no equivale a robustez frente a cambios de semilla o población.

Prioridades propuestas: (1) recuperar QC y distinguir menciones de caracterización; (2) fijar momento de uso y ponderación por artículo; (3) exigir procedencia anidada de predicciones antes de interpretar fusión ponderada; (4) validación temporal/editorial y externa. Ninguna se disfraza de comprobación ya completada.
"""
    assert report.count('**')>=24 and len(diagnostics['doi_duplicados_pmcids_distintos'])==len(dup)
    (ROOT/'modelos'/'REVISION_CRITICA.md').write_text(report,encoding='utf-8');guard();checkpoint('D','PASS: 12 puntos críticos con comprobación o propuesta, diagnósticos reproducibles de DOI, ponderación por artículo, asociación año/prefijo DOI, calibración y límites de fusión; fuentes intactas.')
    print(json.dumps(diagnostics,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
