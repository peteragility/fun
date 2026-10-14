(() => {
  'use strict';
  const chapters = Array.from(document.querySelectorAll('section.chapter'));
  if (!chapters.length) return;
  const bar = document.createElement('div');
  bar.className = 'position-bar';
  bar.innerHTML =
    '<span class="pb-label">你喺邊</span>' +
    '<span class="pb-num" data-num></span>' +
    '<span class="pb-title" data-title></span>' +
    '<button class="pb-jump" type="button">下一個故事</button>';
  const storyAnchor = document.getElementById('story');
  if (storyAnchor) storyAnchor.insertBefore(bar, storyAnchor.firstChild);
  const num = bar.querySelector('[data-num]');
  const title = bar.querySelector('[data-title]');
  const jump = bar.querySelector('.pb-jump');
  const update = (chapter) => {
    chapters.forEach((c) => c.removeAttribute('data-current'));
    chapter.setAttribute('data-current', 'true');
    const id = chapter.id;
    num.textContent = id.replace(/^ch-/, '').padStart(2, '0');
    title.textContent = (chapter.querySelector('h2') || {}).textContent || '';
  };
  chapters[0].setAttribute('data-current', 'true');
  update(chapters[0]);
  jump.addEventListener('click', () => {
    const current = chapters.findIndex((c) => c.getAttribute('data-current') === 'true');
    const next = chapters[Math.min(chapters.length - 1, current + 1)];
    if (next) {
      next.scrollIntoView({ behavior: 'smooth', block: 'start' });
      update(next);
    }
  });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((e) => e.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
      if (visible.length) {
        const ch = visible[0].target.closest('section.chapter');
        if (ch) update(ch);
      }
    }, { rootMargin: '-120px 0px -60% 0px' });
    chapters.forEach((c) => observer.observe(c));
  }
  document.documentElement.dataset.storyReady = 'true';
})();
