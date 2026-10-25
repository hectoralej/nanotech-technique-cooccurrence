(() => {
  const number = value => Number(value).toLocaleString('es-CR', { maximumFractionDigits: 2 });
  const pct = value => `${(Number(value) * 100).toLocaleString('es-CR', { maximumFractionDigits: 2 })}%`;
  const fixed = (value, digits = 2) => {
    const rounded = Number(Number(value).toFixed(digits));
    const formatted = Math.abs(rounded).toLocaleString('es-CR', { minimumFractionDigits: digits, maximumFractionDigits: digits });
    return rounded < 0 ? `−${formatted}` : formatted;
  };
  const signedDelta = value => `${Number(value) > 0 ? '+' : ''}${fixed(value, 3)}`;
  const deltaInterval = (value, ci) => `${signedDelta(value)} (IC 95 %: ${fixed(ci?.[0], 3)} a ${fixed(ci?.[1], 3)})`;
  const interval = metric => {
    if (!metric || metric.valor == null) return 'No reportado';
    const value = fixed(metric.valor);
    const ci = metric.ic95;
    return ci?.length === 2 ? `${value} (IC 95 %: ${fixed(ci[0])} a ${fixed(ci[1])})` : value;
  };
  const percentageInterval = metric => {
    if (!metric || metric.valor == null) return 'No reportado';
    const value = pct(metric.valor);
    const ci = metric.ic95;
    return ci?.length === 2 ? `${value} (IC 95 %: ${pct(ci[0])}–${pct(ci[1])})` : value;
  };
  const create = (tag, textValue, className) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (textValue != null) node.textContent = String(textValue);
    return node;
  };
  function table(rows, headers, baselineId, metricFormat) {
    const wrap = create('div', null, 'model-table-wrap');
    const tableNode = create('table', null, 'model-table');
    const head = create('thead'); const headRow = create('tr');
    headers.forEach(header => headRow.append(create('th', header)));
    head.append(headRow); tableNode.append(head);
    const body = create('tbody');
    rows.forEach(row => {
      const tr = create('tr', null, row.id === baselineId ? 'baseline-row' : '');
      metricFormat(row).forEach(value => tr.append(create('td', value)));
      body.append(tr);
    });
    tableNode.append(body); wrap.append(tableNode); return wrap;
  }
  function metricTable(rows, headers) {
    const wrap = create('div', null, 'model-table-wrap'); const node = create('table', null, 'model-table');
    const head = create('thead'); const tr = create('tr'); headers.forEach(label => tr.append(create('th', label))); head.append(tr); node.append(head);
    const body = create('tbody'); rows.forEach(row => { const line = create('tr', null, row.baseline ? 'baseline-row' : ''); row.values.forEach(value => line.append(create('td', value))); body.append(line); });
    node.append(body); wrap.append(node); return wrap;
  }
  function unavailable(id, message) { document.getElementById(id).replaceChildren(create('p', message, 'no-data')); }
  async function load(path) {
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
    return response.json();
  }
  async function loadText(path) {
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
    return response.text();
  }
  function sourceLink(path, label) {
    const link = create('a', label);
    link.href = path;
    link.setAttribute('download', '');
    return link;
  }
  function renderFinalModel(card, baselineSource) {
    const reference = card.desempeno_de_referencia_validacion_cruzada;
    const baselineMatch = baselineSource.match(/Línea base[^\n]*exactitud\s+(\d+(?:\.\d+)?)/i);
    if (!baselineMatch) throw new Error('No se pudo leer la línea base de ANALISIS_04_RECORTES.md.');
    const cards = create('div', null, 'model-metrics');
    [
      ['Exactitud de referencia', reference.exactitud],
      ['F1 macro de referencia', reference.f1_macro],
      ['Exactitud de la clase mayoritaria', Number(baselineMatch[1])]
    ].forEach(([label, value]) => {
      const item = create('div', null, 'model-metric');
      item.append(create('span', label), create('strong', fixed(value, 3)));
      cards.append(item);
    });
    const limits = create('ul');
    card.limitaciones.forEach(text => limits.append(create('li', text)));
    const source = create('p', null, 'data-source');
    source.append('Fuentes: ', sourceLink('data/modelo_card_final.json', 'modelo_card.json'), ' · ', sourceLink('data/metricas_06_nffa.json', 'metricas_06.json (brazo A)'), ' · ', sourceLink('data/analisis_04_recortes.md', 'ANALISIS_04_RECORTES.md (línea base)'));
    document.getElementById('final-model-results').replaceChildren(
      create('p', `${card.nombre} · ${card.version}`, 'model-summary'),
      create('p', card.modelo),
      create('p', `Entrenamiento: ${card.entrenamiento.datos}. ${card.entrenamiento.epocas} épocas. ${card.entrenamiento.sin_NFFA}.`),
      create('p', `Referencia de validación cruzada: ${reference.validacion}, ${number(reference.articulos)} artículos.`, 'model-summary'),
      cards,
      create('p', 'El modelo final se entrenó con todos los recortes disponibles. No tiene un conjunto de prueba reservado y no se puede evaluar de nuevo sobre esos mismos datos: las cifras mostradas son la estimación de referencia por validación cruzada.', 'data-note'),
      limits, source
    );
  }
  function renderNffa(data) {
    const designs = { A: 'LVD → nuestros recortes (línea base)', B: 'LVD → NFFA → nuestros recortes', C: 'Como B, con etiquetas NFFA mezcladas' };
    const rows = data.tabla.map(arm => ({ baseline: arm.brazo === 'A', values: [
      `${arm.brazo} · ${designs[arm.brazo]}`,
      `${fixed(arm.acc_media, 3)} ± ${fixed(arm.acc_sd, 3)}`,
      `${fixed(arm.f1_media, 3)} ± ${fixed(arm.f1_sd, 3)}`,
      fixed(arm.f1_ensamble, 3)
    ] }));
    const differences = Object.entries(data.diferencias).map(([comparison, value]) => ({ values: [
      comparison.replaceAll(' - ', ' − '), signedDelta(value.f1), `${fixed(value.IC95.f1[0], 3)} a ${fixed(value.IC95.f1[1], 3)}`
    ] }));
    const details = create('details');
    details.append(create('summary', 'Ver tablas A/B/C y diferencias con IC 95 %'),
      metricTable(rows, ['Brazo', 'Exactitud (media ± sd)', 'F1 macro (media ± sd)', 'F1 macro (ensamble de 3 semillas)']),
      metricTable(differences, ['Diferencia del ensamble', 'ΔF1 macro', 'IC 95 %'])
    );
    const source = create('p', null, 'data-source');
    source.append('Fuentes: ', sourceLink('data/analisis_06_nffa.md', 'ANALISIS_06_NFFA.md'), ' · ', sourceLink('data/metricas_06_nffa.json', 'entrada_kabre/06_nffa/metricas_06.json'), '.');
    document.getElementById('nffa-results').replaceChildren(
      create('p', `Diseño: DINOv2 ViT-S/14 (LVD-142M), receta del cuaderno 04, cinco particiones por artículo, tres semillas por brazo y ${number(data.articulos_comunes)} artículos comunes. La métrica predefinida fue el F1 macro por artículo, con probabilidades promediadas entre semillas e IC 95 % por bootstrap de artículos (2.000 remuestreos).`),
      create('p', 'NFFA-EUROPE Majority SEM (B2SHARE 1nysp-05236, CC BY 4.0): siete morfologías, 8.204 teselas de entrenamiento y 912 de validación durante ocho épocas. Se recortó la banda blanca de metadatos del instrumento y se verificaron los MD5 de las siete carpetas utilizadas.'),
      details,
      create('h3', 'Lectura', 'model-subheading'),
      create('p', 'El preentrenamiento con NFFA no mejoró de forma detectable: el IC de B − A incluye cero y su centro es negativo. El control con etiquetas mezcladas empeoró con claridad frente a la línea base (C − A). Las etiquetas reales parecen evitar ese daño, pero no superan la línea base; B − C apenas excluye cero.'),
      create('p', 'La exactitud interna en NFFA llegó a 0,968: fue una tarea fácil, con poco que aprender. En el brazo A, promediar las tres semillas aportó aproximadamente +0,013 de exactitud y +0,016 de F1 macro frente a una semilla; por eso la demo usa el ensamble.'),
      create('h3', 'Límites del experimento', 'model-subheading'),
      create('p', 'La etapa de NFFA corrió una vez (semilla 0) y con una sola configuración: ocho épocas, tasa de aprendizaje 3 × 10⁻⁵, ajuste completo y 224 px. La etiqueta «Particles» es ruidosa. No se probaron 384 px ni MicroNet con ResNet50. Este resultado nulo se limita a esa receta y a esta muestra.'),
      source
    );
  }
  function setupFigureViewer() {
    document.querySelectorAll('[data-model-figure]').forEach(link => {
      link.addEventListener('click', event => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        const dialog = create('dialog', null, 'image-lightbox');
        dialog.setAttribute('aria-label', 'Figura de resultados ampliada');
        const form = create('form'); form.method = 'dialog';
        const close = create('button', '×', 'lightbox-close'); close.setAttribute('aria-label', 'Cerrar figura ampliada'); form.append(close);
        const figure = create('figure'); const img = create('img');
        img.src = link.href; img.alt = link.querySelector('img').alt;
        figure.append(img, create('figcaption', img.alt));
        dialog.append(form, figure); document.body.append(dialog);
        dialog.addEventListener('close', () => { dialog.remove(); link.focus(); }, { once: true });
        dialog.showModal();
      });
    });
  }
  async function render() {
    try {
      const [tabular, image, recrops, fusion, nffaData, finalCard, baselineSource] = await Promise.all([
        load('../modelo_tabular/metricas_tabular.json'), load('../modelo/metricas.json'),
        load('data/analisis_recortes.json'), load('data/analisis_fusion_04.json'),
        load('data/metricas_06_nffa.json'), load('data/modelo_card_final.json'), loadText('data/analisis_04_recortes.md')
      ]);
      const models = tabular.modelos || [];
      const size = models.filter(model => model.tarea === 'tamano_log10');
      const sizeBase = size.find(model => model.id === 'tamano_media_clase')?.id;
      document.getElementById('size-results').replaceChildren(table(
        size,
        ['Modelo', 'Variante', 'Artículos', 'R² (IC 95 %)'],
        sizeBase,
        model => [model.nombre, model.variante, number(model.n_articulos), interval(model.metricas?.r2)]
      ));
      for (const [task, id] of [['clase_3', 'class3-results'], ['clase_4', 'class4-results']]) {
        const rows = models.filter(model => model.tarea === task);
        const baselineTask = task.replace('_', '');
        const baselineId = rows.find(model => model.id === `${baselineTask}_mayoritaria`)?.id;
        document.getElementById(id).replaceChildren(table(
          rows,
          ['Modelo', 'Artículos', 'Exactitud (IC 95 %)', 'F1 macro (IC 95 %)'],
          baselineId,
          model => [model.nombre, number(model.n_articulos), percentageInterval(model.metricas?.exactitud), percentageInterval(model.metricas?.f1_macro)]
        ));
      }
      const imageRoot = document.getElementById('image-model');
      const metrics = image;
      const summary = create('p', `${metrics.backbone || 'Modelo de imagen'} · ${metrics.evaluacion || 'evaluación por artículo'} · ${number(metrics.n_articulos)} artículos · ${number(metrics.n_imagenes)} imágenes`, 'model-summary');
      const cards = create('div', null, 'model-metrics');
      [
        ['Exactitud', pct(metrics.accuracy)],
        ['Exactitud balanceada', pct(metrics.accuracy_balanceada)],
        ['F1 macro', pct(metrics.f1_macro)],
        ['Línea base de exactitud', pct(metrics.linea_base)]
      ].forEach(([label, value]) => {
        const card = create('div', null, 'model-metric');
        card.append(create('span', label), create('strong', value)); cards.append(card);
      });
      imageRoot.replaceChildren(summary, cards, create('p', metrics.nota || 'No se incluyó una nota de limitaciones.', 'model-note'));
      const recropRows = [];
      for (const [key, label] of [['resnet50','ResNet50'],['dinov2_vits14','DINOv2 ViT-S/14']]) {
        const model = recrops[key]; if (!model) continue;
        const base = model.figura_completa_03 || {}; const crop = model.recortes || {}; const diff = model.diferencia_IC95 || {};
        recropRows.push({ values: [`${label} · figura completa 03 (referencia)`, number(model.n_articulos), pct(base.acc), pct(base.acc_bal), pct(base.f1), '—', '—'], baseline: true });
        recropRows.push({ values: [`${label} · recortes 04`, number(model.n_articulos), pct(crop.acc), pct(crop.acc_bal), pct(crop.f1), '—', '—'] });
        recropRows.push({ values: [`Δ recortes 04 − figura 03`, number(model.n_articulos), deltaInterval(model.dif_acc, diff.acc), 'No reportado en el JSON', deltaInterval(model.dif_f1, diff.f1), 'n/a', 'n/a'] });
        const control = model.control_mismas_vistas;
        if (control) recropRows.push({ values: [`${label} · control con igual número medio de vistas`, number(model.n_articulos), pct(control.acc), 'No reportado', pct(control.f1), `${number(control.vistas_medias_03)} vistas (03)`, `${number(control.vistas_medias_04)} vistas (04)`] });
      }
      document.getElementById('recrop-results').replaceChildren(metricTable(recropRows, ['Experimento', 'Artículos', 'Exactitud', 'Exactitud balanceada', 'F1 macro', 'Vistas 03', 'Vistas 04']));
      const fusionRows = [];
      if (fusion.modelos) {
        const labels = { medidas: 'Medidas', imagen_03: 'Imagen 03 (figura completa)', imagen_04: 'Imagen 04 (recortes)', fusion_03: 'Fusión 03', fusion_04: 'Fusión 04' };
        fusionRows.push({ values: ['Línea base mayoritaria', number(fusion.n_articulos), pct(fusion.linea_base_mayoritaria_acc), 'No reportado', 'No reportado'], baseline: true });
        Object.entries(fusion.modelos).forEach(([key, value]) => fusionRows.push({ values: [labels[key] || key, number(fusion.n_articulos), pct(value.acc), pct(value.acc_bal), pct(value.f1)] }));
        const delta = fusion.diferencias?.['fusion_04 - fusion_03']; const ci = delta?.IC95 || {};
        if (delta) fusionRows.push({ values: ['Diferencia Fusión 04 − Fusión 03', number(fusion.n_articulos), deltaInterval(delta.acc, ci.acc), 'No reportado', deltaInterval(delta.f1, ci.f1)] });
      }
      document.getElementById('fusion-results').replaceChildren(create('h3','Comparación de fusión, evaluada por artículo','model-subheading'), metricTable(fusionRows, ['Modelo', 'Artículos', 'Exactitud', 'Exactitud balanceada', 'F1 macro']));
      renderNffa(nffaData);
      renderFinalModel(finalCard, baselineSource);
    } catch (error) {
      ['size-results', 'class3-results', 'class4-results', 'image-model', 'recrop-results', 'fusion-results', 'nffa-results', 'final-model-results'].forEach(id => unavailable(id, `No se pudieron cargar las métricas. Comprueba que el servidor se inició desde producto/. (${error.message})`));
    }
  }
  setupFigureViewer();
  render();
})();
