"""Guarda decisiones visuales manuales: no clasifica imágenes."""
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
FLOW = OUT.parents[1]

def guardar(lote, decisiones):
    plan = json.loads((FLOW/'lotes'/f'{lote}.json').read_text(encoding='utf-8'))
    assert plan['asignado'] in ('codex', 'ambos')
    assert len(decisiones) == len(plan['figuras'])
    rows = []
    for figura, decision in zip(plan['figuras'], decisiones):
        # micro, espectro, otro, superpuestas, limpio, técnicas, confianza, nota, cascada, calidad
        m,s,o,superp,limpio,tecnicas,conf,nota,*extra = decision
        assert min(m,s,o)>=0 and m+s+o>0
        assert superp in ('si','no','na') and limpio in ('si','no','na')
        assert conf in (1,2,3) and len(nota.split())<=12
        assert (s>0) == (superp!='na') == (limpio!='na')
        row = dict(n=figura['n'],paneles=m+s+o,n_micro=m,n_espectro=s,n_otro=o,
                   curvas_superpuestas=superp,espectro_limpio=limpio,tecnicas=tecnicas,
                   calidad=extra[1] if len(extra)>1 else 'buena',confianza=conf,nota=nota)
        if extra and extra[0]: row['cascada']=True
        rows.append(row)
    target=OUT/f'{lote}.jsonl'
    assert not target.exists(), 'No sobrescribir un lote terminado'
    temp=target.with_suffix('.jsonl.tmp')
    temp.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    temp.replace(target)
    now=datetime.now(timezone.utc).isoformat()
    with (OUT/'CHECKPOINTS_RONDA4.md').open('a',encoding='utf-8') as file:
        file.write(f'\n{now}: {lote}, {len(rows)} figuras, confianza 1: {sum(r["confianza"]==1 for r in rows)}. Revisión visual desde cero, reglas 24-oct.\n')
    print(lote,len(rows),'confianza_1',sum(r['confianza']==1 for r in rows))

if __name__=='__main__':
    guardar(sys.argv[1],json.loads(sys.stdin.read()))
