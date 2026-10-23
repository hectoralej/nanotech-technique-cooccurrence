"""Reproducible keyword mentions from local JATS methods; no network or LLM extraction."""
from __future__ import annotations
import sys
sys.dont_write_bytecode=True
import hashlib,json,re,os
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
# The bundled Python has lxml; pure-Python requests/yaml may live in the project Python.
sys.path.insert(0,str(ROOT))
sys.path.append(str(Path(os.environ.get('LOCALAPPDATA',r'C:\Users\Hector\AppData\Local'))/'Programs'/'Python'/'Python313'/'Lib'/'site-packages'))
from curation import textprep
sys.path.insert(0,str(ROOT/'modelos'/'ronda2'))
from control import guard,write_json

RULES={
'met_nanoprecipitacion':r'\bnano[ -]?precipitat\w*',
'met_emulsion_evaporacion':r'\bemulsi(?:on|ons|fi\w*)\b|solvent[ -]+evaporat\w*',
'met_pelicula_lipidica':r'(?:thin[ -]+film|lipid[ -]+film|film)[ -]+hydrat\w*|thin[ -]+film[ -]+(?:method|technique)',
'met_gelificacion_ionica':r'\bion(?:ic|otropic)[ -]+gelat\w*',
'met_microfluidica':r'\bmicrofluid\w*',
'met_sonicacion':r'\bsonicat\w*|\bultrasonicat\w*',
'met_homogeneizacion_alta_presion':r'high[ -]+pressure[ -]+homogeni[sz]\w*|\bHPH\b',
'met_extrusion':r'\bextrusi(?:on|ons)\b|\bextrud\w*',
'met_sintesis_verde':r'\bgreen[ -]+synth\w*|\bbiogenic[ -]+synth\w*|\b(?:plant|leaf|leaves|root|fruit|peel|bark|seed|flower|stem|herbal)[ -]+extracts?\b',
'met_sol_gel':r'\bsol[ -]+gels?\b',
'met_coprecipitacion':r'\bco[ -]?precipitat\w*',
'met_hidrotermal':r'\bhydrothermal\w*',
'mat_quitosano':r'\bchitosans?\b',
'mat_PLGA':r'\bPLGA\b|\bpoly.{0,20}(?:lactic|lactide).{0,25}glycoli\w*',
'mat_PEG':r'\bPEG(?:[ -]?\d+)?\b|poly[ -]?ethylene[ -]?glycols?|\bpegylat\w*',
'mat_colesterol':r'\bcholesterols?\b',
'mat_fosfatidilcolina_lecitina':r'\bphosphatidyl[ -]?cholines?\b|\blecithins?\b',
'mat_acido_estearico_lipido_solido':r'\bstearic[ -]+acid\b|\bsolid[ -]+lipids?\b',
'mat_plata':r'\bsilver\b|\bAgNPs?\b|\bAg\b',
'mat_oro':r'\bgold\b|\bAuNPs?\b|\bAu\b',
'mat_silice':r'\bsilica\b|\bsilicon[ -]+dioxide\b|\bSiO2\b',
'mat_oxido_hierro':r'\biron[ -]+oxides?\b|\bFe[23]O[34]\b|\bmagnetite\b|\bmaghemite\b',
'mat_oxido_zinc':r'\bzinc[ -]+oxides?\b|\bZnO\b',
'mat_oxido_titanio':r'\btitanium[ -]+(?:dioxide|oxides?)\b|\bTiO2\b',
'mat_grafeno':r'\bgraphenes?\b',
'mat_almidon_celulosa':r'\bstarches?\b|\bstarch\b|\bcellulos\w*',
'ctx_carga_farmaco':r'\bloaded\b|\bencapsulat\w*',
'ctx_DLS':r'\bdynamic[ -]+light[ -]+scattering\b|\bzetasizers?\b|\bDLS\b',
}

def scope_text(pmcid):
    article=textprep.article_text(pmcid)
    methods='\n'.join(f'{h} {p}' for h,p in article['methods'])
    if methods.strip():return methods,'metodos'
    return textprep.full_text(pmcid),'texto_completo_sin_referencias'

def literal(text,match):
    start=max(0,match.start()-90);end=min(len(text),start+200)
    if match.end()>end:start=max(0,match.end()-200);end=match.end()
    return text[start:end]

def main():
    guard();HERE.mkdir(exist_ok=True)
    articles=pd.read_csv(ROOT/'curation'/'ext_articulos.csv',encoding='utf-8-sig',keep_default_na=False)
    articles=articles[articles.tier.isin(['E1','E2'])]
    rows=[];positive=[];sources=[]
    patterns={flag:re.compile(rx,re.I) for flag,rx in RULES.items()}
    for i,pm in enumerate(articles.pmcid):
        text,scope=scope_text(pm);assert text.strip(),f'Texto vacío {pm}'
        rec={'pmcid':pm}
        for flag,rx in patterns.items():
            match=rx.search(text);rec[flag]=int(match is not None)
            if match:
                quote=literal(text,match);assert quote in text and len(quote)<=200
                positive.append({'pmcid':pm,'bandera':flag,'frase_exacta':quote,'coincidencia':match.group(),'fuente':scope})
        rows.append(rec);sources.append({'pmcid':pm,'fuente':scope,'n_caracteres':len(text),'sha256_texto':hashlib.sha256(text.encode()).hexdigest()})
        if (i+1)%250==0:print(f'Formulación: {i+1}/{len(articles)} textos leídos',flush=True)
    frame=pd.DataFrame(rows);counts=frame.drop(columns='pmcid').sum();kept=counts[counts>=10].index.tolist()
    frame[['pmcid',*kept]].to_csv(HERE/'formulacion_articulos.csv',index=False,encoding='utf-8-sig')
    rates=pd.DataFrame({'bandera':counts.index,'n_articulos':counts.values,'tasa':counts.values/len(frame),'retenida':counts.values>=10})
    rates.to_csv(HERE/'tasas_banderas.csv',index=False,encoding='utf-8-sig');pd.DataFrame(sources).to_csv(HERE/'fuentes_texto.csv',index=False,encoding='utf-8-sig')
    positives=pd.DataFrame(positive);pool=positives[positives.bandera.isin(kept)].sort_values(['pmcid','bandera']).reset_index(drop=True)
    idx=np.random.default_rng(0).choice(len(pool),30,replace=False);examples=pool.iloc[idx].reset_index(drop=True)
    review_path=HERE/'revision_evidencias.json';reviews=json.loads(review_path.read_text(encoding='utf-8')) if review_path.exists() else {}
    examples['revision']=[reviews.get(f'{r.pmcid}|{r.bandera}',{}).get('revision','pendiente') for r in examples.itertuples()]
    examples['nota_revision']=[reviews.get(f'{r.pmcid}|{r.bandera}',{}).get('nota','') for r in examples.itertuples()]
    examples.to_csv(HERE/'evidencia_formulacion.csv',index=False,encoding='utf-8-sig')
    assert set(examples.pmcid)<=set(frame.pmcid) and frame.pmcid.is_unique and len(examples)==30
    write_json(HERE/'reglas.json',{'reglas':RULES,'retenidas':kept,'descartadas_menos_10':counts[counts<10].index.tolist(),'semilla':0,'muestreo':'30 pares artículo-bandera positivos, uniformes sin reemplazo sobre banderas retenidas','definicion':'Presencia textual; no demuestra que el método se usó en la nanopartícula objetivo.'})
    write_json(HERE/'validacion_B1.json',{'articulos':len(frame),'fuentes':pd.Series([x['fuente'] for x in sources]).value_counts().to_dict(),'banderas_retenidas':len(kept),'descartadas':counts[counts<10].index.tolist(),'ejemplos':30,'revisados':int(examples.revision.ne('pendiente').sum()),'correctos':int(examples.revision.eq('correcto').sum()),'porcentaje_correcto':float(100*examples.revision.eq('correcto').mean()) if examples.revision.ne('pendiente').all() else None})
    guard();print(rates.to_string(index=False));print(examples[['pmcid','bandera','frase_exacta']].to_json(orient='records',force_ascii=False,indent=2))

if __name__=='__main__':main()
