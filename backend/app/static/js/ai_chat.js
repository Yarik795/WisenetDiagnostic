(function () {
  "use strict";

  const activeStreams = new Set();

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function renderCharts(root) {
    if (typeof echarts === "undefined") return;
    const scope = root || document;
    scope.querySelectorAll(".chat-chart[data-echart]").forEach(function (el) {
      if (el.dataset.rendered === "1") return;
      let option;
      try {
        option = JSON.parse(el.getAttribute("data-echart"));
      } catch (e) {
        console.warn("[ai-chat] invalid chart json", e);
        return;
      }
      const chart = echarts.init(el, null, { renderer: "canvas" });
      chart.setOption(option);
      el.dataset.rendered = "1";
    });
  }

  function scrollChatToBottom() {
    const box = document.getElementById("ai-chat-messages");
    if (box) {
      box.scrollTop = box.scrollHeight;
    }
  }

  function appendTable(parent, table) {
    if (!table || !table.rows || !table.rows.length) return;
    const details = document.createElement("details");
    details.className = "chat-details";
    details.open = false;
    const summary = document.createElement("summary");
    summary.textContent =
      "Таблица данных (" + (table.row_count || table.rows.length) + " строк)";
    details.appendChild(summary);

    const wrap = document.createElement("div");
    wrap.className = "chat-table-wrap";
    const tbl = document.createElement("table");
    tbl.className = "chat-table";

    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");
    (table.columns || []).forEach(function (col) {
      const th = document.createElement("th");
      th.textContent = col;
      headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    tbl.appendChild(thead);

    const tbody = document.createElement("tbody");
    table.rows.slice(0, 100).forEach(function (row) {
      const tr = document.createElement("tr");
      (table.columns || []).forEach(function (col) {
        const td = document.createElement("td");
        td.textContent = row[col] != null ? String(row[col]) : "";
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    tbl.appendChild(tbody);
    wrap.appendChild(tbl);
    details.appendChild(wrap);
    parent.appendChild(details);
  }

  function appendSql(parent, sql) {
    if (!sql) return;
    const details = document.createElement("details");
    details.className = "chat-details";
    const summary = document.createElement("summary");
    summary.textContent = "SQL-запрос";
    details.appendChild(summary);
    const pre = document.createElement("pre");
    pre.className = "chat-sql";
    pre.textContent = sql;
    details.appendChild(pre);
    parent.appendChild(details);
  }

  function appendChart(parent, chartOption) {
    if (!chartOption || typeof echarts === "undefined") return;
    const el = document.createElement("div");
    el.className = "chat-chart";
    el.setAttribute("data-echart", JSON.stringify(chartOption));
    parent.appendChild(el);
    renderCharts(parent);
  }

  function startStream(turnEl) {
    const url = turnEl.getAttribute("data-stream-url");
    if (!url || activeStreams.has(url)) return;
    activeStreams.add(url);

    const assistantMsg = turnEl.querySelector(".chat-msg--assistant");
    if (!assistantMsg) return;
    const textEl = assistantMsg.querySelector(".chat-msg-text");
    const bodyEl = assistantMsg.querySelector(".chat-msg-body");
    if (!textEl || !bodyEl) return;

    textEl.textContent = "";
    textEl.classList.add("chat-msg-text--typing");

    const toolEl = document.createElement("div");
    toolEl.className = "chat-tool-status";
    toolEl.hidden = true;
    bodyEl.insertBefore(toolEl, textEl);

    const source = new EventSource(url);

    source.addEventListener("tool", function (ev) {
      try {
        const data = JSON.parse(ev.data);
        toolEl.hidden = false;
        toolEl.textContent = "Запрос к данным: " + (data.name || "…");
      } catch (e) {
        toolEl.hidden = false;
        toolEl.textContent = "Запрос к данным…";
      }
      scrollChatToBottom();
    });

    source.addEventListener("delta", function (ev) {
      toolEl.hidden = true;
      textEl.classList.remove("chat-msg-text--typing");
      try {
        const chunk = JSON.parse(ev.data);
        textEl.textContent += typeof chunk === "string" ? chunk : String(chunk);
      } catch (e) {
        textEl.textContent += ev.data;
      }
      scrollChatToBottom();
    });

    source.addEventListener("done", function (ev) {
      source.close();
      activeStreams.delete(url);
      textEl.classList.remove("chat-msg-text--typing", "chat-msg-text--pending");
      textEl.removeAttribute("data-pending");
      toolEl.remove();

      let data;
      try {
        data = JSON.parse(ev.data);
      } catch (e) {
        return;
      }

      if (data.text && !textEl.textContent) {
        textEl.textContent = data.text;
      }
      appendChart(bodyEl, data.chart);
      appendTable(bodyEl, data.table);
      appendSql(bodyEl, data.sql);
      scrollChatToBottom();
    });

    source.addEventListener("error", function (ev) {
      source.close();
      activeStreams.delete(url);
      textEl.classList.remove("chat-msg-text--typing", "chat-msg-text--pending");
      toolEl.remove();
      if (!textEl.textContent) {
        try {
          const data = JSON.parse(ev.data || "{}");
          textEl.textContent = data.text || "Ошибка при получении ответа.";
        } catch (e) {
          textEl.textContent = "Ошибка при получении ответа.";
        }
      }
    });
  }

  document.body.addEventListener("htmx:afterSwap", function (ev) {
    const target = ev.detail && ev.detail.target;
    if (!target) return;
    target.querySelectorAll(".ai-chat-turn[data-stream-url]").forEach(startStream);
    renderCharts(target);
    scrollChatToBottom();
  });

  document.addEventListener("DOMContentLoaded", function () {
    renderCharts(document);
    scrollChatToBottom();

    const form = document.getElementById("ai-chat-form");
    if (form) {
      form.addEventListener("submit", function () {
        const textarea = form.querySelector("textarea[name=text]");
        if (textarea) {
          setTimeout(function () {
            textarea.value = "";
          }, 0);
        }
      });
    }
  });
})();
