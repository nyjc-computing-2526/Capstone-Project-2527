(() => {
  const defaultCollapseMedia = '(max-width: 760px)';
  const headers = Array.from(document.querySelectorAll('header[data-nav-profile]')).filter((header) => {
    return header.querySelector('.nav-menu-toggle') && header.querySelector('.nav-panel');
  });
  if (!headers.length) return;

  const controllers = headers.map((header) => {
    const collapseQuery = window.matchMedia(header.dataset.navCollapseMedia || defaultCollapseMedia);
    const button = header.querySelector('.nav-menu-toggle');
    const label = header.querySelector('.nav-menu-toggle-text');
    const panel = header.querySelector('.nav-panel');
    return { header, button, label, panel, collapseQuery };
  });

  const applyState = ({ header, button, label, panel, collapseQuery }) => {
    if (!button || !label || !panel) return;

    const isOpen = () => header.getAttribute('data-menu-open') === 'true';
    const onMobile = collapseQuery.matches;
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

  controllers.forEach(({ header, button, panel, collapseQuery }) => {
    const isOpen = () => header.getAttribute('data-menu-open') === 'true';

    button.addEventListener('click', () => {
      if (!collapseQuery.matches) return;
      header.setAttribute('data-menu-open', isOpen() ? 'false' : 'true');
      applyState({
        header,
        button,
        label: header.querySelector('.nav-menu-toggle-text'),
        panel,
        collapseQuery,
      });
    });

    panel.querySelectorAll('a[href]').forEach((link) => {
      link.addEventListener('click', () => {
        if (!collapseQuery.matches) return;
        header.setAttribute('data-menu-open', 'false');
        applyState({
          header,
          button,
          label: header.querySelector('.nav-menu-toggle-text'),
          panel,
          collapseQuery,
        });
      });
    });
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;

    controllers.forEach(({ header, button, panel, collapseQuery }) => {
      if (!collapseQuery.matches) return;
      if (header.getAttribute('data-menu-open') !== 'true') return;
      header.setAttribute('data-menu-open', 'false');
      applyState({
        header,
        button,
        label: header.querySelector('.nav-menu-toggle-text'),
        panel,
        collapseQuery,
      });
      button.focus();
    });
  });

  controllers.forEach((controller) => {
    const onChange = () => applyState(controller);
    if (typeof controller.collapseQuery.addEventListener === 'function') {
      controller.collapseQuery.addEventListener('change', onChange);
    } else {
      controller.collapseQuery.addListener(onChange);
    }
  });

  controllers.forEach(applyState);
})();
