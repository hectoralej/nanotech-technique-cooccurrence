"""Serializa cajas trazadas manualmente; no segmenta ni clasifica imagenes."""
import json
import runpy
import sys
from pathlib import Path
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
CAJAS = OUT.parents[1]
validar = runpy.run_path(str(CAJAS.parent / 'consolidar_cajas.py'))['validar']

def guardar(lote, raw):
    plan = json.loads((CAJAS / 'lotes' / (lote+'.json')).read_text(encoding='utf-8-sig'))
    assert plan['asignado'] in ('codex', 'ambos')
    bloques = [b for b in raw.strip().split('\n\n') if b.strip()]
    assert len(bloques) == len(plan['figuras']), (len(bloques), len(plan['figuras']))
    data, notas, avisos = {}, {}, {}
    for fig, bloque in zip(plan['figuras'], bloques):
        paneles = []
        for line in bloque.splitlines():
            if line.startswith('#'):
                notas[fig['fig_id']] = line[1:].strip()
                continue
            t, x0, y0, x1, y1, *flags = line.split()
            p = dict(tipo={'m':'micro', 's':'espectro', 'o':'otro'}[t], caja=[round(float(x),3) for x in (x0,y0,x1,y1)])
            if 'c' in flags: p['cascada'] = True
            for flag in flags:
                if flag.startswith('p='): p.update(padre=int(flag[2:]), rel='inset')
                if flag.startswith('t='): p['tecnica'] = flag[2:]
            if 'bio' in flags: p['contenido'] = 'biologico'
            if 'contexto' in flags: p['contenido'] = 'particulas_en_contexto_biologico'
            if '?' in flags: p['contenido'] = 'indeterminado'
            paneles.append(p)
        esperado = fig['esperado']['micro'] + fig['esperado']['espectro']
        err, aviso = validar(paneles, esperado)
        assert not err, (fig['fig_id'],err)
        if aviso: avisos[fig['fig_id']] = aviso
        data[fig['fig_id']] = paneles
    data['_revision'] = {'notas':notas, 'discrepancias_estimacion_lote':avisos, 'reglas':'v2, contenido biologico 25-oct', 'metodo':'Cajas manuales sobre cuadricula; sin pies ni otros revisores'}
    target = OUT / (lote+'.json')
    assert not target.exists(), 'No sobrescribir lote terminado'
    tmp = target.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    tmp.replace(target)
    with (OUT/'CHECKPOINTS_RONDA4.md').open('a',encoding='utf-8') as file:
        file.write(f'\n{datetime.now(timezone.utc).isoformat()}: {lote}, {len(plan["figuras"])} figuras, {len(notas)} notas, {len(avisos)} discrepancias de estimacion; estructura valida.\n')
    print(lote, 'figuras',len(plan['figuras']), 'notas',len(notas), 'discrepancias',len(avisos))

if __name__ == '__main__': guardar(sys.argv[1], sys.stdin.read())
