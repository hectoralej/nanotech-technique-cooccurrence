(() => {
  const $ = id => document.getElementById(id);
  const state = { rows: [], articles: new Map(), page: 0, size: 24 };
  const clean = value => String(value ?? '').trim();
  const make = (tag, cls, value) => { const node = document.createElement(tag); if (cls) node.className = cls; if (value != null) node.textContent = String(value); return node; };
  const safeUrl = value => /^https:\/\/doi\.org\//i.test(clean(value)) ? clean(value) : '';
  function filtered() { const cls = $('gallery-class').value; return state.rows.filter(row => !cls || row.clase === cls); }
  function render() {
    const rows = filtered(); const pages = Math.max(1, Math.ceil(rows.length / state.size)); state.page = Math.min(state.page, pages - 1);
    const slice = rows.slice(state.page * state.size, (state.page + 1) * state.size); const root = $('gallery-results'); root.replaceChildren();
    $('gallery-count').textContent = `${rows.length.toLocaleString('es-CR')} recortes · ${slice.length ? (state.page * state.size + 1).toLocaleString('es-CR') : 0}–${(state.page * state.size + slice.length).toLocaleString('es-CR')}`;
    $('gallery-page').textContent = rows.length ? `${state.page + 1} / ${pages}` : '';
    $('gallery-prev').disabled = state.page === 0; $('gallery-next').disabled = state.page >= pages - 1;
    if (!slice.length) root.append(make('p', 'no-data', 'No hay recortes para esta clase.'));
    slice.forEach(row => {
      const article = state.articles.get(row.pmcid) || {}; const card = make('article', 'gallery-card');
      const head = make('div', 'gallery-card-head'); head.append(make('strong', '', `${row.pmcid || 'PMCID no reportado'} · ${row.fig_id || 'Figura no reportada'} · panel ${row.panel || '?'}`)); head.append(make('span', 'tag', row.clase || 'Clase no reportada')); card.append(head);
      if (row.crop_available === true && row.crop_web) { const img = make('img', 'gallery-crop'); img.src = row.crop_web; img.alt = `Recorte ${row.panel || ''} de ${row.fig_id || ''}`; img.loading = 'lazy'; img.decoding = 'async'; card.append(img); }
      else card.append(make('div', 'gallery-missing', 'Miniatura no disponible en esta copia.'));
      card.append(make('p', '', `${row.tipo || 'Tipo no reportado'} · ${row.contenido || 'Contenido no reportado'} · técnica: ${row.tecnica || 'no asignada'}`));
      if (article.title) card.append(make('p', 'gallery-title', article.title));
      const credit = make('div', 'gallery-credit'); credit.append(make('span', '', `Licencia: ${article.license || article.license_epmc || 'no confirmada'}`));
      const doi = safeUrl(article.doi_link); if (doi) { const link = make('a', '', 'Abrir artículo / DOI ↗'); link.href = doi; link.target = '_blank'; link.rel = 'noopener noreferrer'; credit.append(link); }
      card.append(credit); root.append(card);
    });
  }
  async function init() {
    try {
      const [panelResponse, figureResponse, articleResponse] = await Promise.all([fetch('data/paneles_recortados.json'), fetch('data/figuras.json'), fetch('data/articulos.json')]);
      if (![panelResponse, figureResponse, articleResponse].every(response => response.ok)) throw new Error('No se pudieron leer los JSON del Atlas.');
      const [panels, figures, articles] = await Promise.all([panelResponse.json(), figureResponse.json(), articleResponse.json()]);
      state.rows = panels; figures.forEach(row => { if (!state.articles.has(row.pmcid)) state.articles.set(row.pmcid, row); }); articles.forEach(row => state.articles.set(row.pmcid, { ...state.articles.get(row.pmcid), ...row }));
      [...new Set(panels.map(row => clean(row.clase)).filter(Boolean))].sort().forEach(value => { const option = document.createElement('option'); option.value = value; option.textContent = value; $('gallery-class').append(option); });
      const params = new URLSearchParams(location.search); if (params.has('class')) $('gallery-class').value = params.get('class');
      $('gallery-class').addEventListener('change', () => { state.page = 0; render(); }); $('gallery-prev').addEventListener('click', () => { state.page--; render(); }); $('gallery-next').addEventListener('click', () => { state.page++; render(); }); render();
    } catch (error) { $('gallery-results').replaceChildren(make('p', 'load-error', error.message)); $('gallery-count').textContent = 'Error de carga'; }
  }
  init();
})();
