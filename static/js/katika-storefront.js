/* Accessible carousel: intentionally leaves native shop functions untouched. */
(() => {
  const root = document.querySelector('[data-katika-slider]');
  if (!root) return;
  const panels = Array.from(root.querySelectorAll('[data-slide]'));
  const dots = Array.from(root.querySelectorAll('[data-slide-dot]'));
  if (panels.length < 2) return;
  let current = 0;
  let interval;
  const show = (n) => {
    current = (n + panels.length) % panels.length;
    panels.forEach((panel, i) => { panel.hidden = i !== current; });
    dots.forEach((dot, i) => {
      dot.classList.toggle('active', i === current);
      dot.setAttribute('aria-pressed', String(i === current));
    });
  };
  const pause = () => { if (interval) clearInterval(interval); interval = undefined; };
  const play = () => {
    pause();
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      interval = window.setInterval(() => show(current + 1), 6500);
    }
  };
  dots.forEach((dot, i) => dot.addEventListener('click', () => { show(i); play(); }));
  root.addEventListener('mouseenter', pause);
  root.addEventListener('mouseleave', play);
  root.addEventListener('focusin', pause);
  root.addEventListener('focusout', (e) => { if (!root.contains(e.relatedTarget)) play(); });
  document.addEventListener('visibilitychange', () => { document.hidden ? pause() : play(); });
  play();
})();
