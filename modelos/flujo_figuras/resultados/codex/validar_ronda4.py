"""Consolidación aislada solo Codex; amplía a R el glob de la copia."""
from pathlib import Path
from datetime import datetime, timezone
import json,os,shutil,subprocess,sys

OUT=Path(__file__).resolve().parent
FLOW=OUT.parents[1]
stage=OUT/'_validacion_ronda4'
(stage/'resultados'/'codex').mkdir(parents=True,exist_ok=True)
lots=[];rows=[]
for f in sorted(OUT.glob('[LR][0-9][0-9][0-9].jsonl')):
    plan=json.loads((FLOW/'lotes'/f'{f.stem}.json').read_text(encoding='utf-8'))
    records=[json.loads(line) for line in f.read_text(encoding='utf-8').splitlines() if line.strip()]
    assert [r['n'] for r in records]==[r['n'] for r in plan['figuras']],f
    for r in records:
        assert r['paneles']==r['n_micro']+r['n_espectro']+r['n_otro'],(f,r['n'])
        assert r['confianza'] in (1,2,3) and len(r['nota'].split())<=12
        assert r['curvas_superpuestas'] in ('si','no','na') and r['espectro_limpio'] in ('si','no','na')
        if 'n_bio' in r: assert isinstance(r['n_bio'],int) and 0<=r['n_bio']<=r['n_otro']
    rows.extend(records);lots.append(f.stem)
    shutil.copy2(f,stage/'resultados'/'codex'/f.name)
source=(FLOW/'consolidar.py').read_text(encoding='utf-8')
source=source.replace('carpeta.glob("L*.jsonl")','carpeta.glob("[LR]*.jsonl")')
(stage/'consolidar.py').write_text(source,encoding='utf-8')
shutil.copy2(FLOW/'plan_lotes.csv',stage/'plan_lotes.csv')
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
proc=subprocess.run([sys.executable,str(stage/'consolidar.py')],capture_output=True,text=True,encoding='utf-8',env=env)
(stage/'consolidacion.log').write_text(proc.stdout+proc.stderr,encoding='utf-8')
assert proc.returncode==0,proc.stderr
assert 'Errores de formato' not in proc.stdout,proc.stdout[-3000:]
report=dict(fecha=datetime.now(timezone.utc).isoformat(),estado='PASS',lotes=lots,figuras=len(rows),
            confianza_1=sum(r['confianza']==1 for r in rows),
            aislamiento='Solo Codex; salidas dentro de resultados/codex',
            ajuste_copia='glob L*.jsonl -> [LR]*.jsonl; original intacto')
(OUT/'VALIDACION_RONDA4.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='lotes'},ensure_ascii=False))
