(() => {
  const root = document.getElementById('crop-sample'); if (!root) return;
  const make = (tag, cls, value) => { const node = document.createElement(tag); if (cls) node.className = cls; if (value != null) node.textContent = String(value); return node; };
  const classLabels = {lipidico: 'Lipídico', polimerico: 'Polimérico', inorganico: 'Inorgánico', nanomaterial: 'Nanomaterial'};
  const json = async (url) => { const response = await fetch(url); if (!response.ok) throw new Error('No se pudo cargar el índice de paneles y sus créditos.'); return response.json(); };
  async function init() {
    try {
      const [rows, articles] = await Promise.all([json('data/paneles_recortados.json'), json('data/articulos.json')]);
      const credits = new Map(articles.map(article => [article.pmcid, article]));
      const reusableCredit = row => { const article = credits.get(row.pmcid); return article && /^https:\/\/doi\.org\//.test(article.doi_link || '') && ['cc by', 'cc0'].includes((article.license_epmc || '').toLowerCase()); };
      const classes = ['lipidico','polimerico','inorganico','nanomaterial']; const grid = make('div','crop-sample-grid');
      classes.forEach(className => {
        const section = make('section','crop-sample-class'); section.append(make('h3','',classLabels[className]));
        const group = rows.filter(row => row.clase === className && row.tipo === 'micro' && row.contenido === 'particulas' && row.elegible_morfologia_bool === true && !row.padre && row.crop_available === true && row.crop_web && reusableCredit(row)).slice(0,3);
        if (!group.length) section.append(make('p','no-data','Sin miniaturas disponibles para esta clase.'));
        group.forEach(row => {
          const article = credits.get(row.pmcid); const figure = make('figure','crop-sample-card'); const img = make('img','',null);
          img.src = row.crop_web; img.alt = `${classLabels[className]}: recorte de ${row.fig_id}, panel ${row.panel}`; img.loading = 'lazy'; img.decoding = 'async';
          img.addEventListener('error', () => img.replaceWith(make('p', 'no-data', 'Miniatura no disponible.')), {once: true});
          const caption = make('figcaption','',`${row.fig_id} · panel ${row.panel} · ${article.license_epmc.toUpperCase()} · `);
          const doi = make('a','',`DOI: ${article.doi || article.doi_link.replace('https://doi.org/', '')}`); doi.href = article.doi_link; doi.target = '_blank'; doi.rel = 'noopener noreferrer'; caption.append(doi);
          figure.append(img,caption); section.append(figure);
        });
        grid.append(section);
      }); root.replaceChildren(grid);
    } catch (error) { root.replaceChildren(make('p','load-error',error.message)); }
  }
  init();
})();
