"""Ejecuta consolidar.py sin cambiarlo, en copia aislada con resultados SOLO Codex."""
import datetime, json, os, re, shutil, subprocess, sys
from pathlib import Path
OUT=Path(__file__).resolve().parent
FLOW=OUT.parents[1]
rows=[]; lots=[]
for f in sorted(OUT.glob('L[0-9][0-9][0-9].jsonl')):
 plan=json.loads((FLOW/'lotes'/f'{f.stem}.json').read_text(encoding='utf-8'))
 rr=[json.loads(x) for x in f.read_text(encoding='utf-8').splitlines() if x.strip()]
 assert [x['n'] for x in rr]==[x['n'] for x in plan['figuras']]
 assert plan['asignado'] in ['codex','ambos']
 for r in rr:
  assert r['paneles']==r['n_micro']+r['n_espectro']+r['n_otro']
  assert r['confianza'] in [1,2,3] and len(r['nota'].split())<=12
 rows.extend(rr);lots.append(f.stem)
stage=OUT/'_validacion_aislada';(stage/'resultados/codex').mkdir(parents=True,exist_ok=True)
for name in ['consolidar.py','plan_lotes.csv']:shutil.copy2(FLOW/name,stage/name)
for lot in lots:shutil.copy2(OUT/f'{lot}.jsonl',stage/'resultados/codex'/f'{lot}.jsonl')
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
result=subprocess.run([sys.executable,str(stage/'consolidar.py')],capture_output=True,text=True,encoding='utf-8',env=env)
(stage/'consolidacion.log').write_text(result.stdout+result.stderr,encoding='utf-8')
assert result.returncode==0, result.stderr
assert 'Errores de formato' not in result.stdout, 'Ver consolidacion.log'
report={'hora':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).isoformat(timespec='seconds'),'zona_horaria':'America/Phoenix','estado':'PASS','lotes':lots,'figuras':len(rows),'confianza_1':sum(r['confianza']==1 for r in rows),'alcance':'solo Codex, consolidar.py sin modificar; no se leyeron resultados de Claude; todas las salidas dentro de resultados/codex'}
(OUT/'VALIDACION_AISLADA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'CHECKPOINTS.md').open('a',encoding='utf-8') as fp:fp.write(f'\n## {report["hora"]}\n{len(lots)} lotes, {len(rows)} figuras, confianza 1: {report["confianza_1"]}. Consolidación aislada PASS.\n')
print(json.dumps(report,ensure_ascii=False))
