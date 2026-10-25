"""Informe descriptivo BIO; solo JSONL Codex, sin exclusiones ni variante B.
Por defecto exige cobertura completa; --permitir-incompleto informa ausencias.
"""
from pathlib import Path
import argparse, collections, csv, hashlib, json, re
from datetime import datetime, timezone
FLOW = Path(__file__).resolve().parent
ROOT = FLOW.parents[1]
OUT = FLOW / 'resultados/codex'
LABELS = ('particulas','biologico','particulas_en_contexto_biologico','mixto','indeterminado')

def read(p):
    with p.open(encoding='utf-8-sig',newline='') as h: return list(csv.DictReader(h))

def write(p, cols, rows):
    tmp=p.with_suffix(p.suffix+'.tmp')
    with tmp.open('w',encoding='utf-8-sig',newline='') as h:
        w=csv.DictWriter(h,fieldnames=cols);w.writeheader();w.writerows(rows)
    tmp.replace(p)

def norm(s):
    return re.sub('[^a-z0-9]','',re.sub(r'^(?:figure|fig)\.?\s*','',s.strip(),flags=re.I).casefold())

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--permitir-incompleto',action='store_true');args=ap.parse_args()
    plan=read(FLOW/'bio_plan.csv');assert len({r['fig_id'] for r in plan})==len(plan)
    lots=collections.defaultdict(list)
    for r in plan: lots[r['lote_b']].append(r)
    annotations={};sources=[];provenance=[];missing=[]
    for lot, fs in sorted(lots.items()):
        p=OUT/(lot+'.jsonl')
        if not p.exists(): missing.append(lot);continue
        ds=[json.loads(l) for l in p.read_text(encoding='utf-8-sig').splitlines() if l.strip()]
        fs=sorted(fs,key=lambda f:int(f['n_b']));assert len(ds)==len(fs),(lot,'longitud')
        for n,(d,f) in enumerate(zip(ds,fs),1):
            assert set(d)=={'n','n_bio','contenido','confianza','nota'}
            assert type(d['n']) is int and d['n']==int(f['n_b'])==n
            assert type(d['n_bio']) is int and d['n_bio']>=0
            assert type(d['confianza']) is int and d['confianza'] in (1,2,3)
            assert d['contenido'] in LABELS and len(d['nota'].split())<=12
            assert d['contenido']!='particulas' or d['n_bio']==0
            assert d['contenido'] not in LABELS[1:4] or d['n_bio']>0
            assert f['fig_id'] not in annotations
            annotations[f['fig_id']]={k:d[k] for k in ['n_bio','contenido','confianza','nota']}
            provenance.append(dict(fig_id=f['fig_id'],lote=lot,revisor='codex',archivo=str(p.relative_to(ROOT))))
        sources.append(dict(archivo=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    if missing and not args.permitir_incompleto: raise RuntimeError('Faltan JSONL locales: '+','.join(missing))
    keys={}
    for f in plan:
        pm,fg=f['fig_id'].split('|',1);key=(pm,norm(fg));assert key not in keys,('colisión',key);keys[key]=f['fig_id']
    image_fig=collections.defaultdict(set)
    for t in read(ROOT/'modelos/tipologia_figuras/tipologia_figuras.csv'):
        image_fig[(t['pmcid'],Path(t['archivo_grafico'].replace('\\','/')).name)].add(norm(t['figura']))
    index=read(ROOT/'modelos/comparacion/entrada_kabre/indice_embeddings.csv')
    assert len({(r['pmcid'],r['image_file']) for r in index})==len(index)
    article_folds=collections.defaultdict(set);cross=[]
    for r in index:
        assert r['fold'] in {'0','1','2','3','4'};article_folds[r['pmcid']].add(r['fold'])
        figs=image_fig.get((r['pmcid'],Path(r['image_file'].replace('\\','/')).name),set())
        assert len(figs)<=1,('imagen ambigua',r['pmcid'],r['image_file'])
        fid=keys.get((r['pmcid'],next(iter(figs)))) if figs else None
        d=annotations.get(fid,{})
        cross.append({**r,'fig_id':fid or '', 'contenido':d.get('contenido',''),'estado':'revisada' if d else ('sin_anotacion_local' if fid else 'sin_enlace_bio')})
    assert all(len(v)==1 for v in article_folds.values()),'Artículo en varios folds'
    assert len(cross)==len(index)
    rows=[dict(fig_id=f['fig_id'],**annotations[f['fig_id']]) for f in plan if f['fig_id'] in annotations]
    write(FLOW/'contenido_bio.csv',['fig_id','n_bio','contenido','confianza','nota'],rows)
    write(OUT/'PROCEDENCIA_CONTENIDO_BIO.csv',['fig_id','lote','revisor','archivo'],provenance)
    write(OUT/'CRUCE_CONTENIDO_BIO.csv',['pmcid','image_file','clase_modelo','fold','fig_id','contenido','estado'],cross)
    counts=collections.Counter(r['contenido'] for r in rows);states=collections.Counter(r['estado'] for r in cross)
    status='COBERTURA LOCAL PARCIAL' if missing else 'COMPLETO'
    lines=['# Contenido biológico: informe descriptivo','',f'Estado: **{status}**.',f'Plan: {len(plan)} figuras; revisadas localmente: {len(rows)}; sin JSONL local: {len(plan)-len(rows)}.','B061–B069 se comunicaron como completados en un ZIP; el usuario indicó omitir su revisión. No se infieren etiquetas de archivos ausentes.' if missing else 'Cobertura completa.','','No se generan variantes B ni listas de exclusión. figuras_vision.csv permanece intacto.','','## Figuras por contenido','','| Contenido | Figuras |','|---|---:|']
    lines += [f'| {k} | {counts[k]} |' for k in LABELS]
    lines += ['','## Cruce con el modelo de clase','',f'{len(index)} imágenes de {len(article_folds)} artículos. Unión: pmcid + archivo en tipología, luego pmcid + figura normalizada en bio_plan.','Las siguientes tablas cuentan imágenes del índice, no artículos únicos ni recortes. Indeterminado y falta de anotación se mantienen separados.']
    for col,title in [('clase_modelo','clase de portador'),('fold','fold')]:
        lines += ['',f'### Por {title}','','| Grupo | Total | particulas | biologico | particulas_en_contexto_biologico | mixto | indeterminado | Sin revisión/enlace local |','|---|---:|---:|---:|---:|---:|---:|---:|']
        for g in sorted({r[col] for r in cross}):
            sub=[r for r in cross if r[col]==g];c=collections.Counter(r['contenido'] for r in sub)
            lines.append('| '+' | '.join([g or 'sin_clase',str(len(sub)),*[str(c[k]) for k in LABELS],str(sum(r['estado']!='revisada' for r in sub))])+' |')
    lines += ['','## Validación y límites','',f'- Esquema, longitud y secuencia n: PASS ({len(sources)} lotes).','- Identificadores únicos, cruce sin multiplicación/pérdidas, un fold por artículo: PASS.',f'- Estado del cruce: {dict(states)}.','- Lotes sin JSONL: '+(', '.join(missing) or 'ninguno')+'.','- La validación estructural no certifica la exactitud semántica de las etiquetas visuales.','- Procedencia, cruce y hashes se conservan en resultados/codex; sin recomendaciones de exclusión para entrenar.','']
    (FLOW/'CONTENIDO_BIO.md').write_text('\n'.join(lines),encoding='utf-8')
    audit=dict(fecha_utc=datetime.now(timezone.utc).isoformat(),estado=status,figuras_plan=len(plan),figuras_revisadas=len(rows),lotes_ausentes=missing,por_contenido=dict(counts),cruce=dict(states),fuentes=sources)
    (OUT/'VALIDACION_CONSOLIDACION_BIO.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    assert len(read(FLOW/'contenido_bio.csv'))==len(rows)
    print(json.dumps({k:v for k,v in audit.items() if k!='fuentes'},ensure_ascii=False))

if __name__=='__main__': main()
