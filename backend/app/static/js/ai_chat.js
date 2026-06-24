(function () {
  "use strict";

  const activeStreams = new Set();
  const chartInstances = new WeakMap();

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function renderMarkdown(text) {
    if (!text) return "";
    let html = escapeHtml(text);
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/^- (.+)$/gm, "<li>$1</li>");
    html = html.replace(/(<li>.*<\/li>\n?)+/g, function (block) {
      return "<ul>" + block + "</ul>";
    });
    html = html.replace(/\n/g, "<br>");
    return html;
  }

  function applyMarkdownToAssistant(root) {
    const scope = root || document;
    scope.querySelectorAll(".chat-msg--assistant .chat-msg-text").forEach(function (el) {
      if (el.dataset.markdown === "1" || el.dataset.pending === "1") return;
      const raw = el.textContent || "";
      if (!raw.trim()) return;
      el.innerHTML = renderMarkdown(raw);
      el.dataset.markdown = "1";
    });
  }

  function formatDisplayTime(date) {
    const pad = function (n) {
      return String(n).padStart(2, "0");
    };
    return (
      pad(date.getDate()) +
      "." +
      pad(date.getMonth() + 1) +
      "." +
      date.getFullYear() +
      " " +
      pad(date.getHours()) +
      ":" +
      pad(date.getMinutes())
    );
  }

  function appendTimestamp(bodyEl) {
    if (bodyEl.querySelector(".chat-msg-time")) return;
    const el = document.createElement("div");
    el.className = "chat-msg-time";
    el.textContent = formatDisplayTime(new Date());
    bodyEl.appendChild(el);
  }

  function setSessionCookie(sessionId) {
    if (!sessionId) return;
    document.cookie =
      "ai_chat_session=" +
      encodeURIComponent(sessionId) +
      "; path=/; max-age=2592000; SameSite=Lax";
  }

  function showErrorBanner(text) {
    const banner = document.getElementById("ai-chat-error-banner");
    if (!banner) return;
    banner.textContent = text;
    banner.hidden = false;
  }

  function hideErrorBanner() {
    const banner = document.getElementById("ai-chat-error-banner");
    if (banner) banner.hidden = true;
  }

  function resizeCharts() {
    if (typeof echarts === "undefined") return;
    document.querySelectorAll(".chat-chart[data-rendered='1']").forEach(function (el) {
      const chart = chartInstances.get(el);
      if (chart) chart.resize();
    });
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
      el.setAttribute("role", "img");
      el.setAttribute("aria-label", option.title?.text || "График данных");
      chartInstances.set(el, chart);

      const toolbar = document.createElement("div");
      toolbar.className = "chat-chart-toolbar";
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn btn-ghost btn-sm";
      btn.textContent = "Скачать PNG";
      btn.addEventListener("click", function () {
        const url = chart.getDataURL({ type: "png", pixelRatio: 2 });
        const a = document.createElement("a");
        a.href = url;
        a.download = "chart.png";
        a.click();
      });
      toolbar.appendChild(btn);
      el.parentNode.insertBefore(toolbar, el.nextSibling);
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
    details.addEventListener("toggle", function () {
      if (details.open) setTimeout(resizeCharts, 50);
    });
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
    details.addEventListener("toggle", function () {
      if (details.open) setTimeout(resizeCharts, 50);
    });
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

  function appendRetryButton(turnEl, url) {
    if (turnEl.querySelector(".chat-retry-btn")) return;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-ghost btn-sm chat-retry-btn";
    btn.textContent = "Повторить";
    btn.addEventListener("click", function () {
      turnEl.removeAttribute("data-stream-done");
      const assistantMsg = turnEl.querySelector(".chat-msg--assistant");
      if (assistantMsg) {
        const textEl = assistantMsg.querySelector(".chat-msg-text");
        if (textEl) {
          textEl.textContent = "";
          textEl.removeAttribute("data-markdown");
          textEl.dataset.pending = "1";
          textEl.classList.add("chat-msg-text--pending");
        }
        assistantMsg.querySelectorAll(".chat-details, .chat-chart, .chat-chart-toolbar, .chat-retry-btn").forEach(function (n) {
          n.remove();
        });
      }
      activeStreams.delete(url);
      startStream(turnEl);
    });
    const body = turnEl.querySelector(".chat-msg--assistant .chat-msg-body");
    if (body) body.appendChild(btn);
  }

  function startStream(turnEl) {
    const url = turnEl.getAttribute("data-stream-url");
    if (!url || turnEl.dataset.streamDone === "1") return;
    if (activeStreams.has(url)) return;
    activeStreams.add(url);
    hideErrorBanner();

    const assistantMsg = turnEl.querySelector(".chat-msg--assistant");
    if (!assistantMsg) return;
    const textEl = assistantMsg.querySelector(".chat-msg-text");
    const bodyEl = assistantMsg.querySelector(".chat-msg-body");
    if (!textEl || !bodyEl) return;

    textEl.textContent = "";
    textEl.removeAttribute("data-markdown");
    textEl.classList.add("chat-msg-text--typing");

    const toolEl = document.createElement("div");
    toolEl.className = "chat-tool-status";
    toolEl.hidden = true;
    bodyEl.insertBefore(toolEl, textEl);

    const source = new EventSource(url);
    let plainText = "";

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
        const piece = typeof chunk === "string" ? chunk : String(chunk);
        plainText += piece;
        textEl.textContent = plainText;
      } catch (e) {
        plainText += ev.data;
        textEl.textContent = plainText;
      }
      scrollChatToBottom();
    });

    source.addEventListener("done", function (ev) {
      source.close();
      activeStreams.delete(url);
      turnEl.dataset.streamDone = "1";
      textEl.classList.remove("chat-msg-text--typing", "chat-msg-text--pending");
      textEl.removeAttribute("data-pending");
      toolEl.remove();

      let data;
      try {
        data = JSON.parse(ev.data);
      } catch (e) {
        appendRetryButton(turnEl, url);
        showErrorBanner("Не удалось разобрать ответ сервера.");
        return;
      }

      if (data.text) {
        plainText = data.text;
        textEl.textContent = plainText;
      }
      applyMarkdownToAssistant(turnEl);
      appendChart(bodyEl, data.chart);
      appendTable(bodyEl, data.table);
      appendSql(bodyEl, data.sql);
      appendTimestamp(bodyEl);
      scrollChatToBottom();
    });

    source.addEventListener("error", function (ev) {
      source.close();
      activeStreams.delete(url);
      turnEl.dataset.streamDone = "1";
      textEl.classList.remove("chat-msg-text--typing", "chat-msg-text--pending");
      textEl.removeAttribute("data-pending");
      toolEl.remove();
      let errText = "Ошибка при получении ответа.";
      try {
        const data = JSON.parse(ev.data || "{}");
        if (data.text) errText = data.text;
      } catch (e) {
        /* generic */
      }
      if (!plainText) {
        textEl.textContent = errText;
      }
      applyMarkdownToAssistant(turnEl);
      appendTimestamp(bodyEl);
      appendRetryButton(turnEl, url);
      showErrorBanner(errText);
      scrollChatToBottom();
    });
  }

  document.body.addEventListener("htmx:afterSwap", function (ev) {
    const target = ev.detail && ev.detail.target;
    if (!target) return;
    const swapped = ev.detail.elt;
    const turn =
      swapped && swapped.classList && swapped.classList.contains("ai-chat-turn")
        ? swapped
        : target.querySelector(".ai-chat-turn:last-child");
    if (turn && turn.hasAttribute("data-stream-url")) {
      startStream(turn);
    }
    renderCharts(target);
    scrollChatToBottom();
  });

  document.addEventListener("DOMContentLoaded", function () {
    renderCharts(document);
    applyMarkdownToAssistant(document);
    scrollChatToBottom();

    const form = document.getElementById("ai-chat-form");
    if (form) {
      const sessionInput = form.querySelector('input[name="session_id"]');
      if (sessionInput) setSessionCookie(sessionInput.value);

      form.addEventListener("submit", function () {
        hideErrorBanner();
        const textarea = form.querySelector("textarea[name=text]");
        if (textarea) {
          setTimeout(function () {
            textarea.value = "";
          }, 0);
        }
        if (sessionInput) setSessionCookie(sessionInput.value);
      });

      const textarea = form.querySelector("textarea[name=text]");
      if (textarea) {
        textarea.addEventListener("keydown", function (ev) {
          if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            form.requestSubmit();
          }
        });
      }
    }

    const historyToggle = document.getElementById("ai-chat-history-toggle");
    const layout = document.querySelector(".ai-chat-layout");
    if (historyToggle && layout) {
      historyToggle.addEventListener("click", function () {
        layout.classList.toggle("ai-chat-layout--history-collapsed");
      });
    }

    window.addEventListener("resize", resizeCharts);
  });
})();
