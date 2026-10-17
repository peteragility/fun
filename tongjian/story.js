(() => {
  'use strict';
  // Story/raw mode switch. Story is the default; the choice persists when storage works
  // and silently falls back to the default when it does not.
  const MODE_KEY = 'fun-tongjian-mode';
  const storedMode = () => { try { return localStorage.getItem(MODE_KEY); } catch { return null; } };
  const storeMode = mode => { try { localStorage.setItem(MODE_KEY, mode); } catch { /* no persistence */ } };
  const storyBtn = document.getElementById('modeStory');
  const rawBtn = document.getElementById('modeRaw');
  const storyPart = document.getElementById('story');
  const volumesPart = document.getElementById('volumes');
  const applyMode = mode => {
    const raw = mode === 'raw';
    document.body.dataset.mode = raw ? 'raw' : 'story';
    if (storyBtn && rawBtn) {
      storyBtn.classList.toggle('active', !raw);
      rawBtn.classList.toggle('active', raw);
      storyBtn.setAttribute('aria-pressed', String(!raw));
      rawBtn.setAttribute('aria-pressed', String(raw));
    }
    if (storyPart) storyPart.hidden = raw;
    if (volumesPart) volumesPart.hidden = !raw;
  };
  if (storyBtn && rawBtn) {
    storyBtn.addEventListener('click', () => { applyMode('story'); storeMode('story'); });
    rawBtn.addEventListener('click', () => { applyMode('raw'); storeMode('raw'); });
    applyMode(storedMode() === 'raw' ? 'raw' : 'story');
  }
  const chapters = Array.from(document.querySelectorAll('section.chapter'));
  if (!chapters.length) return;

  // Reading time badge: ~450 characters a minute is a comfortable clip for this prose.
  chapters.forEach((chapter) => {
    const meta = chapter.querySelector('.chapter-meta');
    if (!meta || meta.querySelector('.read-time')) return;
    const chars = (chapter.textContent.match(/[\u4e00-\u9fff]/g) || []).length;
    const minutes = Math.max(1, Math.round(chars / 450));
    const badge = document.createElement('span');
    badge.className = 'read-time';
    badge.textContent = '\u7D04 ' + minutes + ' \u5206\u9418';
    meta.appendChild(badge);
  });

  // Reading progress: remember the chapter you are in, offer to resume on return.
  const CHAPTER_KEY = 'fun-tongjian-chapter';
  const readChapter = () => { try { return localStorage.getItem(CHAPTER_KEY); } catch { return null; } };
  const saveChapter = id => { try { localStorage.setItem(CHAPTER_KEY, id); } catch { /* no persistence */ } };
  const resumeId = readChapter();
  const resumeChapter = chapters.find(c => c.id === resumeId && c.id !== chapters[0].id);
  if (resumeChapter) {
    const head = document.querySelector('.book-head');
    if (head) {
      const pill = document.createElement('a');
      pill.className = 'resume-story';
      pill.href = '#' + resumeChapter.id;
      pill.textContent = '\u7E7C\u7E8C\u8B80 ' + resumeChapter.id.replace(/^ch-/, '') + ' \u00B7 ' +
        ((resumeChapter.querySelector('h2') || {}).textContent || '').slice(0, 18);
      head.appendChild(pill);
    }
  }
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
    saveChapter(id);
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
