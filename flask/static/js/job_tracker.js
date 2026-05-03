/* ============================================================
   job_tracker.js — JobTrack shared JavaScript
   Loaded on every page via base.html.
   ============================================================ */


/* ── Modal helpers ─────────────────────────────────────────── */

/** Open a modal by id */
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}

/** Close a modal by id */
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

/** Close modal when clicking the dark overlay */
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

/** Close modal on Escape key */
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(el => el.classList.remove('open'));
  }
});


/* ── Delete confirmation ────────────────────────────────────── */

/**
 * Ask for confirmation before submitting a hidden delete form.
 * @param {string} formId - The id of the hidden <form> element
 */
function confirmDelete(formId) {
  if (window.confirm('Are you sure you want to delete this item?')) {
    document.getElementById(formId)?.submit();
  }
}


/* ── Edit modal helpers ─────────────────────────────────────── */

/**
 * Populate and open the application edit modal.
 * Replaces /0/ in the form action with the real record id.
 * Called inline from kanban card edit buttons.
 *
 * @param {Object} data - { id, title, company_id, status, date_applied, notes }
 */
function openApplicationEditModal(data) {
  const modal = document.getElementById('modal-edit');
  if (!modal) return;

  // Fill each named field with the matching value
  Object.entries(data).forEach(([key, val]) => {
    const el = modal.querySelector(`[name="${key}"]`);
    if (el) el.value = val ?? '';
  });

  // Patch the form action URL: swap placeholder id 0 with real id
  const form = modal.querySelector('form');
  if (form && data.id) {
    form.action = form.dataset.baseAction.replace('/0/', `/${data.id}/`);
  }

  openModal('modal-edit');
}

/**
 * Populate and open the company edit modal.
 * Called inline from company card edit buttons.
 *
 * @param {Object} data - { id, name, secteur, localisation, notes }
 */
function openCompanyEditModal(data) {
  const modal = document.getElementById('modal-edit');
  if (!modal) return;

  ['name', 'secteur', 'localisation', 'notes'].forEach(key => {
    const el = modal.querySelector(`[name="${key}"]`);
    if (el) el.value = data[key] ?? '';
  });

  const form = modal.querySelector('form');
  if (form) {
    form.action = form.dataset.baseAction.replace('/0/', `/${data.id}/`);
  }

  openModal('modal-edit');
}


/* ── Company search filter ──────────────────────────────────── */

/**
 * Filter company cards in real time by matching text content.
 * Attached to the search input via oninput in entreprises.html.
 */
function filterCompanies() {
  const query = document.getElementById('search')?.value.toLowerCase() ?? '';
  document.querySelectorAll('#company-grid .company-card').forEach(card => {
    card.hidden = !card.textContent.toLowerCase().includes(query);
  });
}


/* ── Statistics charts (Chart.js) ───────────────────────────── */

/**
 * Initialise Chart.js charts on the statistics page.
 * Reads data injected into window.STATS_DATA by the template.
 * Called at the bottom of statistiques.html via a small inline script.
 */
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