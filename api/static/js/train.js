(function () {
  if (!window.api.hasSessionCookie()) {
    window.location.replace(window.PAGES.LOGIN);
    return;
  }

  const btn = document.getElementById("train-btn");
  const statusCard = document.getElementById("status-card");
  const statusText = document.getElementById("status-text");
  const spinner = document.getElementById("status-spinner");
  const result = document.getElementById("result");
  const logoutBtn = document.getElementById("logout-btn");

  function setRunning() {
    btn.disabled = true;
    btn.textContent = "Training&hellip";
    statusCard.classList.remove("hidden");
    spinner.style.display = "inline-block";
    statusText.textContent = "Running&hellip";
    result.textContent = "";
  }

  function setDone(body) {
    btn.disabled = false;
    btn.textContent = "Start training";
    spinner.style.display = "none";
    statusText.textContent = body && body.success ? "Done" : "Failed";
    result.textContent = JSON.stringify(body, null, 2);
  }

  btn.addEventListener("click", function () {
    if (!window.confirm("Run the full training pipeline? This can take minutes.")) return;
    setRunning();
    window.api.trainModel()
      .then(function (body) { setDone(body); })
      .catch(function (err) {
        setDone({ success: false, message: err.message, data: null });
      });
  });

  logoutBtn.addEventListener("click", function () {
    document.cookie = "thread_id=; Max-Age=0; path=/";
    window.location.replace(window.PAGES.LOGIN);
  });
})();
