(() => {
  "use strict";

  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const formatTime = (value) => {
    if (!value) return "time not preserved";
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
  };

  const badgeClass = (status) => status === "QUALIFIED" ? "pass" : "progress";
  const statusClass = (status) => status === "QUALIFIED" ? "status-qualified" : "status-in-progress";
  const compactMilestone = (value) => String(value || "").replace(/^CWTV\.V/, "");

  function renderSummary(data) {
    const summary = data.summary;
    byId("current-milestone").textContent = `Current · ${summary.current_milestone}`;
    const cards = [
      ["Tracked milestones", summary.tracked_milestones],
      ["Qualified", summary.qualified_milestones],
      ["Passed events", summary.passed_events],
      ["Failed events", summary.failed_events],
      ["Corrections", summary.corrections],
      ["Commits", summary.commits],
    ];
    byId("summary-grid").innerHTML = cards.map(([label, value]) => `
      <article class="summary-card">
        <span class="label">${escapeHtml(label)}</span>
        <span class="value">${escapeHtml(value)}</span>
      </article>
    `).join("");

    const completion = Number(summary.tracked_completion_percent || 0);
    byId("overall-progress-label").textContent = `${completion.toFixed(1)}%`;
    requestAnimationFrame(() => {
      byId("overall-progress-bar").style.width = `${Math.max(0, Math.min(100, completion))}%`;
    });
    byId("ledger-head").textContent = `${data.ledger.head_event_id} · ${data.ledger.event_count} events`;
  }

  function renderMilestones(data) {
    byId("milestone-list").innerHTML = data.milestones.map((item) => {
      const currentClass = item.milestone === data.summary.current_milestone ? "current-milestone-card" : "";
      const progress = Math.max(0, Math.min(100, Number(item.progress_percent) || 0));
      return `
        <article class="milestone-card ${statusClass(item.status)} ${currentClass}">
          <div class="milestone-top">
            <div class="milestone-title">
              <h3><code>${escapeHtml(item.milestone)}</code></h3>
              <span class="badge ${badgeClass(item.status)}">${escapeHtml(item.status)}</span>
            </div>
            <strong>${escapeHtml(item.progress_percent)}%</strong>
          </div>
          <div class="progress-track"><div class="progress-bar" data-progress="${progress}"></div></div>
          <div class="milestone-meta">
            <span>Difficulty<strong>${escapeHtml(item.observed_difficulty)}/5</strong></span>
            <span>Failures<strong>${escapeHtml(item.failure_count)}</strong></span>
            <span>Corrections<strong>${escapeHtml(item.correction_count)}</strong></span>
            <span>Elapsed<strong>${escapeHtml(item.elapsed_label)}</strong></span>
            <span>Command runtime<strong>${escapeHtml(item.recorded_command_runtime_label)}</strong></span>
          </div>
        </article>
      `;
    }).join("");

    requestAnimationFrame(() => {
      document.querySelectorAll(".milestone-card .progress-bar[data-progress]").forEach((bar) => {
        bar.style.width = `${bar.dataset.progress}%`;
      });
    });
  }

  function renderDifficulty(data) {
    const container = byId("difficulty-chart");
    const items = data.milestones;
    if (!container || !items.length) return;

    const width = Math.max(300, Math.floor(container.getBoundingClientRect().width || 300));
    const height = width < 430 ? 270 : 300;
    const left = width < 430 ? 28 : 34;
    const right = width < 430 ? 12 : 18;
    const top = 22;
    const bottom = width < 430 ? 52 : 44;
    const chartHeight = height - top - bottom;
    const usableWidth = Math.max(1, width - left - right);
    const step = items.length > 1 ? usableWidth / (items.length - 1) : usableWidth;
    const y = (score) => top + chartHeight - ((Number(score) - 1) / 4) * chartHeight;
    const points = items.map((item, index) => ({
      x: items.length > 1 ? left + step * index : left + usableWidth / 2,
      y: y(item.observed_difficulty),
      item,
    }));
    const linePath = points.map((point, index) => `${index === 0 ? "M" : "L"}${point.x},${point.y}`).join(" ");
    const baseline = y(1);
    const areaPath = points.length > 1
      ? `${linePath} L${points.at(-1).x},${baseline} L${points[0].x},${baseline} Z`
      : "";
    const grid = [1, 2, 3, 4, 5].map((score) => {
      const yy = y(score);
      return `<line class="axis" x1="${left}" y1="${yy}" x2="${width - right}" y2="${yy}"></line><text x="4" y="${yy + 3}">${score}</text>`;
    }).join("");
    const marks = points.map((point, index) => {
      const score = Number(point.item.observed_difficulty);
      const severity = score >= 4 ? "high" : score >= 2.5 ? "mid" : "";
      const labelY = height - (index % 2 === 0 ? 20 : 8);
      return `
        <circle class="point ${severity}" cx="${point.x}" cy="${point.y}" r="4.5"></circle>
        <text class="x-label" x="${point.x}" y="${labelY}" text-anchor="middle">${escapeHtml(compactMilestone(point.item.milestone))}</text>
        <text class="score" x="${point.x}" y="${Math.max(12, point.y - 10)}" text-anchor="middle">${escapeHtml(point.item.observed_difficulty)}</text>
      `;
    }).join("");

    container.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
        <defs>
          <linearGradient id="difficultyLineGradient" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="#22d3ee"></stop>
            <stop offset="52%" stop-color="#60a5fa"></stop>
            <stop offset="100%" stop-color="#a78bfa"></stop>
          </linearGradient>
          <linearGradient id="difficultyAreaGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#22d3ee" stop-opacity=".18"></stop>
            <stop offset="100%" stop-color="#22d3ee" stop-opacity="0"></stop>
          </linearGradient>
        </defs>
        ${grid}
        ${areaPath ? `<path class="area" d="${areaPath}"></path>` : ""}
        <path class="line" d="${linePath}"></path>
        ${marks}
      </svg>
    `;
  }

  function renderTiming(data) {
    const current = data.milestones.find((item) => item.milestone === data.summary.current_milestone) || data.milestones.at(-1);
    if (!current) {
      byId("timing-list").textContent = "No timing data recorded.";
      return;
    }
    const rows = [
      ["Current milestone", current.milestone],
      ["Elapsed", current.elapsed_label],
      ["Recorded command runtime", current.recorded_command_runtime_label],
      ["Active session time", current.active_session_label],
      ["Paused time", current.paused_label],
      ["Explicit breaks", current.session_data_present ? current.break_count : "not preserved"],
    ];
    byId("timing-list").innerHTML = rows.map(([label, value]) => `
      <div class="timing-row"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>
    `).join("");
  }

  function renderFailures(data) {
    const tbody = byId("failures-body");
    if (!data.failures.length) {
      tbody.innerHTML = `<tr><td colspan="5">No failed events recorded.</td></tr>`;
      return;
    }
    tbody.innerHTML = data.failures.map((event) => `
      <tr>
        <td><code>${escapeHtml(event.milestone)}</code></td>
        <td>${escapeHtml(formatTime(event.occurred_at))}</td>
        <td>${escapeHtml(event.component || "—")}</td>
        <td>${escapeHtml(event.summary)}</td>
        <td>${escapeHtml(event.correction || "—")}</td>
      </tr>
    `).join("");
  }

  function renderArtifacts(data) {
    const seen = new Set();
    const unique = data.artifacts.filter((event) => {
      const key = `${event.artifact?.name || ""}|${event.artifact?.sha256 || ""}|${event.event_type}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
    byId("artifact-list").innerHTML = unique.length ? unique.map((event) => `
      <div class="stack-item">
        <strong><code>${escapeHtml(event.artifact.name)}</code></strong>
        <div class="sub">${escapeHtml(event.event_type)} · ${escapeHtml(formatTime(event.occurred_at))}</div>
        <div class="sub">${event.artifact.sha256 ? `SHA-256 ${escapeHtml(event.artifact.sha256)}` : "SHA-256 recorded after finalized archive verification"}</div>
      </div>
    `).join("") : `<div class="stack-item">No artifact events recorded.</div>`;
  }

  function renderCommits(data) {
    byId("commit-list").innerHTML = data.commits.length ? data.commits.map((event) => `
      <div class="stack-item">
        <strong><code>${escapeHtml(event.commit)}</code></strong>
        <div class="sub">${escapeHtml(event.summary)}</div>
        <div class="sub">${escapeHtml(formatTime(event.occurred_at))}</div>
      </div>
    `).join("") : `<div class="stack-item">No commit events recorded.</div>`;
  }

  function renderTimeline(data) {
    byId("timeline").innerHTML = data.events.map((event) => {
      const klass = event.result === "FAILED" ? "failed" : (event.result === "PASS" || event.result === "QUALIFIED" ? "passed" : "");
      const evidence = event.evidence?.length ? `<small>${escapeHtml(event.evidence.join(" · "))}</small>` : "";
      const duration = event.duration_seconds != null ? `<small>Duration: ${escapeHtml(event.duration_seconds)}s</small>` : "";
      return `
        <article class="timeline-item ${klass}">
          <div class="timeline-time">${escapeHtml(formatTime(event.occurred_at))}</div>
          <div class="timeline-type"><code>${escapeHtml(event.event_type)}</code></div>
          <div class="timeline-summary"><strong>${escapeHtml(event.milestone)}</strong> · ${escapeHtml(event.summary)}${duration}${evidence}</div>
        </article>
      `;
    }).join("");
  }

  function setupRevealAnimations() {
    const items = [...document.querySelectorAll(".summary-card, .overall-progress, .milestone-card, .panel, .table-wrap, .timeline-item")];
    items.forEach((item, index) => {
      item.classList.add("reveal");
      item.style.setProperty("--reveal-delay", `${Math.min(index % 6, 5) * 35}ms`);
    });

    if (!("IntersectionObserver" in window)) {
      items.forEach((item) => item.classList.add("is-visible"));
      return;
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.06, rootMargin: "0px 0px -28px 0px" });

    items.forEach((item) => observer.observe(item));
  }

  let dashboardData = null;
  let resizeTimer = null;

  function renderAll(data) {
    dashboardData = data;
    renderSummary(data);
    renderMilestones(data);
    renderDifficulty(data);
    renderTiming(data);
    renderFailures(data);
    renderArtifacts(data);
    renderCommits(data);
    renderTimeline(data);
    setupRevealAnimations();
  }

  window.addEventListener("resize", () => {
    if (!dashboardData) return;
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(() => renderDifficulty(dashboardData), 120);
  });

  fetch("./progress-data.json", { cache: "no-store" })
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then(renderAll)
    .catch((error) => {
      console.error(error);
      byId("load-error").hidden = false;
      byId("current-milestone").textContent = "Data unavailable";
    });
})();
