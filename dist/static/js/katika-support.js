(() => {
  const field = document.querySelector('#kt-support-body');
  const counter = document.querySelector('[data-support-count]');
  if (field && counter) {
    const sync = () => { counter.textContent = String(field.value.length); };
    field.addEventListener('input', sync);
    sync();
  }
})();
