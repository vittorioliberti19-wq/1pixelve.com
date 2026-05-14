// 1PIXEL Conteo dashboard

const API_BASE = "https://1pixel-conteo-api.ai-ffd.workers.dev";
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
  MotoBike: { label: "Motos/Bicicletas", icon: "🏍" },
  Truck: { label: "Camiones", icon: "🚚" },
  Van: { label: "Camionetas", icon: "🚐" },
  Bus: { label: "Buses", icon: "🚌" },
  Human: { label: "Peatones", icon: "🚶" },
};

const PERIOD_LABEL = {
  day: {
    title: "Hoy",
    footMain: "objetos únicos",
    chartTitle: "Tráfico por hora",
    chartSub: "Hora local Caracas (GMT-4)",
  },
  week: {
    title: "Últimos 7 días",
    footMain: "detecciones (eventos)",
    chartTitle: "Tráfico por día",
    chartSub: "Suma diaria de eventos",
  },
  month: {
    title: "Últimos 30 días",
    footMain: "detecciones (eventos)",
    chartTitle: "Tráfico por día",
    chartSub: "Suma diaria de eventos",
  },
};

let currentGallery = "3h";
let currentPeriod = "day";
let currentDate = todayKey();
let chart = null;
let refreshTimer = null;

function todayKey() {
  const now = new Date();
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  // We want the Caracas calendar day (UTC-4). For most users we approximate
  // with their local day; the worker converts internally either way.
  return local.toISOString().slice(0, 10);
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("year").textContent = new Date().getFullYear();
  initDateInput();
  bindControls();
  renderTabs();
  loadData();
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(loadData, REFRESH_MS);
});

function initDateInput() {
  const inp = document.getElementById("date-input");
  inp.value = currentDate;
  inp.max = todayKey();
}

function bindControls() {
  document
    .getElementById("refresh-btn")
    .addEventListener("click", () => loadData({ force: true }));
  document
    .getElementById("retry-btn")
    .addEventListener("click", () => loadData());

  for (const btn of document.querySelectorAll(".period-btn")) {
    btn.addEventListener("click", () => {
      const period = btn.dataset.period;
      if (period === currentPeriod) return;
      currentPeriod = period;
      for (const b of document.querySelectorAll(".period-btn")) {
        b.classList.toggle("active", b.dataset.period === period);
      }
      loadData();
    });
  }

  document.getElementById("date-input").addEventListener("change", (e) => {
    const v = e.target.value;
    if (!v) return;
    currentDate = v;
    loadData();
  });
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
      loadData();
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

async function loadData({ force = false } = {}) {
  setState("loading");
  document.getElementById("last-update").textContent = "Cargando…";

  try {
    const params = new URLSearchParams({
      gallery: currentGallery,
      period: currentPeriod,
      date: currentDate,
    });
    if (force) params.set("_", String(Date.now()));
    const url = `${API_BASE}/api/data?${params.toString()}`;
    const res = await fetch(url);
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || body.error || `HTTP ${res.status}`);
    }
    const data = await res.json();
    if (!data.active) {
      setState("inactive");
      const el = document.querySelector("#state-inactive p");
      if (el) el.textContent = data.message || "Galería próximamente.";
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
  const fmt = (n) => (n == null ? "—" : Number(n).toLocaleString("es-VE"));
  const meta = PERIOD_LABEL[data.period] || PERIOD_LABEL.day;

  document.getElementById("kpi-main-label").textContent = meta.title;
  const mainValue =
    data.totals.unique != null ? data.totals.unique : data.totals.raw;
  document.getElementById("kpi-main").textContent = fmt(mainValue);
  document.getElementById("kpi-main-foot").textContent = meta.footMain;

  document.getElementById("kpi-lifetime").textContent = fmt(
    data.totals.lifetime,
  );

  if (data.peak && data.peak.count > 0) {
    document.getElementById("kpi-peak").textContent = fmt(data.peak.count);
    document.getElementById("kpi-peak-foot").textContent =
      data.period === "day"
        ? `En ${data.peak.label}`
        : `Día más alto: ${data.peak.label}`;
  } else {
    document.getElementById("kpi-peak").textContent = "—";
    document.getElementById("kpi-peak-foot").textContent = "sin datos";
  }

  const ts = data.generated_at ? new Date(data.generated_at) : new Date();
  const cachedTag = data.cached ? " · caché" : "";
  document.getElementById("last-update").textContent =
    `${data.label} · Actualizado ${ts.toLocaleTimeString("es-VE", {
      hour: "2-digit",
      minute: "2-digit",
    })}${cachedTag}`;

  document.getElementById("chart-title").textContent =
    `${meta.chartTitle} · ${meta.title}`;
  document.getElementById("chart-sub").textContent = meta.chartSub;
  document.getElementById("types-title").textContent =
    data.period === "day"
      ? "Desglose por tipo · Hoy"
      : `Desglose por tipo · ${formatScopeLabel(data.breakdown_scope)}`;

  renderChart(data.series, data.period);
  renderTypes(
    data.byType || {},
    data.unknown_types || {},
    data.sample_events || 0,
  );
}

function formatScopeLabel(yyyymmdd) {
  if (!yyyymmdd) return "último día";
  const [y, m, d] = yyyymmdd.split("-").map(Number);
  return `${String(d).padStart(2, "0")}/${String(m).padStart(2, "0")}/${y}`;
}

function renderChart(series, period) {
  const ctx = document.getElementById("hourly-chart").getContext("2d");
  const labels = series.labels || [];
  const data = series.data || [];
  const grad = ctx.createLinearGradient(0, 0, 0, 280);
  grad.addColorStop(0, "rgba(139, 92, 255, 0.55)");
  grad.addColorStop(1, "rgba(139, 92, 255, 0.02)");

  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: period === "day" ? "line" : "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Conteo",
          data,
          fill: period === "day",
          backgroundColor: period === "day" ? grad : "rgba(139,92,255,0.6)",
          borderColor: "#b69bff",
          borderWidth: period === "day" ? 2 : 0,
          borderRadius: period === "day" ? 0 : 8,
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
          ticks: {
            color: "#5e5e6e",
            font: { size: 10 },
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: period === "day" ? 12 : 10,
          },
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

function renderTypes(byType, unknown, sample) {
  const grid = document.getElementById("types-grid");
  while (grid.firstChild) grid.removeChild(grid.firstChild);

  const knownEntries = Object.entries(byType);
  const merged = {};
  for (const [key, count] of knownEntries) {
    if (key === "Bike" || key === "Bicycle" || key === "Motorcycle") {
      merged.MotoBike = (merged.MotoBike || 0) + count;
    } else {
      merged[key] = (merged[key] || 0) + count;
    }
  }
  const final = [
    ["Car", merged.Car || 0],
    ["MotoBike", merged.MotoBike || 0],
    ["Van", merged.Van || 0],
    ["Truck", merged.Truck || 0],
    ["Bus", merged.Bus || 0],
    ["Human", merged.Human || 0],
  ];
  for (const [key, count] of Object.entries(unknown || {})) {
    if (key === "Bike" || key === "Bicycle" || key === "Motorcycle") {
      // also fold any unknown bike/moto labels into the same bucket
      const motoIdx = final.findIndex(([k]) => k === "MotoBike");
      if (motoIdx >= 0) final[motoIdx][1] += count;
      continue;
    }
    final.push([`unknown:${key}`, count]);
  }

  const total = final.reduce((a, [, v]) => a + v, 0) || 1;

  for (const [key, count] of final) {
    const card = document.createElement("div");
    card.className = "type-card" + (count === 0 ? " is-zero" : "");

    let label, icon;
    if (key.startsWith("unknown:")) {
      const raw = key.slice("unknown:".length);
      label = raw;
      icon = "·";
    } else {
      const meta = VEHICLE_META[key] || { label: key, icon: "·" };
      label = meta.label;
      icon = meta.icon;
    }
    const pct = total ? ((count / total) * 100).toFixed(1) : "0.0";

    const iconEl = document.createElement("span");
    iconEl.className = "type-icon";
    iconEl.textContent = icon;

    const labelEl = document.createElement("span");
    labelEl.className = "type-label";
    labelEl.textContent = label;

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
    `${total.toLocaleString("es-VE")} objetos únicos · ${sample.toLocaleString("es-VE")} eventos`;
}
