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

(() => {
  const slideshow = document.querySelector('.features-slideshow');
  if (!slideshow) return;

  const track = slideshow.querySelector('[data-feature-track]');
  const slides = Array.from(slideshow.querySelectorAll('[data-feature-slide]'));
  const dotsRoot = slideshow.querySelector('[data-feature-dots]');
  const prevButton = slideshow.querySelector('[data-feature-prev]');
  const nextButton = slideshow.querySelector('[data-feature-next]');
  if (!track || !slides.length || !dotsRoot || !prevButton || !nextButton) return;

  let activeIndex = Math.max(
    0,
    slides.findIndex((slide) => slide.classList.contains('is-active')),
  );

  const dots = slides.map((_, index) => {
    const dot = document.createElement('button');
    dot.type = 'button';
    dot.className = 'slideshow-dot';
    dot.setAttribute('aria-label', `Go to feature ${index + 1}`);
    dot.addEventListener('click', () => setActiveSlide(index));
    dotsRoot.appendChild(dot);
    return dot;
  });

  function setActiveSlide(index) {
    activeIndex = (index + slides.length) % slides.length;
    slides.forEach((slide, slideIndex) => {
      const isActive = slideIndex === activeIndex;
      slide.classList.toggle('is-active', isActive);
      slide.setAttribute('aria-hidden', isActive ? 'false' : 'true');
    });
    dots.forEach((dot, dotIndex) => {
      const isActive = dotIndex === activeIndex;
      dot.classList.toggle('is-active', isActive);
      dot.setAttribute('aria-current', isActive ? 'true' : 'false');
    });
  }

  prevButton.addEventListener('click', () => setActiveSlide(activeIndex - 1));
  nextButton.addEventListener('click', () => setActiveSlide(activeIndex + 1));

  slideshow.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') {
      event.preventDefault();
      setActiveSlide(activeIndex - 1);
    }
    if (event.key === 'ArrowRight') {
      event.preventDefault();
      setActiveSlide(activeIndex + 1);
    }
  });

  setActiveSlide(activeIndex);
})();
