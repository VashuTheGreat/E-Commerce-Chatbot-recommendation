async function requestJson(url, options = {}) {
  const res = await fetch(url, { credentials: "include", ...options });
  const text = await res.text();
  let body;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = { data: null, message: text, success: res.ok };
  }
  if (!res.ok && !(body && body.success === false)) {
    throw new Error((body && body.message) || `HTTP ${res.status}`);
  }
  return body;
}

async function getHealth() {
  return requestJson(window.API_ENDPOINTS.HEALTH);
}

async function getAvailableTimeOptions() {
  const body = await requestJson(window.API_ENDPOINTS.AVAILABLE_TIME);
  return (body && body.data) || [];
}

async function loginUser(minutes) {
  const url = `${window.API_ENDPOINTS.USER_LOGIN}/${minutes}`;
  const res = await requestJson(url);
  if (res && res.success) {
    const durationMs = minutes * 60 * 1000;
    const expiryTime = Date.now() + durationMs;
    localStorage.setItem("session_expiry", expiryTime);
    localStorage.setItem("session_duration_minutes", minutes);
    window.location.href = window.PAGES.CHAT;
  } else {
    throw new Error((res && res.message) || "Failed to start session");
  }
}

async function trainModel() {
  return requestJson(window.API_ENDPOINTS.TRAIN, { method: "GET" });
}

function streamChat({ body, file, onChunk, onDone, onError }) {
  const fd = new FormData();
  fd.append("body", JSON.stringify(body));
  if (file) fd.append("file", file);

  fetch(window.API_ENDPOINTS.CHAT, {
    method: "POST",
    credentials: "include",
    body: fd,
  })
    .then(async (res) => {
      if (!res.ok || !res.body) {
        const txt = await res.text();
        throw new Error(txt || `HTTP ${res.status}`);
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let idx;
        while ((idx = buffer.indexOf("\n")) >= 0) {
          const line = buffer.slice(0, idx).trim();
          buffer = buffer.slice(idx + 1);
          if (line) onChunk(line);
        }
      }
      onDone && onDone();
    })
    .catch((err) => onError && onError(err));
}

function hasSessionCookie() {
  return document.cookie.split(";").some((c) => c.trim().startsWith("thread_id="));
}

window.api = {
  getHealth,
  getAvailableTimeOptions,
  loginUser,
  trainModel,
  streamChat,
  hasSessionCookie,
};
