# Kabré: qué sabemos, qué hay que comprobar y cómo trabajar allí

Acceso: solo Héctor. Plazo del proyecto: domingo 25 de octubre, 5:45 pm. **Regla de oro: el producto no puede depender de Kabré.** Todo lo que se haga allí tiene una versión de respaldo en la computadora (modelo congelado en CPU); Kabré es un extra para subir la calidad.

## 1. Lo que se sabe (y lo que no)
Encontrado en la web:
- Kabré es el clúster del Laboratorio Nacional de Computación Avanzada (CNCA) del CeNAT, descrito como heterogéneo, con secciones por área de aplicación ([Revista Tecnología en Marcha, 2020](https://revistas.tec.ac.cr/index.php/tec_marcha/article/view/5087)).
- Un artículo de detección sísmica en Costa Rica describe en su sección de inteligencia artificial nodos **Nukwa** con GPU en dos configuraciones: Xeon E3 de 4 núcleos con 16 GB de RAM y una **Tesla K40c**, y Xeon Silver de 24 núcleos con 32 GB de RAM y una **Tesla V100 de 32 GB** ([arXiv 2109.02723](https://arxiv.org/pdf/2109.02723)). Es consistente con lo que recuerda Héctor: un tipo de nodo bastante más potente que otro.
- Una hoja de referencia del CNCA de 2017 usa colas PBS/Torque (`qsub`) y menciona nodos Zárate, Tule y Cadejos ([hoja de referencia, UCR](https://jeisson.ecci.ucr.ac.cr/tmp/old/proy1/kabre-cheatsheet.pdf)). **Está desactualizada**: no menciona Nukwa ni Kura. No usarla como guía de comandos.

**No se encontró** documentación pública sobre acceso a internet desde los nodos de cómputo, cuota de disco ni la lista actual de colas. Nada de eso se debe dar por supuesto: se comprueba en la sección 2. La fuente oficial es la documentación del CNCA (`cluster.cenat.ac.cr`) o su soporte (`cnca@cenat.ac.cr`).

## 1b. Lo que muestran las capturas del portal de Héctor (23 oct)
- **Acceso:** SSH por el puerto **22022** (`ssh -p 22022 usuario@…`) con **doble factor** (QR en una app de autenticación; al entrar piden contraseña y luego el código de 6 dígitos). También hay un portal web, **Kabré OnDemand** (versión 3.0.3), con: *Files* (explorador y **subida de archivos desde el navegador**), *Jobs*, *Clusters* (terminal de Kabré), *Interactive Apps* (**Jupyter Notebook** y **RStudio**) y *Mutüä*.
- **Formulario de Jupyter:** cola, horas, nodos, núcleos (por defecto 4), memoria (por defecto 16 GB), nodo exclusivo y aviso por correo.
- **Colas visibles:** `nukwa`, `nukwa-wide`, `nukwa-long`, `nukwa-debug`, `nukwa-v100`, `nukwa-l40s`, `kura`, `kura-wide`, `kura-long`, `kura-debug`, `kura-test`, `dribe`, `dribe-long`, `dribe-debug`.

**Lectura (a confirmar con `sinfo`/el reconocimiento de abajo, no es un hecho verificado):**
- `nukwa-v100` y `nukwa-l40s` son colas **por tipo de GPU**: V100 (32 GB, la que describía el artículo sísmico) y **L40S (48 GB, arquitectura más reciente)**. Para entrenar una CNN o un transformer, la **L40S** debería ser la más potente; la V100 sigue siendo buena.
- `nukwa` a secas, `-wide` y `-long` parecen variantes por tamaño y duración sobre los mismos nodos; `-debug` es para pruebas cortas.
- `kura` y `dribe` no aparecen en ninguna fuente que encontré. **No asumir que tienen GPU**: pueden ser nodos de CPU. Se comprueba con `sinfo` (columna de recursos `GRES`).

**Colas recomendadas:** `nukwa-debug` para la prueba de humo; `nukwa-l40s` para entrenamiento (si hay GPU libre; si hay cola larga, `nukwa-v100`); `kura*` solo si el reconocimiento muestra GPU.

**Dos ventajas de OnDemand:** (1) se puede **subir el zip desde el navegador** (*Files → Upload*) sin `scp` ni el segundo factor por SSH; (2) un Jupyter en un nodo con GPU incluye una **terminal** (*New → Terminal*): ahí se ejecuta la prueba de humo directamente en el nodo de cómputo, que es justo donde hay que medir si hay internet.

**Seguridad:** no compartir el QR, los códigos de 6 dígitos ni la contraseña con nadie, ni con ninguna IA. Las salidas de la prueba de humo no contienen secretos.

## 2. Reconocimiento (30 minutos, Héctor, hoy)
**Camino más corto (sin SSH):** en OnDemand → *Interactive Apps → Jupyter Notebook* → cola `nukwa-debug`, 1 hora, 4 núcleos, 16 GB → *Launch*. Dentro: *Upload* de `modelos/kabre/prueba_de_humo.py` y, en una terminal, `python prueba_de_humo.py`. Pega a Claude el JSON que escribe (nodo, GPU, internet, librerías, disco). Después repite en `nukwa-l40s`. Los comandos de abajo sirven si prefieres el SSH.
Desde el nodo de acceso (login), anotando la salida de cada comando en `KABRE_NOTAS.md` (sin contraseñas ni claves):
1. `hostname; whoami; echo $HOME; df -h $HOME` y `quota -s` (si existe): espacio disponible.
2. `sinfo` (si usa Slurm) o `qstat -q` (si usa PBS): colas, GPU y límites de tiempo. `scontrol show partition` da los máximos.
3. `module avail 2>&1 | head -60`: ¿hay Python, CUDA, PyTorch o Anaconda como módulo?
4. `python3 --version; which python3 pip3 conda`.
5. **Internet desde el login:** `curl -sI https://pypi.org | head -1` y `curl -sI https://github.com | head -1`.
6. **Internet desde un nodo de cómputo** (la prueba que importa): un trabajo mínimo de 2 minutos en una cola con GPU que ejecute `hostname; nvidia-smi; curl -sI https://pypi.org | head -1; python3 -c "import torch;print(torch.__version__)"`.
7. Si hay internet en el login pero no en los nodos: instalar los paquetes en un entorno virtual **desde el login** (el entorno queda en el disco compartido y los nodos lo usan) y llevar los pesos del modelo preentrenado en el paquete (sección 3).

## 3. Cómo pasar cosas de y hacia Kabré: zips, no GitHub
**Recomendación: zip + `scp`/`rsync`.** Razones: el repositorio es privado y para clonarlo en un clúster compartido habría que dejar credenciales allí; los datos que se necesitan son pequeños (unos 300 MB); y un zip con una versión fija es reproducible.

- **Paquete de subida** (`kabre_paquete_v0.1.zip`, lo prepara Claude/Codex en la computadora): `curation/v0.1/tabla_modelo.csv`, los 4 CSV `ext_*`, el zip de imágenes (260 MB), los scripts de `modelos/`, los pesos preentrenados que se vayan a usar (descargados antes en la computadora si los nodos no tienen internet), una lista de dependencias y las plantillas de trabajo.
- **Cambios de código:** se editan en la computadora, se vuelve a empaquetar solo `modelos/` (unos KB) y se sube. Editar a mano en el clúster solo para arreglos mínimos, y copiar el cambio de vuelta.
- **Resultados de vuelta:** solo archivos pequeños (métricas en JSON, predicciones, un archivo de pesos). No traer las imágenes de vuelta.
- Si resulta que los nodos de acceso sí tienen internet y Héctor quiere usar Git, usar `git clone` de una **copia pública solo con código** o un token de solo lectura que se revoque al terminar; no dejar credenciales con permisos de escritura en un clúster compartido.
- Disco: los términos de uso desaconsejan almacenar grandes volúmenes. Nuestros ~300 MB de imágenes más embeddings caben, pero conviene confirmar la cuota y no guardar nada innecesario.

## 4. Qué se hace allí (por orden de complejidad)
1. **Prueba de humo (30 min):** un trabajo corto que cargue `tabla_modelo.csv` y una imagen, ejecute un modelo preentrenado en GPU y escriba un archivo de salida. Confirma que todo el circuito funciona (conexión, colas, entorno, GPU, transferencia).
2. **Embeddings de las 2.149 imágenes** con un modelo preentrenado congelado (minutos en una V100) + clasificador ligero encima, evaluado con `fold` por artículo. Es el respaldo y la línea base de imágenes.
3. **CNN con ajuste fino** del modelo preentrenado en las micrografías (el modelo principal), con puntos de control por época y evaluación por artículo.
4. **Modelo multimodal:** imagen + descriptores + espectros (la meta). Se empieza con la fusión simple de vectores.

**Trabajos de 6 horas** como propone Héctor, con **puntos de control en cada época** y scripts que reanudan desde el último punto; así, si hay que cambiar de nodo (de Nukwa a Kura o a otra cola) o la cola se corta, no se pierde el avance. Pide primero la cola corta para depurar y después la larga.

## 5. Cuándo se corta Kabré del plan
- **Viernes 23 mediodía:** si la prueba de humo no funciona, se abandona Kabré para esta entrega y se usa la computadora (embeddings en CPU con un modelo preentrenado). Kabré queda para después del hackatón.
- **Sábado 24 mediodía:** lo que no haya terminado en Kabré no entra en el video; lo que ya tenga métricas verificadas, sí.

## 6. Preguntas para el profesor William (conexión a Teams del viernes)
1. ¿Nos recomienda un modelo preentrenado concreto para micrografías electrónicas (TEM/SEM) con pocas imágenes, o mejor ajustar uno general?
2. Con ~2.000 imágenes de unos 1.700 artículos, ¿es razonable el ajuste fino de una CNN o es mejor quedarnos con embeddings congelados?
3. ¿Cómo debemos presentar la evaluación para que sea convincente (validación por artículo, intervalos de confianza, línea base)?
4. ¿Hay algún compañero o docente que conozca el sistema de colas de Kabré, o un contacto de soporte para el acceso a internet desde los nodos?
5. Sobre el seminario 2: ¿qué espera ver en la entrega (informe, presentación, código)?

## 7. Reparto propuesto (pendiente de confirmar por Héctor)
- **Héctor:** modelos (tabulares con su Codex hoy; CNN y multimodal en Kabré), por continuidad con su experiencia.
- **Bryan:** video (guion y montaje junto a Carlos) y validaciones científicas (revisar que las conclusiones y las limitaciones del video sean correctas; cotejar una muestra de extracciones). Si queda tiempo, apoya a Carlos con la interfaz.
- **Carlos:** web (Atlas) y grabación de la demo.
Si Bryan deja de hacer el modelo de imágenes, su archivo `INSTRUCCIONES_CLAUDE_BRYAN.md` se reemplaza por uno de video y validación.
