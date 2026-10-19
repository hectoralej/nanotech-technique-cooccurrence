# make all  reproduce todo el analisis (en Windows sin make: .\run_all.ps1)
# Requiere Python >= 3.11 y: pip install -r requirements.txt
PY ?= python

.PHONY: all test ids sample pilot scale gold analyze hypotheses figures report clean-cache

all: test ids sample pilot scale analyze hypotheses figures report

test:
	$(PY) -m pytest tests -q

ids:            # IDs por familia (Europe PMC, cursorMark, cache cruda) -> data/ids/
	$(PY) -m src.search

sample:         # orden de muestreo estratificado reproducible (semilla en config/sampling.yaml)
	$(PY) -m src.sample

pilot:
	$(PY) -m src.extract --pilot

scale:          # descarga permitida + deteccion; criterio de parada de precision (brief 4.3)
	$(PY) -m src.extract --trend --scale

gold:           # conjunto de validacion: muestra, paquetes de revision, metricas (la anotacion es manual)
	$(PY) -m src.gold sample
	$(PY) -m src.gold packets
	$(PY) -m src.gold build-provisional
	$(PY) -m src.gold evaluate

analyze:
	$(PY) -m src.analyze

hypotheses:
	$(PY) -m src.hypotheses

figures:
	$(PY) -m src.plots

report:
	$(PY) -m src.report

clean-cache:    # borra el XML crudo descargado (no se redistribuye)
	rm -rf data/cache/fulltext
