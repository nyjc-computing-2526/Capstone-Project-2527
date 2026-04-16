(() => {
  const header = document.querySelector('header[data-nav-profile="landing"]');
  if (!header) return;

  const button = header.querySelector('.nav-menu-toggle');
  const label = header.querySelector('.nav-menu-toggle-text');
  const panel = header.querySelector('.nav-panel');
  if (!button || !label || !panel) return;

  const mobileQuery = window.matchMedia('(max-width: 760px)');

  const isOpen = () => header.getAttribute('data-menu-open') === 'true';

  const applyState = () => {
    const onMobile = mobileQuery.matches;
    header.setAttribute('data-nav-enhanced', 'true');
    button.hidden = !onMobile;

    if (!onMobile) {
      header.removeAttribute('data-menu-open');
      panel.hidden = false;
      button.setAttribute('aria-expanded', 'false');
      button.setAttribute('aria-label', 'Open navigation menu');
      label.textContent = 'Menu';
      return;
    }

    const open = isOpen();
    panel.hidden = !open;
    button.setAttribute('aria-expanded', String(open));
    button.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    label.textContent = open ? 'Close' : 'Menu';
  };

  button.addEventListener('click', () => {
    if (!mobileQuery.matches) return;
    header.setAttribute('data-menu-open', isOpen() ? 'false' : 'true');
    applyState();
  });

  panel.querySelectorAll('a[href]').forEach((link) => {
    link.addEventListener('click', () => {
      if (!mobileQuery.matches) return;
      header.setAttribute('data-menu-open', 'false');
      applyState();
    });
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || !mobileQuery.matches || !isOpen()) return;
    header.setAttribute('data-menu-open', 'false');
    applyState();
    button.focus();
  });

  if (typeof mobileQuery.addEventListener === 'function') {
    mobileQuery.addEventListener('change', applyState);
  } else {
    mobileQuery.addListener(applyState);
  }

  applyState();
})();
