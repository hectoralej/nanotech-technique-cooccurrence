(() => {
  document.querySelectorAll('.quality-notice').forEach(notice => {
    const key = 'nano2predict-quality-notice-dismissed';
    try { notice.hidden = sessionStorage.getItem(key) === '1'; } catch { /* Storage may be disabled; close button still works. */ }
    notice.querySelector('button')?.addEventListener('click', () => {
      notice.hidden = true;
      try { sessionStorage.setItem(key, '1'); } catch { /* Dismissal remains for this page. */ }
    });
  });
})();
