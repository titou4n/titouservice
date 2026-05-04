/* ============================================================
   job_tracker.js — JobTrack shared JavaScript
   Loaded on every page via base.html.
   ============================================================ */


/* ── Modal helpers ─────────────────────────────────────────── */

function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(el => el.classList.remove('open'));
  }
});


/* ── Delete confirmation ────────────────────────────────────── */

function confirmDelete(formId) {
  if (window.confirm('Are you sure you want to delete this item?')) {
    document.getElementById(formId)?.submit();
  }
}


/* ── Edit modal helpers ─────────────────────────────────────── */

function openApplicationEditModal(dataset) {
  const modal = document.getElementById('modal-edit');
  const form  = modal.querySelector('form');

  const baseAction = form.dataset.baseAction;
  form.action = baseAction.replace('/0', '/' + dataset.id);

  form.querySelector('[name="title"]').value        = dataset.title       || '';
  form.querySelector('[name="company_id"]').value   = dataset.companyId   || '';
  form.querySelector('[name="status"]').value       = dataset.status      || '';
  form.querySelector('[name="date_applied"]').value = dataset.dateApplied || '';
  form.querySelector('[name="notes"]').value        = dataset.notes       || '';

  modal.classList.add('open');
}

function openCompanyEditModal(dataset) {
  const modal = document.getElementById('modal-edit');
  const form  = modal.querySelector('form');

  const baseAction = form.dataset.baseAction;
  form.action = baseAction.replace('/0', '/' + dataset.id);

  form.querySelector('[name="name"]').value         = dataset.name         || '';
  form.querySelector('[name="secteur"]').value      = dataset.secteur      || '';
  form.querySelector('[name="localisation"]').value = dataset.localisation || '';
  form.querySelector('[name="notes"]').value        = dataset.notes        || '';

  modal.classList.add('open');
}


/* ── Company search filter ──────────────────────────────────── */

function filterCompanies() {
  const query = document.getElementById('search')?.value.toLowerCase() ?? '';
  document.querySelectorAll('#company-grid .company-card').forEach(card => {
    card.hidden = !card.textContent.toLowerCase().includes(query);
  });
}


/* ── Statistics charts (Chart.js) ───────────────────────────── */

function initStats() {
  const el = document.getElementById('stats-data');
  
  console.log('initStats called');
  console.log('stats-data element:', el);

  if (!el) {
    console.warn('stats-data introuvable — on est pas sur la page stats');
    return;
  }

  console.log('raw statuts:', el.dataset.statuts);
  console.log('raw byStatus:', el.dataset.byStatus);
  console.log('raw statusColors:', el.dataset.statusColors);
  console.log('raw topLabels:', el.dataset.topLabels);
  console.log('raw topData:', el.dataset.topData);

  try {
    const statuts      = JSON.parse(el.dataset.statuts);
    const byStatus     = JSON.parse(el.dataset.byStatus);
    const statusColors = JSON.parse(el.dataset.statusColors);
    const topCompanies = {
      labels: JSON.parse(el.dataset.topLabels),
      data:   JSON.parse(el.dataset.topData),
    };

    console.log('parsed statuts:', statuts);
    console.log('parsed byStatus:', byStatus);
    console.log('parsed topCompanies:', topCompanies);
    console.log('Chart disponible ?', typeof Chart);
    console.log('canvas chart-status:', document.getElementById('chart-status'));
    console.log('canvas chart-companies:', document.getElementById('chart-companies'));

    initStatsCharts(statuts, byStatus, statusColors, topCompanies);

  } catch(err) {
    console.error('Erreur dans initStats:', err);
  }
}


/*function initStats() {
  const el = document.getElementById('stats-data');
  if (!el) return;  // page sans stats → on sort silencieusement

  const statuts      = JSON.parse(el.dataset.statuts);
  const byStatus     = JSON.parse(el.dataset.byStatus);
  const statusColors = JSON.parse(el.dataset.statusColors);
  const topCompanies = {
    labels: JSON.parse(el.dataset.topLabels),
    data:   JSON.parse(el.dataset.topData),
  };

  initStatsCharts(statuts, byStatus, statusColors, topCompanies);
}*/

function initStatsCharts(statuts, byStatus, statusColors, topCompanies) {

  // Doughnut chart — breakdown by status
  const ctx1 = document.getElementById('chart-status');
  if (ctx1) {
    new Chart(ctx1, {
      type: 'doughnut',
      data: {
        labels: statuts,
        datasets: [{
          data:            statuts.map(s => byStatus[s]),
          backgroundColor: statuts.map(s => statusColors[s]),
          borderWidth:     2,
          borderColor:     '#fff',
          hoverOffset:     6,
        }]
      },
      options: {
        responsive:          true,
        maintainAspectRatio: false,
        cutout:              '65%',
        plugins: {
          legend: {
            position: 'right',
            labels: { font: { size: 12 }, padding: 12, boxWidth: 14 }
          }
        }
      }
    });
  }

  // Horizontal bar chart — top companies
  const ctx2 = document.getElementById('chart-companies');
  if (ctx2 && topCompanies.labels.length) {
    new Chart(ctx2, {
      type: 'bar',
      data: {
        labels: topCompanies.labels,
        datasets: [{
          label:           'Applications',
          data:            topCompanies.data,
          backgroundColor: '#6366f120',
          borderColor:     '#6366f1',
          borderWidth:     2,
          borderRadius:    6,
        }]
      },
      options: {
        responsive:          true,
        maintainAspectRatio: false,
        indexAxis:           'y',
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#f1f3f9' }, ticks: { stepSize: 1 } },
          y: { grid: { display: false } }
        }
      }
    });
  }
}

// FIX : appelé après les déclarations, au niveau global
document.addEventListener('DOMContentLoaded', initStats);