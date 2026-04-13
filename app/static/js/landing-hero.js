(() => {
  const page = document.querySelector(".landing-page");
  if (!page) return;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const revealNodes = page.querySelectorAll("[data-reveal]");
  const mediaShell = page.querySelector(".hero-image-shell");
  const heroImage = page.querySelector(".hero-image");

  const revealAll = () => {
    revealNodes.forEach((node) => node.classList.add("is-visible"));
  };

  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealAll();
  } else {
    const observer = new IntersectionObserver(
      (entries, observerInstance) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observerInstance.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -12% 0px", threshold: 0.2 },
    );

    revealNodes.forEach((node) => observer.observe(node));
  }

  if (reduceMotion || !mediaShell || !heroImage) return;

  const setTilt = (x, y) => {
    mediaShell.style.transform = `rotateX(${y}deg) rotateY(${x}deg)`;
  };

  mediaShell.addEventListener("mousemove", (event) => {
    const box = mediaShell.getBoundingClientRect();
    const x = ((event.clientX - box.left) / box.width - 0.5) * 5;
    const y = ((event.clientY - box.top) / box.height - 0.5) * -5;
    setTilt(x, y);
  });

  mediaShell.addEventListener("mouseleave", () => {
    setTilt(0, 0);
  });

  let ticking = false;
  const updateDrift = () => {
    const drift = Math.min(window.scrollY * 0.07, 16);
    heroImage.style.setProperty("--hero-drift", `${drift}px`);
    ticking = false;
  };

  window.addEventListener(
    "scroll",
    () => {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(updateDrift);
    },
    { passive: true },
  );
})();
