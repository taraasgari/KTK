(() => {
  'use strict';
  const sidebar = document.querySelector('[data-pa-sidebar]');
  const overlay = document.querySelector('[data-pa-overlay]');

  function openSidebar() {
    sidebar?.classList.add('open');
    overlay?.classList.add('show');
    document.body.style.overflow = 'hidden';
  }
  function closeSidebar() {
    sidebar?.classList.remove('open');
    overlay?.classList.remove('show');
    document.body.style.overflow = '';
  }

  document.addEventListener('click', (event) => {
    if (event.target.closest('[data-pa-open]')) {
      openSidebar();
      return;
    }
    if (event.target.closest('[data-pa-close]') || event.target.closest('[data-pa-overlay]')) {
      closeSidebar();
      return;
    }
    const close = event.target.closest('[data-pa-message-close]');
    if (close) close.closest('.pa-message')?.remove();

    const accountMenu = event.target.closest('.pa-account-menu');
    document.querySelectorAll('.pa-account-menu[open]').forEach((item) => {
      if (item !== accountMenu) item.removeAttribute('open');
    });
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeSidebar();
      document.querySelectorAll('.pa-account-menu[open]').forEach((item) => item.removeAttribute('open'));
    }
  });
})();
