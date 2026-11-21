(() => {
  'use strict';
  document.querySelectorAll('[data-product-gallery]').forEach(gallery => {
    const main = gallery.querySelector('[data-gallery-main]');
    const buttons = [...gallery.querySelectorAll('[data-gallery-thumb]')];
    buttons.forEach(button => button.addEventListener('click', () => {
      const url = button.dataset.full;
      if (url && main) { main.src = url; main.alt = button.dataset.alt || ''; }
      buttons.forEach(other => { other.classList.toggle('is-active', other === button); other.setAttribute('aria-pressed', String(other === button)); });
    }));
  });
  document.querySelectorAll('[data-detail-buy]').forEach(form => {
    const input = form.querySelector('input[name="quantity"]');
    const clamp = value => Math.max(Number(input.min) || 1, Math.min(Number(input.max) || 20, value || 1));
    form.querySelector('[data-qty-plus]')?.addEventListener('click', () => { input.value = clamp(Number(input.value) + 1); });
    form.querySelector('[data-qty-minus]')?.addEventListener('click', () => { input.value = clamp(Number(input.value) - 1); });
    input.addEventListener('change', () => { input.value = clamp(Number(input.value)); });
  });
  document.querySelectorAll('[data-product-tabs]').forEach(box => {
    const tabs = [...box.querySelectorAll('[data-product-tab]')];
    const panels = [...box.querySelectorAll('[data-tab-panel]')];
    const narrow = window.matchMedia('(max-width: 800px)');
    let selected = 'description';
    function activate(button, focusSection=false) {
      selected = button.dataset.productTab;
      tabs.forEach(tab => {
        const active = tab === button;
        tab.setAttribute('aria-pressed', String(active));
        tab.classList.toggle('is-selected', active);
      });
      panels.forEach(panel => { panel.hidden = narrow.matches && panel.dataset.tabPanel !== selected; });
      if (focusSection && !narrow.matches) {
        box.querySelector(`[data-tab-panel="${selected}"]`)?.scrollIntoView({behavior:'smooth',block:'nearest',inline:'nearest'});
      }
    }
    tabs.forEach((button,i) => {
      button.addEventListener('click', () => activate(button,true));
      button.addEventListener('keydown',event => {
        if (!['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
        event.preventDefault();
        const idx=event.key==='Home'?0:event.key==='End'?tabs.length-1:(i+(event.key==='ArrowLeft'?-1:1)+tabs.length)%tabs.length;
        activate(tabs[idx],true);tabs[idx].focus();
      });
    });
    narrow.addEventListener('change', () => activate(tabs.find(tab => tab.dataset.productTab === selected)));
    activate(tabs[0]);
  });
})();
