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

function getChipFilterValues(container, chipSelector) {
  if (!container) return [];
  const chips = container.querySelectorAll(chipSelector);
  if (!chips.length) return [];
  const allValues = Array.from(chips).map((chip) => chip.value);
  const activeChips = Array.from(chips).filter((chip) => chip.classList.contains("is-active"));
  if (activeChips.length === chips.length) return allValues;
  if (!activeChips.length) return [];
  return activeChips.map((chip) => chip.value);
}

function setPaymentsChipActive(chip, active) {
  chip.classList.toggle("is-active", active);
  chip.setAttribute("aria-pressed", active ? "true" : "false");
}

function setOnlyPaymentsChipActive(container, chipSelector, value) {
  if (!container) return;
  container.querySelectorAll(chipSelector).forEach((chip) => {
    setPaymentsChipActive(chip, chip.value === value);
  });
}

function resetPaymentsChips(container, chipSelector) {
  if (!container) return;
  container.querySelectorAll(chipSelector).forEach((chip) => {
    setPaymentsChipActive(chip, true);
  });
}

function filterPaymentsSeries(series, months, parties, metric) {
  const monthSet = new Set(months);
  const partySet = new Set(parties);
  const filteredMonths = series.months.filter((month) => monthSet.has(month));
  const filteredParties = series.parties.filter((party) => partySet.has(party));
  const valueMatrix = metric === "count" ? series.count_matrix || {} : series.matrix || {};
  const matrix = {};
  filteredParties.forEach((party) => {
    matrix[party] = filteredMonths.map((month) => {
      const idx = series.months.indexOf(month);
      return idx >= 0 && valueMatrix[party] ? valueMatrix[party][idx] || 0 : 0;
    });
  });
  const partyTotals = {};
  filteredParties.forEach((party) => {
    partyTotals[party] = (matrix[party] || []).reduce((sum, val) => sum + val, 0);
  });
  const approvedKey = metric === "count" ? "count" : "amount";
  const approvedSource = series.approved || {};
  const approvedArr = approvedSource[approvedKey] || [];
  const approved = filteredMonths.map((month) => {
    const idx = series.months.indexOf(month);
    return idx >= 0 && approvedArr[idx] !== undefined ? approvedArr[idx] : 0;
  });
  return {
    months: filteredMonths,
    parties: filteredParties,
    matrix,
    party_totals: partyTotals,
    approved,
    approved_total: approved.reduce((sum, val) => sum + val, 0),
    metric: metric || "amount",
    colors: series.colors || {},
  };
}

function formatPaymentsMetricValue(value, metric) {
  if (metric === "count") {
    const n = Math.round(value);
    const mod10 = n % 10;
    const mod100 = n % 100;
    let word = "заявок";
    if (mod100 < 11 || mod100 > 14) {
      if (mod10 === 1) word = "заявка";
      else if (mod10 >= 2 && mod10 <= 4) word = "заявки";
    }
    return `${n} ${word}`;
  }
  return `${formatPaymentsRub(value)} ₽`;
}

function paymentsBarOption(data) {
  const textColor = "#e8eaed";
  const axisColor = "#9aa0a6";
  const gridColor = "#2d323c";
  const metric = data.metric || "amount";
  const hasApproved = (data.approved || []).some((val) => val > 0);
  if (!data.months.length || (!data.parties.length && !hasApproved)) {
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
  const barSeries = data.parties.map((party) => ({
    name: party,
    type: "bar",
    stack: "total",
    emphasis: { focus: "series" },
    itemStyle: { color: data.colors[party] || "#6b7280" },
    data: data.matrix[party] || [],
  }));
  if (hasApproved) {
    barSeries.push({
      name: "Согласовано",
      type: "bar",
      stack: "total",
      emphasis: { focus: "series" },
      itemStyle: { color: data.colors["Согласовано"] || "#34d399" },
      data: data.approved || [],
    });
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
        const positive = params.filter((item) => item.value > 0);
        const lines = positive.map((item) => {
          total += item.value;
          return `${item.marker}${item.seriesName}: ${formatPaymentsMetricValue(item.value, metric)}`;
        });
        const pct = (val) => (total > 0 ? ` (${Math.round((val / total) * 100)}%)` : "");
        return [
          `<strong>${month}</strong>`,
          ...positive.map(
            (item) =>
              `${item.marker}${item.seriesName}: ${formatPaymentsMetricValue(item.value, metric)}${pct(item.value)}`
          ),
          `<strong>Итого: ${formatPaymentsMetricValue(total, metric)}</strong>`,
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
        formatter: (val) => {
          if (metric === "count") return val;
          return val >= 1_000_000
            ? `${(val / 1_000_000).toFixed(1)}M`
            : val >= 1000
              ? `${(val / 1000).toFixed(0)}k`
              : val;
        },
      },
      splitLine: { lineStyle: { color: gridColor } },
    },
    series: barSeries,
  };
}

function paymentsPieOption(data) {
  const textColor = "#e8eaed";
  const axisColor = "#9aa0a6";
  const metric = data.metric || "amount";
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
        const pct = Math.round(params.percent || 0);
        return `${params.marker}${params.name}: ${formatPaymentsMetricValue(val, metric)} (${pct}%)`;
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
        label: {
          color: textColor,
          formatter: (params) => `${params.name}\n${Math.round(params.percent)}%`,
        },
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
  const metric = store.metric || "amount";
  const months = getChipFilterValues(filterEl.querySelector("[data-filter-month]"), "[data-month-chip]");
  const parties = getChipFilterValues(filterEl.querySelector("[data-filter-party]"), "[data-party-chip]");
  const minRaw = filterEl.querySelector("[data-filter-min]")?.value;
  const minAmount = minRaw ? parseFloat(minRaw) : 0;
  const filtered = filterPaymentsSeries(series, months, parties, metric);
  barChart.setOption(paymentsBarOption(filtered), true);
  pieChart.setOption(paymentsPieOption(filtered), true);
  applyPaymentsTableFilters(sectionId, months, parties, minAmount);
}

function bindPaymentsMetricToggle(sectionId, metricEl) {
  if (metricEl.dataset.paymentsMetricBound === "1") return;
  metricEl.dataset.paymentsMetricBound = "1";
  metricEl.querySelectorAll("[data-metric]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const store = paymentsChartStore.get(sectionId);
      if (!store) return;
      const metric = btn.dataset.metric;
      if (!metric || store.metric === metric) return;
      store.metric = metric;
      metricEl.querySelectorAll("[data-metric]").forEach((b) => {
        b.classList.toggle("active", b.dataset.metric === metric);
      });
      updatePaymentsChartsForSection(sectionId);
    });
  });
}

function bindPaymentsChartFilters(sectionId, filterEl) {
  if (filterEl.dataset.paymentsFilterBound === "1") return;
  filterEl.dataset.paymentsFilterBound = "1";
  const onChange = () => updatePaymentsChartsForSection(sectionId);
  const monthContainer = filterEl.querySelector("[data-filter-month]");
  const partyContainer = filterEl.querySelector("[data-filter-party]");
  monthContainer?.addEventListener("click", (event) => {
    const chip = event.target.closest("[data-month-chip]");
    if (!chip || !monthContainer.contains(chip)) return;
    setPaymentsChipActive(chip, !chip.classList.contains("is-active"));
    onChange();
  });
  partyContainer?.addEventListener("click", (event) => {
    const chip = event.target.closest("[data-party-chip]");
    if (!chip || !partyContainer.contains(chip)) return;
    setPaymentsChipActive(chip, !chip.classList.contains("is-active"));
    onChange();
  });
  filterEl.querySelector("[data-filter-min]")?.addEventListener("input", onChange);
  filterEl.querySelector("[data-filter-reset]")?.addEventListener("click", () => {
    resetPaymentsChips(monthContainer, "[data-month-chip]");
    resetPaymentsChips(partyContainer, "[data-party-chip]");
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
    const metricEl = scope.querySelector(`[data-payments-metric="${sectionId}"]`);
    if (!barEl || !pieEl || !filterEl) return;
    const barChart = echarts.init(barEl, null, { renderer: "canvas" });
    const pieChart = echarts.init(pieEl, null, { renderer: "canvas" });
    paymentsChartStore.set(sectionId, {
      series,
      barChart,
      pieChart,
      filterEl,
      metricEl,
      metric: "amount",
    });
    bindPaymentsChartFilters(sectionId, filterEl);
    if (metricEl) bindPaymentsMetricToggle(sectionId, metricEl);
    updatePaymentsChartsForSection(sectionId);
    barChart.on("click", (params) => {
      if (!params?.name) return;
      const monthContainer = filterEl.querySelector("[data-filter-month]");
      if (!monthContainer) return;
      setOnlyPaymentsChipActive(monthContainer, "[data-month-chip]", params.name);
      updatePaymentsChartsForSection(sectionId);
    });
    pieChart.on("click", (params) => {
      if (!params?.name) return;
      const partyContainer = filterEl.querySelector("[data-filter-party]");
      if (!partyContainer) return;
      setOnlyPaymentsChipActive(partyContainer, "[data-party-chip]", params.name);
      updatePaymentsChartsForSection(sectionId);
    });
  });
}

if (!window.__paymentsChartsResizeBound) {
  window.__paymentsChartsResizeBound = true;
  window.addEventListener("resize", resizePaymentsCharts);
}

const arsenalChartStore = new Map();

function arsenalEmptyOption(message = "Нет данных") {
  return {
    backgroundColor: "transparent",
    title: {
      text: message,
      left: "center",
      top: "middle",
      textStyle: { color: "#9aa0a6", fontSize: 14, fontWeight: 400 },
    },
  };
}

function arsenalDonutOption(chartData) {
  const textColor = "#e8eaed";
  const entries = chartData.entries || [];
  if (!entries.length) return arsenalEmptyOption();
  return {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "item",
      formatter: (params) =>
        `${params.marker}${params.name}: ${params.value} (${Math.round(params.percent || 0)}%)`,
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
        label: {
          color: textColor,
          formatter: (params) => `${params.name}\n${Math.round(params.percent)}%`,
        },
        data: entries.map((item) => ({
          name: item.name,
          value: item.value,
          itemStyle: { color: chartData.colors?.[item.name] || "#6b7280" },
        })),
      },
    ],
  };
}

function arsenalBarOption(labels, values, options = {}) {
  const textColor = "#e8eaed";
  const axisColor = "#9aa0a6";
  const gridColor = "#2d323c";
  const horizontal = Boolean(options.horizontal);
  const suffix = options.suffix || "";
  if (!labels.length || !values.some((val) => val > 0)) {
    return arsenalEmptyOption();
  }
  const categoryAxis = {
    type: "category",
    data: labels,
    axisLabel: { color: axisColor, rotate: horizontal ? 0 : 35 },
    axisLine: { lineStyle: { color: gridColor } },
  };
  const valueAxis = {
    type: "value",
    axisLabel: { color: axisColor },
    splitLine: { lineStyle: { color: gridColor } },
  };
  return {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter: (params) => {
        const item = params?.[0];
        if (!item) return "";
        return `${item.name}: ${item.value}${suffix}`;
      },
    },
    grid: horizontal
      ? { left: 120, right: 24, top: 16, bottom: 24 }
      : { left: 48, right: 16, top: 24, bottom: 72 },
    xAxis: horizontal ? valueAxis : categoryAxis,
    yAxis: horizontal ? categoryAxis : valueAxis,
    series: [
      {
        type: "bar",
        data: values,
        itemStyle: { color: options.color || "#3b82f6", borderRadius: horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0] },
        label: horizontal
          ? {
              show: true,
              position: "right",
              color: textColor,
              formatter: (params) => `${params.value}${suffix}`,
            }
          : undefined,
      },
    ],
  };
}

function arsenalDocsStackOption(chartData) {
  const textColor = "#e8eaed";
  const axisColor = "#9aa0a6";
  const gridColor = "#2d323c";
  const systems = chartData.systems || [];
  if (!systems.length) return arsenalEmptyOption();
  const hasValues = (chartData.yes || []).some((val) => val > 0)
    || (chartData.no || []).some((val) => val > 0)
    || (chartData.dash || []).some((val) => val > 0);
  if (!hasValues) return arsenalEmptyOption();
  return {
    backgroundColor: "transparent",
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    legend: {
      bottom: 0,
      textStyle: { color: textColor },
    },
    grid: { left: 48, right: 16, top: 24, bottom: 48 },
    xAxis: {
      type: "category",
      data: systems,
      axisLabel: { color: axisColor },
      axisLine: { lineStyle: { color: gridColor } },
    },
    yAxis: {
      type: "value",
      axisLabel: { color: axisColor },
      splitLine: { lineStyle: { color: gridColor } },
    },
    series: [
      {
        name: "Да",
        type: "bar",
        stack: "docs",
        itemStyle: { color: "#10b981" },
        data: chartData.yes || [],
      },
      {
        name: "Нет",
        type: "bar",
        stack: "docs",
        itemStyle: { color: "#ef4444" },
        data: chartData.no || [],
      },
      {
        name: "—",
        type: "bar",
        stack: "docs",
        itemStyle: { color: "#6b7280" },
        data: chartData.dash || [],
      },
    ],
  };
}

function arsenalManufacturersOption(chartData) {
  const labels = chartData.manufacturers || [];
  const values = chartData.counts || [];
  if (!labels.length) return arsenalEmptyOption();
  return {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter: (params) => {
        const item = params?.[0];
        if (!item) return "";
        return `${item.name}: ${item.value}`;
      },
    },
    grid: { left: 120, right: 24, top: 16, bottom: 24 },
    xAxis: {
      type: "value",
      axisLabel: { color: "#9aa0a6" },
      splitLine: { lineStyle: { color: "#2d323c" } },
    },
    yAxis: {
      type: "category",
      data: labels,
      axisLabel: { color: "#9aa0a6" },
      axisLine: { lineStyle: { color: "#2d323c" } },
    },
    series: [
      {
        type: "bar",
        data: values.map((value, idx) => ({
          value,
          itemStyle: {
            color: chartData.colors?.[labels[idx]] || "#3b82f6",
            borderRadius: [0, 4, 4, 0],
          },
        })),
        label: {
          show: true,
          position: "right",
          color: "#e8eaed",
        },
      },
    ],
  };
}

function disposeArsenalCharts(root) {
  const scope = root || document;
  scope.querySelectorAll("[data-arsenal-chart]").forEach((el) => {
    const chart = echarts.getInstanceByDom(el);
    if (chart) chart.dispose();
  });
  arsenalChartStore.clear();
}

function currentArsenalObjectTypeFilter() {
  const select = document.querySelector(
    '#arsenal-object-type, form[hx-get="/arsenal/partials/dashboard"] select[name="object_type"]'
  );
  return select?.value || "";
}

function loadArsenalDetail(queryParams) {
  if (typeof htmx === "undefined") return;
  const params = new URLSearchParams(queryParams);
  const objectType = currentArsenalObjectTypeFilter();
  if (objectType) {
    params.set("object_type", objectType);
  }
  const panel = document.getElementById("arsenal-detail-panel");
  if (panel) {
    panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
  htmx.ajax("GET", `/arsenal/partials/detail?${params.toString()}`, {
    target: "#arsenal-detail-panel",
    swap: "innerHTML",
  });
}

function resolveArsenalDashboard(root) {
  const scope = root || document;
  let dashboard = null;
  if (scope instanceof Element && scope.hasAttribute("data-arsenal-dashboard")) {
    dashboard = scope;
  } else if (scope instanceof Document || scope instanceof Element) {
    dashboard = scope.querySelector("[data-arsenal-dashboard]");
  }
  if (!dashboard) {
    dashboard = document.querySelector("[data-arsenal-dashboard]");
  }
  // outerHTML swap: HTMX afterSwap target is the removed node, not the new dashboard.
  if (dashboard && !dashboard.isConnected) {
    dashboard = document.querySelector("[data-arsenal-dashboard]");
  }
  return dashboard;
}

function initArsenalCharts(root) {
  if (typeof echarts === "undefined") return;
  const dashboard = resolveArsenalDashboard(root);
  if (!dashboard) return;

  disposeArsenalCharts(dashboard);
  const scriptEl = dashboard.querySelector("[data-arsenal-charts]");
  if (!scriptEl) return;

  let chartData;
  try {
    chartData = JSON.parse(scriptEl.textContent || "{}");
  } catch (err) {
    console.error("[wisenet] arsenal chart data parse error", err);
    return;
  }

  const objectTypesEl = dashboard.querySelector('[data-arsenal-chart="object_types"]');
  if (objectTypesEl) {
    const chart = echarts.init(objectTypesEl, null, { renderer: "canvas" });
    chart.setOption(arsenalDonutOption(chartData.object_types || {}), true);
    chart.on("click", (params) => {
      if (!params?.name) return;
      loadArsenalDetail({
        dimension: "object_type",
        value: params.name,
      });
    });
    arsenalChartStore.set("object_types", chart);
  }

  const fillEl = dashboard.querySelector('[data-arsenal-chart="fill_sections"]');
  if (fillEl) {
    const fill = chartData.fill_sections || {};
    const chart = echarts.init(fillEl, null, { renderer: "canvas" });
    chart.setOption(
      arsenalBarOption(fill.labels || [], fill.values || [], {
        horizontal: true,
        suffix: "%",
        color: "#10b981",
      }),
      true
    );
    chart.on("click", (params) => {
      const label = params.name || params.axisValue;
      if (!label) return;
      loadArsenalDetail({
        dimension: "fill_section",
        value: label,
      });
    });
    arsenalChartStore.set("fill_sections", chart);
  }

  const errorsEl = dashboard.querySelector('[data-arsenal-chart="errors"]');
  if (errorsEl) {
    const errors = chartData.errors || {};
    const chart = echarts.init(errorsEl, null, { renderer: "canvas" });
    chart.setOption(
      arsenalBarOption(errors.labels || [], errors.values || [], {
        color: "#f59e0b",
      }),
      true
    );
    chart.on("click", (params) => {
      const label = params.name || params.axisValue;
      if (!label) return;
      loadArsenalDetail({
        dimension: "errors_section",
        value: label,
      });
    });
    arsenalChartStore.set("errors", chart);
  }

  const docsEl = dashboard.querySelector('[data-arsenal-chart="docs"]');
  if (docsEl) {
    const chart = echarts.init(docsEl, null, { renderer: "canvas" });
    chart.setOption(arsenalDocsStackOption(chartData.docs || {}), true);
    chart.on("click", (params) => {
      const systemType = params.name || params.axisValue;
      const status = params.seriesName;
      if (!systemType || !status) return;
      loadArsenalDetail({
        dimension: "docs",
        system_type: systemType,
        status,
        value: systemType,
      });
    });
    arsenalChartStore.set("docs", chart);
  }

  dashboard.querySelectorAll('[data-arsenal-chart^="systems_"]').forEach((el) => {
    const key = el.dataset.arsenalChart.replace("systems_", "");
    const systemData = chartData.systems?.[key] || {};
    const chart = echarts.init(el, null, { renderer: "canvas" });
    chart.setOption(arsenalManufacturersOption(systemData), true);
    chart.on("click", (params) => {
      const manufacturer = params.name || params.axisValue;
      if (!manufacturer) return;
      loadArsenalDetail({
        dimension: "manufacturer",
        system_type: key,
        value: manufacturer,
      });
    });
    arsenalChartStore.set(el.dataset.arsenalChart, chart);
  });
}

function resizeArsenalCharts() {
  arsenalChartStore.forEach((chart) => chart.resize());
}

if (!window.__arsenalChartsResizeBound) {
  window.__arsenalChartsResizeBound = true;
  window.addEventListener("resize", resizeArsenalCharts);
}

const PAYMENTS_SECTION_KEYS = ["az_mb", "az_ca", "vsp_mb", "vsp_ca"];

function collectPaymentsEmailParams() {
  const params = new URLSearchParams();
  PAYMENTS_SECTION_KEYS.forEach((key) => {
    const sectionId = `modern-${key}`;
    const store = paymentsChartStore.get(sectionId);
    const metric = store?.metric === "count" ? "count" : "amount";
    params.set(`m_${key}`, metric);
  });
  return params.toString();
}

function collectPaymentsViewParams() {
  const tabsNav = document.querySelector("[data-payments-tabs]");
  const kindBtn = tabsNav?.querySelector("[data-payments-tab].active");
  const kind = kindBtn?.dataset.paymentsTab || "modern";
  const params = new URLSearchParams({ kind });
  PAYMENTS_SECTION_KEYS.forEach((key) => {
    const sectionId = `${kind}-${key}`;
    const store = paymentsChartStore.get(sectionId);
    const metric = store?.metric === "count" ? "count" : "amount";
    params.set(`m_${key}`, metric);
  });
  return params.toString();
}

function initPaymentsExportActions(root) {
  const scope = root || document;
  scope.querySelectorAll("[data-payments-export]").forEach((btn) => {
    if (btn.dataset.paymentsExportBound === "1") return;
    btn.dataset.paymentsExportBound = "1";
    btn.addEventListener("click", () => {
      window.location.href = `/payments/export.html?${collectPaymentsViewParams()}`;
    });
  });
  scope.querySelectorAll("[data-payments-email]").forEach((btn) => {
    if (btn.dataset.paymentsEmailBound === "1") return;
    btn.dataset.paymentsEmailBound = "1";
    btn.addEventListener("click", async () => {
      if (btn.disabled) return;
      btn.disabled = true;
      try {
        const res = await fetch(`/payments/report/email?${collectPaymentsEmailParams()}`, {
          method: "POST",
        });
        const data = await res.json();
        showToast(data.ok ? "success" : "error", data.message || "Неизвестная ошибка");
      } catch (err) {
        showToast("error", "Не удалось отправить отчёт на почту");
        console.error("[wisenet] payments email error", err);
      } finally {
        btn.disabled = false;
      }
    });
  });
}

function initArsenalExportActions(root) {
  const scope = root || document;
  scope.querySelectorAll("[data-arsenal-export]").forEach((btn) => {
    if (btn.dataset.arsenalExportBound === "1") return;
    btn.dataset.arsenalExportBound = "1";
    btn.addEventListener("click", () => {
      const select = document.getElementById("arsenal-object-type");
      const objectType = select ? select.value : "";
      const params = new URLSearchParams();
      if (objectType) params.set("object_type", objectType);
      const qs = params.toString();
      window.location.href = qs ? `/arsenal/export.html?${qs}` : "/arsenal/export.html";
    });
  });
  scope.querySelectorAll("[data-arsenal-email]").forEach((btn) => {
    if (btn.dataset.arsenalEmailBound === "1") return;
    btn.dataset.arsenalEmailBound = "1";
    btn.addEventListener("click", async () => {
      if (btn.disabled) return;
      btn.disabled = true;
      try {
        const select = document.getElementById("arsenal-object-type");
        const objectType = select ? select.value : "";
        const params = new URLSearchParams();
        if (objectType) params.set("object_type", objectType);
        const qs = params.toString();
        const url = qs ? `/arsenal/report/email?${qs}` : "/arsenal/report/email";
        const res = await fetch(url, { method: "POST" });
        const data = await res.json();
        showToast(data.ok ? "success" : "error", data.message || "Неизвестная ошибка");
      } catch (err) {
        showToast("error", "Не удалось отправить отчёт на почту");
        console.error("[wisenet] arsenal email error", err);
      } finally {
        btn.disabled = false;
      }
    });
  });
}

function collectRvrRepeatParams() {
  const params = new URLSearchParams();
  const fromInput = document.querySelector("[data-rvr-date-from]");
  const toInput = document.querySelector("[data-rvr-date-to]");
  const thresholdSelect = document.querySelector("[data-rvr-threshold]");
  const objectTypeSelect = document.querySelector("[data-rvr-object-type]");
  if (fromInput && fromInput.value) params.set("from", fromInput.value);
  if (toInput && toInput.value) params.set("to", toInput.value);
  if (thresholdSelect && thresholdSelect.value) {
    params.set("threshold", thresholdSelect.value);
  }
  if (objectTypeSelect && objectTypeSelect.value) {
    params.set("object_type", objectTypeSelect.value);
  }
  return params;
}

function updateRvrRepeatLinks() {
  const params = collectRvrRepeatParams();
  const qs = params.toString();
  const exportLink = document.getElementById("rvr-export-link");
  if (exportLink) {
    exportLink.href = qs
      ? `/rvr-repeat/export.xlsx?${qs}`
      : "/rvr-repeat/export.xlsx";
  }
}

function closeAllRvrRepeatDetails(scope) {
  const root = scope || document;
  root.querySelectorAll("[data-rvr-detail-row]").forEach((row) => {
    row.hidden = true;
  });
  root.querySelectorAll("[data-rvr-kind-block]").forEach((block) => {
    block.hidden = true;
  });
  root.querySelectorAll("[data-rvr-cell-toggle]").forEach((btn) => {
    btn.setAttribute("aria-expanded", "false");
  });
}

function openRvrRepeatDetail(rowId, kind, scope) {
  const root = scope || document;
  closeAllRvrRepeatDetails(root);

  const detailRow = root.querySelector(`[data-rvr-detail-row="${rowId}"]`);
  const kindBlock = root.querySelector(
    `[data-rvr-kind-block="${rowId}"][data-kind="${kind}"]`
  );
  const toggleBtn = root.querySelector(
    `[data-rvr-cell-toggle][data-row-id="${rowId}"][data-kind="${kind}"]`
  );

  if (detailRow) detailRow.hidden = false;
  if (kindBlock) kindBlock.hidden = false;
  if (toggleBtn) toggleBtn.setAttribute("aria-expanded", "true");
}

function initRvrRepeatMatrix(root) {
  const scope = root || document;
  const reportRoot =
    scope.id === "rvr-repeat-report-root"
      ? scope
      : scope.querySelector("#rvr-repeat-report-root");
  if (!reportRoot || reportRoot.dataset.rvrMatrixBound === "1") return;
  reportRoot.dataset.rvrMatrixBound = "1";

  reportRoot.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-rvr-cell-toggle]");
    if (!btn || !reportRoot.contains(btn)) return;

    const rowId = btn.dataset.rowId;
    const kind = btn.dataset.kind;
    if (!rowId || !kind) return;

    const isOpen = btn.getAttribute("aria-expanded") === "true";
    if (isOpen) {
      closeAllRvrRepeatDetails(reportRoot);
      return;
    }
    openRvrRepeatDetail(rowId, kind, reportRoot);
  });
}

function initRvrRepeatActions(root) {
  const scope = root || document;
  updateRvrRepeatLinks();
  initRvrRepeatMatrix(scope);

  const form = document.getElementById("rvr-repeat-filters");
  if (form && form.dataset.rvrFiltersBound !== "1") {
    form.dataset.rvrFiltersBound = "1";
    form.addEventListener("change", () => {
      updateRvrRepeatLinks();
    });
  }

  scope.querySelectorAll("[data-rvr-ai-check]").forEach((btn) => {
    if (btn.dataset.rvrAiCheckBound === "1") return;
    btn.dataset.rvrAiCheckBound = "1";
    const defaultLabel = btn.textContent || "Проверить через AI";
    btn.addEventListener("htmx:beforeRequest", () => {
      if (btn.disabled) return;
      btn.dataset.rvrAiWasEnabled = "1";
      btn.disabled = true;
      btn.textContent = "Анализ…";
    });
    btn.addEventListener("htmx:afterRequest", () => {
      if (btn.dataset.rvrAiWasEnabled !== "1") return;
      delete btn.dataset.rvrAiWasEnabled;
      btn.disabled = false;
      btn.textContent = defaultLabel;
    });
  });

  scope.querySelectorAll("[data-rvr-email]").forEach((btn) => {
    if (btn.dataset.rvrEmailBound === "1") return;
    btn.dataset.rvrEmailBound = "1";
    const defaultLabel = btn.textContent || "Отправить на почту";
    btn.addEventListener("click", async () => {
      if (btn.disabled) return;
      btn.disabled = true;
      btn.textContent = "Отправка…";
      try {
        const params = collectRvrRepeatParams();
        const qs = params.toString();
        const url = qs
          ? `/rvr-repeat/report/email?${qs}`
          : "/rvr-repeat/report/email";
        const res = await fetch(url, { method: "POST" });
        const data = await res.json();
        showToast(data.ok ? "success" : "error", data.message || "Неизвестная ошибка");
      } catch (err) {
        showToast("error", "Не удалось отправить отчёт на почту");
        console.error("[wisenet] rvr-repeat email error", err);
      } finally {
        btn.disabled = false;
        btn.textContent = defaultLabel;
      }
    });
  });
}

function initPaymentsPage(root) {
  initPaymentsTabs(root);
  initPaymentsCollapsibles(root);
  initPaymentsTables(root);
  initPaymentsCharts(root);
  initPaymentsExportActions(root);
}

document.addEventListener("DOMContentLoaded", () => {
  initServerToasts();
  initPaymentsPage();
  initArsenalCharts();
  initArsenalExportActions();
  initRvrRepeatActions();
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
  initArsenalCharts(e.detail?.target);
  initPaymentsExportActions(e.detail?.target);
  initRvrRepeatActions(e.detail?.target);
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
