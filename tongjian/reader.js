(() => {
  'use strict';
  const key = 'fun-tongjian-reading-v1';
  const read = () => { try { return JSON.parse(localStorage.getItem(key) || 'null'); } catch { return null; } };
  const save = value => { try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch { return false; } };
  const valid = value => value && Number.isInteger(value.volume) && value.volume >= 1 && value.volume <= 294;
  const page = volume => String(volume).padStart(3, '0') + '.html';
  const previous = read();
  const resume = document.getElementById('resumeReading');
  if (resume && valid(previous)) {
    const anchor = /^p-\d+$/.test(previous.anchor) ? '#' + previous.anchor : '';
    resume.href = 'volumes/' + page(previous.volume) + anchor;
    resume.textContent = '繼續閱讀 · 卷' + previous.volume;
    resume.hidden = false;
  }
  const redirectLegacy = () => {
    const legacy = /^#j(\d{1,3})$/.exec(location.hash);
    if (resume && legacy && valid({volume:Number(legacy[1])})) location.replace('volumes/' + page(Number(legacy[1])));
  };
  redirectLegacy();
  if (resume) window.addEventListener('hashchange', redirectLegacy);
  const main = document.querySelector('main[data-volume]');
  if (main) {
    const volume = Number(main.dataset.volume);
    let size = valid(previous) && Number.isFinite(previous.size) ? Math.max(16, Math.min(26, previous.size)) : 18;
    let anchor = /^#p-\d+$/.test(location.hash) ? location.hash.slice(1) : 'p-1';
    const persist = () => {
      if (window.scrollY > 0 || /^#p-\d+$/.test(location.hash)) {
        try { history.replaceState(null, '', '#' + anchor); } catch { /* Reading remains usable in restricted frames. */ }
      }
      const saved = save({volume, anchor, size});
      document.getElementById('readingStatus').textContent = saved ? '閱讀位置記錄在此瀏覽器；分享段落可複製網址。' : '瀏覽器未能保存位置；可把本卷網址加入書籤。';
    };
    const paintSize = () => document.documentElement.style.setProperty('--reading-size', size + 'px');
    paintSize(); persist();
    document.getElementById('fontDown').onclick = () => { size = Math.max(16, size - 1); paintSize(); persist(); };
    document.getElementById('fontUp').onclick = () => { size = Math.min(26, size + 1); paintSize(); persist(); };
    document.getElementById('volumeJump').onchange = event => {
      const volume = Number(event.target.value);
      if (valid({volume})) location.assign(page(volume));
    };
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        const visible = entries.filter(entry => entry.isIntersecting).sort((a,b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible.length) { anchor = visible[0].target.id; persist(); }
      }, {rootMargin:'-100px 0px -60% 0px'});
      document.querySelectorAll('.juan p[id]').forEach(paragraph => observer.observe(paragraph));
    }
    window.addEventListener('pagehide', persist);
  }
  const search = document.getElementById('volumeSearch');
  if (search) search.addEventListener('input', () => {
    const query = search.value.trim().toLocaleLowerCase(); let count = 0;
    const exactEra = [...document.querySelectorAll('.volume-link')].some(link => link.dataset.era === query);
    document.querySelectorAll('.volume-link').forEach(link => {
      const matches = exactEra ? link.dataset.era === query : (link.textContent + ' ' + Number(/(\d+)\.html$/.exec(link.getAttribute('href'))[1])).toLocaleLowerCase().includes(query);
      link.hidden = !matches; if (matches) count++;
    });
    document.querySelectorAll('.era').forEach(era => era.hidden = !era.querySelector('.volume-link:not([hidden])'));
    document.getElementById('searchStatus').textContent = count ? count + ' 卷符合' : '找不到符合的卷目；可試朝代名稱或卷號。';
  });
  document.documentElement.dataset.readerReady = 'true';
})();
