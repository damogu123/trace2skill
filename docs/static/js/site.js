(() => {
  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('#nav-links');

  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', String(isOpen));
    });

    navLinks.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        navLinks.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  const copyButton = document.querySelector('.copy-button');
  if (copyButton) {
    copyButton.addEventListener('click', async () => {
      const targetId = copyButton.dataset.copyTarget;
      const target = targetId ? document.getElementById(targetId) : null;
      if (!target) return;

      const text = target.textContent.trim();
      try {
        await navigator.clipboard.writeText(text);
      } catch (_) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.setAttribute('readonly', '');
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
      }

      const label = copyButton.querySelector('.copy-label');
      if (label) label.textContent = '已复制';
      copyButton.classList.add('copied');
      window.setTimeout(() => {
        if (label) label.textContent = '复制 BibTeX';
        copyButton.classList.remove('copied');
      }, 1800);
    });
  }

})();
