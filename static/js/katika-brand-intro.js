/* KTK: show a fullscreen splash for 3 seconds, then show the homepage. */
(() => {
  'use strict';

  const root = document.documentElement;
  const intro = document.getElementById('ktk-brand-intro');
  if (!intro || !root.classList.contains('ktk-brand-intro-pending')) return;

  const TOTAL_MS = 3000;
  const FADE_MS = 300;
  let started = false;

  function start() {
    if (started) return;
    started = true;

    const reduceMotion = window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Keep the body scroll-locked throughout the three-second intro.
    window.setTimeout(() => {
      root.classList.add('ktk-brand-intro-done');
    }, reduceMotion ? TOTAL_MS : TOTAL_MS - FADE_MS);

    window.setTimeout(() => {
      root.classList.remove('ktk-brand-intro-pending', 'ktk-brand-intro-done');
      intro.remove();
    }, TOTAL_MS);
  }

  const image = intro.querySelector('img');
  if (!image || image.complete) {
    start();
  } else {
    image.addEventListener('load', start, { once: true });
    image.addEventListener('error', start, { once: true });
    // Avoid a permanently blocked page on a failed/stalled image request.
    window.setTimeout(start, 1200);
  }
})();
