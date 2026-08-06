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
    title.textContent = check.ok ? `PASS · ${check.id}` : `FAIL · ${check.id}`;
    detail.textContent = check.description;

    copy.append(title, detail);
    item.append(dot, copy);
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
    setText("governance-state", data.governance.status);
    setText("governance-chip", data.governance.status);
    setText("agent-count", data.governance.agents);
    setText("skill-count", data.governance.skills);
    setText("scenario-count", data.harness.scenarios);
    setText("evidence-count", data.harness.evidence_files);
    setText("report-count", data.harness.report_files);
    setText("llm-state", data.safety.llm_provider);
    setText("mutation-state", data.safety.mutating_skills_enabled ? "ENABLED" : "DISABLED");
    setText("phase-label", data.system.harness_phase);
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
