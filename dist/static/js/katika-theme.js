/* One persisted theme preference shared by the storefront and owner console. */
(() => {
  'use strict';
  const STORAGE_KEY = 'ktk-theme';
  const root = document.documentElement;

  function normalize(value) {
    return value === 'dark' || value === 'night' ? 'dark' : 'light';
  }

  function readTheme() {
    try {
      const current = localStorage.getItem(STORAGE_KEY);
      if (current === 'dark' || current === 'light') return current;
      // Migrate the previous owner-only preference once, without overriding a shared choice.
      return normalize(localStorage.getItem('ktk-owner-theme'));
    } catch (_) {
      return 'light';
    }
  }

  function applyTheme(value) {
    const theme = normalize(value);
    root.dataset.ktTheme = theme;
    root.dataset.ktkTheme = theme === 'dark' ? 'night' : 'day';
    root.style.colorScheme = theme;
    document.querySelectorAll('[data-kt-theme-toggle], [data-pa-theme]').forEach((button) => {
      button.setAttribute('aria-pressed', String(theme === 'dark'));
      button.setAttribute('aria-label', theme === 'dark' ? 'فعال کردن حالت روز' : 'فعال کردن حالت شب');
      button.title = theme === 'dark' ? 'حالت روز' : 'حالت شب';
    });
  }

  function saveTheme(value) {
    const theme = normalize(value);
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (_) {}
    applyTheme(theme);
  }

  applyTheme(readTheme());

  document.addEventListener('click', (event) => {
    const toggle = event.target.closest('[data-kt-theme-toggle], [data-pa-theme]');
    if (toggle) {
      event.preventDefault();
      saveTheme(root.dataset.ktTheme === 'dark' ? 'light' : 'dark');
      return;
    }

    if (!event.target.closest('[data-kt-language-menu]')) {
      document.querySelectorAll('[data-kt-language-menu][open]').forEach((menu) => menu.removeAttribute('open'));
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      document.querySelectorAll('[data-kt-language-menu][open]').forEach((menu) => menu.removeAttribute('open'));
    }
  });

  window.addEventListener('storage', (event) => {
    if (event.key === STORAGE_KEY) applyTheme(readTheme());
  });
  window.addEventListener('pageshow', () => applyTheme(readTheme()));
})();
