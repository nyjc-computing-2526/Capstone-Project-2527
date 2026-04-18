(function () {
  var STORAGE_KEY = "navHighlightGeometry";

  function readStored() {
    try {
      var raw = sessionStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      var o = JSON.parse(raw);
      if (
        !o ||
        typeof o.profile !== "string" ||
        typeof o.left !== "number" ||
        typeof o.top !== "number" ||
        typeof o.width !== "number" ||
        typeof o.height !== "number"
      ) {
        return null;
      }
      return o;
    } catch (_) {
      return null;
    }
  }

  function writeStored(profile, geom) {
    try {
      sessionStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          profile: profile,
          left: geom.left,
          top: geom.top,
          width: geom.width,
          height: geom.height,
        })
      );
    } catch (_) {}
  }

  function geometry(shell, el) {
    var sr = shell.getBoundingClientRect();
    var ar = el.getBoundingClientRect();
    var underlineHeight = 2;
    return {
      left: ar.left - sr.left + shell.scrollLeft,
      top: ar.bottom - sr.top + shell.scrollTop - underlineHeight,
      width: ar.width,
      height: underlineHeight,
    };
  }

  function paint(pill, g, instant) {
    if (instant) pill.classList.add("nav-highlight-pill--no-transition");
    pill.style.left = g.left + "px";
    pill.style.top = g.top + "px";
    pill.style.width = g.width + "px";
    pill.style.height = g.height + "px";
    if (instant) {
      void pill.offsetWidth;
      pill.classList.remove("nav-highlight-pill--no-transition");
    }
  }

  function init() {
    var header = document.querySelector("header[data-nav-profile]");
    if (!header) return;

    var shell = header.querySelector(".nav-primary");
    var pill = header.querySelector(".nav-highlight-pill");
    if (!shell || !pill) return;

    var profile = header.getAttribute("data-nav-profile");
    var active = shell.querySelector("a.nav-active");

    if (!active) {
      pill.style.opacity = "0";
      return;
    }

    document.documentElement.classList.add("nav-highlight-prepared");

    var target = geometry(shell, active);
    var stored = readStored();
    var canAnimate =
      stored &&
      stored.profile === profile &&
      stored.width > 0 &&
      stored.height > 0;

    pill.style.opacity = "1";

    if (canAnimate) {
      paint(pill, stored, true);
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          paint(pill, target, false);
        });
      });
    } else {
      paint(pill, target, true);
    }

    shell.querySelectorAll("ul a[href]").forEach(function (a) {
      a.addEventListener("click", function () {
        var cur = shell.querySelector("a.nav-active");
        if (!cur) return;
        writeStored(profile, geometry(shell, cur));
      });
    });

    window.addEventListener("resize", function () {
      var cur = shell.querySelector("a.nav-active");
      if (!cur) return;
      paint(pill, geometry(shell, cur), true);
    });

    window.addEventListener("pageshow", function (ev) {
      if (!ev.persisted) return;
      var cur = shell.querySelector("a.nav-active");
      if (!cur) return;
      paint(pill, geometry(shell, cur), true);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
