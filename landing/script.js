(function () {
  "use strict";

  /* Scroll reveal */
  var revealEls = document.querySelectorAll(".reveal");
  if (revealEls.length && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
    );
    revealEls.forEach(function (el) { observer.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* Count-up */
  function animateCount(el) {
    var target = parseFloat(el.getAttribute("data-count"));
    if (isNaN(target)) return;
    var suffix = el.getAttribute("data-suffix") || "";
    var prefix = el.getAttribute("data-prefix") || "";
    var decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
    var duration = parseInt(el.getAttribute("data-duration") || "1400", 10);
    var start = 0;
    var startTime = null;

    function format(val) {
      if (decimals === 0) {
        return prefix + Math.round(val).toLocaleString("ru-RU") + suffix;
      }
      return prefix + val.toLocaleString("ru-RU", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      }) + suffix;
    }

    function step(ts) {
      if (!startTime) startTime = ts;
      var progress = Math.min((ts - startTime) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = format(start + (target - start) * eased);
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = format(target);
    }
    requestAnimationFrame(step);
  }

  var countEls = document.querySelectorAll("[data-count]");
  if (countEls.length && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var countObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animateCount(entry.target);
            countObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );
    countEls.forEach(function (el) { countObserver.observe(el); });
  } else {
    countEls.forEach(function (el) {
      var target = parseFloat(el.getAttribute("data-count"));
      var suffix = el.getAttribute("data-suffix") || "";
      var prefix = el.getAttribute("data-prefix") || "";
      var decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
      if (!isNaN(target)) {
        el.textContent = decimals === 0
          ? prefix + Math.round(target).toLocaleString("ru-RU") + suffix
          : prefix + target.toLocaleString("ru-RU", { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) + suffix;
      }
    });
  }

  /* Smooth scroll */
  var nav = document.querySelector(".site-nav");
  var navOffset = function () { return nav ? nav.offsetHeight + 8 : 0; };

  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function (e) {
      var id = link.getAttribute("href");
      if (!id || id.length <= 1) return;
      var target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      window.scrollTo({
        top: target.getBoundingClientRect().top + window.scrollY - navOffset(),
        behavior: "smooth"
      });
    });
  });

  /* Sticky nav active section */
  var navLinks = document.querySelectorAll(".site-nav__links a[data-section]");
  var sections = [];
  navLinks.forEach(function (link) {
    var id = link.getAttribute("data-section");
    var sec = document.getElementById(id);
    if (sec) sections.push({ id: id, el: sec, link: link });
  });

  if (sections.length) {
    var onScroll = function () {
      var pos = window.scrollY + navOffset() + 80;
      var current = sections[0];
      sections.forEach(function (s) {
        if (s.el.offsetTop <= pos) current = s;
      });
      navLinks.forEach(function (l) { l.classList.remove("is-active"); });
      if (current && current.link) current.link.classList.add("is-active");
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* Demo tab galleries */
  var demoTitles = {
    summary: "dashboard / summary",
    payments: "reports / payments",
    rvr: "reports / rvr-repeat · ai-check",
    chat: "ai-chat / sql-agent"
  };

  document.querySelectorAll("[data-demo-gallery]").forEach(function (gallery) {
    var tabs = gallery.querySelectorAll("[data-demo-tab]");
    var panels = gallery.querySelectorAll("[data-demo-panel]");
    var titleEl = document.getElementById("demo-frame-title");
    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        var key = tab.getAttribute("data-demo-tab");
        tabs.forEach(function (t) { t.classList.toggle("is-active", t === tab); });
        panels.forEach(function (p) {
          p.classList.toggle("is-active", p.getAttribute("data-demo-panel") === key);
        });
        if (titleEl && demoTitles[key]) titleEl.textContent = demoTitles[key];
      });
    });
  });

  /* Interactive traffic-light table */
  var trafficRows = document.querySelectorAll("[data-traffic-row]");
  var trafficDetail = document.getElementById("traffic-detail");
  var trafficData = {
    "vsp-north": "ВСП Северный: СКУД offline 1 сут. · NVR в норме · биотерминал OK",
    "vsp-center": "ВСП Центральный: температура HDD 56°C (warn) · 2 канала warn · СКУД OK",
    "office-tb": "Офис ТБ: архив 4 сут. (error) · HDD 63°C · 3 канала error · биотерминал offline",
    "kic": "КИЦ: все категории в норме · 8 каналов OK"
  };

  function selectTrafficRow(row) {
    trafficRows.forEach(function (r) { r.classList.remove("is-selected"); });
    row.classList.add("is-selected");
    if (trafficDetail) {
      var key = row.getAttribute("data-traffic-row");
      trafficDetail.textContent = trafficData[key] || "";
    }
  }

  trafficRows.forEach(function (row) {
    row.addEventListener("click", function () { selectTrafficRow(row); });
  });
  if (trafficRows.length) selectTrafficRow(trafficRows[0]);
})();
