const byId = (id) => document.getElementById(id);

function setText(id, value) {
  const element = byId(id);
  if (element) element.textContent = value;
}

function renderChecks(checks) {
  const container = byId("governance-checks");
  container.replaceChildren();
  checks.forEach((check) => {
    const item = document.createElement("div");
    item.className = `check ${check.ok ? "ok" : "fail"}`;
    const dot = document.createElement("span");
    dot.className = "check-dot";
    dot.setAttribute("aria-hidden", "true");
    const copy = document.createElement("div");
    const title = document.createElement("strong");
    const detail = document.createElement("small");
    title.textContent = `${check.ok ? "PASS" : "FAIL"} · ${check.id}`;
    detail.textContent = check.description;
    copy.append(title, detail);
    item.append(dot, copy);
    container.append(item);
  });
}

function renderTargets(targets) {
  const container = byId("target-grid");
  container.replaceChildren();
  targets.forEach((target) => {
    const card = document.createElement("article");
    card.className = `target-card state-${target.state.toLowerCase()}`;
    const heading = document.createElement("div");
    heading.className = "target-heading";
    const copy = document.createElement("div");
    const title = document.createElement("strong");
    const kind = document.createElement("small");
    title.textContent = target.name;
    kind.textContent = `${target.id} · ${target.kind}`;
    copy.append(title, kind);
    const state = document.createElement("span");
    state.className = "target-state";
    state.textContent = target.state;
    heading.append(copy, state);
    const checks = document.createElement("ul");
    target.checks.forEach((check) => {
      const item = document.createElement("li");
      item.innerHTML = `<span>${check.id}</span><strong>${check.state}</strong>`;
      checks.append(item);
    });
    const authority = document.createElement("p");
    authority.className = "target-authority";
    authority.textContent = `${target.actions} ação(ões) allowlisted · plan-only`;
    card.append(heading, checks, authority);
    container.append(card);
  });
}

function renderActions(actions) {
  const container = byId("action-list");
  container.replaceChildren();
  actions.forEach((action) => {
    const item = document.createElement("div");
    item.className = "action-item";
    const name = document.createElement("strong");
    name.textContent = action.id;
    const meta = document.createElement("span");
    meta.textContent = `${action.risk} · ${action.mode}`;
    item.append(name, meta);
    container.append(item);
  });
}

async function loadSnapshot() {
  try {
    const response = await fetch("/api/snapshot", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    setText("generated-at", `snapshot ${data.generated_at}`);
    setText("system-version", `versão ${data.system.version}`);
    setText("system-mode", data.system.mode);
    setText("hero-phase", data.system.harness_phase);
    setText("phase-label", data.system.harness_phase);
    setText("roadmap-phase", data.system.harness_phase);
    setText("governance-state", data.governance.status);
    setText("governance-chip", data.governance.status);
    setText("agent-count", data.governance.agents);
    setText("skill-count", data.governance.skills);
    setText("target-count", data.ecosystem.targets.length);
    setText("ecosystem-chip", data.ecosystem.status);
    setText("scenario-count", data.harness.scenarios);
    setText("evidence-count", data.harness.evidence_files);
    setText("report-count", data.harness.report_files);
    setText("llm-state", data.safety.llm_provider);
    setText("mutation-state", data.safety.mutating_skills_enabled ? "ENABLED" : "DISABLED");
    setText("action-mode", data.actions.execution_enabled ? "ENABLED" : "PLAN");
    renderTargets(data.ecosystem.targets);
    renderActions(data.actions.catalog);
    renderChecks(data.governance.checks);
  } catch (error) {
    setText("generated-at", "snapshot indisponível");
    const container = byId("governance-checks");
    container.replaceChildren();
    const message = document.createElement("p");
    message.className = "error-state";
    message.textContent = `Não foi possível ler o snapshot observacional: ${error.message}`;
    container.append(message);
  }
}

loadSnapshot();
setInterval(loadSnapshot, 15000);
