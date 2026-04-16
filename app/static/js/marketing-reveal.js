(() => {
  const page = document.querySelector('.about-main, .features-main, .contact-main');
  if (!page) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const revealNodes = page.querySelectorAll('[data-marketing-reveal]');

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
    { rootMargin: '0px 0px -10% 0px', threshold: 0.18 },
  );

  revealNodes.forEach((node) => observer.observe(node));
})();
