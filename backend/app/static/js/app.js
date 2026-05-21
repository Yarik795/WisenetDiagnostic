const COLLAPSED_KEY = "wisenet-collapsed-objects";

function loadCollapsed() {
  try {
    const raw = localStorage.getItem(COLLAPSED_KEY);
    return raw ? new Set(JSON.parse(raw)) : new Set();
  } catch {
    return new Set();
  }
}

function saveCollapsed(set) {
  localStorage.setItem(COLLAPSED_KEY, JSON.stringify([...set]));
}

function applyCollapsedState() {
  const collapsed = loadCollapsed();
  document.querySelectorAll("[data-object-group]").forEach((el) => {
    const name = el.dataset.objectGroup;
    if (collapsed.has(name)) {
      el.classList.add("collapsed");
    } else {
      el.classList.remove("collapsed");
    }
  });
}

function setAllGroupsCollapsed(collapsedAll) {
  const collapsed = loadCollapsed();
  document.querySelectorAll("[data-object-group]").forEach((group) => {
    const name = group.dataset.objectGroup;
    if (!name) return;
    if (collapsedAll) {
      collapsed.add(name);
      group.classList.add("collapsed");
    } else {
      collapsed.delete(name);
      group.classList.remove("collapsed");
    }
  });
  saveCollapsed(collapsed);
}

function toggleObjectGroup(group) {
  const name = group.dataset.objectGroup;
  if (!name) return;
  const collapsed = loadCollapsed();
  if (collapsed.has(name)) {
    collapsed.delete(name);
  } else {
    collapsed.add(name);
  }
  saveCollapsed(collapsed);
  group.classList.toggle("collapsed");
}

function initGroupToggles() {
  document.body.addEventListener("click", (e) => {
    const header = e.target.closest("[data-toggle-group]");
    if (!header) return;
    const group = header.closest("[data-object-group]");
    if (!group) return;
    toggleObjectGroup(group);
  });

  document.body.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    const header = e.target.closest("[data-toggle-group]");
    if (!header) return;
    e.preventDefault();
    const group = header.closest("[data-object-group]");
    if (!group) return;
    toggleObjectGroup(group);
  });

  const collapseAllBtn = document.getElementById("objects-collapse-all");
  const expandAllBtn = document.getElementById("objects-expand-all");
  if (collapseAllBtn) {
    collapseAllBtn.addEventListener("click", () => setAllGroupsCollapsed(true));
  }
  if (expandAllBtn) {
    expandAllBtn.addEventListener("click", () => setAllGroupsCollapsed(false));
  }
}

function initMobileSidebar() {
  const btn = document.getElementById("mobile-menu-btn");
  const sidebar = document.getElementById("sidebar");
  if (!btn || !sidebar) return;
  btn.addEventListener("click", () => sidebar.classList.toggle("open"));
  document.addEventListener("click", (e) => {
    if (
      sidebar.classList.contains("open") &&
      !sidebar.contains(e.target) &&
      e.target !== btn
    ) {
      sidebar.classList.remove("open");
    }
  });
}

function initClientSearch() {
  const input = document.getElementById("objects-search");
  if (!input) return;
  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    document.querySelectorAll("[data-object-group]").forEach((group) => {
      let visible = false;
      group.querySelectorAll("[data-recorder-row]").forEach((row) => {
        const text = (row.dataset.searchText || "").toLowerCase();
        const match = !q || text.includes(q);
        row.style.display = match ? "" : "none";
        if (match) visible = true;
      });
      const title = (group.dataset.objectGroup || "").toLowerCase();
      if (!q || title.includes(q)) visible = true;
      group.style.display = visible ? "" : "none";
    });
  });
}

function initHighlightObject() {
  const params = new URLSearchParams(window.location.search);
  const obj = params.get("object");
  if (!obj) return;
  const collapsed = loadCollapsed();
  collapsed.delete(obj);
  saveCollapsed(collapsed);
  const group = document.querySelector(
    `[data-object-group="${CSS.escape(obj)}"]`
  );
  if (group) {
    group.classList.remove("collapsed");
    group.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (typeof htmx === "undefined") {
    showToast(
      "error",
      "Не загружен HTMX — кнопки «Проверить» и формы не работают. Обновите страницу или переустановите приложение."
    );
    console.error("[wisenet] htmx is undefined — проверьте /static/js/htmx.min.js");
  }
  applyCollapsedState();
  initGroupToggles();
  initMobileSidebar();
  initClientSearch();
  initHighlightObject();
});

document.body.addEventListener("htmx:afterSwap", () => {
  applyCollapsedState();
});

function showToast(type, message) {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => el.remove(), 5000);
}

document.body.addEventListener("showToast", (e) => {
  const detail = e.detail;
  if (detail && detail.type && detail.message) {
    showToast(detail.type, detail.message);
  }
});

function logHtmxClient(eventName, detail) {
  const payload = {
    ts: new Date().toISOString(),
    source: "browser",
    event: eventName,
    path: detail?.pathInfo?.requestPath || detail?.requestConfig?.path,
    status: detail?.xhr?.status,
    error: detail?.error,
  };
  console.info("[wisenet]", JSON.stringify(payload));
}

document.body.addEventListener("htmx:sendError", (e) => logHtmxClient("htmx_send_error", e.detail));
document.body.addEventListener("htmx:responseError", (e) =>
  logHtmxClient("htmx_response_error", e.detail)
);
document.body.addEventListener("htmx:swapError", (e) => logHtmxClient("htmx_swap_error", e.detail));
