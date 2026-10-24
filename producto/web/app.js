(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const byId = id => document.getElementById(id);
  const state = { articles: [], panels: [], descriptors: [], spectra: [], page: 0, selected: null, pageSize: 24, qc: null, model: null, showAllPanels: false };
  const filters = { search: byId('search'), family: byId('family'), usage: byId('usage'), tier: byId('tier'), variant: byId('variant'), technique: byId('technique') };
  const carrierTypes = [
    ['liposome', 'Liposoma'], ['LNP', 'LNP (nanopartícula lipídica)'], ['SLN', 'SLN'], ['NLC', 'NLC'],
    ['PLN', 'PLN'], ['micelle', 'Micela'], ['nanogel', 'Nanogel'], ['nanoemulsion', 'Nanoemulsión'],
    ['cubosome', 'Cubosoma'], ['polymeric_NP', 'Polimérica'], ['inorganic_NP', 'Inorgánica'],
    ['nanomaterial', 'Nanomaterial'], ['other', 'Otro']
  ];
  const carrierLabels = new Map(carrierTypes);
  const usageLabels = new Map([['nanoportador', 'Nanoportador'], ['nanomaterial', 'Nanomaterial']]);

  const escText = value => value == null || value === '' ? 'No reportado' : String(value);
  const number = value => value == null || value === '' ? 'No reportado' : String(value);
  const text = (tag, value, className) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    node.textContent = value == null ? '' : String(value);
    return node;
  };
  const clean = value => (value || '').toString().trim();
  const articleKey = row => row.pmcid || row.doi || '';
  const carrierLabel = article => carrierLabels.get(clean(article.carrier_type)) || 'Otro';
  const usageLabel = value => usageLabels.get(clean(value).toLowerCase()) || clean(value);
  const panelKey = row => `${row.pmcid || ''}/${row.image_file || ''}`;
  const sourceLink = row => {
    const url = clean(row.doi_link);
    return /^https:\/\/doi\.org\//i.test(url) ? url : '';
  };
  const safeImageLicense = article => {
    const license = (article.license_epmc || '').toLowerCase().replaceAll('_', ' ');
    return /\bcc\s*by\b|\bcc0\b/.test(license) && !/\bnc\b|\bnd\b/.test(license);
  };
  const options = (select, values, labelFor = value => value) => {
    [...new Set(values.map(clean).filter(Boolean))].sort((a,b) => a.localeCompare(b,'es',{sensitivity:'base'})).forEach(value => {
      const option = document.createElement('option'); option.value = value; option.textContent = labelFor(value); select.append(option);
    });
  };
  const setCount = (id, value) => { byId(id).textContent = Number(value || 0).toLocaleString('es-CR'); };

  async function loadJson(path, optional = false) {
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) {
      if (optional) return null;
      throw new Error(`No se pudo leer ${path} (${response.status})`);
    }
    return response.json();
  }

  function initFilters() {
    const carrierCounts = new Map(carrierTypes.map(([value]) => [value, 0]));
    state.articles.forEach(article => {
      const value = clean(article.carrier_type);
      if (carrierCounts.has(value)) carrierCounts.set(value, carrierCounts.get(value) + 1);
    });
    filters.family.options[0].textContent = `Todos los portadores (${state.articles.length.toLocaleString('es-CR')})`;
    carrierTypes.forEach(([value, label]) => {
      const count = carrierCounts.get(value) || 0;
      if (!count) return;
      const option = document.createElement('option'); option.value = value;
      option.textContent = `${label} (${count.toLocaleString('es-CR')})`; filters.family.append(option);
    });
    options(filters.usage, state.articles.map(a => a.categoria_uso), usageLabel);
    options(filters.variant, state.panels.map(p => p.variant));
    options(filters.technique, state.spectra.map(s => s.technique));
    Object.values(filters).forEach(control => control.addEventListener(control === filters.search ? 'input' : 'change', () => { state.page = 0; renderResults(); }));
  }

  function passes(article) {
    const q = clean(filters.search.value).toLowerCase();
    const pmc = articleKey(article);
    const linkedPanels = state.panels.filter(p => p.pmcid === pmc);
    const linkedSpectra = state.spectra.filter(s => s.pmcid === pmc);
    const searchText = [article.title, article.doi, article.doi_link, article.pmcid, article.family, article.carrier_type].join(' ').toLowerCase();
    if (q && !searchText.includes(q)) return false;
    const family = filters.family.value;
    if (family && article.carrier_type !== family) return false;
    if (filters.usage.value && article.categoria_uso !== filters.usage.value) return false;
    if (filters.tier.value && article.tier !== filters.tier.value) return false;
    if (filters.variant.value && !linkedPanels.some(p => p.variant === filters.variant.value)) return false;
    if (filters.technique.value && !linkedSpectra.some(s => s.technique === filters.technique.value)) return false;
    return true;
  }

  function renderResults() {
    const found = state.articles.filter(passes);
    const pages = Math.max(1, Math.ceil(found.length / state.pageSize));
    state.page = Math.min(state.page, pages - 1);
    const slice = found.slice(state.page * state.pageSize, (state.page + 1) * state.pageSize);
    const list = byId('results'); list.replaceChildren();
    byId('result-count').textContent = `${found.length.toLocaleString('es-CR')} artículos`;
    byId('page-label').textContent = found.length ? `${state.page + 1} / ${pages}` : '';
    byId('previous').disabled = state.page === 0;
    byId('next').disabled = state.page >= pages - 1;
    if (!slice.length) list.append(text('p', 'No hay artículos que coincidan con estos filtros.', 'no-data'));
    slice.forEach(article => {
      const card = document.createElement('button'); card.type = 'button';
      card.className = `result-card${articleKey(article) === state.selected ? ' active' : ''}`;
      card.dataset.key = articleKey(article);
      card.append(text('span', escText(article.title), 'result-title'));
      const meta = text('span', `${article.year || 'Año no reportado'} · ${article.pmcid || 'PMCID no reportado'}`, 'result-meta'); card.append(meta);
      const tags = text('span', '', 'result-tags');
      if (article.carrier_type) tags.append(text('span', carrierLabel(article), 'tag family'));
      if (article.tier) tags.append(text('span', article.tier, 'tag'));
      if (article.categoria_uso) tags.append(text('span', usageLabel(article.categoria_uso), 'tag'));
      card.append(tags); list.append(card);
    });
  }

  function block(title) {
    const section = text('section', '', 'detail-block'); section.append(text('h3', title)); return section;
  }

  function modelConfidence(value) {
    const confidence = Number(value);
    if (!Number.isFinite(confidence)) return 'confianza no reportada';
    return `${(confidence <= 1 ? confidence * 100 : confidence).toLocaleString('es-CR', { maximumFractionDigits: 1 })}%`;
  }

  function makeSimilarCard(neighbor) {
    const card = text('div', '', 'similar-card');
    const sourceArticle = state.articles.find(item => item.pmcid === neighbor.pmcid);
    const sourcePanel = state.panels.find(item => panelKey(item) === panelKey(neighbor));
    if (sourceArticle && sourcePanel?.imagen_local === true && safeImageLicense(sourceArticle)) {
      const image = document.createElement('img'); image.loading = 'lazy';
      image.src = `../imagenes/${encodeURIComponent(neighbor.pmcid)}/${encodeURIComponent(neighbor.image_file)}`;
      image.alt = `Micrografía similar de ${neighbor.pmcid}`;
      card.append(image);
    } else {
      card.append(text('div', 'Vista previa no disponible', 'similar-placeholder'));
    }
    card.append(text('strong', neighbor.pmcid || 'PMCID no reportado'));
    card.append(text('span', neighbor.image_file || 'Archivo no reportado'));
    card.append(text('small', `Similitud: ${modelConfidence(neighbor.similitud)}`));
    return card;
  }

  function appendModelEvidence(container, panel) {
    if (!state.model) return;
    const key = panelKey(panel);
    const prediction = state.model.predictions.get(key);
    const neighbors = (state.model.similars[key] || []).filter((neighbor, index, list) =>
      list.findIndex(candidate => panelKey(candidate) === panelKey(neighbor)) === index
    ).slice(0, 5);
    if (!prediction && !neighbors.length) return;
    const section = text('div', '', 'panel-model-evidence');
    if (prediction) {
      section.append(text('strong', `Predicción del modelo: ${prediction.prediccion || 'no reportada'} (${modelConfidence(prediction.confianza)})`, 'model-prediction'));
    }
    if (neighbors.length) {
      section.append(text('span', 'Micrografías parecidas', 'similar-heading'));
      const list = text('div', '', 'similar-grid');
      neighbors.forEach(neighbor => list.append(makeSimilarCard(neighbor)));
      section.append(list);
    }
    container.append(section);
  }

  function makeMicrograph(panel, article) {
    const card = text('div', '', 'micro-card');
    const imageBox = text('div', '', 'micro-image');
    const file = clean(panel.image_file);
    const local = `../imagenes/${encodeURIComponent(article.pmcid || '')}/${encodeURIComponent(file)}`;
    if (file && panel.imagen_local === true && safeImageLicense(article)) {
      const img = document.createElement('img'); img.loading = 'lazy'; img.alt = `${panel.variant || 'Micrografía'} · ${panel.sample || 'muestra no reportada'}`;
      img.src = local;
      img.onerror = () => {
        img.remove(); const fallback = text('div', '', 'image-placeholder');
        fallback.append(text('span', file || 'Archivo de imagen no reportado'));
        fallback.append(text('small', 'Imagen no disponible en esta copia'));
        imageBox.append(fallback);
      };
      imageBox.append(img);
    } else {
      const fallback = text('div', '', 'image-placeholder');
      fallback.append(text('span', file || 'Archivo de imagen no reportado'));
      const detail = !file ? 'La base no incluye nombre de archivo'
        : panel.imagen_local === false ? 'No está en la copia local; consulta el DOI'
          : 'Vista no cargada o licencia no confirmada';
      fallback.append(text('small', detail));
      imageBox.append(fallback);
    }
    card.append(imageBox);
    const cap = text('div', '', 'micro-caption');
    cap.append(text('strong', `${panel.fig || 'Figura no reportada'} · ${panel.variant || 'Técnica no reportada'}`));
    cap.append(text('div', panel.sample || 'Muestra no reportada'));
    if (panel.clase_modelo || panel.microscopia || panel.fold !== undefined && panel.fold !== '') {
      cap.append(text('div', `Clase del artículo (base de datos): ${panel.clase_modelo || 'no reportada'}`));
      cap.append(text('div', `Microscopía: ${panel.microscopia || 'no reportada'} · Fold: ${panel.fold || 'no reportado'}`));
    }
    if (panel.scale_bar_in_caption) cap.append(text('div', `Barra: ${panel.scale_bar_in_caption}`));
    if (sourceLink(article)) { const a = text('a', 'Imagen de un artículo de acceso abierto; ver licencia en el enlace · DOI ↗'); a.href = sourceLink(article); a.target = '_blank'; a.rel = 'noopener noreferrer'; cap.append(a); }
    appendModelEvidence(cap, panel);
    card.append(cap); return card;
  }

  function renderDetail(key) {
    const article = state.articles.find(item => articleKey(item) === key);
    if (!article) return;
    if (state.selected !== key) state.showAllPanels = false;
    state.selected = key;
    renderResults();
    const detail = byId('detail'); detail.replaceChildren();
    const kicker = text('div', '', 'detail-kicker');
    kicker.append(text('span', article.carrier_type ? carrierLabel(article) : 'Portador no reportado', 'tag family'));
    if (article.tier) kicker.append(text('span', article.tier, 'tag'));
    if (article.license_epmc) kicker.append(text('span', article.license_epmc, 'tag'));
    detail.append(kicker);
    detail.append(text('h2', escText(article.title), 'detail-title'));
    const meta = text('div', '', 'article-meta');
    meta.append(text('span', article.year || 'Año no reportado'));
    meta.append(text('span', article.pmcid || 'PMCID no reportado'));
    if (sourceLink(article)) { const link = text('a', article.doi || 'Abrir DOI ↗'); link.href = sourceLink(article); link.target = '_blank'; link.rel = 'noopener noreferrer'; meta.append(link); }
    const copy = text('button', 'Copiar cita/DOI', 'copy-citation'); copy.type = 'button';
    copy.addEventListener('click', async () => {
      const citation = `${article.title || 'Artículo'}${sourceLink(article) ? `. DOI: ${sourceLink(article)}` : ''}${article.pmcid ? ` · ${article.pmcid}` : ''}`;
      try {
        if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(citation);
        else {
          const field = document.createElement('textarea'); field.value = citation; field.setAttribute('readonly', '');
          field.style.position = 'fixed'; field.style.opacity = '0'; document.body.append(field); field.select();
          const copied = document.execCommand('copy'); field.remove(); if (!copied) throw new Error('clipboard unavailable');
        }
        copy.textContent = 'Cita/DOI copiados';
      } catch { copy.textContent = 'No se pudo copiar'; }
    });
    meta.append(copy);
    if (article.license_epmc || article.license_color) meta.append(text('span', `Licencia: ${article.license_epmc || article.license_color}`));
    detail.append(meta);
    const panels = state.panels.filter(p => p.pmcid === article.pmcid);
    const descriptors = state.descriptors.filter(d => d.pmcid === article.pmcid);
    const spectra = state.spectra.filter(s => s.pmcid === article.pmcid);
    const counts = text('div', '', 'detail-counts');
    [['Micrografías', panels.length], ['Descriptores', descriptors.length], ['Espectros', spectra.length]].forEach(([label, value]) => {
      const item = text('span', ''); item.append(text('b', value), document.createTextNode(` ${label}`)); counts.append(item);
    }); detail.append(counts);

    const micro = block('Micrografías');
    if (!panels.length) micro.append(text('p', 'No se reportaron micrografías.', 'no-data'));
    else {
      const visiblePanels = state.showAllPanels ? panels : panels.slice(0, 5);
      const grid = text('div', '', 'micro-grid'); visiblePanels.forEach(item => grid.append(makeMicrograph(item, article))); micro.append(grid);
      if (panels.length > 5) {
        const toggle = text('button', state.showAllPanels ? 'Mostrar menos' : `Ver todas (${panels.length})`, 'show-all-panels'); toggle.type = 'button';
        toggle.addEventListener('click', () => { state.showAllPanels = !state.showAllPanels; renderDetail(key); }); micro.append(toggle);
      }
    }
    detail.append(micro);

    const descriptorBlock = block('Descriptores');
    if (!descriptors.length) descriptorBlock.append(text('p', 'No se reportaron descriptores.', 'no-data'));
    else {
      const wrap = text('div', '', 'table-wrap'); const table = document.createElement('table');
      const head = document.createElement('thead'), hrow = document.createElement('tr');
      ['Muestra','Tamaño nm','PDI','Zeta mV','Medio','Fuente / cita'].forEach(label => hrow.append(text('th', label)));
      head.append(hrow); table.append(head); const body = document.createElement('tbody');
      descriptors.forEach(row => {
        const tr = document.createElement('tr');
        tr.append(text('td', number(row.sample), 'sample'));
        tr.append(text('td', number(row.size_nm), 'number'));
        tr.append(text('td', number(row.pdi), 'number'));
        tr.append(text('td', number(row.zeta_mV), 'number'));
        tr.append(text('td', number(row.medium)));
        const td = text('td', '', 'quote'); const details = document.createElement('details');
        details.append(text('summary', row.source ? `Ver cita · ${row.source}` : 'Ver cita textual'));
        details.append(text('blockquote', row.quote || 'Cita no reportada.'));
        td.append(details); tr.append(td); body.append(tr);
      });
      table.append(body); wrap.append(table); descriptorBlock.append(wrap);
    }
    detail.append(descriptorBlock);

    const spectrumBlock = block('Espectros');
    if (!spectra.length) spectrumBlock.append(text('p', 'No se reportaron espectros.', 'no-data'));
    else {
      const list = text('div', '', 'spectra-list');
      spectra.forEach(row => { const item = text('div', '', 'spectrum'); item.append(text('b', row.technique || 'Técnica no reportada')); item.append(text('small', `${row.fig || 'Figura no reportada'} · ${row.sample || row.applies_to || 'Muestra no reportada'}`)); list.append(item); });
      spectrumBlock.append(list);
    }
    detail.append(spectrumBlock);
  }

  function renderQc() {
    if (!state.qc) { byId('qc-note').textContent = 'La tabla de control de calidad no está disponible.'; return; }
    byId('qc-note').textContent = state.qc.note;
    const table = document.createElement('table');
    const thead = document.createElement('thead'), head = document.createElement('tr');
    ['Campo','Sí','No','No comprobable'].forEach(value => head.append(text('th', value)));
    thead.append(head); table.append(thead);
    const body = document.createElement('tbody');
    state.qc.rows.forEach(row => {
      const tr = document.createElement('tr');
      [row.field, row.si, row.no, row.no_comprobable].forEach((value, index) => tr.append(text('td', value, index ? 'number' : '')));
      body.append(tr);
    });
    table.append(body); byId('qc-table').replaceChildren(table);
  }

  function metricPercent(value) {
    const metric = Number(value);
    if (value == null || value === '' || !Number.isFinite(metric)) return 'No reportado';
    return `${(metric <= 1 ? metric * 100 : metric).toLocaleString('es-CR', { maximumFractionDigits: 2 })}%`;
  }

  function renderModelOverview() {
    const section = byId('modelo');
    if (!state.model) { section.hidden = true; return; }
    section.hidden = false; section.replaceChildren();
    const heading = text('div', '', 'section-heading');
    const title = text('div', '', ''); title.append(text('p', 'PREDICCIÓN Y EVALUACIÓN', 'eyebrow'), text('h2', 'Modelo de clasificación'));
    heading.append(title); section.append(heading);
    if (state.model.isTest) section.append(text('p', 'Datos de prueba locales: no representan resultados del modelo ni deben compartirse como métricas finales.', 'model-test-warning'));
    const metrics = state.model.metrics;
    if (metrics.tarea || metrics.backbone) section.append(text('p', [metrics.tarea, metrics.backbone].filter(Boolean).join(' · '), 'model-summary'));
    section.append(text('p', 'Evaluado por artículo, sin mezclar figuras de un mismo artículo entre entrenamiento y prueba.', 'model-evaluation'));
    const cards = text('div', '', 'model-metrics');
    [['Exactitud', metricPercent(metrics.accuracy)], ['Exactitud balanceada', metricPercent(metrics.accuracy_balanceada)], ['F1 macro', metricPercent(metrics.f1_macro)], ['Línea base (exactitud)', metricPercent(metrics.linea_base)]]
      .forEach(([label, value]) => { const card = text('div', '', 'model-metric'); card.append(text('span', label), text('strong', value)); cards.append(card); });
    section.append(cards);
    if (metrics.nota) section.append(text('p', metrics.nota, 'model-note'));
    if (metrics.evaluacion || metrics.n_imagenes != null || metrics.n_articulos != null) {
      const details = [metrics.evaluacion, metrics.n_imagenes != null ? `${metrics.n_imagenes} imágenes` : '', metrics.n_articulos != null ? `${metrics.n_articulos} artículos` : ''].filter(Boolean).join(' · ');
      section.append(text('p', details, 'model-summary'));
    }
    const matrix = metrics.matriz_confusion || metrics.confusion_matrix || metrics.confusionMatrix;
    const matrixBlock = block('Matriz de confusión');
    if (matrix == null) matrixBlock.append(text('p', 'No reportada en el archivo de métricas.', 'no-data'));
    else {
      const code = text('pre', '', 'confusion-matrix'); code.textContent = JSON.stringify(matrix, null, 2); matrixBlock.append(code);
    }
    section.append(matrixBlock);
    const more = text('a', 'Ver escalera de modelos y limitaciones →', 'text-link');
    more.href = 'modelos.html'; section.append(more);
  }

  async function loadOptionalJson(path) {
    try { return await loadJson(path, true); } catch { return null; }
  }

  async function loadModelData() {
    const availability = await loadOptionalJson('data/model-status.json');
    if (availability?.available !== true) return null;
    const [metrics, predictions, similars] = await Promise.all([
      loadOptionalJson('../modelo/metricas.json'), loadOptionalJson('../modelo/predicciones.json'), loadOptionalJson('../modelo/similares.json')
    ]);
    if (!metrics || !Array.isArray(predictions) || !similars || typeof similars !== 'object' || Array.isArray(similars)) return null;
    const testPredictions = predictions.some(row => row.prueba === true);
    const testNeighbors = Object.values(similars).some(rows => Array.isArray(rows) && rows.some(row => row.prueba === true));
    return {
      metrics,
      predictions: new Map(predictions.map(row => [panelKey(row), row])),
      similars,
      isTest: metrics.prueba === true || testPredictions || testNeighbors
    };
  }

  async function init() {
    try {
      const [articles, panels, descriptors, spectra, summary, qc, model] = await Promise.all([
        loadJson('data/articulos.json'), loadJson('data/paneles.json'), loadJson('data/descriptores.json'), loadJson('data/espectros.json'), loadJson('data/summary.json'), loadJson('data/qc_summary.json', true), loadModelData()
      ]);
      state.articles = articles; state.panels = panels; state.descriptors = descriptors; state.spectra = spectra; state.qc = qc; state.model = model;
      setCount('count-articles', summary.articles); setCount('count-panels', summary.panels); setCount('count-descriptors', summary.descriptors); setCount('count-spectra', summary.spectra);
      byId('data-stamp').textContent = 'DATOS DE LA BASE · PREPARACIÓN V0.1';
      initFilters(); renderQc(); renderModelOverview(); renderResults();
      if (state.articles.length) renderDetail(articleKey(state.articles[0]));
      byId('previous').addEventListener('click', () => { state.page--; renderResults(); });
      byId('next').addEventListener('click', () => { state.page++; renderResults(); });
      byId('results').addEventListener('click', event => {
        const card = event.target.closest('.result-card'); if (card) renderDetail(card.dataset.key);
      });
    } catch (error) {
      const message = text('p', `No se pudieron cargar los datos del atlas: ${error.message}`, 'load-error');
      byId('results').replaceChildren(message);
      byId('data-stamp').textContent = 'ERROR DE CARGA';
    }
  }
  init();
})();
