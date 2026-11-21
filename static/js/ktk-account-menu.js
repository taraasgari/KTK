/* Close the account dropdown on outside click and Escape; no global theme changes. */
(() => {
  const menu = document.querySelector('[data-kt-account-menu]');
  if (!menu) return;
  document.addEventListener('pointerdown', event => {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.open) {
      menu.open = false;
      menu.querySelector('summary')?.focus();
    }
  });
})();
