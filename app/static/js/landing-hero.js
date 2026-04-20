(() => {
  const page = document.querySelector('.landing-home');
  if (!page) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const revealNodes = page.querySelectorAll('[data-reveal]');

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
    { rootMargin: '0px 0px -12% 0px', threshold: 0.2 },
  );

  revealNodes.forEach((node) => observer.observe(node));
})();
