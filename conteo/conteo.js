// 1PIXEL Conteo dashboard
// Reads `1pixel-conteo-api` Worker for password-gated Camlytics data.

const API_BASE = "https://1pixel-conteo-api.ai-ffd.workers.dev";
const TOKEN_KEY = "1pixel_conteo_token";
const REFRESH_MS = 60 * 60 * 1000;

const GALLERIES = [
  {
    id: "3h",
    short: "Av 3H",
    label: "AV 3H Corredor Gastronómico",
    active: true,
  },
  {
    id: "calle77",
    short: "Calle 77",
    label: "Calle 77 con Av. Bella Vista",
    active: false,
  },
  {
    id: "cecilio",
    short: "Cecilio Acosta",
    label: "Calle 67 Cecilio Acosta",
    active: false,
  },
  {
    id: "bellavista",
    short: "Bella Vista 72",
    label: "Bella Vista con Calle 72",
    active: false,
  },
  {
    id: "5dejulio",
    short: "5 de Julio",
    label: "5 de Julio con Delicias",
    active: false,
  },
  { id: "vereda", short: "Vereda", label: "Vereda del Lago", active: false },
];

const VEHICLE_META = {
  Car: { label: "Carros", icon: "🚗" },
  Motorcycle: { label: "Motos", icon: "🏍" },
  Truck: { label: "Camiones", icon: "🚚" },
  Bus: { label: "Buses", icon: "🚌" },
  Bicycle: { label: "Bicicletas", icon: "🚲" },
  Human: { label: "Peatones", icon: "🚶" },
  Other: { label: "Otros", icon: "·" },
};

let currentGallery = "3h";
let chart = null;
let refreshTimer = null;

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("year").textContent = new Date().getFullYear();
  bindDashboardControls();
  showDashboard();
});

// ---------- Auth ----------

function getToken() {
  try {
    const raw = localStorage.getItem(TOKEN_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (parsed.exp && parsed.exp * 1000 < Date.now()) {
      localStorage.removeItem(TOKEN_KEY);
      return null;
    }
    return parsed.token;
  } catch {
    return null;
  }
}

function setToken(token, exp) {
  localStorage.setItem(TOKEN_KEY, JSON.stringify({ token, exp }));
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function bindDashboardControls() {
  document
    .getElementById("refresh-btn")
    .addEventListener("click", () =>
      loadGallery(currentGallery, { force: true }),
    );
  document
    .getElementById("retry-btn")
    .addEventListener("click", () => loadGallery(currentGallery));
}

// ---------- Views ----------

function showDashboard() {
  renderTabs();
  loadGallery(currentGallery);
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(() => loadGallery(currentGallery), REFRESH_MS);
}

function renderTabs() {
  const wrap = document.getElementById("tabs");
  while (wrap.firstChild) wrap.removeChild(wrap.firstChild);
  for (const g of GALLERIES) {
    const btn = document.createElement("button");
    btn.className = "tab" + (g.id === currentGallery ? " active" : "");
    btn.dataset.gallery = g.id;
    const dot = document.createElement("span");
    dot.className = "tab-dot" + (g.active ? " live" : "");
    btn.appendChild(dot);
    btn.appendChild(document.createTextNode(g.short));
    btn.addEventListener("click", () => {
      currentGallery = g.id;
      for (const child of wrap.children) {
        child.classList.toggle("active", child.dataset.gallery === g.id);
      }
      loadGallery(g.id);
    });
    wrap.appendChild(btn);
  }
}

function setState(name) {
  for (const s of ["loading", "data", "inactive", "error"]) {
    const el = document.getElementById(`state-${s}`);
    if (el) el.hidden = s !== name;
  }
}

// ---------- Data ----------

async function loadGallery(galleryId, { force = false } = {}) {
  setState("loading");
  document.getElementById("last-update").textContent = "Cargando…";

  try {
    const url = `${API_BASE}/api/data?gallery=${encodeURIComponent(galleryId)}${force ? "&_=" + Date.now() : ""}`;
    const res = await fetch(url);
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || body.error || `HTTP ${res.status}`);
    }
    const data = await res.json();
    if (!data.active) {
      setState("inactive");
      const el = document.querySelector("#state-inactive p");
      if (el)
        el.textContent =
          data.message || "Galería próximamente. Sin datos disponibles aún.";
      document.getElementById("last-update").textContent = data.label || "";
      return;
    }
    renderData(data);
    setState("data");
  } catch (err) {
    document.getElementById("state-error-msg").textContent = err.message;
    setState("error");
    document.getElementById("last-update").textContent = "Error al cargar";
  }
}

function renderData(data) {
  const fmtNumber = (n) => (n || 0).toLocaleString("es-VE");
  document.getElementById("kpi-today").textContent = fmtNumber(
    data.totals.today,
  );
  document.getElementById("kpi-week").textContent = fmtNumber(data.totals.week);
  document.getElementById("kpi-month").textContent = fmtNumber(
    data.totals.month,
  );

  const ts = data.generated_at ? new Date(data.generated_at) : new Date();
  const cachedTag = data.cached ? " · desde caché" : "";
  document.getElementById("last-update").textContent =
    `${data.label} · Actualizado ${ts.toLocaleTimeString("es-VE", {
      hour: "2-digit",
      minute: "2-digit",
    })}${cachedTag}`;

  renderHourly(data.hourly || []);
  renderTypes(data.byType || {}, data.sample_events || 0);
}

function renderHourly(hourly) {
  const ctx = document.getElementById("hourly-chart").getContext("2d");
  const labels = Array.from(
    { length: 24 },
    (_, i) => i.toString().padStart(2, "0") + "h",
  );
  const grad = ctx.createLinearGradient(0, 0, 0, 280);
  grad.addColorStop(0, "rgba(139, 92, 255, 0.55)");
  grad.addColorStop(1, "rgba(139, 92, 255, 0.02)");

  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Conteo",
          data: hourly,
          fill: true,
          backgroundColor: grad,
          borderColor: "#b69bff",
          borderWidth: 2,
          tension: 0.35,
          pointRadius: 0,
          pointHoverRadius: 5,
          pointHoverBackgroundColor: "#ff3bd4",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#1c1c25",
          borderColor: "rgba(139, 92, 255, 0.4)",
          borderWidth: 1,
          titleColor: "#fff",
          bodyColor: "#d6d6e0",
          padding: 12,
        },
      },
      scales: {
        x: {
          grid: { color: "rgba(255,255,255,0.04)" },
          ticks: { color: "#5e5e6e", font: { size: 10 } },
        },
        y: {
          beginAtZero: true,
          grid: { color: "rgba(255,255,255,0.04)" },
          ticks: { color: "#5e5e6e", font: { size: 10 }, precision: 0 },
        },
      },
    },
  });
}

function renderTypes(byType, sample) {
  const grid = document.getElementById("types-grid");
  while (grid.firstChild) grid.removeChild(grid.firstChild);

  const entries = Object.entries(byType).filter(([, v]) => v > 0);
  entries.sort((a, b) => b[1] - a[1]);
  const total = entries.reduce((a, [, v]) => a + v, 0) || 1;

  if (entries.length === 0) {
    const msg = document.createElement("p");
    msg.style.color = "var(--text-faint)";
    msg.style.fontSize = "0.85rem";
    msg.textContent = "Sin detecciones registradas para hoy.";
    grid.appendChild(msg);
    document.getElementById("types-sample").textContent = "0 eventos";
    return;
  }

  for (const [key, count] of entries) {
    const meta = VEHICLE_META[key] || { label: key, icon: "·" };
    const pct = ((count / total) * 100).toFixed(1);

    const card = document.createElement("div");
    card.className = "type-card";

    const iconEl = document.createElement("span");
    iconEl.className = "type-icon";
    iconEl.textContent = meta.icon;

    const labelEl = document.createElement("span");
    labelEl.className = "type-label";
    labelEl.textContent = meta.label;

    const valueEl = document.createElement("span");
    valueEl.className = "type-value";
    valueEl.textContent = count.toLocaleString("es-VE");

    const pctEl = document.createElement("span");
    pctEl.className = "type-pct";
    pctEl.textContent = `${pct}% del total`;

    card.appendChild(iconEl);
    card.appendChild(labelEl);
    card.appendChild(valueEl);
    card.appendChild(pctEl);
    grid.appendChild(card);
  }
  document.getElementById("types-sample").textContent =
    `Sobre ${sample.toLocaleString("es-VE")} eventos analizados`;
}
