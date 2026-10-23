"""V2 evaluation: imports R1 preprocessing/metrics/bootstrap without editing R1."""
from __future__ import annotations
import sys
sys.dont_write_bytecode=True
import hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.inspection import permutation_importance
from sklearn.model_selection import GridSearchCV,GroupKFold
from sklearn.metrics import confusion_matrix
from threadpoolctl import threadpool_limits
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;OUT=HERE/'resultados'
sys.path.insert(0,str(ROOT/'modelos'/'tabular'))
import tabular_common as base
sys.path.insert(0,str(ROOT/'modelos'/'ronda2'))
from control import guard,write_json
RULES=json.loads((ROOT/'modelos'/'formulacion'/'reglas.json').read_text(encoding='utf-8'))
FORM=RULES['retenidas'];SAFE=[c for c in FORM if c.startswith(('met_','ctx_'))];MATERIAL=[c for c in RULES['reglas'] if c.startswith('mat_')]

def data():
    d=base.load_dataset();f=pd.read_csv(ROOT/'modelos'/'formulacion'/'formulacion_articulos.csv',encoding='utf-8-sig')
    d=d.merge(f,on='pmcid',how='left',validate='many_to_one');assert d[FORM].notna().all().all()
    d['log10_size_nm']=np.log10(d.size_nm)
    OUT.mkdir(parents=True,exist_ok=True);d.to_csv(HERE/'dataset_v2.csv',index=False,encoding='utf-8-sig')
    return d

def safe_features(features,task):
    if task=='tamano':
        assert not {'size_nm','log10_size_nm','target'}&set(features)
        return
    assert not set(features)&(base.FORBIDDEN|set(MATERIAL)|{'target','zeta_signo','pdi_menor_03'})
    assert all(c in base.CLASS_FEATURES or c in SAFE for c in features)
    base.assert_classification_features([c for c in features if c not in SAFE])
    if task=='zeta':assert 'zeta_mV' not in features
    if task=='pdi':assert 'pdi' not in features

def progress(text):
    print(text,flush=True)
    with (HERE/'PROGRESO_B.md').open('a',encoding='utf-8') as f:f.write(text+'\n')

def evaluate(key,task,variant,d,features,estimator,tune=False,permutation=True):
    safe_features(features,task);X=d[features];reg=task=='tamano'
    y=np.log10(d.size_nm.to_numpy(float)) if reg else d.target.to_numpy(str);labels=sorted(set(y)) if not reg else None
    pred=np.empty(len(d),float if reg else object);probs=np.full((len(d),len(labels)),np.nan) if not reg else None
    digest=hashlib.sha256()
    for p in [Path(__file__),HERE/'run_models.py',ROOT/'modelos'/'formulacion'/'formulacion_articulos.csv',ROOT/'modelos'/'tabular'/'dataset_descriptores.csv',ROOT/'modelos'/'tabular'/'tabular_common.py']:digest.update(p.read_bytes())
    digest.update(json.dumps([key,features],sort_keys=True).encode());fingerprint=digest.hexdigest()
    cache=OUT/'cache'/key;cache.mkdir(parents=True,exist_ok=True);folds=[];imp=[];coefs=[]
    for fold in range(5):
        tr=np.flatnonzero(d.fold.to_numpy()!=fold);te=np.flatnonzero(d.fold.to_numpy()==fold)
        assert len(te)>0 and not set(d.iloc[tr].pmcid)&set(d.iloc[te].pmcid)
        path=cache/f'fold_{fold}.json';old=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        if old.get('fingerprint')==fingerprint:
            pred[te]=old['pred'];folds.append(old['info']);imp+=old['importance'];coefs+=old['coefficients']
            if not reg:probs[te]=old['probabilities']
            continue
        progress(f'{key}: fold {fold} · train {d.iloc[tr].pmcid.nunique()} / test {d.iloc[te].pmcid.nunique()} artículos')
        pipe=base.pipeline_for(clone(estimator),X);extra={}
        with threadpool_limits(limits=1):
            if tune:
                search=GridSearchCV(pipe,{'model__alpha':[.01,.1,1,10,100]},cv=GroupKFold(4),scoring='neg_mean_absolute_error',n_jobs=1,error_score='raise')
                search.fit(X.iloc[tr],y[tr],groups=d.iloc[tr].pmcid);pipe=search.best_estimator_;extra['alpha']=float(search.best_params_['model__alpha'])
            else:pipe.fit(X.iloc[tr],y[tr])
            yp=pipe.predict(X.iloc[te]);pred[te]=yp
            if not reg:
                model_labels=list(pipe.named_steps['model'].classes_);prob=pipe.predict_proba(X.iloc[te])[:,[model_labels.index(l) for l in labels]];probs[te]=prob
                repeat=clone(pipe).fit(X.iloc[tr],y[tr]);np.testing.assert_array_equal(yp,repeat.predict(X.iloc[te]));np.testing.assert_allclose(prob,repeat.predict_proba(X.iloc[te])[:,[model_labels.index(l) for l in labels]],rtol=0,atol=1e-12)
                extra['repeticion_identica']=True
            local=[]
            if permutation:
                importance=permutation_importance(pipe,X.iloc[te],y[te],scoring='r2' if reg else 'f1_macro',n_repeats=3,random_state=0,n_jobs=1)
                local=[{'fold':fold,'variable':c,'importancia':float(v),'std':float(sd)} for c,v,sd in zip(features,importance.importances_mean,importance.importances_std)]
        coef=base.coefficients(pipe,fold)
        if not reg and len(labels)==2:
            for r in coef:r['clase']=str(pipe.named_steps['model'].classes_[1])
        info={'fold':fold,'n_train':len(tr),'n_test':len(te),'train_articulos':int(d.iloc[tr].pmcid.nunique()),'test_articulos':int(d.iloc[te].pmcid.nunique()),**extra,**base.metric_values(y[te],yp,'regresion' if reg else 'clasificacion',labels)}
        folds.append(info);imp+=local;coefs+=coef
        write_json(path,{'fingerprint':fingerprint,'pred':np.asarray(yp).tolist(),'probabilities':probs[te].tolist() if not reg else None,'info':info,'importance':local,'coefficients':coef})
    metrics=base.metric_values(y,pred,'regresion' if reg else 'clasificacion',labels);ci=base.bootstrap_by_article(y,pred,d.pmcid.to_numpy(),'regresion' if reg else 'clasificacion',labels)
    output=d[['pmcid','sample','fold']].copy();output['y_real']=y;output['y_pred']=pred
    output=output[['pmcid','sample','y_real','y_pred','fold']]
    if not reg:
        assert np.isfinite(probs).all() and np.allclose(probs.sum(axis=1),1)
        for i,l in enumerate(labels):output['p_'+l]=probs[:,i]
        cm=confusion_matrix(y,pred,labels=labels,normalize='true');pd.DataFrame(cm,index=labels,columns=labels).to_csv(OUT/f'confusion_{key}.csv',encoding='utf-8-sig')
    output.to_csv(OUT/f'predicciones_{key}.csv',index=False,encoding='utf-8-sig')
    if imp:pd.DataFrame(imp).to_csv(OUT/f'importancia_{key}.csv',index=False,encoding='utf-8-sig')
    if coefs:pd.DataFrame(coefs).to_csv(OUT/f'coeficientes_{key}.csv',index=False,encoding='utf-8-sig')
    byclass=[]
    if reg:
        for c,indices in d.groupby('clase_modelo').indices.items():byclass.append({'clase':c or 'sin_clase','n':len(indices),'r2':float(base.r2_score(y[indices],pred[indices]))})
    result={'id':key,'tarea':task,'variante':variant,'entradas':features,'n_filas':len(d),'n_articulos':int(d.pmcid.nunique()),'evaluacion':'5 particiones por artículo','metricas':{m:{'valor':v,'ic95':ci[m]} for m,v in metrics.items()},'por_fold':folds,'clases':labels,'r2_por_clase':byclass,'predicciones':str((OUT/f'predicciones_{key}.csv').relative_to(ROOT)),'fingerprint':fingerprint}
    write_json(OUT/f'metricas_{key}.json',result);progress(f'VALIDADO {key}: {metrics}');return result
