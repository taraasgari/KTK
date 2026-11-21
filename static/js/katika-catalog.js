/* Collection interactions: browser state only for view preference, server owns results. */
(() => {
  const grid = document.querySelector('[data-catalog-products]');
  if (!grid) return;
  const toggles = document.querySelectorAll('[data-catalog-view]');
  function setView(mode) {
    const value = mode === 'list' ? 'list' : 'grid';
    grid.classList.toggle('is-list', value === 'list');
    toggles.forEach((btn) => {
      const active = btn.dataset.catalogView === value;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-pressed', String(active));
    });
    try { localStorage.setItem('ktk-catalog-view', value); } catch (error) {}
  }
  let savedView = 'grid';
  try { savedView = localStorage.getItem('ktk-catalog-view') || 'grid'; } catch (error) {}
  setView(savedView);
  toggles.forEach((button) => button.addEventListener('click', () => setView(button.dataset.catalogView)));

  document.querySelectorAll('[data-catalog-select]').forEach((select) => select.addEventListener('change', () => {
    const url = new URL(window.location.href);
    url.searchParams.set(select.dataset.catalogSelect, select.value);
    url.searchParams.delete('page');
    window.location.assign(url.toString());
  }));

  document.querySelectorAll('[data-quantity-stepper]').forEach((stepper) => {
    const input = stepper.querySelector('input[type="number"]');
    if (!input) return;
    const limit = Number(input.max || 20);
    const clamp = (n) => Math.max(1, Math.min(limit, Number.isFinite(n) ? n : 1));
    stepper.querySelector('[data-qty-plus]').addEventListener('click', () => { input.value = String(clamp(Number(input.value) + 1)); });
    stepper.querySelector('[data-qty-minus]').addEventListener('click', () => { input.value = String(clamp(Number(input.value) - 1)); });
    input.addEventListener('change', () => { input.value = String(clamp(Number(input.value))); });
  });

  const filterToggle = document.querySelector('[data-catalog-filters-toggle]');
  const sidebar = document.querySelector('#catalog-filters');
  filterToggle?.addEventListener('click', () => {
    const expanded = filterToggle.getAttribute('aria-expanded') !== 'true';
    sidebar.classList.toggle('is-open', expanded);
    filterToggle.setAttribute('aria-expanded', String(expanded));
  });

  const range = document.querySelector('[data-kt-price-range]');
  if (range) {
    const lower = range.querySelector('[data-min-range]');
    const upper = range.querySelector('[data-max-range]');
    const inputMin = range.querySelector('[data-price-min]');
    const inputMax = range.querySelector('[data-price-max]');
    const track = range.querySelector('[data-kt-price-sliders]');
    const boundsMin = Number(lower.min || 0);
    const boundsMax = Number(upper.max || 0);
    function normalize(n, fallback) { return Number.isFinite(n) ? Math.min(boundsMax, Math.max(boundsMin, n)) : fallback; }
    function sync(fromRange) {
      let low = normalize(Number(fromRange ? lower.value : inputMin.value), boundsMin);
      let high = normalize(Number(fromRange ? upper.value : inputMax.value), boundsMax);
      if (low > high) { if (fromRange) { high = low; } else { low = high; } }
      lower.value = low; upper.value = high;
      inputMin.value = low; inputMax.value = high;
      const divisor = Math.max(1, boundsMax - boundsMin);
      track.style.setProperty('--price-low', `${(low - boundsMin) / divisor * 100}%`);
      track.style.setProperty('--price-high', `${(high - boundsMin) / divisor * 100}%`);
    }
    lower.addEventListener('input', () => sync(true));
    upper.addEventListener('input', () => sync(true));
    inputMin.addEventListener('change', () => sync(false));
    inputMax.addEventListener('change', () => sync(false));
    sync(true);
  }
})();
