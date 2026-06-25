(function () {
  const healthBadge = document.getElementById("health-badge");
  const healthMsg = document.getElementById("health-msg");
  const timeGrid = document.getElementById("time-grid");
  const apiTable = document.getElementById("api-table");

  function makeTimeCard(opt) {
    const card = document.createElement("div");
    card.className = "card";
    card.style.padding = "1rem";
    card.style.background = "#0b1220";
    const icon = document.createElement("div");
    icon.style.fontSize = "1.5rem";
    icon.textContent = opt.icon || "⏱";
    const label = document.createElement("div");
    label.className = "font-bold mt-1";
    label.textContent = opt.label;
    const desc = document.createElement("div");
    desc.style.fontSize = "0.8rem";
    desc.style.color = "var(--muted)";
    desc.textContent = opt.description || "";
    const secs = document.createElement("div");
    secs.style.fontSize = "0.75rem";
    secs.style.marginTop = "0.25rem";
    secs.style.color = "var(--muted)";
    secs.textContent = opt.seconds + "s";
    card.appendChild(icon);
    card.appendChild(label);
    card.appendChild(desc);
    card.appendChild(secs);
    return card;
  }

  function makeRow(method, path, auth) {
    const tr = document.createElement("tr");
    tr.style.borderTop = "1px solid var(--border)";
    const td1 = document.createElement("td");
    td1.className = "py-2";
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = method;
    if (method === "GET") badge.style.color = "var(--success)";
    else if (method === "POST") badge.style.color = "var(--accent)";
    else if (method === "PUT") badge.style.color = "#f59e0b";
    else if (method === "DELETE") badge.style.color = "var(--error)";
    td1.appendChild(badge);
    const td2 = document.createElement("td");
    td2.style.fontFamily = "ui-monospace, monospace";
    td2.textContent = path;
    const td3 = document.createElement("td");
    td3.textContent = auth;
    tr.appendChild(td1); tr.appendChild(td2); tr.appendChild(td3);
    return tr;
  }

  async function loadHealth() {
    try {
      const body = await window.api.getHealth();
      healthBadge.classList.add("success");
      healthBadge.textContent = "Healthy";
      healthMsg.textContent = (body && body.message) || "Server is fit and fine";
    } catch (err) {
      healthBadge.classList.add("error");
      healthBadge.textContent = "Unreachable";
      healthMsg.textContent = err.message;
    }
  }

  async function loadTimeOptions() {
    try {
      const options = await window.api.getAvailableTimeOptions();
      options.forEach(function (opt) { timeGrid.appendChild(makeTimeCard(opt)); });
    } catch (err) {
      timeGrid.textContent = "Failed to load options: " + err.message;
    }
  }

  function renderEndpoints() {
    const rows = [
      ["GET", window.API_ENDPOINTS.HEALTH, "no"],
      ["GET", window.API_ENDPOINTS.AVAILABLE_TIME, "no"],
      ["GET", window.API_ENDPOINTS.USER_LOGIN + "/{minutes}", "no"],
      ["POST", window.API_ENDPOINTS.CHAT, "yes (thread_id cookie)"],
      ["GET", window.API_ENDPOINTS.TRAIN, "yes (thread_id cookie)"],
    ];
    rows.forEach(function (r) { apiTable.appendChild(makeRow(r[0], r[1], r[2])); });
  }

  loadHealth();
  loadTimeOptions();
  renderEndpoints();
})();
