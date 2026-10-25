(() => {
  const $ = (id) => document.getElementById(id);
  const state = { figures: [], panels: [], panelsByFigure: new Map(), page: 0, pageSize: 12, selectedTechniques: new Set(), topTechniques: new Set(), panelBin: '' , showBoxes: true };
  const filters = { search: $('figure-search'), destination: $('destination'), techniques: $('figure-techniques'), techniqueMode: $('technique-mode'), family: $('figure-family'), carrierClass: $('carrier-class'), queue: $('include-queue') };
  const clean = value => String(value ?? '').trim();
  const label = (value, fallback = 'No reportado') => clean(value) || fallback;
  const fmt = value => Number(value || 0).toLocaleString('es-CR');
  const make = (tag, className, value) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = String(value);
    return node;
  };
  const highlight = (node, value, query) => {
    const text = String(value ?? ''); const term = clean(query); if (!term) { node.textContent = text; return; }
    const lower = text.toLocaleLowerCase('es'), needle = term.toLocaleLowerCase('es'); let at = 0; const fragment = document.createDocumentFragment(); let index;
    while ((index = lower.indexOf(needle, at)) >= 0) { fragment.append(document.createTextNode(text.slice(at,index))); const mark = document.createElement('mark'); mark.textContent = text.slice(index,index+term.length); fragment.append(mark); at = index + term.length; }
    fragment.append(document.createTextNode(text.slice(at))); node.replaceChildren(fragment);
  };
  const choices = (select, values, display = value => value) => {
    [...new Set(values.map(clean).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'es', { sensitivity: 'base' })).forEach(value => {
      const option = make('option', '', display(value)); option.value = value; select.append(option);
    });
  };
  const safeDoi = value => /^https:\/\/doi\.org\//i.test(clean(value)) ? clean(value) : '';
  const accepted = row => row.accepted === true;
  const figurePanels = figure => state.panelsByFigure.get(figure.fig_id) || [];
  const figureTechniques = figure => Array.isArray(figure.tecnicas_normalizadas) ? figure.tecnicas_normalizadas : clean(figure.tecnicas).split(/[|;+]/).map(clean).filter(Boolean);
  const figureFamilies = figure => Array.isArray(figure.familias_tecnicas) ? figure.familias_tecnicas : [];
  const matchesTechnique = (value, techniques) => value === '__other__' ? techniques.some(name => !state.topTechniques.has(name)) : techniques.includes(value);

  function filterData() {
    const query = clean(filters.search.value).toLocaleLowerCase('es');
    return state.figures.filter(figure => {
      if (!filters.queue.checked && !accepted(figure)) return false;
      if (figure.destino_vision === 'excluir') return false;
      if (filters.destination.value && figure.destino_vision !== filters.destination.value) return false;
      if (filters.carrierClass.value && figure.clase_modelo !== filters.carrierClass.value) return false;
      if (filters.family.value && !figureFamilies(figure).includes(filters.family.value)) return false;
      if (state.panelBin) {
        const count = Number(figure.paneles || figure.n || 0); const [min, max] = state.panelBin === '9+' ? [9, Infinity] : state.panelBin.includes('–') ? state.panelBin.split('–').map(Number) : [Number(state.panelBin), Number(state.panelBin)];
        if (count < min || count > max) return false;
      }
      const techniques = figureTechniques(figure);
      if (state.selectedTechniques.has('__missing__') && techniques.length) return false;
      const selected = [...state.selectedTechniques].filter(value => value !== '__missing__');
      if (selected.length) {
        const matches = selected.filter(value => matchesTechnique(value, techniques)).length;
        if (filters.techniqueMode.value === 'all' ? matches !== selected.length : matches === 0) return false;
      }
      const text = [figure.pmcid, figure.figura, figure.title, figure.destino_vision, figure.tecnicas].join(' ').toLocaleLowerCase('es');
      if (query && !text.includes(query)) return false;
      return true;
    });
  }

  function drawOriginal(card, figure, panels) {
    const wrap = make('div', 'figure-image-wrap');
    if (figure.image_available && figure.image_web) {
      const img = make('img', 'figure-original'); img.alt = `${figure.figura || 'Figura'} · ${figure.pmcid}`; img.loading = 'lazy'; img.decoding = 'async';
      img.tabIndex = 0; img.setAttribute('role', 'button'); img.setAttribute('aria-label', `Ampliar ${figure.figura || 'figura'} de ${figure.pmcid}`);
      const overlay = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      overlay.setAttribute('class', 'figure-boxes'); overlay.setAttribute('viewBox', '0 0 1 1'); overlay.setAttribute('preserveAspectRatio', 'none');
      panels.forEach(panel => {
        const values = ['x0', 'y0', 'x1', 'y1'].map(key => Number(panel[key]));
        if (!values.every(Number.isFinite) || values[0] < 0 || values[1] < 0 || values[2] > 1 || values[3] > 1 || values[2] <= values[0] || values[3] <= values[1]) return;
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', values[0]); rect.setAttribute('y', values[1]); rect.setAttribute('width', values[2] - values[0]); rect.setAttribute('height', values[3] - values[1]);
        rect.setAttribute('class', `box-${clean(panel.tipo).replace(/[^a-z]/gi, '') || 'other'}`);
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title'); title.textContent = `Panel ${label(panel.panel)} · ${label(panel.tipo)} · ${label(panel.tecnica)}`; rect.append(title); overlay.append(rect);
      });
      img.addEventListener('load', () => { wrap.style.minHeight = '0'; wrap.style.aspectRatio = `${img.naturalWidth} / ${img.naturalHeight}`; });
      img.addEventListener('click', () => openLightbox(figure));
      img.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openLightbox(figure); } });
      img.src = figure.image_web; wrap.append(img, overlay);
    } else {
      wrap.classList.add('figure-image-missing');
      wrap.append(make('span', 'missing-symbol', '▧'), make('p', '', 'Imagen original no disponible en esta copia local.'), make('small', '', 'Las cajas y metadatos siguen disponibles; no se simula una imagen.'));
    }
    card.append(wrap);
  }

  function renderCard(figure) {
    const panels = figurePanels(figure);
    const card = make('article', 'figure-card');
    const head = make('div', 'figure-card-head');
    const title = make('h3'); highlight(title, `${label(figure.figura, 'Figura')} · ${label(figure.pmcid)}`, filters.search.value); head.append(title);
    const status = make('span', `tag ${accepted(figure) ? 'accepted-tag' : 'queue-tag'}`, accepted(figure) ? 'Aceptada' : 'En cola de revisión'); head.append(status); card.append(head);
    const summary = make('p', 'figure-card-summary', `${label(figure.destino_vision)} · ${label(figure.tecnicas, 'Técnica no reportada')} · ${panels.length} paneles segmentados`); card.append(summary);
    if (figure.destino_vision === 'superpuesto') card.append(make('p', 'overlap-warning', 'Espectros superpuestos: identificados como no utilizables para entrenamiento.'));
    if (figure.title) { const articleTitle = make('p','figure-article-title'); highlight(articleTitle, figure.title, filters.search.value); card.append(articleTitle); }
    const doi = safeDoi(figure.doi_link);
    const citation = make('div', 'figure-citation');
    if (doi) { const link = make('a', '', 'Abrir artículo / DOI ↗'); link.href = doi; link.target = '_blank'; link.rel = 'noopener noreferrer'; citation.append(link); }
    citation.append(make('span', '', `Licencia indicada en el repositorio: ${label(figure.license, 'no confirmada')}`)); card.append(citation);
    drawOriginal(card, figure, panels);

    const cropSection = make('details', 'crop-details');
    const cropSummary = make('summary', '', `Paneles recortados (${panels.length})`); cropSection.append(cropSummary);
    if (!panels.length) cropSection.append(make('p', 'no-data', 'No hay paneles asociados en el índice de recortes.'));
    const list = make('div', 'crop-list');
    panels.forEach(panel => {
      const row = make('div', 'crop-row');
      if (panel.crop_available && panel.crop_web) {
        const image = make('img', 'crop-thumb'); image.src = panel.crop_web; image.alt = `Recorte del panel ${label(panel.panel)}`; image.loading = 'lazy'; image.decoding = 'async'; row.append(image);
      } else row.append(make('div', 'crop-missing', 'Miniatura pendiente del paquete de imágenes.'));
      const meta = make('div', 'crop-meta');
      meta.append(make('strong', '', `Panel ${label(panel.panel)} · ${label(panel.tipo)}`));
      meta.append(make('span', '', `Técnica: ${label(panel.tecnica)}`));
      meta.append(make('span', '', `Contenido: ${label(panel.contenido)}`));
      meta.append(make('span', '', `Clase: ${label(panel.clase)}`));
      meta.append(make('span', '', `Elegible para morfología: ${panel.elegible_morfologia_bool ? 'sí' : 'no'}`));
      if (panel.padre) meta.append(make('span', '', `Panel hijo de ${panel.padre} · ${label(panel.rel)}`));
      if (panel.cascada_bool) meta.append(make('span', 'cascade-tag', 'Segmentación en cascada'));
      row.append(meta); list.append(row);
    });
    cropSection.append(list); card.append(cropSection);
    return card;
  }

  function render() {
    const found = filterData();
    const pages = Math.max(1, Math.ceil(found.length / state.pageSize));
    state.page = Math.min(state.page, pages - 1);
    const start = state.page * state.pageSize;
    const visible = found.slice(start, start + state.pageSize);
    $('figure-result-count').textContent = `${fmt(found.length)} figuras · ${fmt(visible.length ? start + 1 : 0)}–${fmt(start + visible.length)}`;
    $('figure-page-label').textContent = found.length ? `${state.page + 1} / ${pages}` : '';
    $('figure-previous').disabled = state.page === 0; $('figure-next').disabled = state.page >= pages - 1;
    const results = $('figure-results'); results.replaceChildren();
    if (!visible.length) results.append(make('p', 'no-data', 'No hay figuras que coincidan con los filtros.'));
    visible.forEach(figure => results.append(renderCard(figure)));
  }

  function lightboxBoxOverlay(figure) {
    const dialog = $('image-lightbox'); const image = dialog.querySelector('figure > img');
    dialog.querySelector('.lightbox-boxes')?.remove();
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); svg.setAttribute('class', 'lightbox-boxes'); svg.setAttribute('viewBox', '0 0 1 1'); svg.setAttribute('preserveAspectRatio', 'none');
    figurePanels(figure).forEach(panel => {
      const v = ['x0','y0','x1','y1'].map(k => Number(panel[k]));
      if (!v.every(Number.isFinite) || v[0] < 0 || v[1] < 0 || v[2] > 1 || v[3] > 1 || v[2] <= v[0] || v[3] <= v[1]) return;
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect'); rect.setAttribute('x', v[0]); rect.setAttribute('y', v[1]); rect.setAttribute('width', v[2]-v[0]); rect.setAttribute('height', v[3]-v[1]); rect.setAttribute('class', `box-${clean(panel.tipo).replace(/[^a-z]/gi, '') || 'other'}${panel.padre ? ' inset-box' : ''}`); svg.append(rect);
    });
    image.insertAdjacentElement('afterend', svg);
    const align = () => { const frame = image.parentElement.getBoundingClientRect(); const box = image.getBoundingClientRect(); svg.style.left = `${box.left-frame.left}px`; svg.style.top = `${box.top-frame.top}px`; svg.style.right = 'auto'; svg.style.bottom = 'auto'; svg.style.width = `${box.width}px`; svg.style.height = `${box.height}px`; };
    image.addEventListener('load', align, { once: true }); if (image.complete) align();
  }

  function ensureLightboxImage() {
    const figure = $('image-lightbox').querySelector('figure');
    let image = figure.querySelector('img');
    if (!image) { image = document.createElement('img'); figure.insertBefore(image, figure.querySelector('figcaption')); }
    return image;
  }

  function openLightbox(figure) {
    const dialog = $('image-lightbox'); const candidates = filterData().filter(row => row.image_available && row.image_web);
    state.lightboxFigures = candidates; state.lightboxIndex = Math.max(0, candidates.findIndex(row => row.fig_id === figure.fig_id));
    const current = candidates[state.lightboxIndex] || figure; const image = ensureLightboxImage();
    image.src = current.image_web; image.alt = `${current.figura || 'Figura'} · ${current.pmcid}`;
    dialog.querySelector('figcaption').textContent = `${current.figura || 'Figura'} · ${current.pmcid} · ${label(current.tecnicas, 'Sin técnica asignada')}`;
    dialog.classList.toggle('boxes-hidden', !state.showBoxes); lightboxBoxOverlay(current);
    if (!dialog.open) dialog.showModal();
  }

  function moveLightbox(delta) {
    if (!state.lightboxFigures?.length) return;
    state.lightboxIndex = (state.lightboxIndex + delta + state.lightboxFigures.length) % state.lightboxFigures.length;
    const figure = state.lightboxFigures[state.lightboxIndex]; const dialog = $('image-lightbox');
    const image = ensureLightboxImage(); image.src = figure.image_web; image.alt = `${figure.figura || 'Figura'} · ${figure.pmcid}`;
    dialog.querySelector('figcaption').textContent = `${figure.figura || 'Figura'} · ${figure.pmcid} · ${label(figure.tecnicas, 'Sin técnica asignada')}`;
    lightboxBoxOverlay(figure);
  }

  async function init() {
    try {
      const [figures, panels, summary] = await Promise.all([
        fetch('data/figuras.json').then(response => { if (!response.ok) throw new Error('figuras.json no disponible'); return response.json(); }),
        fetch('data/paneles_recortados.json').then(response => { if (!response.ok) throw new Error('paneles_recortados.json no disponible'); return response.json(); }),
        fetch('data/figuras_summary.json').then(response => { if (!response.ok) throw new Error('figuras_summary.json no disponible'); return response.json(); })
      ]);
      state.figures = figures; state.panels = panels;
      state.panelsByFigure = new Map();
      panels.forEach(panel => {
        const linked = state.panelsByFigure.get(panel.fig_id) || [];
        linked.push(panel); state.panelsByFigure.set(panel.fig_id, linked);
      });
      $('total-figures').textContent = fmt(summary.figures_total); $('accepted-figures').textContent = fmt(summary.figures_accepted); $('queue-figures').textContent = fmt(summary.figures_queue); $('total-crops').textContent = fmt(summary.panels_total); $('queue-toggle-count').textContent = fmt(summary.figures_queue_visible); $('queue-toggle-total').textContent = fmt(summary.figures_queue);
      const excluded = summary.figures_excluded_destination + summary.figures_queue_excluded_destination;
      $('image-note').textContent = `${fmt(summary.figures_original_available)} de ${fmt(summary.figures_total)} figuras tienen imagen local con licencia reutilizable; ${fmt(summary.panels_crop_available)} de ${fmt(summary.panels_total)} miniaturas de panel están disponibles. Las demás muestran un marcador explícito. La vista deja fuera ${fmt(excluded)} registros con destino “excluir” (${fmt(summary.figures_excluded_destination)} aceptados y ${fmt(summary.figures_queue_excluded_destination)} en cola).`;
      choices(filters.destination, figures.filter(accepted).filter(row => row.destino_vision !== 'excluir').map(row => row.destino_vision));
      const techniqueCounts = summary.visible_figure_technique_counts || {};
      state.topTechniques = new Set(summary.top_techniques || []);
      const scope = summary.figures_accepted_visible;
      $('technique-scope-note').textContent = `Filtro y gráficos: ${fmt(scope)} figuras aceptadas y visibles, ${fmt(summary.visible_figures_without_technique)} sin técnica tras normalizar. En las ${fmt(summary.figures_total)} figuras fuente hay ${fmt(summary.figures_without_technique)} sin técnica. La diferencia previa (${fmt(summary.visible_figures_without_raw_technique)} frente a ${fmt(summary.figures_without_raw_technique)}) era el alcance; al quitar marcadores no técnicos cambian ligeramente ambas cifras. Las técnicas de panel no se filtran: faltan en 8.010 de 8.108 paneles.`;
      const addChip = (value, caption, host = filters.techniques) => {
        const chip = make('label', 'technique-chip'); const checkbox = document.createElement('input'); checkbox.type = 'checkbox'; checkbox.value = value;
        checkbox.addEventListener('change', () => { if (checkbox.checked) { if (value === '__missing__') { filters.techniques.querySelectorAll('input:not([value="__missing__"])').forEach(box => { box.checked = false; state.selectedTechniques.delete(box.value); }); } else { const missing = filters.techniques.querySelector('input[value="__missing__"]'); if (missing) missing.checked = false; state.selectedTechniques.delete('__missing__'); } state.selectedTechniques.add(value); } else state.selectedTechniques.delete(value); state.page = 0; render(); });
        chip.append(checkbox, make('span', '', caption)); host.append(chip);
      };
      addChip('__missing__', `Sin técnica asignada (${fmt(summary.visible_figures_without_technique)})`);
      const others = make('details', 'technique-others');
      others.append(make('summary', '', `Otras técnicas · desplegar ${Object.keys(techniqueCounts).filter(name => !state.topTechniques.has(name)).length} etiquetas`));
      const otherChips = make('div', 'other-technique-chips');
      addChip('__other__', `Cualquier técnica fuera de las 10 principales (${fmt(summary.technique_other_visible_figures)})`, otherChips);
      Object.entries(summary.technique_families || {}).forEach(([family, names]) => {
        const option = make('option', '', `${family} (${fmt((summary.technique_family_visible_counts || {})[family] || 0)})`); option.value = family; filters.family.append(option);
        const sorted = names.filter(name => name in techniqueCounts).sort((a, b) => (techniqueCounts[b] || 0) - (techniqueCounts[a] || 0) || a.localeCompare(b, 'es'));
        for (const [host, included] of [[filters.techniques, sorted.filter(name => state.topTechniques.has(name))], [otherChips, sorted.filter(name => !state.topTechniques.has(name))]]) {
          if (!included.length) continue;
          const heading = make('strong', 'technique-family-label', family); heading.style.flexBasis = '100%'; host.append(heading);
          included.forEach(name => addChip(name, `${name} (${fmt(techniqueCounts[name])})`, host));
        }
      });
      others.append(otherChips); filters.techniques.append(others);
      choices(filters.carrierClass, figures.map(row => row.clase_modelo));
      const params = new URLSearchParams(location.search);
      if (params.has('destination')) filters.destination.value = params.get('destination');
      if (params.has('class')) filters.carrierClass.value = params.get('class');
      if (params.has('family')) filters.family.value = params.get('family');
      if (params.has('technique')) { const checkbox = [...filters.techniques.querySelectorAll('input')].find(item => item.value === params.get('technique')); if (checkbox) { checkbox.checked = true; state.selectedTechniques.add(checkbox.value); const details = checkbox.closest('details'); if (details) details.open = true; } }
      if (params.has('panels')) state.panelBin = params.get('panels');
      [filters.search, filters.destination, filters.carrierClass, filters.family, filters.queue, filters.techniqueMode].forEach(control => control.addEventListener(control === filters.search ? 'input' : 'change', () => { state.page = 0; render(); }));
      $('figure-previous').addEventListener('click', () => { state.page -= 1; render(); }); $('figure-next').addEventListener('click', () => { state.page += 1; render(); });
      render();
    } catch (error) {
      $('figure-results').replaceChildren(make('p', 'load-error', `No se pudo cargar la vista de figuras: ${error.message}. Ejecute build_data.py desde producto y vuelva a cargar.`));
      $('figure-result-count').textContent = 'Error al cargar';
    }
  }
  $('image-lightbox')?.addEventListener('click', event => {
    if (event.target.closest('.lightbox-prev')) moveLightbox(-1);
    if (event.target.closest('.lightbox-next')) moveLightbox(1);
    if (event.target.closest('.lightbox-toggle')) { state.showBoxes = !state.showBoxes; $('image-lightbox').classList.toggle('boxes-hidden', !state.showBoxes); }
  });
  $('image-lightbox')?.addEventListener('keydown', event => { if (event.key === 'ArrowLeft') moveLightbox(-1); if (event.key === 'ArrowRight') moveLightbox(1); });
  init();
})();
