(() => {
  const marketingPage = document.querySelector('.about-main, .features-main, .contact-main, .legal-main');
  const appPageMain = document.querySelector('.app-hero-page main');
  const page = marketingPage || appPageMain;
  if (!page) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (appPageMain) {
    const autoRevealTargets = appPageMain.querySelectorAll(
      '.top-section, .activity-controls, .my-activities-column, .hero, .main-card, .participants-card, .activity-card-link, .activity-control, .p-item, .input-group, .input-row, h1, h2, h3, form button, .muted-text'
    );
    autoRevealTargets.forEach((node, index) => {
      if (node.hasAttribute('data-marketing-reveal')) return;
      node.setAttribute('data-marketing-reveal', '');
      node.style.setProperty('--reveal-delay', `${Math.min(index * 35, 280)}ms`);
    });
  }

  const revealNodes = page.querySelectorAll('[data-marketing-reveal]');
  if (!revealNodes.length) return;

  revealNodes.forEach((node) => {
    const delay = node.getAttribute('data-reveal-delay');
    if (delay) {
      node.style.setProperty('--reveal-delay', delay);
    }
  });

  const revealAll = () => {
    revealNodes.forEach((node) => node.classList.add('is-visible'));
  };

  if (reduceMotion || !('IntersectionObserver' in window)) {
    revealAll();
    return;
  }

  const observer = new IntersectionObserver(
    (entries, observerInstance) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observerInstance.unobserve(entry.target);
      });
    },
    { rootMargin: '0px 0px -6% 0px', threshold: 0.05 },
  );

  revealNodes.forEach((node) => observer.observe(node));
})();
