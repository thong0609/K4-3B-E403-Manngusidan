/**
 * ScriptScout API Service Layer
 * 
 * Single source of truth cho mọi network request.
 * UI components không bao giờ gọi fetch() trực tiếp — luôn đi qua API.
 * Exposed as: window.API
 */
(function () {
  "use strict";

  const BASE = window.location.origin.includes(":8000")
    ? ""
    : "http://127.0.0.1:8000";

  /**
   * Internal: Generic request helper.
   * Throws Error với message từ API hoặc HTTP status nếu thất bại.
   */
  async function request(method, path, body) {
    const options = {
      method,
      headers: body ? { "Content-Type": "application/json" } : {},
      body: body ? JSON.stringify(body) : undefined,
    };
    const res = await fetch(`${BASE}${path}`, options);
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP ${res.status}: ${res.statusText}`);
    }
    return res;
  }

  window.API = {
    /** Check server availability */
    async health() {
      const res = await fetch(`${BASE}/`);
      if (!res.ok) throw new Error("offline");
      return res.json();
    },

    /** Create a new script generation session */
    async createSession(topic, learningGoal, audience, durationMinutes) {
      const res = await request("POST", "/api/sessions", {
        topic,
        learning_goal: learningGoal,
        audience,
        duration_minutes: Number(durationMinutes),
      });
      return res.json();
    },

    /** Trigger the web search agent for a session */
    async startSearch(sessionId) {
      const res = await request("POST", `/api/sessions/${sessionId}/search`);
      return res.json();
    },

    /** Get current session state (used for polling) */
    async getSession(sessionId) {
      const res = await request("GET", `/api/sessions/${sessionId}`);
      return res.json();
    },

    /** Fetch all sources for a session */
    async getSources(sessionId) {
      const res = await request("GET", `/api/sessions/${sessionId}/sources`);
      return res.json();
    },

    /** Add a custom URL as a source */
    async addSource(sessionId, url) {
      const res = await request("POST", `/api/sessions/${sessionId}/sources`, { url });
      return res.json();
    },

    /** Toggle a source active state */
    async toggleSource(sessionId, code, isActive) {
      const res = await request("PATCH", `/api/sessions/${sessionId}/sources/${code}`, {
        is_active: isActive,
      });
      return res.json();
    },

    /** Kick off script generation */
    async generateScript(sessionId) {
      const res = await request("POST", `/api/sessions/${sessionId}/script`);
      return res.json();
    },

    /**
     * Export the script.
     * @param {"markdown"|"json"} format
     */
    async export(sessionId, format = "markdown") {
      const res = await request("GET", `/api/sessions/${sessionId}/export?format=${format}`);
      return format === "json" ? res.json() : res.text();
    },

    /**
     * Poll session status until "sources_ready" or "error".
     * @param {string} sessionId
     * @param {object} options
     * @param {function} [options.onAttempt] - Called each poll: (status, attempt)
     * @param {number}   [options.intervalMs=2500]
     * @param {number}   [options.maxAttempts=120]  -- 120 × 2500ms = 300s max
     */
    async pollUntilReady(sessionId, { onAttempt, intervalMs = 2500, maxAttempts = 120 } = {}) {
      for (let attempt = 0; attempt < maxAttempts; attempt++) {
        await new Promise((r) => setTimeout(r, intervalMs));
        const session = await this.getSession(sessionId);
        if (onAttempt) onAttempt(session.status, attempt);
        // Accept sources_ready or done (backend may set done if search + script ran together)
        if (session.status === "sources_ready" || session.status === "done") return session;
        if (session.status === "error") {
          throw new Error(session.error || "Agent gặp lỗi trong quá trình xử lý.");
        }
      }
      throw new Error("Quá thời gian chờ (>300s). Hãy kiểm tra lại kết nối mạng hoặc API key Tavily.");
    },
  };
})();
