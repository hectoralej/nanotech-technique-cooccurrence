"""Late fusion of supplied OOF scores. Synthetic tests are strictly isolated."""
from __future__ import annotations
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score,confusion_matrix
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'modelos'/'tabular'))
import tabular_common as common
sys.path.insert(0,str(ROOT/'modelos'/'ronda2'))
from control import guard,write_json
LABELS=['inorganico','lipidico','nanomaterial','polimerico'];PCOLS=['p_'+c for c in LABELS]
DEFAULT_TABULAR=ROOT/'modelos'/'tabular_v2'/'resultados'/'predicciones_clase4_mediciones_logistica.csv'

def csv(path):return pd.read_csv(path,encoding='utf-8-sig',keep_default_na=False)
def assert_origin(frame,synthetic):
    if not synthetic:assert 'sintetico' not in frame or not frame.sintetico.astype(str).str.lower().isin(['true','1']).any(),'Datos sintéticos detectados en entrada real'
def digest(ids):return hashlib.sha256('|'.join(map(str,ids)).encode()).hexdigest()
def weight_for_fold(y,tab,image,folds,held):
    train=folds!=held;assert train.any()
    grid=np.linspace(0,1,11)
    scored=[(f1_score(y[train],np.asarray(LABELS)[(w*tab[train]+(1-w)*image[train]).argmax(axis=1)],labels=LABELS,average='macro',zero_division=0),float(w)) for w in grid]
    return sorted(scored,key=lambda item:(-item[0],abs(item[1]-.5),item[1]))[0][1]
def probabilities(frame):
    present=[c in frame.columns for c in PCOLS]
    if all(present):
        probs=frame[PCOLS].to_numpy(float);assert np.isfinite(probs).all() and (probs>=0).all() and (probs<=1).all() and np.allclose(probs.sum(axis=1),1,atol=1e-4)
        return probs,'probabilidades por clase suministradas'
    assert not any(present),'Probabilidades incompletas: se necesitan las cuatro clases'
    confidence=pd.to_numeric(frame.confianza,errors='raise').to_numpy(float);assert ((confidence>=0)&(confidence<=1)).all()
    probs=np.repeat(((1-confidence)/3)[:,None],4,axis=1)
    for i,(label,c) in enumerate(zip(frame.prediccion,confidence)):probs[i,LABELS.index(label)]=c
    return probs,'solo confianza: score de clase predicha=confianza; resto uniforme; no son probabilidades calibradas verificadas'

def run(synthetic=False,tabular_path=DEFAULT_TABULAR):
    guard();cohort=csv(HERE/'conjunto_comparacion.csv');inventory=csv(HERE/'imagenes_comparacion.csv');cohort.fold=cohort.fold.astype(int)
    assert cohort.pmcid.is_unique;output=HERE/('resultados_sintetico' if synthetic else 'resultados');input_dir=HERE/'entrada_kabre'
    if synthetic:
        output.mkdir(exist_ok=True);input_dir=output/'entrada_sintetica';input_dir.mkdir(exist_ok=True);rng=np.random.default_rng(0);rows=[]
        for r in cohort.itertuples():
            pr=rng.dirichlet(np.ones(4));pr[LABELS.index(r.clase_modelo)]+=0.6;pr/=pr.sum();label=LABELS[int(pr.argmax())]
            rows.append({'pmcid':r.pmcid,'image_file':inventory.loc[inventory.pmcid.eq(r.pmcid),'image_file'].iloc[0],'real':r.clase_modelo,'prediccion':label,'confianza':float(pr.max()),'fold':r.fold,**dict(zip(PCOLS,pr)),'sintetico':True})
        pd.DataFrame(rows).to_csv(input_dir/'predicciones_simulado.csv',index=False,encoding='utf-8-sig')
    files=sorted(input_dir.glob('predicciones_*.csv')) if input_dir.exists() else []
    if not files:
        print('PENDIENTE Kabré: no hay predicciones de imagen reales. No se crea resultados/comparacion_justa.json.');return None
    tab=csv(tabular_path);assert tab.groupby('pmcid').y_real.nunique().eq(1).all() and tab.groupby('pmcid').fold.nunique().eq(1).all();assert set(PCOLS)<=set(tab)
    assert np.allclose(tab[PCOLS].to_numpy(float).sum(axis=1),1)
    tab=tab.groupby('pmcid').agg({**{c:'mean' for c in PCOLS},'y_real':'first','fold':'first'})
    tables={};sources={};allowed=set(zip(inventory.pmcid,inventory.image_file));fold_lookup=cohort.set_index('pmcid').fold.to_dict();class_lookup=cohort.set_index('pmcid').clase_modelo.to_dict()
    common_ids=set(cohort.pmcid)&set(tab.index)
    for path in files:
        frame=csv(path);assert {'pmcid','image_file','real','prediccion','confianza','fold'}<=set(frame)
        assert_origin(frame,synthetic)
        frame=frame[[pair in allowed for pair in zip(frame.pmcid,frame.image_file)]].copy();assert len(frame)>0
        assert not frame.duplicated(['pmcid','image_file']).any(),'Imagen repetida'
        assert frame.groupby('pmcid').fold.nunique().eq(1).all()
        assert np.array_equal(frame.fold.astype(int),frame.pmcid.map(fold_lookup)),'Fold Kabré incompatible'
        assert np.array_equal(frame.real,frame.pmcid.map(class_lookup)),'Etiqueta Kabré incompatible'
        pr,source=probabilities(frame);frame[PCOLS]=pr
        ag=frame.groupby('pmcid')[PCOLS].mean();tables[path.stem]=ag;sources[path.stem]=source;common_ids&=set(ag.index)
    ids=sorted(common_ids);assert ids,'Intersección vacía'
    effective=cohort.set_index('pmcid').loc[ids].reset_index();y=effective.clase_modelo.to_numpy(str);folds=effective.fold.to_numpy(int)
    assert set(folds)==set(range(5)),'Se requieren los cinco folds'
    assert np.array_equal(tab.loc[ids,'fold'].astype(int),folds) and np.array_equal(tab.loc[ids,'y_real'],y)
    tabpr=tab.loc[ids,PCOLS].to_numpy(float);experiments=[];output.mkdir(exist_ok=True)
    if synthetic:assert output.resolve().is_relative_to((HERE/'resultados_sintetico').resolve())
    effective.to_csv(output/'conjunto_efectivo.csv',index=False,encoding='utf-8-sig')
    for name,image in tables.items():
        ip=image.loc[ids,PCOLS].to_numpy(float);weighted=np.zeros_like(tabpr);weights=[]
        for fold in range(5):
            w=weight_for_fold(y,tabpr,ip,folds,fold);te=folds==fold;weighted[te]=w*tabpr[te]+(1-w)*ip[te]
            weights.append({'fold_test':fold,'peso_tabular':w,'folds_seleccion':[k for k in range(5) if k!=fold],'train_articulos':int((~te).sum()),'train_pmids_hash':digest(np.asarray(ids)[~te])})
        methods={}
        for method,pr in [('solo_tabular',tabpr),('solo_imagen',ip),('fusion_media',(tabpr+ip)/2),('fusion_ponderada',weighted)]:
            yp=np.asarray(LABELS)[pr.argmax(axis=1)];metrics=common.metric_values(y,yp,'clasificacion',LABELS);ci=common.bootstrap_by_article(y,yp,np.asarray(ids),'clasificacion',LABELS)
            record={'n_articulos':len(ids),'pmcid_hash':digest(ids),'folds_hash':digest(folds),'metricas':{m:{'valor':v,'ic95':ci[m]} for m,v in metrics.items()},'matriz_confusion_normalizada':confusion_matrix(y,yp,labels=LABELS,normalize='true').tolist()}
            methods[method]=record
            pd.DataFrame({'pmcid':ids,'real':y,'prediccion':yp,'fold':folds,**{c:pr[:,i] for i,c in enumerate(PCOLS)},'sintetico':synthetic}).to_csv(output/f'{name}_{method}.csv',index=False,encoding='utf-8-sig')
        assert len({r['pmcid_hash'] for r in methods.values()})==1 and len({r['folds_hash'] for r in methods.values()})==1
        experiments.append({'modelo_imagen':name,'fuente_scores':sources[name],'metodos':methods,'pesos_por_fold':weights})
    result={'sintetico':synthetic,'n_articulos_manifest':len(cohort),'n_articulos_comunes':len(ids),'faltan_predicciones_para':sorted(set(cohort.pmcid)-set(ids)),'clases':LABELS,'tabular':str(tabular_path.relative_to(ROOT)),'entradas_tabulares':['log10_size_nm','zeta_mV','pdi','indicadores_faltante'],'experimentos':experiments,'limite':'Pesos elegidos exclusivamente con etiquetas de otros folds sobre scores OOF. Para anidamiento totalmente estricto se necesitan scores internos por outer-fold del clúster; el protocolo suministrado no contiene esa procedencia. No se afirma validación externa ni calibración de scores reconstruidos.'}
    write_json(output/'comparacion_justa.json',result);guard();print(f'Comparación {"SINTÉTICA" if synthetic else "real"}: {len(ids)} artículos, todos los métodos y modelos usan mismos IDs/folds.');return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--sintetico',action='store_true');parser.add_argument('--tabular',type=Path,default=DEFAULT_TABULAR);args=parser.parse_args();run(args.sintetico,args.tabular)
