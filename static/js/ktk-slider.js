// Minimal progressive carousel: no CDN / no third-party package.
(() => {
  const root = document.querySelector('[data-ktk-slider]');
  if (!root) return;
  const slides = Array.from(root.querySelectorAll('[data-slide]'));
  if (slides.length < 2) return;
  let index = 0;
  const update = (next) => {
    index = (next + slides.length) % slides.length;
    slides.forEach((el, i) => { el.hidden = i !== index; });
  };
  root.querySelector('[data-slider-next]')?.addEventListener('click', () => update(index + 1));
  root.querySelector('[data-slider-prev]')?.addEventListener('click', () => update(index - 1));
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    let interval = setInterval(() => update(index + 1), 6500);
    root.addEventListener('mouseenter', () => clearInterval(interval));
    root.addEventListener('mouseleave', () => { clearInterval(interval); interval = setInterval(() => update(index + 1), 6500); });
  }
})();
