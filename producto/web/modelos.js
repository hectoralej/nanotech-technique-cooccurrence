(() => {
  const number = value => Number(value).toLocaleString('es-CR', { maximumFractionDigits: 2 });
  const pct = value => `${(Number(value) * 100).toLocaleString('es-CR', { maximumFractionDigits: 2 })}%`;
  const interval = metric => {
    if (!metric || metric.valor == null) return 'No reportado';
    const value = number(metric.valor);
    const ci = metric.ic95;
    return ci?.length === 2 ? `${value} (IC 95 %: ${number(ci[0])}–${number(ci[1])})` : value;
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
  function unavailable(id, message) { document.getElementById(id).replaceChildren(create('p', message, 'no-data')); }
  async function load(path) {
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
    return response.json();
  }
  async function render() {
    try {
      const [tabular, image] = await Promise.all([
        load('../modelo_tabular/metricas_tabular.json'), load('../modelo/metricas.json')
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
    } catch (error) {
      ['size-results', 'class3-results', 'class4-results', 'image-model'].forEach(id => unavailable(id, `No se pudieron cargar las métricas. Comprueba que el servidor se inició desde producto/. (${error.message})`));
    }
  }
  render();
})();
