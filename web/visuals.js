(() => {
  const root = document.getElementById('atlas-charts');
  if (!root) return;
  const fmt = value => Number(value || 0).toLocaleString('es-CR');
  const el = (tag, cls, value) => { const node = document.createElement(tag); if (cls) node.className = cls; if (value != null) node.textContent = String(value); return node; };
  const navigate = params => { const query = new URLSearchParams(params); location.href = `figuras.html?${query}`; };
  const card = title => { const node = el('article', 'chart-card'); node.append(el('h3', '', title)); return node; };
  const bars = (title, entries, param) => {
    const section = card(title); const max = Math.max(1, ...entries.map(item => item.count));
    const plot = el('div', `bar-plot${title.startsWith('Técnicas') || title.startsWith('Familias') ? ' technique-plot' : ''}`); plot.setAttribute('role', 'list');
    entries.forEach(item => {
      const button = el('button', 'bar-item'); button.type = 'button'; button.title = `${item.label}: ${fmt(item.count)}. Filtrar`;
      button.setAttribute('aria-label', `${item.label}: ${fmt(item.count)}. Abrir filtro`); button.setAttribute('role', 'listitem');
      const bar = el('span', 'chart-bar'); bar.style.height = `${Math.max(2, item.count / max * 100)}%`; bar.setAttribute('aria-hidden', 'true');
      button.append(bar, el('b', 'bar-count', fmt(item.count)), el('span', 'bar-label', item.label));
      button.addEventListener('click', () => navigate({ [param]: item.value })); plot.append(button);
    });
    section.append(plot); return section;
  };
  function donut(title, entries) {
    const section = card(title); const total = entries.reduce((sum, item) => sum + item.count, 0) || 1;
    let angle = 0; const stops = [];
    entries.forEach((item, index) => { const next = angle + item.count / total * 360; stops.push(`${['#167c72','#347fc4','#c56a16','#8354a4','#71818a'][index % 5]} ${angle}deg ${next}deg`); angle = next; });
    const wrap = el('div', 'donut-wrap'); const donutNode = el('div', 'donut-chart'); donutNode.style.background = `conic-gradient(${stops.join(',')})`; donutNode.setAttribute('role', 'img'); donutNode.setAttribute('aria-label', entries.map(item => `${item.label}: ${fmt(item.count)}`).join('; '));
    const hole = el('span', 'donut-hole', fmt(total)); donutNode.append(hole); wrap.append(donutNode);
    const legend = el('div', 'chart-legend'); entries.forEach((item, index) => { const button = el('button', 'legend-item'); button.type = 'button'; button.append(el('i', '', ''), el('span', '', `${item.label} · ${fmt(item.count)}`)); button.querySelector('i').style.backgroundColor = ['#167c72','#347fc4','#c56a16','#8354a4','#71818a'][index % 5]; button.addEventListener('click', () => navigate({ class: item.value })); legend.append(button); });
    wrap.append(legend); section.append(wrap); return section;
  }
  async function init() {
    try {
      const [response, summaryResponse] = await Promise.all([fetch('data/figuras.json'), fetch('data/figuras_summary.json')]);
      if (!response.ok || !summaryResponse.ok) throw new Error('JSON de figuras no disponible');
      const [figures, summary] = await Promise.all([response.json(), summaryResponse.json()]);
      const visible = figures.filter(row => row.accepted === true && row.destino_vision !== 'excluir');
      const destinations = ['simple','pareja','compuesta','superpuesto'].map(value => ({ label: value, value, count: visible.filter(row => row.destino_vision === value).length })).filter(row => row.count);
      const classLabels = { lipidico: 'Lipídico', polimerico: 'Polimérico', inorganico: 'Inorgánico', nanomaterial: 'Nanomaterial' };
      const classes = [...new Set(visible.map(row => row.clase_modelo).filter(Boolean))].sort().map(value => ({ label: classLabels[value] || value, value, count: visible.filter(row => row.clase_modelo === value).length }));
      const visibleCounts = summary.visible_figure_technique_counts || {};
      const topTechniques = summary.top_techniques || [];
      const techniques = topTechniques.map(value => ({ label: value, value, count: visibleCounts[value] || 0 }));
      techniques.push({ label: 'Otras técnicas', value: '__other__', count: summary.technique_other_visible_figures || 0 });
      techniques.push({ label: 'Sin técnica', value: '__missing__', count: summary.visible_figures_without_technique || 0 });
      const families = Object.entries(summary.technique_family_visible_counts || {}).map(([value, count]) => ({ label: value, value, count }));
      const panelBins = [
        { label: '1', min: 1, max: 1 }, { label: '2', min: 2, max: 2 }, { label: '3–4', min: 3, max: 4 },
        { label: '5–8', min: 5, max: 8 }, { label: '9+', min: 9, max: Infinity }
      ].map(bin => ({ ...bin, value: bin.label, count: visible.filter(row => { const n = Number(row.paneles || row.n || 0); return n >= bin.min && n <= bin.max; }).length }));
      const techniqueChart = bars('Técnicas · 10 principales y otras', techniques, 'technique');
      techniqueChart.append(el('p', 'chart-explainer', `Alcance inicial: ${fmt(visible.length)} figuras aceptadas y visibles; ${fmt(summary.visible_figures_without_technique)} sin técnica tras depurar marcadores. En las ${fmt(summary.figures_total)} figuras fuente, ${fmt(summary.figures_without_technique)} quedan sin técnica. Una figura puede contar en varias barras.`));
      const familyChart = bars('Familias de técnicas', families, 'family');
      familyChart.append(el('p', 'chart-explainer', 'Las familias agrupan las etiquetas normalizadas; una figura puede pertenecer a más de una familia.'));
      root.replaceChildren(bars('Destino visual', destinations, 'destination'), donut('Clase del portador', classes), techniqueChart, familyChart, bars('Paneles por figura', panelBins, 'panels'));
    } catch (error) { root.replaceChildren(el('p', 'load-error', `No se pudo cargar el resumen visual: ${error.message}`)); }
  }
  init();
})();
