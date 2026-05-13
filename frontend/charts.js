// ── AIRA CHARTS & VISUALISATIONS ──
// Shared chart utilities for all 15 AIRA screens
// Uses Chart.js, D3.js, and Canvas API

// ── AIRA COLOUR PALETTE ──
const AIRA_COLORS = {
  blue:    '#2E2EFF',
  cyan:    '#00D4FF',
  green:   '#00FF88',
  amber:   '#FFB800',
  red:     '#FF3355',
  purple:  '#CC44FF',
  orange:  '#FF6B35',
  white:   '#E8F0FF',
  gray:    '#6B7A99',
};

// ── CHART.JS GLOBAL DEFAULTS ──
if (typeof Chart !== 'undefined') {
  Chart.defaults.color          = '#6B7A99';
  Chart.defaults.borderColor    = 'rgba(46,46,255,0.12)';
  Chart.defaults.backgroundColor = 'rgba(46,46,255,0.08)';
  Chart.defaults.font.family    = "'Exo 2', sans-serif";
  Chart.defaults.font.size      = 11;
}

// ── RISK GAUGE (Canvas API) ──
function drawRiskGauge(canvasId, score, options = {}) {
  const canvas  = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx     = canvas.getContext('2d');
  const cx      = canvas.width  / 2;
  const cy      = canvas.height * 0.88;
  const radius  = Math.min(canvas.width, canvas.height) * 0.72;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const color = score >= 80 ? AIRA_COLORS.red
              : score >= 60 ? AIRA_COLORS.amber
              : score >= 40 ? AIRA_COLORS.cyan
              : AIRA_COLORS.green;

  // Background arc
  ctx.beginPath();
  ctx.arc(cx, cy, radius, Math.PI, 2 * Math.PI);
  ctx.strokeStyle = 'rgba(46,46,255,0.12)';
  ctx.lineWidth   = options.lineWidth || 14;
  ctx.stroke();

  // Score arc
  const endAngle = Math.PI + (score / 100) * Math.PI;
  ctx.beginPath();
  ctx.arc(cx, cy, radius, Math.PI, endAngle);
  ctx.strokeStyle = color;
  ctx.lineWidth   = options.lineWidth || 14;
  ctx.lineCap     = 'round';
  ctx.stroke();

  // Tick marks
  for (let i = 0; i <= 10; i++) {
    const angle  = Math.PI + (i / 10) * Math.PI;
    const inner  = radius - 20;
    const outer  = radius - 8;
    ctx.beginPath();
    ctx.moveTo(cx + inner * Math.cos(angle), cy + inner * Math.sin(angle));
    ctx.lineTo(cx + outer * Math.cos(angle), cy + outer * Math.sin(angle));
    ctx.strokeStyle = 'rgba(107,122,153,0.4)';
    ctx.lineWidth   = 1;
    ctx.stroke();
  }
}

// ── DONUT CHART (Chart.js) ──
function createDonutChart(canvasId, labels, data, colors) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  return new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors || [
          AIRA_COLORS.blue, AIRA_COLORS.cyan,
          AIRA_COLORS.green, AIRA_COLORS.amber,
          AIRA_COLORS.purple
        ],
        borderWidth: 0,
        hoverOffset: 4
      }]
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      cutout:              '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color:    AIRA_COLORS.gray,
            padding:  12,
            font:     { size: 10 },
            boxWidth: 10
          }
        }
      }
    }
  });
}

// ── LINE CHART (Chart.js) ──
function createLineChart(canvasId, labels, datasets, options = {}) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  const formattedDatasets = datasets.map((d, i) => ({
    label:           d.label || `Series ${i+1}`,
    data:            d.data,
    borderColor:     d.color || AIRA_COLORS.blue,
    backgroundColor: d.fill ? (d.color || AIRA_COLORS.blue).replace(')', ',0.08)').replace('rgb','rgba') : 'transparent',
    tension:         0.4,
    fill:            d.fill || false,
    pointRadius:     d.pointRadius !== undefined ? d.pointRadius : 0,
    borderWidth:     2
  }));

  return new Chart(canvas, {
    type: 'line',
    data: { labels, datasets: formattedDatasets },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      plugins: { legend: { display: datasets.length > 1 } },
      scales: {
        x: {
          ticks: { color: AIRA_COLORS.gray, font: { size: 9 }, maxTicksLimit: 8 },
          grid:  { color: 'rgba(46,46,255,0.06)' }
        },
        y: {
          min:   options.min !== undefined ? options.min : 0,
          max:   options.max !== undefined ? options.max : 100,
          ticks: { color: AIRA_COLORS.gray, font: { size: 9 } },
          grid:  { color: 'rgba(46,46,255,0.06)' }
        }
      }
    }
  });
}

// ── BAR CHART (Chart.js) ──
function createBarChart(canvasId, labels, datasets, options = {}) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  const formattedDatasets = datasets.map((d, i) => ({
    label:           d.label || `Series ${i+1}`,
    data:            d.data,
    backgroundColor: d.colors || d.color || AIRA_COLORS.blue,
    borderRadius:    4
  }));

  return new Chart(canvas, {
    type: 'bar',
    data: { labels, datasets: formattedDatasets },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      plugins: { legend: { display: datasets.length > 1 } },
      scales: {
        x: {
          ticks: { color: AIRA_COLORS.gray, font: { size: 9 } },
          grid:  { color: 'rgba(46,46,255,0.06)' }
        },
        y: {
          min:   0,
          max:   options.max || 100,
          ticks: { color: AIRA_COLORS.gray, font: { size: 9 } },
          grid:  { color: 'rgba(46,46,255,0.06)' }
        }
      }
    }
  });
}

// ── COMPLIANCE HEATMAP (Pure HTML/CSS) ──
function createHeatmap(containerId, sectors, frameworks, scores) {
  const container = document.getElementById(containerId);
  if (!container) return;

  function scoreColor(s) {
    if (s >= 85) return '#1D9E75';
    if (s >= 70) return '#5BC8A0';
    if (s >= 55) return '#EF9F27';
    return '#E24B4A';
  }

  let html = '<div style="display:flex;flex-direction:column;gap:4px">';

  // Headers
  html += '<div style="display:flex;gap:4px;margin-left:90px;margin-bottom:2px">';
  frameworks.forEach(f => {
    html += `<div style="flex:1;font-size:7px;color:#6B7A99;text-align:center;letter-spacing:1px">${f}</div>`;
  });
  html += '</div>';

  // Rows
  sectors.forEach((sector, si) => {
    html += '<div style="display:flex;gap:4px;align-items:center">';
    html += `<div style="width:82px;font-size:9px;color:#6B7A99;text-align:right;padding-right:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${sector}</div>`;
    frameworks.forEach((_, fi) => {
      const score = scores[si] ? scores[si][fi] || 0 : 0;
      html += `<div style="flex:1;height:22px;background:${scoreColor(score)};display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:600;color:#fff;cursor:pointer" title="${sector} × ${frameworks[fi]}: ${score}%">${score}</div>`;
    });
    html += '</div>';
  });

  html += '</div>';
  container.innerHTML = html;
}

// ── RISK SCORE COLOR ──
function riskColor(score) {
  if (score >= 80) return AIRA_COLORS.red;
  if (score >= 60) return AIRA_COLORS.amber;
  if (score >= 40) return AIRA_COLORS.cyan;
  return AIRA_COLORS.green;
}

// ── RISK LEVEL LABEL ──
function riskLabel(score) {
  if (score >= 80) return 'critical';
  if (score >= 60) return 'high';
  if (score >= 40) return 'medium';
  return 'low';
}

// ── LIVE CLOCK ──
function startClock(elementIds) {
  function update() {
    const n = new Date();
    const t = String(n.getUTCHours()).padStart(2,'0')  + ':' +
              String(n.getUTCMinutes()).padStart(2,'0') + ':' +
              String(n.getUTCSeconds()).padStart(2,'0') + ' UTC';
    (Array.isArray(elementIds) ? elementIds : [elementIds]).forEach(id => {
      const el = document.getElementById(id);
      if (el) el.textContent = t;
    });
  }
  setInterval(update, 1000);
  update();
}

// ── API HELPER ──
async function fetchAIRA(endpoint, method = 'GET', body = null) {
  const BASE_URL = 'http://127.0.0.1:8000';
  const token    = localStorage.getItem('aira_token') || '';

  const options = {
    method,
    headers: {
      'Content-Type':  'application/json',
      'Authorization': `Bearer ${token}`
    }
  };
  if (body) options.body = JSON.stringify(body);

  try {
    const res  = await fetch(BASE_URL + endpoint, options);
    const data = await res.json();
    return { success: res.ok, data, status: res.status };
  } catch (err) {
    return { success: false, error: err.message };
  }
}

// ── FORMAT NUMBERS ──
function formatNumber(n) {
  if (n >= 1000000) return (n/1000000).toFixed(1) + 'M';
  if (n >= 1000)    return (n/1000).toFixed(1)    + 'K';
  return n.toString();
}

// Export for module use
if (typeof module !== 'undefined') {
  module.exports = {
    AIRA_COLORS, drawRiskGauge, createDonutChart,
    createLineChart, createBarChart, createHeatmap,
    riskColor, riskLabel, startClock, fetchAIRA, formatNumber
  };
}
