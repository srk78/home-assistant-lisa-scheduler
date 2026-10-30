/* LISA Scheduler sidebar panel: upcoming matches and training sessions. */

const REFRESH_MS = 60000;
const FILTERS = [
  { id: "all", label: "All" },
  { id: "match", label: "Matches" },
  { id: "training", label: "Trainings" },
];
const TYPE_LABELS = { match: "Match", training: "Training" };

const escapeHtml = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
  );

class LisaSchedulerPanel extends HTMLElement {
  constructor() {
    super();
    this._events = [];
    this._filter = "all";
    this._error = null;
    this._loaded = false;
    this._timer = null;
    this.attachShadow({ mode: "open" });
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first) {
      this._load();
    }
  }

  set narrow(value) {
    this._narrow = value;
    this._render();
  }

  connectedCallback() {
    this._timer = setInterval(() => this._load(), REFRESH_MS);
    this._render();
  }

  disconnectedCallback() {
    clearInterval(this._timer);
    this._timer = null;
  }

  async _load() {
    if (!this._hass) return;
    try {
      const result = await this._hass.connection.sendMessagePromise({
        type: "lisa_scheduler/upcoming_events",
      });
      this._events = result.events;
      this._error = null;
    } catch (err) {
      this._error = err.message || "Could not load the schedule";
    }
    this._loaded = true;
    this._render();
  }

  _visibleEvents() {
    return this._events.filter((e) => this._filter === "all" || e.event_type === this._filter);
  }

  _formatDay(iso) {
    const locale = this._hass?.locale?.language || undefined;
    return new Date(iso).toLocaleDateString(locale, {
      weekday: "long",
      day: "numeric",
      month: "long",
    });
  }

  _formatTime(iso) {
    const locale = this._hass?.locale?.language || undefined;
    return new Date(iso).toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" });
  }

  _renderBody() {
    if (this._error) {
      return `<div class="message error">${escapeHtml(this._error)}</div>`;
    }
    if (!this._loaded) {
      return `<div class="message">Loading…</div>`;
    }
    const events = this._visibleEvents();
    if (!events.length) {
      return `<div class="message">No upcoming events.</div>`;
    }

    const days = new Map();
    for (const event of events) {
      const day = event.start_time.slice(0, 10);
      if (!days.has(day)) days.set(day, []);
      days.get(day).push(event);
    }

    let html = "";
    for (const [, dayEvents] of days) {
      html += `<h2>${escapeHtml(this._formatDay(dayEvents[0].start_time))}</h2>`;
      for (const event of dayEvents) {
        const type = TYPE_LABELS[event.event_type] || "Event";
        const end = event.end_time_estimated ? "~" : "";
        html += `
          <div class="event ${escapeHtml(event.event_type)}">
            <div class="time">${this._formatTime(event.start_time)}<span>${end}${this._formatTime(event.end_time)}</span></div>
            <div class="details">
              <div class="title">${escapeHtml(event.title || type)}</div>
              ${event.location ? `<div class="location">${escapeHtml(event.location)}</div>` : ""}
            </div>
            <span class="badge">${escapeHtml(type)}</span>
          </div>`;
      }
    }
    return html;
  }

  _render() {
    if (!this.shadowRoot) return;
    const tabs = FILTERS.map(
      (f) =>
        `<button class="tab ${f.id === this._filter ? "active" : ""}" data-filter="${f.id}">${f.label}</button>`
    ).join("");

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          min-height: 100%;
          background: var(--primary-background-color);
          color: var(--primary-text-color);
          font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
        }
        header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 16px;
          padding: 12px 16px;
          background: var(--app-header-background-color, var(--primary-color));
          color: var(--app-header-text-color, #fff);
        }
        header h1 { margin: 0; font-size: 20px; font-weight: 400; }
        header button.menu {
          display: ${this._narrow ? "inline-block" : "none"};
        }
        .tabs { display: flex; gap: 8px; }
        button {
          font: inherit;
          cursor: pointer;
        }
        .tab {
          padding: 6px 14px;
          border: 1px solid currentColor;
          border-radius: 16px;
          background: transparent;
          color: inherit;
          opacity: 0.8;
        }
        .tab.active { background: rgba(255, 255, 255, 0.25); opacity: 1; }
        main { max-width: 760px; margin: 0 auto; padding: 8px 16px 32px; }
        h2 {
          margin: 24px 0 8px;
          font-size: 14px;
          font-weight: 500;
          text-transform: capitalize;
          color: var(--secondary-text-color);
        }
        .event {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 8px;
          padding: 12px 16px;
          border-radius: 12px;
          border-left: 4px solid var(--divider-color);
          background: var(--card-background-color, #fff);
          box-shadow: var(--ha-card-box-shadow, none);
        }
        .event.match { border-left-color: var(--accent-color, #ff9800); }
        .event.training { border-left-color: var(--primary-color, #03a9f4); }
        .time { min-width: 56px; font-weight: 500; font-variant-numeric: tabular-nums; }
        .time span { display: block; font-weight: 400; color: var(--secondary-text-color); }
        .details { flex: 1; min-width: 0; }
        .title { font-weight: 500; overflow-wrap: anywhere; }
        .location { color: var(--secondary-text-color); font-size: 13px; }
        .badge {
          padding: 2px 10px;
          border-radius: 10px;
          font-size: 12px;
          background: var(--secondary-background-color);
          color: var(--secondary-text-color);
        }
        .message { padding: 48px 0; text-align: center; color: var(--secondary-text-color); }
        .message.error { color: var(--error-color, #db4437); }
      </style>
      <header>
        <button class="menu" aria-label="Menu">☰</button>
        <h1>Upcoming games &amp; training</h1>
        <div class="tabs">${tabs}</div>
      </header>
      <main>${this._renderBody()}</main>`;

    this.shadowRoot.querySelectorAll(".tab").forEach((button) =>
      button.addEventListener("click", () => {
        this._filter = button.dataset.filter;
        this._render();
      })
    );
    this.shadowRoot.querySelector(".menu").addEventListener("click", () =>
      this.dispatchEvent(new Event("hass-toggle-menu", { bubbles: true, composed: true }))
    );
  }
}

customElements.define("lisa-scheduler-panel", LisaSchedulerPanel);
