const COLLAPSED_KEY = "wisenet-collapsed-objects";
const TIME_DASHBOARD_COLLAPSED_KEY = "wisenet-time-dashboard-collapsed";
const CATEGORY_DASHBOARD_COLLAPSED_PREFIX = "wisenet-category-dashboard-collapsed:";

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

function findObjectGroup(name) {
  if (!name) return null;
  for (const el of document.querySelectorAll("[data-object-group]")) {
    if (el.getAttribute("data-object-group") === name) {
      return el;
    }
  }
  return null;
}

let objectDeepLinkScrolledKey = null;

function getObjectDeepLinkKey() {
  const params = new URLSearchParams(window.location.search);
  const obj = params.get("object");
  const hash = window.location.hash;
  if (!obj && !(hash && hash.startsWith("#recorder-row-"))) {
    return null;
  }
  return `${obj || ""}|${hash}`;
}

function applyObjectDeepLinkFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const obj = params.get("object");
  if (!obj) return;
  const collapsed = loadCollapsed();
  collapsed.delete(obj);
  saveCollapsed(collapsed);
  const group = findObjectGroup(obj);
  if (group) {
    group.classList.remove("collapsed");
  }
}

function scrollToObjectDeepLinkOnce() {
  const key = getObjectDeepLinkKey();
  if (!key || key === objectDeepLinkScrolledKey) return;
  objectDeepLinkScrolledKey = key;

  const hash = window.location.hash;
  if (hash && hash.startsWith("#recorder-row-")) {
    const row = document.querySelector(hash);
    if (row) {
      row.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
  }

  const obj = new URLSearchParams(window.location.search).get("object");
  if (obj) {
    const group = findObjectGroup(obj);
    if (group) {
      group.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }
}

function getTimeDashboardCollapsedPreference() {
  try {
    const raw = localStorage.getItem(TIME_DASHBOARD_COLLAPSED_KEY);
    if (raw === null) return null;
    return raw === "1";
  } catch {
    return null;
  }
}

function saveTimeDashboardCollapsed(collapsed) {
  localStorage.setItem(TIME_DASHBOARD_COLLAPSED_KEY, collapsed ? "1" : "0");
}

function applyTimeDashboardState(root) {
  const el = root || document.querySelector("[data-time-dashboard]");
  if (!el) return;
  const defaultExpanded = el.dataset.defaultExpanded === "true";
  const pref = getTimeDashboardCollapsedPreference();
  const collapsed = pref !== null ? pref : !defaultExpanded;
  if (collapsed) {
    el.classList.add("collapsed");
    const body = el.querySelector(".time-dashboard-body");
    if (body) body.classList.add("time-dashboard-body--collapsed");
    const header = el.querySelector(".time-dashboard-header");
    if (header) header.setAttribute("aria-expanded", "false");
  } else {
    el.classList.remove("collapsed");
    const body = el.querySelector(".time-dashboard-body");
    if (body) body.classList.remove("time-dashboard-body--collapsed");
    const header = el.querySelector(".time-dashboard-header");
    if (header) header.setAttribute("aria-expanded", "true");
  }
}

function toggleTimeDashboard(dashboard) {
  const collapsed = !dashboard.classList.contains("collapsed");
  dashboard.classList.toggle("collapsed", collapsed);
  const body = dashboard.querySelector(".time-dashboard-body");
  if (body) body.classList.toggle("time-dashboard-body--collapsed", collapsed);
  const header = dashboard.querySelector(".time-dashboard-header");
  if (header) header.setAttribute("aria-expanded", collapsed ? "false" : "true");
  saveTimeDashboardCollapsed(collapsed);
}

function categoryDashboardStorageKey(category) {
  return `${CATEGORY_DASHBOARD_COLLAPSED_PREFIX}${category}`;
}

function getCategoryDashboardCollapsedPreference(category) {
  try {
    const raw = localStorage.getItem(categoryDashboardStorageKey(category));
    if (raw === null) return null;
    return raw === "1";
  } catch {
    return null;
  }
}

function saveCategoryDashboardCollapsed(category, collapsed) {
  localStorage.setItem(categoryDashboardStorageKey(category), collapsed ? "1" : "0");
}

function applyCategoryDashboardState(root) {
  const nodes = root
    ? root.querySelectorAll("[data-category-dashboard]")
    : document.querySelectorAll("[data-category-dashboard]");
  nodes.forEach((el) => {
    const category = el.dataset.categoryDashboard;
    if (!category) return;
    const defaultExpanded = el.dataset.defaultExpanded === "true";
    const pref = getCategoryDashboardCollapsedPreference(category);
    const collapsed = pref !== null ? pref : !defaultExpanded;
    const body = el.querySelector(".time-dashboard-body");
    const header = el.querySelector(".time-dashboard-header");
    el.classList.toggle("collapsed", collapsed);
    if (body) body.classList.toggle("time-dashboard-body--collapsed", collapsed);
    if (header) header.setAttribute("aria-expanded", collapsed ? "false" : "true");
  });
}

function toggleCategoryDashboard(dashboard) {
  const category = dashboard.dataset.categoryDashboard;
  const collapsed = !dashboard.classList.contains("collapsed");
  dashboard.classList.toggle("collapsed", collapsed);
  const body = dashboard.querySelector(".time-dashboard-body");
  if (body) body.classList.toggle("time-dashboard-body--collapsed", collapsed);
  const header = dashboard.querySelector(".time-dashboard-header");
  if (header) header.setAttribute("aria-expanded", collapsed ? "false" : "true");
  if (category) saveCategoryDashboardCollapsed(category, collapsed);
}

function initCategoryDashboards() {
  applyCategoryDashboardState();
  document.body.addEventListener("click", (e) => {
    const header = e.target.closest("[data-toggle-category-dashboard]");
    if (!header) return;
    if (e.target.closest(".time-dashboard-actions")) return;
    const dash = header.closest("[data-category-dashboard]");
    if (dash) toggleCategoryDashboard(dash);
  });
  document.body.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    const header = e.target.closest("[data-toggle-category-dashboard]");
    if (!header) return;
    e.preventDefault();
    const dash = header.closest("[data-category-dashboard]");
    if (dash) toggleCategoryDashboard(dash);
  });
}

function scrollToHighlightedCategory() {
  const highlighted = document.querySelector(".category-dashboard--highlight");
  if (highlighted) {
    highlighted.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function initTimeDashboard() {
  applyTimeDashboardState();
  applyCategoryDashboardState();
  document.body.addEventListener("click", (e) => {
    const header = e.target.closest("[data-toggle-time-dashboard]");
    if (!header) return;
    if (e.target.closest(".time-dashboard-actions")) return;
    const dash = header.closest("[data-time-dashboard]");
    if (dash) toggleTimeDashboard(dash);
  });
  document.body.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    const header = e.target.closest("[data-toggle-time-dashboard]");
    if (!header) return;
    e.preventDefault();
    const dash = header.closest("[data-time-dashboard]");
    if (dash) toggleTimeDashboard(dash);
  });
}

function initServerToasts() {
  document.querySelectorAll("#toast-container .toast").forEach((el) => {
    setTimeout(() => el.remove(), 5000);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initServerToasts();
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
  applyObjectDeepLinkFromUrl();
  scrollToObjectDeepLinkOnce();
  initTimeDashboard();
  initCategoryDashboards();
  scrollToHighlightedCategory();
});

document.body.addEventListener("htmx:afterSwap", () => {
  applyCollapsedState();
  applyObjectDeepLinkFromUrl();
  applyTimeDashboardState();
  applyCategoryDashboardState();
  scrollToHighlightedCategory();
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

document.body.addEventListener("htmx:sendError", (e) => {
  logHtmxClient("htmx_send_error", e.detail);
  if (e.detail?.requestConfig?.path === "/objects/sync-cmdb") {
    showToast("error", "Нет связи с сервером при обновлении из CMDB.");
  }
});
document.body.addEventListener("htmx:responseError", (e) => {
  logHtmxClient("htmx_response_error", e.detail);
  if (e.detail?.requestConfig?.path === "/objects/sync-cmdb") {
    showToast("error", "Не удалось обновить список из CMDB. Проверьте cmdb.xlsx и логи.");
  }
});
document.body.addEventListener("htmx:swapError", (e) => logHtmxClient("htmx_swap_error", e.detail));
