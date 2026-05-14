// 1PIXEL Conteo dashboard

const API_BASE = "https://1pixel-conteo-api.ai-ffd.workers.dev";
const TOKEN_KEY = "1pixel_conteo_token";
const REFRESH_MS = 60 * 60 * 1000;

// Impactos publicitarios: personas estimadas por vehículo × tasa de atención
// efectiva sobre la pantalla LED. Personas (Human) no multiplican ocupancia.
const OCCUPANCY = {
  Car: 2.2,
  Motorcycle: 1.5,
  Bike: 1.5,
  Bicycle: 1.0,
  Van: 3.5,
  Truck: 1.5,
  Bus: 35,
  Human: 1.0,
};
const ATTENTION_FACTOR = 0.6;

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
let contextChart = null;
let donutChart = null;
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
  bindLogin();
  initDateInput();
  bindControls();
  renderTabs();
  if (getToken()) enterDashboard();
  else showLogin();
});

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

function showLogin() {
  document.getElementById("login-view").hidden = false;
  document.getElementById("dashboard-view").hidden = true;
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
  setTimeout(() => document.getElementById("password").focus(), 50);
}

function enterDashboard() {
  document.getElementById("login-view").hidden = true;
  document.getElementById("dashboard-view").hidden = false;
  loadData();
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(loadData, REFRESH_MS);
}

function bindLogin() {
  const form = document.getElementById("login-form");
  const btn = document.getElementById("login-btn");
  const errBox = document.getElementById("login-error");
  const input = document.getElementById("password");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errBox.hidden = true;
    btn.disabled = true;
    btn.querySelector(".btn-text").textContent = "Validando…";
    btn.querySelector(".btn-spinner").hidden = false;
    try {
      const res = await fetch(`${API_BASE}/auth`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: input.value }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(
          data.error === "invalid_password"
            ? "Contraseña incorrecta."
            : data.detail || "Error de autenticación.",
        );
      }
      setToken(data.token, data.exp);
      input.value = "";
      enterDashboard();
    } catch (err) {
      errBox.textContent = err.message;
      errBox.hidden = false;
    } finally {
      btn.disabled = false;
      btn.querySelector(".btn-text").textContent = "Entrar";
      btn.querySelector(".btn-spinner").hidden = true;
    }
  });
}

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
  document.getElementById("logout-btn").addEventListener("click", () => {
    clearToken();
    showLogin();
  });

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
  document.getElementById("last-update").textContent = force
    ? "Trayendo datos en vivo… (~10s)"
    : "Cargando…";
  const refreshBtn = document.getElementById("refresh-btn");
  if (force) refreshBtn.classList.add("is-spinning");

  try {
    const params = new URLSearchParams({
      gallery: currentGallery,
      period: currentPeriod,
      date: currentDate,
    });
    if (force) {
      params.set("fresh", "1");
      params.set("_", String(Date.now()));
    }
    const url = `${API_BASE}/api/data?${params.toString()}`;
    const token = getToken();
    if (!token) {
      showLogin();
      return;
    }
    const res = await fetch(url, {
      headers: { Authorization: "Bearer " + token },
    });
    if (res.status === 401) {
      clearToken();
      showLogin();
      return;
    }
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
  } finally {
    document.getElementById("refresh-btn").classList.remove("is-spinning");
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

  renderDelta(data.delta);
  renderImpacts(data);

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
  renderContextChart(data);
  renderTypes(
    data.byType || {},
    data.unknown_types || {},
    data.sample_events || 0,
  );
  renderDonut(data.byType || {}, data.unknown_types || {});
  renderRankings(data.top_hours || [], data.top_weekdays || []);
}

function renderDelta(delta) {
  const el = document.getElementById("kpi-delta");
  if (!delta || delta.pct_change == null) {
    el.hidden = true;
    return;
  }
  const pct = delta.pct_change;
  const up = pct >= 0;
  el.hidden = false;
  el.classList.toggle("is-up", up);
  el.classList.toggle("is-down", !up);
  const arrow = up ? "▲" : "▼";
  const sign = up ? "+" : "";
  el.textContent = `${arrow} ${sign}${pct.toFixed(1)}% vs período anterior`;
}

function renderImpacts(data) {
  const el = document.getElementById("kpi-impacts");
  const foot = document.getElementById("kpi-impacts-foot");
  const raw = data?.totals?.raw || 0;
  const byType = data?.byType || {};
  const period = data?.period || "day";
  if (!raw) {
    el.textContent = "—";
    foot.textContent = "sin datos";
    return;
  }
  let people = 0;
  let vehicles = 0;
  for (const [type, count] of Object.entries(byType)) {
    const occ = OCCUPANCY[type] ?? 1;
    people += count * occ;
    vehicles += count;
  }
  const pplPerVehicle = vehicles > 0 ? people / vehicles : 1;
  const impacts = Math.round(raw * pplPerVehicle * ATTENTION_FACTOR);
  el.textContent = impacts.toLocaleString("es-VE");
  const periodTxt =
    period === "day"
      ? "estimado hoy"
      : period === "week"
        ? "estimado en 7 días"
        : "estimado en 30 días";
  foot.textContent = `${periodTxt} · ${pplPerVehicle.toFixed(1)} pers/veh · atención ${(ATTENTION_FACTOR * 100).toFixed(0)}%`;
}

function renderContextChart(data) {
  const titleEl = document.getElementById("context-chart-title");
  let ctxData = null;
  let isHourly = false;
  if (data.period === "day" && data.daily_context) {
    titleEl.textContent = "Tráfico por día · 7 días alrededor";
    ctxData = data.daily_context;
    isHourly = false;
  } else if (
    (data.period === "week" || data.period === "month") &&
    data.hourly_context
  ) {
    titleEl.textContent = `Tráfico por hora · ${formatScopeLabel(data.breakdown_scope)}`;
    ctxData = data.hourly_context;
    isHourly = true;
  } else {
    return;
  }

  const canvas = document.getElementById("context-chart");
  const ctx = canvas.getContext("2d");
  const grad = ctx.createLinearGradient(0, 0, 0, 280);
  grad.addColorStop(0, "rgba(255, 59, 212, 0.55)");
  grad.addColorStop(1, "rgba(255, 59, 212, 0.02)");

  if (contextChart) contextChart.destroy();
  contextChart = new Chart(ctx, {
    type: isHourly ? "line" : "bar",
    data: {
      labels: ctxData.labels,
      datasets: [
        {
          label: "Conteo",
          data: ctxData.data,
          fill: isHourly,
          backgroundColor: isHourly ? grad : "rgba(255, 59, 212, 0.55)",
          borderColor: "#ff8de2",
          borderWidth: isHourly ? 2 : 0,
          borderRadius: isHourly ? 0 : 8,
          tension: 0.35,
          pointRadius: 0,
          pointHoverRadius: 5,
        },
      ],
    },
    options: chartOptions(isHourly),
  });
}

function chartOptions(isHourly) {
  return {
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
          maxTicksLimit: isHourly ? 12 : 10,
        },
      },
      y: {
        beginAtZero: true,
        grid: { color: "rgba(255,255,255,0.04)" },
        ticks: { color: "#5e5e6e", font: { size: 10 }, precision: 0 },
      },
    },
  };
}

function renderDonut(byType, unknown) {
  const merged = {};
  for (const [k, v] of Object.entries(byType)) {
    if (k === "Bike" || k === "Bicycle" || k === "Motorcycle") {
      merged.MotoBike = (merged.MotoBike || 0) + v;
    } else if (v > 0) {
      merged[k] = v;
    }
  }
  for (const [k, v] of Object.entries(unknown || {})) {
    if (k === "Bike" || k === "Bicycle" || k === "Motorcycle") {
      merged.MotoBike = (merged.MotoBike || 0) + v;
    } else if (v > 0) {
      merged[`?${k}`] = v;
    }
  }
  const colors = [
    "#8b5cff",
    "#ff3bd4",
    "#00ffa3",
    "#ffb547",
    "#5cbcff",
    "#ff5470",
    "#a5ff5c",
    "#5c6bff",
  ];
  const entries = Object.entries(merged).sort((a, b) => b[1] - a[1]);
  const labels = entries.map(([k]) => {
    if (k.startsWith("?")) return k.slice(1);
    const meta = VEHICLE_META[k];
    return meta ? meta.label : k;
  });
  const data = entries.map(([, v]) => v);
  const total = data.reduce((a, b) => a + b, 0);
  document.getElementById("donut-sub").textContent =
    total > 0 ? `${total.toLocaleString("es-VE")} objetos` : "sin datos";

  const ctx = document.getElementById("types-donut").getContext("2d");
  if (donutChart) donutChart.destroy();
  if (total === 0) return;
  donutChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data,
          backgroundColor: colors.slice(0, entries.length),
          borderColor: "#0c0c10",
          borderWidth: 2,
          hoverOffset: 8,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "62%",
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#9b9bab", font: { size: 11 }, boxWidth: 12 },
        },
        tooltip: {
          backgroundColor: "#1c1c25",
          borderColor: "rgba(139, 92, 255, 0.4)",
          borderWidth: 1,
          callbacks: {
            label: (ctx) => {
              const v = ctx.parsed;
              const pct = ((v / total) * 100).toFixed(1);
              return ` ${ctx.label}: ${v.toLocaleString("es-VE")} (${pct}%)`;
            },
          },
        },
      },
    },
  });
}

function renderRankings(topHours, topWeekdays) {
  const fmt = (n) => Number(n).toLocaleString("es-VE");
  const hList = document.getElementById("rank-hours");
  while (hList.firstChild) hList.removeChild(hList.firstChild);
  if (topHours.length === 0) {
    const li = document.createElement("li");
    li.className = "rank-empty";
    li.textContent = "Sin datos suficientes.";
    hList.appendChild(li);
  } else {
    for (let i = 0; i < topHours.length; i++) {
      const item = topHours[i];
      const li = document.createElement("li");
      const rank = document.createElement("span");
      rank.className = "rank-pos";
      rank.textContent = `${i + 1}`;
      const lbl = document.createElement("span");
      lbl.className = "rank-label";
      lbl.textContent = item.label;
      const val = document.createElement("span");
      val.className = "rank-val";
      val.textContent = fmt(item.count);
      li.appendChild(rank);
      li.appendChild(lbl);
      li.appendChild(val);
      hList.appendChild(li);
    }
  }

  const wdList = document.getElementById("rank-weekdays");
  while (wdList.firstChild) wdList.removeChild(wdList.firstChild);
  if (topWeekdays.length === 0) {
    const li = document.createElement("li");
    li.className = "rank-empty";
    li.textContent = "Sin datos suficientes.";
    wdList.appendChild(li);
  } else {
    for (let i = 0; i < topWeekdays.length; i++) {
      const item = topWeekdays[i];
      const li = document.createElement("li");
      const rank = document.createElement("span");
      rank.className = "rank-pos";
      rank.textContent = `${i + 1}`;
      const lbl = document.createElement("span");
      lbl.className = "rank-label";
      lbl.textContent = item.label;
      const val = document.createElement("span");
      val.className = "rank-val";
      val.textContent = `${fmt(Math.round(item.avg))} prom.`;
      li.appendChild(rank);
      li.appendChild(lbl);
      li.appendChild(val);
      wdList.appendChild(li);
    }
  }
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
