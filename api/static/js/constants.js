const API_ENDPOINTS = Object.freeze({
  HEALTH: "/api/v1/common/health",
  AVAILABLE_TIME: "/api/v1/common/available_time",
  USER_LOGIN: "/api/v1/user/login",
  CHAT: "/api/v1/agent/chat",
  TRAIN: "/api/v1/model/train",
});

const PAGES = Object.freeze({
  HOME: "/",
  LOGIN: "/login",
  CHAT: "/chat",
  TRAIN: "/train",
  HEALTH: "/health",
});

window.API_ENDPOINTS = API_ENDPOINTS;
window.PAGES = PAGES;
