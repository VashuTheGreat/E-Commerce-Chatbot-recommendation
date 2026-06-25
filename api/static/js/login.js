(function () {
  const loadingEl = document.getElementById("loading");
  const optionsEl = document.getElementById("options");
  const statusEl = document.getElementById("status");

  function makeOption(opt, isPrimary) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn";
    btn.style.flexDirection = "column";
    btn.style.alignItems = "flex-start";
    btn.style.padding = "1rem";
    btn.style.background = isPrimary ? "var(--accent)" : "#0b1220";
    btn.style.border = "1px solid var(--border)";
    btn.dataset.seconds = String(opt.seconds);

    const top = document.createElement("span");
    top.style.fontSize = "1.1rem";
    const icon = document.createTextNode((opt.icon || "⏱") + " ");
    const strong = document.createElement("strong");
    strong.textContent = opt.label;
    top.appendChild(icon);
    top.appendChild(strong);

    const sub = document.createElement("span");
    sub.style.fontSize = "0.8rem";
    sub.style.color = "var(--muted)";
    sub.style.fontWeight = "400";
    sub.textContent = opt.description || "";

    btn.appendChild(top);
    btn.appendChild(sub);
    btn.addEventListener("click", function () { onPick(opt); });
    return btn;
  }

  function renderOptions(options) {
    loadingEl.classList.add("hidden");
    optionsEl.classList.remove("hidden");
    optionsEl.innerHTML = "";
    options.forEach(function (opt, i) {
      optionsEl.appendChild(makeOption(opt, i === 0));
    });
  }

  function onPick(opt) {
    const minutes = Math.max(1, Math.round(opt.seconds / 60));
    const buttons = optionsEl.querySelectorAll("button");
    buttons.forEach(function (b) { b.disabled = true; });
    statusEl.textContent = "Creating " + opt.label + " session…";
    window.api.loginUser(minutes).catch(function (err) {
      buttons.forEach(function (b) { b.disabled = false; });
      statusEl.innerHTML = "";
      const badge = document.createElement("span");
      badge.className = "badge error";
      badge.textContent = "Error starting session";
      statusEl.appendChild(badge);
      statusEl.appendChild(document.createTextNode(" " + err.message));
    });
  }

  async function init() {
    try {
      const options = await window.api.getAvailableTimeOptions();
      if (!options.length) {
        loadingEl.textContent = "No session options available.";
        return;
      }
      renderOptions(options);
    } catch (err) {
      loadingEl.classList.add("hidden");
      statusEl.innerHTML = "";
      const badge = document.createElement("span");
      badge.className = "badge error";
      badge.textContent = "Server unreachable";
      statusEl.appendChild(badge);
      statusEl.appendChild(document.createTextNode(" " + err.message));
    }
  }

  init();
})();
