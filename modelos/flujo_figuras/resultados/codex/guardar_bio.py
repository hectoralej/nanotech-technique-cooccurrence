from pathlib import Path
import json,sys
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent
FLOW=OUT.parent.parent
LABELS={'p':'particulas','b':'biologico','c':'particulas_en_contexto_biologico','m':'mixto','i':'indeterminado'}
def validate(lot,rows):
    plan=json.loads((FLOW/'lotes'/f'{lot}.json').read_text(encoding='utf-8-sig'))
    assert plan['asignado'] in ('codex','ambos') and plan['tipo']=='contenido_biologico'
    assert len(rows)==len(plan['figuras'])
    for n,row in enumerate(rows,1):
        assert set(row)=={'n','n_bio','contenido','confianza','nota'}
        assert row['n']==n==plan['figuras'][n-1]['n']
        assert type(row['n_bio']) is int and row['n_bio']>=0
        assert row['contenido'] in LABELS.values() and row['confianza'] in (1,2,3)
        assert len(row['nota'].split())<=12
        if row['contenido']=='particulas': assert row['n_bio']==0
        if row['contenido'] in ('biologico','particulas_en_contexto_biologico','mixto'): assert row['n_bio']>0
    return len(rows),sum(x['contenido']!='particulas' for x in rows)
def main():
    arg=sys.argv[1]
    if arg=='--validar':
        checks=[]
        for p in sorted(OUT.glob('B[0-9][0-9][0-9].jsonl')):
            rows=[json.loads(l) for l in p.read_text(encoding='utf-8-sig').splitlines() if l.strip()]
            n,k=validate(p.stem,rows);checks.append({'lote':p.stem,'figuras':n,'no_particulas':k})
        report={'fecha_utc':datetime.now(timezone.utc).isoformat(),'estado':'PASS','lotes':checks,'figuras':sum(c['figuras'] for c in checks),'no_particulas':sum(c['no_particulas'] for c in checks)}
        (OUT/'VALIDACION_BIO.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False));return
    rows=[]
    for n,line in enumerate(sys.stdin.read().strip().splitlines(),1):
        fields,_,note=line.partition('|');label,count,confidence=fields.split()
        rows.append(dict(n=n,n_bio=int(count),contenido=LABELS[label],confianza=int(confidence),nota=note.strip()))
    total,k=validate(arg,rows)
    target=OUT/f'{arg}.jsonl'
    assert not target.exists(), 'No sobrescribir lote existente'
    tmp=target.with_suffix('.jsonl.tmp')
    tmp.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8');tmp.replace(target)
    with (OUT/'CHECKPOINTS_BIO.md').open('a',encoding='utf-8') as f:f.write(f'\n- {datetime.now(timezone.utc).isoformat()}: {arg} guardado, {total} figuras, {k} distintas de particulas. Comprobados esquema y orden.\n')
    print(arg,total,'figuras;',k,'no particulas')
if __name__=='__main__':main()
