"""Prueba aislada del bloqueo de cierre; fixtures fuera del conjunto científico."""
import contextlib
import io
import json
import uuid
from pathlib import Path
import ajuste1 as a

original_out = a.OUT
test_root=(original_out/'_pruebas_temporales').resolve()
test_root.mkdir(exist_ok=True)
try:
 with contextlib.nullcontext(test_root/('cierre_'+uuid.uuid4().hex)) as folder:
  folder.mkdir()
  assert Path(folder).resolve().is_relative_to(test_root)
  a.OUT = Path(folder)
  a.csvout(a.OUT/'orden_articulos.csv', [{'pmcid':'FIXTURE','lote':18}])
  a.csvout(a.OUT/'recortes_v02.csv', [{'pmcid':'FIXTURE','lote':18}])
  a.dump(a.OUT/'progreso.json', {'ajuste1':{},'revision_ajuste1':{}})
  a.dump(a.OUT/'validacion_ajuste1_lote_18.json', {'F3':'PASS'})
  a.dump(a.OUT/'validacion_muestra_ajuste1_lote_18.json', {'mezcla_requerida':False})
  a.dump(a.OUT/'muestras/ajuste1/muestra_lote_18.json', [{'archivo_recorte':str(i)} for i in range(5)])
  with contextlib.redirect_stdout(io.StringIO()):
   a.review(18, [{'ok':True,'veredicto':'fixture, no dato científico'} for _ in range(5)])
  result=json.loads((a.OUT/'progreso.json').read_text(encoding='utf-8'))
  assert result['revision_ajuste1']['18']['bien']==5
  assert not result['revision_ajuste1']['18']['aprobado']
  assert result['revision_ajuste1']['18']['estado']=='PENDIENTE_MEZCLA'
  assert result['ajuste1']['lotes_validados']==[]
  a.dump(a.OUT/'validacion_ajuste1_lote_18.json', {'F3':'FAIL'})
  try:
   a.review(18, [{'ok':True,'veredicto':'fixture'} for _ in range(5)])
   raise RuntimeError('Se permitió revisar con F3 fallida')
  except AssertionError:
   pass
finally:
 a.OUT=original_out
a.dump(a.OUT/'REGRESION_CIERRES_AJUSTE1.json', {'estado':'PASS',
 'cinco_aciertos_sin_mezcla_no_aprueban':True,'F3_fallida_impide_cierre':True,
 'fixtures':'aislados y conservados en _pruebas_temporales para auditoría; no se agregaron al dataset'})
print('PASS: 5/5 sin mezcla no aprueba; F3 fallida impide cierre.')
