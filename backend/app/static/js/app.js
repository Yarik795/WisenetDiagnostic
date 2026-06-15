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

function initKindTabs(root) {
  const scope = root || document;
  scope.querySelectorAll("[data-kind-tabs]").forEach((tabsNav) => {
    const group = tabsNav.closest("[data-object-group]");
    if (!group) return;
    tabsNav.querySelectorAll("[data-kind-tab]").forEach((btn) => {
      if (btn.dataset.kindTabBound === "1") return;
      btn.dataset.kindTabBound = "1";
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const kind = btn.dataset.kindTab;
        if (!kind) return;
        tabsNav.querySelectorAll("[data-kind-tab]").forEach((b) => {
          b.classList.toggle("active", b === btn);
        });
        group.querySelectorAll("[data-kind-panel]").forEach((panel) => {
          const active = panel.dataset.kindPanel === kind;
          panel.hidden = !active;
          panel.classList.toggle("active", active);
        });
      });
    });
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

function initPaymentsTabs(root) {
  const scope = root || document;
  scope.querySelectorAll("[data-payments-tabs]").forEach((tabsNav) => {
    if (tabsNav.dataset.paymentsTabsBound === "1") return;
    tabsNav.dataset.paymentsTabsBound = "1";
    const container = tabsNav.parentElement;
    if (!container) return;
    tabsNav.querySelectorAll("[data-payments-tab]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const kind = btn.dataset.paymentsTab;
        tabsNav.querySelectorAll("[data-payments-tab]").forEach((b) => {
          b.classList.toggle("active", b === btn);
        });
        container.querySelectorAll("[data-payments-panel]").forEach((panel) => {
          panel.classList.toggle("hidden", panel.dataset.paymentsPanel !== kind);
        });
        resizePaymentsCharts();
      });
    });
  });
}

function initPaymentsCollapsibles(root) {
  const scope = root || document;
  scope.querySelectorAll("[data-payments-collapsible]").forEach((block) => {
    const trigger = block.querySelector("[data-payments-collapse-trigger]");
    if (!trigger || trigger.dataset.paymentsCollapseBound === "1") return;
    trigger.dataset.paymentsCollapseBound = "1";
    trigger.addEventListener("click", () => {
      block.classList.toggle("is-open");
      const indicator = block.querySelector(".payments-collapsible-indicator");
      if (indicator) {
        indicator.textContent = block.classList.contains("is-open") ? "−" : "+";
      }
    });
  });
}

function parsePaymentsNumber(txt) {
  if (!txt) return null;
  const cleaned = txt.replace(/\s/g, "").replace(",", ".").trim();
  const num = parseFloat(cleaned);
  return Number.isNaN(num) ? null : num;
}

function initPaymentsTables(root) {
  const scope = root || document;
  scope.querySelectorAll(".payments-data-table").forEach((table) => {
    if (table.dataset.paymentsTableBound === "1") return;
    table.dataset.paymentsTableBound = "1";
    const tableId = table.dataset.paymentsTable;
    const search = scope.querySelector(`[data-payments-search="${tableId}"]`);
    if (search) {
      search.addEventListener("input", () => {
        const q = search.value.trim().toLowerCase();
        table.querySelectorAll("tbody tr").forEach((row) => {
          const filterOk = row.dataset.filterHidden !== "1";
          const searchOk = !q || row.textContent.toLowerCase().includes(q);
          row.style.display = filterOk && searchOk ? "" : "none";
        });
      });
    }
    table.querySelectorAll("thead th").forEach((th, colIdx) => {
      th.style.cursor = "pointer";
      th.addEventListener("click", () => {
        const tbody = table.querySelector("tbody");
        if (!tbody) return;
        const asc = th.dataset.sortDir !== "desc";
        const rows = Array.from(tbody.querySelectorAll("tr"));
        rows.sort((a, b) => {
          const cellA = a.cells[colIdx]?.textContent.trim() || "";
          const cellB = b.cells[colIdx]?.textContent.trim() || "";
          const numA = parsePaymentsNumber(cellA);
          const numB = parsePaymentsNumber(cellB);
          let valA = numA !== null ? numA : cellA.toLowerCase();
          let valB = numB !== null ? numB : cellB.toLowerCase();
          if (valA < valB) return asc ? -1 : 1;
          if (valA > valB) return asc ? 1 : -1;
          return 0;
        });
        th.dataset.sortDir = asc ? "asc" : "desc";
        rows.forEach((row) => tbody.appendChild(row));
      });
    });
  });
}

const paymentsChartStore = new Map();

function formatPaymentsRub(value) {
  return new Intl.NumberFormat("ru-RU", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function parsePaymentsSeriesScript(el) {
  try {
    return JSON.parse(el.textContent);
  } catch (err) {
    console.error("[wisenet] payments series JSON parse error", err);
    return { months: [], parties: [], matrix: {}, party_totals: {}, colors: {} };
  }
}

function getMultiSelectValues(select) {
  if (!select) return [];
  return Array.from(select.selectedOptions).map((opt) => opt.value);
}

function filterPaymentsSeries(series, months, parties) {
  const monthSet = new Set(months);
  const partySet = new Set(parties);
  const filteredMonths = series.months.filter((month) => monthSet.has(month));
  const filteredParties = series.parties.filter((party) => partySet.has(party));
  const matrix = {};
  filteredParties.forEach((party) => {
    matrix[party] = filteredMonths.map((month) => {
      const idx = series.months.indexOf(month);
      return idx >= 0 && series.matrix[party] ? series.matrix[party][idx] || 0 : 0;
    });
  });
  const partyTotals = {};
  filteredParties.forEach((party) => {
    partyTotals[party] = (matrix[party] || []).reduce((sum, val) => sum + val, 0);
  });
  return {
    months: filteredMonths,
    parties: filteredParties,
    matrix,
    party_totals: partyTotals,
    colors: series.colors || {},
  };
}

function paymentsBarOption(data) {
  const textColor = "#e8eaed";
  const axisColor = "#9aa0a6";
  const gridColor = "#2d323c";
  if (!data.months.length || !data.parties.length) {
    return {
      backgroundColor: "transparent",
      title: {
        text: "Нет данных",
        left: "center",
        top: "middle",
        textStyle: { color: axisColor, fontSize: 14, fontWeight: 400 },
      },
    };
  }
  return {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter(params) {
        if (!params?.length) return "";
        const month = params[0].axisValue;
        let total = 0;
        const lines = params
          .filter((item) => item.value > 0)
          .map((item) => {
            total += item.value;
            return `${item.marker}${item.seriesName}: ${formatPaymentsRub(item.value)} ₽`;
          });
        const pct = (val) => (total > 0 ? ` (${((val / total) * 100).toFixed(1)}%)` : "");
        return [
          `<strong>${month}</strong>`,
          ...lines.map((line, idx) => {
            const val = params.filter((p) => p.value > 0)[idx]?.value || 0;
            return line + pct(val);
          }),
          `<strong>Итого: ${formatPaymentsRub(total)} ₽</strong>`,
        ].join("<br>");
      },
    },
    legend: {
      type: "scroll",
      bottom: 0,
      textStyle: { color: textColor },
    },
    grid: { left: 48, right: 16, top: 24, bottom: 48 },
    xAxis: {
      type: "category",
      data: data.months,
      axisLabel: { color: axisColor, rotate: 35 },
      axisLine: { lineStyle: { color: gridColor } },
    },
    yAxis: {
      type: "value",
      axisLabel: {
        color: axisColor,
        formatter: (val) => (val >= 1_000_000 ? `${(val / 1_000_000).toFixed(1)}M` : val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val),
      },
      splitLine: { lineStyle: { color: gridColor } },
    },
    series: data.parties.map((party) => ({
      name: party,
      type: "bar",
      stack: "total",
      emphasis: { focus: "series" },
      itemStyle: { color: data.colors[party] || "#6b7280" },
      data: data.matrix[party] || [],
    })),
  };
}

function paymentsPieOption(data) {
  const textColor = "#e8eaed";
  const axisColor = "#9aa0a6";
  const entries = data.parties
    .map((party) => ({ name: party, value: data.party_totals[party] || 0 }))
    .filter((item) => item.value > 0);
  if (!entries.length) {
    return {
      backgroundColor: "transparent",
      title: {
        text: "Нет данных",
        left: "center",
        top: "middle",
        textStyle: { color: axisColor, fontSize: 14, fontWeight: 400 },
      },
    };
  }
  return {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "item",
      formatter: (params) => {
        const val = params.value || 0;
        return `${params.marker}${params.name}: ${formatPaymentsRub(val)} ₽ (${params.percent}%)`;
      },
    },
    legend: {
      type: "scroll",
      orient: "vertical",
      right: 0,
      top: "middle",
      textStyle: { color: textColor },
    },
    series: [
      {
        type: "pie",
        radius: ["42%", "68%"],
        center: ["38%", "50%"],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 4,
          borderColor: "#1a1d24",
          borderWidth: 2,
        },
        label: { color: textColor, formatter: "{b}\n{d}%" },
        data: entries.map((item) => ({
          name: item.name,
          value: item.value,
          itemStyle: { color: data.colors[item.name] || "#6b7280" },
        })),
      },
    ],
  };
}

function applyPaymentsTableFilters(sectionId, months, parties, minAmount) {
  const table = document.querySelector(`[data-payments-table="${sectionId}"]`);
  if (!table) return;
  const monthSet = new Set(months);
  const partySet = new Set(parties);
  const search = document.querySelector(`[data-payments-search="${sectionId}"]`);
  const q = search ? search.value.trim().toLowerCase() : "";
  table.querySelectorAll("tbody tr[data-month]").forEach((row) => {
    const monthOk = !monthSet.size || monthSet.has(row.dataset.month);
    const partyOk = !partySet.size || partySet.has(row.dataset.party);
    const amount = parseFloat(row.dataset.amount) || 0;
    const amountOk = !minAmount || amount >= minAmount;
    const filterOk = monthOk && partyOk && amountOk;
    row.dataset.filterHidden = filterOk ? "0" : "1";
    const searchOk = !q || row.textContent.toLowerCase().includes(q);
    row.style.display = filterOk && searchOk ? "" : "none";
  });
}

function updatePaymentsChartsForSection(sectionId) {
  const store = paymentsChartStore.get(sectionId);
  if (!store) return;
  const { series, barChart, pieChart, filterEl } = store;
  const months = getMultiSelectValues(filterEl.querySelector("[data-filter-month]"));
  const parties = getMultiSelectValues(filterEl.querySelector("[data-filter-party]"));
  const minRaw = filterEl.querySelector("[data-filter-min]")?.value;
  const minAmount = minRaw ? parseFloat(minRaw) : 0;
  const filtered = filterPaymentsSeries(series, months, parties);
  barChart.setOption(paymentsBarOption(filtered), true);
  pieChart.setOption(paymentsPieOption(filtered), true);
  applyPaymentsTableFilters(sectionId, months, parties, minAmount);
}

function bindPaymentsChartFilters(sectionId, filterEl) {
  if (filterEl.dataset.paymentsFilterBound === "1") return;
  filterEl.dataset.paymentsFilterBound = "1";
  const onChange = () => updatePaymentsChartsForSection(sectionId);
  filterEl.querySelector("[data-filter-month]")?.addEventListener("change", onChange);
  filterEl.querySelector("[data-filter-party]")?.addEventListener("change", onChange);
  filterEl.querySelector("[data-filter-min]")?.addEventListener("input", onChange);
  filterEl.querySelector("[data-filter-reset]")?.addEventListener("click", () => {
    filterEl.querySelectorAll("[data-filter-month] option, [data-filter-party] option").forEach((opt) => {
      opt.selected = true;
    });
    const minInput = filterEl.querySelector("[data-filter-min]");
    if (minInput) minInput.value = "";
    onChange();
  });
}

function disposePaymentsCharts(sectionId) {
  const store = paymentsChartStore.get(sectionId);
  if (!store) return;
  store.barChart?.dispose();
  store.pieChart?.dispose();
  paymentsChartStore.delete(sectionId);
}

function resizePaymentsCharts() {
  paymentsChartStore.forEach((store) => {
    store.barChart?.resize();
    store.pieChart?.resize();
  });
}

function initPaymentsCharts(root) {
  if (typeof echarts === "undefined") {
    console.warn("[wisenet] echarts is undefined — графики оплаты не инициализированы");
    return;
  }
  const scope = root || document;
  scope.querySelectorAll("[data-payments-series]").forEach((scriptEl) => {
    const sectionId = scriptEl.dataset.paymentsSeries;
    if (!sectionId) return;
    disposePaymentsCharts(sectionId);
    const series = parsePaymentsSeriesScript(scriptEl);
    const barEl = scope.querySelector(`[data-payments-chart-bar="${sectionId}"]`);
    const pieEl = scope.querySelector(`[data-payments-chart-pie="${sectionId}"]`);
    const filterEl = scope.querySelector(`[data-payments-filter="${sectionId}"]`);
    if (!barEl || !pieEl || !filterEl) return;
    const barChart = echarts.init(barEl, null, { renderer: "canvas" });
    const pieChart = echarts.init(pieEl, null, { renderer: "canvas" });
    paymentsChartStore.set(sectionId, { series, barChart, pieChart, filterEl });
    bindPaymentsChartFilters(sectionId, filterEl);
    updatePaymentsChartsForSection(sectionId);
    barChart.on("click", (params) => {
      if (!params?.name) return;
      const monthSelect = filterEl.querySelector("[data-filter-month]");
      if (!monthSelect) return;
      Array.from(monthSelect.options).forEach((opt) => {
        opt.selected = opt.value === params.name;
      });
      updatePaymentsChartsForSection(sectionId);
    });
    pieChart.on("click", (params) => {
      if (!params?.name) return;
      const partySelect = filterEl.querySelector("[data-filter-party]");
      if (!partySelect) return;
      Array.from(partySelect.options).forEach((opt) => {
        opt.selected = opt.value === params.name;
      });
      updatePaymentsChartsForSection(sectionId);
    });
  });
}

if (!window.__paymentsChartsResizeBound) {
  window.__paymentsChartsResizeBound = true;
  window.addEventListener("resize", resizePaymentsCharts);
}

function initPaymentsPage(root) {
  initPaymentsTabs(root);
  initPaymentsCollapsibles(root);
  initPaymentsTables(root);
  initPaymentsCharts(root);
}

document.addEventListener("DOMContentLoaded", () => {
  initServerToasts();
  initPaymentsPage();
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
  initKindTabs();
  scrollToHighlightedCategory();
});

document.body.addEventListener("htmx:afterSwap", (e) => {
  applyCollapsedState();
  applyObjectDeepLinkFromUrl();
  applyTimeDashboardState();
  applyCategoryDashboardState();
  initKindTabs(e.detail?.target);
  initPaymentsTabs(e.detail?.target);
  initPaymentsCollapsibles(e.detail?.target);
  initPaymentsTables(e.detail?.target);
  initPaymentsCharts(e.detail?.target);
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
  const cmdbPath = e.detail?.requestConfig?.path;
  if (cmdbPath === "/objects/sync-cmdb" || (cmdbPath && cmdbPath.startsWith("/sources/cmdb"))) {
    showToast("error", "Нет связи с сервером при обновлении из CMDB.");
  }
  if (cmdbPath === "/payments/upload" || (cmdbPath && cmdbPath.startsWith("/sources/requests"))) {
    showToast("error", "Нет связи с сервером при загрузке заявок.");
  }
});
document.body.addEventListener("htmx:responseError", (e) => {
  logHtmxClient("htmx_response_error", e.detail);
  const cmdbPath = e.detail?.requestConfig?.path;
  if (cmdbPath === "/objects/sync-cmdb" || (cmdbPath && cmdbPath.startsWith("/sources/cmdb"))) {
    showToast("error", "Не удалось обновить список из CMDB. Проверьте папку inputData и логи.");
  }
  if (cmdbPath === "/payments/upload" || (cmdbPath && cmdbPath.startsWith("/sources/requests"))) {
    showToast("error", "Не удалось загрузить заявки. Проверьте папку inputData и логи.");
  }
});
document.body.addEventListener("htmx:swapError", (e) => logHtmxClient("htmx_swap_error", e.detail));
