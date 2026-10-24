"""Guarda anotaciones visuales explícitas; no clasifica ni consulta pies u otro revisor."""
import json, sys
from pathlib import Path
OUT=Path(__file__).resolve().parent
FLOW=OUT.parents[1]
lot=sys.argv[1]
plan=json.loads((FLOW/'lotes'/f'{lot}.json').read_text(encoding='utf-8'))
assert plan['asignado'] in ['codex','ambos']
data=json.loads((OUT/f'{lot}_anotaciones.json').read_text(encoding='utf-8'))
assert len(data)==len(plan['figuras'])
rows=[]
for fig, row in zip(plan['figuras'],data):
 m,e,o,curves,clean,tech,quality,confidence,note=row
 assert all(type(x) is int and x>=0 for x in [m,e,o]) and m+e+o>=1
 assert curves in ['si','no','na'] and clean in ['si','no','na']
 assert (e==0)==(curves=='na')==(clean=='na')
 assert quality in ['buena','regular','mala'] and confidence in [1,2,3]
 assert len(note.split())<=12
 rows.append(dict(n=fig['n'],paneles=m+e+o,n_micro=m,n_espectro=e,n_otro=o,curvas_superpuestas=curves,espectro_limpio=clean,tecnicas=tech,calidad=quality,confianza=confidence,nota=note))
assert len({r['n'] for r in rows})==len(rows)
target=OUT/f'{lot}.jsonl'
if target.exists():
 previous=[json.loads(x) for x in target.read_text(encoding='utf-8').splitlines() if x.strip()]
 assert previous==rows, 'No sobrescribir un lote diferente sin revisión explícita.'
else:
 tmp=target.with_suffix('.jsonl.tmp')
 tmp.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8'); tmp.replace(target)
assert len(target.read_text(encoding='utf-8').splitlines())==len(rows)
print(f'{lot}: {len(rows)} figuras guardadas; confianza 1: {sum(r["confianza"]==1 for r in rows)}')
