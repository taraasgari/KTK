/* KTK static visual preview: never sends forms or stores user submissions. */
(() => {
  const langs = ['fa', 'en', 'zh-hans'];
  const current = location.pathname.split('/')[1];
  const lang = langs.includes(current) ? current : 'fa';
  const disabledMessage = {
    fa: 'این نسخه فقط پیش‌نمایش ظاهری است و ثبت اطلاعات فعال نیست.',
    en: 'This is a visual preview only. Submitting data is disabled.',
    'zh-hans': '这只是界面预览，暂不支持提交信息。'
  }[lang];
  function notice() {
    let toast = document.getElementById('ktk-static-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'ktk-static-toast';
      Object.assign(toast.style, {position:'fixed', bottom:'20px', left:'50%',transform:'translateX(-50%)', background:'#191b20',color:'#fff',padding:'14px 22px',borderRadius:'12px',zIndex:'20000',maxWidth:'min(90vw,480px)',textAlign:'center',boxShadow:'0 10px 35px #0004'});
      document.body.append(toast);
    }
    toast.textContent = disabledMessage;
    toast.hidden = false;
    clearTimeout(window.__ktkNoticeTimeout);
    window.__ktkNoticeTimeout = setTimeout(() => {toast.hidden = true;}, 3300);
  }
  document.addEventListener('click', (event) => {
    const langBtn = event.target.closest('[data-static-language]');
    if (langBtn) {
      event.preventDefault();
      const target = langBtn.dataset.staticLanguage;
      if (!langs.includes(target)) return;
      const remainder = langs.includes(location.pathname.split('/')[1]) ? '/' + location.pathname.split('/').slice(2).join('/') : location.pathname;
      location.assign('/' + target + (remainder.startsWith('/') ? remainder : '/' + remainder) + location.search + location.hash);
      return;
    }
    if (event.target.closest('[data-demo-disabled]')) {event.preventDefault(); notice();}
  });
  document.addEventListener('submit', (event) => {
    if (event.target.matches('[data-static-language-form]')) {event.preventDefault(); return;}
    if (event.target.matches('[data-demo-disabled-form]')) {event.preventDefault(); notice(); return;}
  });
  // Client-side demo filter on catalog page; product information came from build-time demo records.
  if (document.querySelector('[data-catalog-products]')) {
    const params = new URLSearchParams(location.search);
    const cards = [...document.querySelectorAll('.kt-catalog-card')];
    const query = (params.get('q') || '').trim().toLocaleLowerCase();
    const groups = params.getAll('category');
    const sizes = params.getAll('size');
    const minimum = Number(params.get('price_min') || 0);
    const maximum = Number(params.get('price_max') || Infinity);
    cards.forEach(card => {
      const price = Number(card.dataset.demoPrice || 0);
      const shown = (!query || card.dataset.demoName?.includes(query) || card.textContent.toLowerCase().includes(query))
        && (!groups.length || groups.includes(card.dataset.demoCategory))
        && (!sizes.length || sizes.includes(card.dataset.demoSize))
        && price >= minimum && price <= maximum;
      card.hidden = !shown;
      card.style.display = shown ? '' : 'none';
    });
    const sort = params.get('sort');
    if (sort) {
      const sorted = cards.slice().sort((a,b) => {
        const ap=Number(a.dataset.demoPrice||0), bp=Number(b.dataset.demoPrice||0);
        if(sort==='price_asc') return ap-bp;
        if(sort==='price_desc') return bp-ap;
        if(sort==='name') return (a.dataset.demoName||'').localeCompare(b.dataset.demoName||'', lang);
        return 0;
      });
      const grid = document.querySelector('[data-catalog-products]');
      sorted.forEach(card => grid.append(card));
    }
    document.querySelectorAll('input[name="category"],input[name="size"]').forEach(input => input.checked = params.getAll(input.name).includes(input.value));
    const count = cards.filter(card=>card.style.display!=='none').length;
    const resultCount = document.querySelector('.kt-results-count');
    if (resultCount && count !== cards.length) resultCount.textContent = lang === 'en' ? `${count} products` : lang === 'zh-hans' ? `${count} 件商品` : `نمایش ${count} محصول`;
  }
  if (document.querySelector('.kt-news-card')) {
    const group = new URLSearchParams(location.search).get('category');
    if (group && group !== 'all') {
      document.querySelectorAll('.kt-news-card').forEach(card=>{
        card.style.display = card.dataset.demoGroup === group ? '' : 'none';
      });
      document.querySelectorAll('.kt-news-categories a').forEach(a=>{
        a.classList.toggle('selected',new URL(a.href,location.origin).searchParams.get('category')===group);
      });
    }
  }
})();
