(() => {
  function moveHighlight(nav, targetLink, immediate = false) {
    if (!nav || !targetLink) return;
    const highlight = nav.querySelector(".organizer-tab-highlight");
    if (!highlight) return;

    const linksWrap = nav.querySelector(".organizer-tab-links");
    if (!linksWrap) return;

    const wrapRect = linksWrap.getBoundingClientRect();
    const targetRect = targetLink.getBoundingClientRect();
    const computed = window.getComputedStyle(linksWrap);
    const isRow = computed.flexDirection.startsWith("row");
    const top = targetRect.top - wrapRect.top + linksWrap.scrollTop;
    const left = targetRect.left - wrapRect.left + linksWrap.scrollLeft;

    if (immediate) {
      highlight.style.transition = "none";
      highlight.style.transform = isRow ? `translateX(${left}px)` : `translateY(${top}px)`;
      highlight.style.right = isRow ? "auto" : "0";
      highlight.style.width = isRow ? `${targetRect.width}px` : "100%";
      highlight.style.height = `${targetRect.height}px`;
      requestAnimationFrame(() => {
        highlight.style.transition = "";
      });
      return;
    }

    highlight.style.transform = isRow ? `translateX(${left}px)` : `translateY(${top}px)`;
    highlight.style.right = isRow ? "auto" : "0";
    highlight.style.width = isRow ? `${targetRect.width}px` : "100%";
    highlight.style.height = `${targetRect.height}px`;
  }

  function initNav(nav) {
    const links = Array.from(nav.querySelectorAll(".organizer-tab-link"));
    if (!links.length) return;

    const active = nav.querySelector(".organizer-tab-link.is-active") || links[0];
    moveHighlight(nav, active);

    links.forEach((link, index) => {
      link.addEventListener("mouseenter", () => moveHighlight(nav, link));
      link.addEventListener("focus", () => moveHighlight(nav, link));
      link.addEventListener("click", () => {
        sessionStorage.setItem("organizer_tab_index", String(index));
      });
    });

    nav.addEventListener("mouseleave", () => moveHighlight(nav, active));
    nav.addEventListener("focusout", (event) => {
      if (!nav.contains(event.relatedTarget)) {
        moveHighlight(nav, active);
      }
    });

    const previousIndex = Number(sessionStorage.getItem("organizer_tab_index"));
    if (!Number.isNaN(previousIndex) && previousIndex >= 0 && previousIndex < links.length) {
      const previousLink = links[previousIndex];
      moveHighlight(nav, previousLink, true);
      requestAnimationFrame(() => moveHighlight(nav, active));
    }
  }

  window.addEventListener("DOMContentLoaded", () => {
    const navs = document.querySelectorAll("[data-organizer-tabs]");
    navs.forEach(initNav);
    window.addEventListener("resize", () => {
      navs.forEach((nav) => {
        const active = nav.querySelector(".organizer-tab-link.is-active");
        moveHighlight(nav, active);
      });
    });
  });
})();
