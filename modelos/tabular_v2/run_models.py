from __future__ import annotations
import json,shutil
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LinearRegression,Ridge,LogisticRegression
from sklearn.ensemble import RandomForestRegressor,HistGradientBoostingRegressor,RandomForestClassifier,HistGradientBoostingClassifier
from engine_v2 import *

def run():
    guard();d=data();review=json.loads((ROOT/'modelos'/'formulacion'/'validacion_B1.json').read_text(encoding='utf-8'));assert review['revisados']==30
    reg=d[d.size_nm.notna()].reset_index(drop=True)
    results=[]
    for model in ['media_clase','lineal','ridge','rf300','hgb']:
        key='tamano_media_clase' if model=='media_clase' else f'tamano_A_{model}'
        r=json.loads((ROOT/'modelos'/'tabular'/'resultados'/f'metricas_{key}.json').read_text(encoding='utf-8'))
        p=pd.read_csv(ROOT/r['predicciones'],encoding='utf-8-sig',keep_default_na=False)
        assert p.pmcid.equals(reg.pmcid) and np.allclose(p.y_real,np.log10(reg.size_nm)) and np.array_equal(p.fold,reg.fold)
        destination=OUT/f'predicciones_{key}.csv';shutil.copyfile(ROOT/r['predicciones'],destination)
        r={**r,'tarea':'tamano','variante':'A','importado_ronda1':True,'predicciones':str(destination.relative_to(ROOT))};write_json(OUT/f'metricas_{key}.json',r);results.append(r)
    for variant,features in [('AF',base.REG_A+FORM),('BF',base.REG_A+['zeta_mV','pdi']+FORM)]:
        for name,model,tune in [('lineal',LinearRegression(),False),('ridge',Ridge(),True),('rf300',RandomForestRegressor(n_estimators=300,min_samples_leaf=3,random_state=0,n_jobs=1),False),('hgb',HistGradientBoostingRegressor(max_iter=300,learning_rate=.05,random_state=0,early_stopping=False),False)]:
            results.append(evaluate(f'tamano_{variant}_{name}','tamano',variant,reg,features,model,tune,permutation=name!='lineal'))
    for task in ['clase4','clase3','zeta','pdi']:
        if task.startswith('clase'):
            frame=d[d.clase_modelo.ne('')&d[['size_nm','zeta_mV','pdi']].notna().any(axis=1)].copy()
            if task=='clase3':frame=frame[frame.clase_modelo.ne('nanomaterial')]
            frame['target']=frame.clase_modelo;features=base.CLASS_FEATURES+SAFE
        elif task=='zeta':
            frame=d[d.zeta_mV.notna()&d.zeta_mV.ne(0)].copy();frame['target']=np.where(frame.zeta_mV<0,'negativo','positivo');features=[c for c in base.CLASS_FEATURES if c!='zeta_mV']+SAFE
        else:
            frame=d[d.pdi.notna()&d.pdi.ge(0)].copy();frame['target']=np.where(frame.pdi<.3,'monodisperso','no_monodisperso');features=[c for c in base.CLASS_FEATURES if c!='pdi']+SAFE
        frame=frame.reset_index(drop=True)
        for forbidden in ['family','carrier_type','categoria_uso','sample','clase_modelo',*MATERIAL,'material_derivado']:
            try:safe_features([*features,forbidden],task)
            except AssertionError:pass
            else:raise AssertionError(f'No se detectó fuga: {forbidden}')
        for name,model in [('mayoritaria',DummyClassifier(strategy='most_frequent')),('logistica',LogisticRegression(max_iter=3000,random_state=0)),('rf',RandomForestClassifier(n_estimators=300,class_weight='balanced',random_state=0,n_jobs=1)),('hgb',HistGradientBoostingClassifier(max_iter=300,learning_rate=.05,random_state=0,early_stopping=False))]:
            results.append(evaluate(f'{task}_{name}',task,'metodos_contexto',frame,features,model,permutation=name!='mayoritaria'))
        if task=='clase4':
            results.append(evaluate('clase4_mediciones_logistica','clase4','mediciones',frame,['log10_size_nm','zeta_mV','pdi'],LogisticRegression(max_iter=3000,random_state=0),permutation=False))
    write_json(ROOT/'producto'/'modelo_tabular'/'metricas_tabular_v2.json',{'modelos':results,'bootstrap_articulos':1000,'evaluacion':'5 folds oficiales por artículo','revision_banderas':review,'nota':'A importada sin modificar ronda1; matrices de clasificación excluyen todos los materiales; medidas puras adicionales para C.'})
    guard();progress('B entrenamiento completo; pendiente reporte y validación final')

if __name__=='__main__':run()
