(() => {
  const headers = Array.from(document.querySelectorAll('header[data-nav-profile]')).filter((header) => {
    return header.querySelector('.nav-menu-toggle') && header.querySelector('.nav-panel');
  });
  if (!headers.length) return;

  const mobileQuery = window.matchMedia('(max-width: 760px)');
  const controllers = headers.map((header) => {
    const button = header.querySelector('.nav-menu-toggle');
    const label = header.querySelector('.nav-menu-toggle-text');
    const panel = header.querySelector('.nav-panel');
    return { header, button, label, panel };
  });

  const applyState = ({ header, button, label, panel }) => {
    if (!button || !label || !panel) return;

    const isOpen = () => header.getAttribute('data-menu-open') === 'true';
    const onMobile = mobileQuery.matches;
    const open = onMobile && isOpen();

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

    panel.hidden = !open;
    button.setAttribute('aria-expanded', String(open));
    button.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    label.textContent = open ? 'Close' : 'Menu';
  };

  controllers.forEach(({ header, button, panel }) => {
    const isOpen = () => header.getAttribute('data-menu-open') === 'true';

    button.addEventListener('click', () => {
      if (!mobileQuery.matches) return;
      header.setAttribute('data-menu-open', isOpen() ? 'false' : 'true');
      applyState({ header, button, label: header.querySelector('.nav-menu-toggle-text'), panel });
    });

    panel.querySelectorAll('a[href]').forEach((link) => {
      link.addEventListener('click', () => {
        if (!mobileQuery.matches) return;
        header.setAttribute('data-menu-open', 'false');
        applyState({ header, button, label: header.querySelector('.nav-menu-toggle-text'), panel });
      });
    });
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || !mobileQuery.matches) return;

    controllers.forEach(({ header, button, panel }) => {
      if (header.getAttribute('data-menu-open') !== 'true') return;
      header.setAttribute('data-menu-open', 'false');
      applyState({ header, button, label: header.querySelector('.nav-menu-toggle-text'), panel });
      button.focus();
    });
  });

  if (typeof mobileQuery.addEventListener === 'function') {
    mobileQuery.addEventListener('change', () => {
      controllers.forEach(applyState);
    });
  } else {
    mobileQuery.addListener(() => {
      controllers.forEach(applyState);
    });
  }

  controllers.forEach(applyState);
})();
