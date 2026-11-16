const state = {
  currentView: 'push',
  portfolio: [],
  selectedTicker: 'RELIANCE.NS'
};

const contentArea = document.getElementById('contentArea');
const overviewCards = document.getElementById('overviewCards');
const dataNotice = document.getElementById('dataNotice');

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

function renderOverview(data) {
  state.portfolio = data.portfolio;
  dataNotice.textContent = data.data_notice;
  overviewCards.innerHTML = '';

  const holdings = data.portfolio.map((item, index) => `
    <article class="stat-card">
      <div class="stat-top">
        <div class="ticker">${item.ticker}</div>
        <div class="delta ${item.change_pct >= 0 ? 'up' : 'down'}">${item.change_pct >= 0 ? '+' : ''}${item.change_pct.toFixed(1)}%</div>
      </div>
      <div class="price">₹${item.price.toLocaleString('en-IN', { maximumFractionDigits: 1 })}</div>
      <div class="signal">${item.signal}</div>
    </article>
  `);

  overviewCards.innerHTML = holdings.slice(0, 5).join('');
  if (holdings.length > 5) {
    const more = document.createElement('details');
    more.className = 'stat-card';
    more.innerHTML = `<summary>Show remaining ${holdings.length - 5} demo holdings</summary><div class="card-stack">${holdings.slice(5).join('')}</div>`;
    overviewCards.appendChild(more);
  }

  const network = document.createElement('div');
  network.className = 'stat-card';
  network.innerHTML = `
    <div class="stat-top">
      <div class="ticker">Network</div>
      <div class="delta up">${data.network_size} synthetic profiles</div>
    </div>
    <div class="price">${data.network_summary.strongest_match}</div>
    <div class="signal">Illustrative network match. No real personal profile data is used.</div>
  `;
  overviewCards.appendChild(network);
}

function renderResultsComparison(results) {
  if (!results) return '';
  const rows = Object.entries(results.metrics).map(([name, values]) => `
    <tr>
      <th>${name}</th>
      <td>${values.current.toLocaleString('en-IN')}</td>
      <td>${values.qoq_pct >= 0 ? '+' : ''}${values.qoq_pct}%</td>
      <td>${values.yoy_pct >= 0 ? '+' : ''}${values.yoy_pct}%</td>
    </tr>
  `).join('');
  return `
    <div class="results-block">
      <h3>Results snapshot · ${results.period}</h3>
      <p class="eyebrow">${results.notice} Values in ${results.unit}.</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Metric</th><th>Current</th><th>QoQ</th><th>YoY</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>
  `;
}

function renderAlertItems(alertData) {
  if (!alertData.items.length) {
    return '<div class="empty-state">No holdings crossed these thresholds.</div>';
  }
  return `<div class="card-stack">${alertData.items.map(item => `
    <article class="news-card">
      <div class="meta-row">
        <span class="badge">${item.ticker}</span>
        <span class="priority">${item.price_change_pct === null ? '—' : `${item.price_change_pct > 0 ? '+' : ''}${item.price_change_pct.toFixed(1)}%`} · ${item.volume_multiple === null ? '—' : `${item.volume_multiple.toFixed(1)}×`} volume</span>
      </div>
      <h3>${item.name}</h3>
      <ul class="accent-list">${item.reasons.map(reason => `<li>${reason}</li>`).join('')}</ul>
      ${item.market_date ? `<p class="eyebrow">Market date: ${item.market_date}</p>` : ''}
    </article>
  `).join('')}</div>`;
}

function renderPush(items, hours, alertData, source) {
  const cards = items.map(item => `
    <article class="news-card">
      <div class="meta-row">
        <span class="badge">${escapeHtml(item.category)}</span>
        <span class="priority">Priority ${item.priority_score}</span>
      </div>
      <h3>${escapeHtml(item.headline)}</h3>
      <p>${escapeHtml(item.summary)}</p>
      ${renderResultsComparison(item.results_comparison)}
      <ul class="accent-list">
        <li><strong>Why it matters:</strong> ${escapeHtml(item.why_it_matters)}</li>
        <li><strong>Company:</strong> ${escapeHtml(item.name)} (${escapeHtml(item.ticker)})</li>
        <li><strong>Related network:</strong> ${item.related_people.length ? item.related_people.map(person => escapeHtml(person.name)).join(', ') : 'No direct overlap'}</li>
        <li><strong>Age:</strong> ${item.age_hours} hours · ${source === 'nse' ? 'NSE exchange filing' : 'synthetic demo announcement'}</li>
      </ul>
      ${item.source_url ? `<p><a class="source-link" href="${escapeHtml(item.source_url)}" target="_blank" rel="noopener noreferrer">Open original NSE filing</a></p>` : ''}
    </article>
  `).join('');

  contentArea.innerHTML = `
    <div class="section-title">Proactive push digest</div>
    <p class="muted-copy">${source === 'nse' ? 'Official NSE announcements for portfolio companies, prioritised and connected to relevant synthetic network profiles.' : 'Synthetic sample announcements; not an exchange filing feed.'}</p>
    <div class="form-controls">
      <label class="select-wrap" for="windowSelect">Window
        <select id="windowSelect">
          ${[24, 72, 168, 720].map(value => `<option value="${value}" ${value === hours ? 'selected' : ''}>${value === 24 ? '24 hours' : `${value / 24} days`}</option>`).join('')}
        </select>
      </label>
      <label class="select-wrap" for="sourceSelect">Feed
        <select id="sourceSelect">
          <option value="nse" ${source === 'nse' ? 'selected' : ''}>NSE live filings</option>
          <option value="demo" ${source === 'demo' ? 'selected' : ''}>Synthetic demo</option>
        </select>
      </label>
    </div>
    <div class="card-stack">${cards || `<div class="empty-state">No ${source === 'nse' ? 'NSE filings' : 'demo announcements'} found in this time window.</div>`}</div>
    <section class="alert-section">
      <div class="section-title">Threshold alerts <span class="demo-label">DEMO</span></div>
      <p class="muted-copy">Evaluate the sample end-of-day moves using thresholds you choose. This prototype does not run a background watcher or send notifications.</p>
      <form id="alertForm" class="form-controls">
        <label class="select-wrap">Price move ≥ ±
          <input id="priceThreshold" type="number" min="0.1" max="100" step="0.1" value="${alertData.thresholds.price_change_pct}">
          <span>%</span>
        </label>
        <label class="select-wrap">Volume ≥
          <input id="volumeThreshold" type="number" min="0.1" max="100" step="0.1" value="${alertData.thresholds.volume_multiple}">
          <span>× average</span>
        </label>
        <button class="primary-btn" type="submit">Evaluate alerts</button>
        <button class="primary-btn" id="liveAlertButton" type="button">Check live portfolio</button>
      </form>
      <div id="alertStatus" class="muted-copy"></div>
      <div id="alertResults">${renderAlertItems(alertData)}</div>
    </section>
  `;

  document.getElementById('windowSelect').addEventListener('change', () => {
    loadPush(Number(document.getElementById('windowSelect').value), document.getElementById('sourceSelect').value);
  });
  document.getElementById('sourceSelect').addEventListener('change', () => {
    loadPush(Number(document.getElementById('windowSelect').value), document.getElementById('sourceSelect').value);
  });
  document.getElementById('alertForm').addEventListener('submit', async event => {
    event.preventDefault();
    const price = document.getElementById('priceThreshold').value;
    const volume = document.getElementById('volumeThreshold').value;
    const target = document.getElementById('alertResults');
    target.textContent = 'Evaluating sample alerts…';
    try {
      const updated = await fetchJson(`/api/alerts?price_change_pct=${encodeURIComponent(price)}&volume_multiple=${encodeURIComponent(volume)}`);
      document.getElementById('alertStatus').textContent = 'Evaluated against synthetic demo data.';
      target.innerHTML = renderAlertItems(updated);
    } catch (error) {
      target.innerHTML = `<div class="empty-state">${error.message}</div>`;
    }
  });
  document.getElementById('liveAlertButton').addEventListener('click', async () => {
    const price = document.getElementById('priceThreshold').value;
    const volume = document.getElementById('volumeThreshold').value;
    const target = document.getElementById('alertResults');
    const status = document.getElementById('alertStatus');
    target.innerHTML = '<div class="empty-state">Checking Yahoo EOD data for portfolio holdings…</div>';
    status.textContent = 'This request fetches quotes on demand; it is not a continuous background watcher.';
    try {
      const live = await fetchJson(`/api/alerts/live?price_change_pct=${encodeURIComponent(price)}&volume_multiple=${encodeURIComponent(volume)}`);
      status.textContent = `${live.summary} Data mode: Yahoo Finance EOD.`;
      target.innerHTML = renderAlertItems(live);
      if (live.errors.length) {
        target.innerHTML += `<div class="empty-state"><strong>Quotes unavailable:</strong><ul class="accent-list">${live.errors.map(item => `<li>${escapeHtml(item.ticker)}: ${escapeHtml(item.error)}</li>`).join('')}</ul></div>`;
      }
    } catch (error) {
      status.textContent = 'Live portfolio check failed.';
      target.innerHTML = `<div class="empty-state">${error.message}</div>`;
    }
  });
}

async function loadPush(hours = 24, source = 'nse') {
  let digest;
  try {
    digest = await fetchJson(`/api/push?window_hours=${hours}&source=${source}`);
  } catch (error) {
    if (source !== 'nse') throw error;
    contentArea.innerHTML = `
      <div class="news-card">
        <h3>NSE filings unavailable</h3>
        <p>${escapeHtml(error.message)}</p>
        <button class="primary-btn" id="demoFeedFallback" type="button">View synthetic demo feed</button>
      </div>
    `;
    document.getElementById('demoFeedFallback').addEventListener('click', () => loadPush(hours, 'demo'));
    return;
  }
  const alerts = await fetchJson('/api/alerts');
  renderPush(digest.items, hours, alerts, source);
}

async function renderPull() {
  const overview = await fetchJson('/api/overview');
  const tickers = [...new Set([
    ...overview.portfolio.map(item => item.ticker),
    ...overview.watchlist.map(item => item.ticker)
  ])];
  state.selectedTicker = tickers.includes(state.selectedTicker) ? state.selectedTicker : tickers[0];

  contentArea.innerHTML = `
    <div class="section-title">On-demand company research</div>
    <p class="muted-copy">Illustrative profiles are clearly marked. Where primary documents have not been ingested, FINN shows source links and withholds unsupported financial claims.</p>
    <div class="filter-row">
      <div class="select-wrap">
        <label for="companySelect">Company</label>
        <select id="companySelect">
          ${tickers.map(ticker => `<option value="${ticker}" ${ticker === state.selectedTicker ? 'selected' : ''}>${ticker}</option>`).join('')}
        </select>
      </div>
    </div>
    <div id="pullDetails"></div>
  `;

  document.getElementById('companySelect').addEventListener('change', async event => {
    state.selectedTicker = event.target.value;
    await renderPullCompanyReport(state.selectedTicker);
  });

  await renderPullCompanyReport(state.selectedTicker);
}

async function renderPullCompanyReport(ticker) {
  const details = document.getElementById('pullDetails');
  details.innerHTML = '<div class="empty-state">Loading company profile…</div>';
  const report = await fetchJson(`/api/company/${encodeURIComponent(ticker)}`);
  const sourceLinks = (report.primary_source_links || []).map(source => `
    <a class="source-link" href="${source.url}" target="_blank" rel="noopener noreferrer">${source.label}</a>
  `).join(' · ');

  if (report.report_status === 'primary_sources_not_loaded') {
    details.innerHTML = `
      <article class="research-card">
        <div class="meta-row">
          <span class="badge">${report.company.name}</span>
          <span class="demo-label">PRIMARY SOURCES NOT LOADED</span>
        </div>
        <p>${report.source_note}</p>
        <h3>Source links</h3>
        <p>${sourceLinks}</p>
        <div class="empty-state">No Revenue / EBITDA / PBT / PAT or narrative analysis is shown until primary company documents are ingested and cited.</div>
        <div class="form-controls"><button class="primary-btn" id="marketButton" type="button">Load live EOD price & volume</button></div>
        <div id="marketDetails"></div>
        <h3>Network signal</h3>
        <div class="tag-row">${report.network.length ? report.network.map(person => `<span class="tag">${person.name} · ${person.role}</span>`).join('') : '<span class="tag">No direct overlap</span>'}</div>
      </article>
      <section id="filedResults"></section>
      <section id="sourceWorkspace"></section>
    `;
    bindMarketButton(ticker);
    loadFiledResults(ticker);
    bindSourceWorkspace(ticker);
    return;
  }

  const metrics = Object.entries(report.financial_snapshot).map(([label, value]) => `
    <div class="metric-box">
      <div class="label">${label.replace('_', ' ')}</div>
      <div class="value">${value}</div>
    </div>
  `).join('');
  const guidance = report.guidance.map(item => `
    <li><strong>${item.metric}</strong>: Guidance ${item.guidance} vs actual ${item.actual}</li>
  `).join('');
  const network = report.network.length ? report.network.map(person => `
    <span class="tag">${person.name} · ${person.role}</span>
  `).join('') : '<span class="tag">No direct overlap</span>';

  details.innerHTML = `
    <article class="research-card">
      <div class="meta-row">
        <span class="badge">${report.company.name}</span>
        <span class="demo-label">ILLUSTRATIVE ONLY</span>
      </div>
      <p>${report.source_note}</p>
      <p>${sourceLinks}</p>
      <div class="form-controls"><button class="primary-btn" id="marketButton" type="button">Load live EOD price & volume</button></div>
      <div id="marketDetails"></div>
      <h3>Business snapshot</h3>
      <p>${report.business_snapshot}</p>
      <div class="two-col">${metrics}</div>
      <h3>Trajectory</h3>
      <p>${report.trajectory}</p>
      <h3>Balance sheet & cash quality</h3>
      <p>${report.balance_sheet}</p>
      <p>${report.cash_quality}</p>
      <h3>Narrative vs numbers</h3>
      <p>${report.narrative_vs_numbers}</p>
      <h3>Guidance check</h3>
      <ul class="accent-list">${guidance}</ul>
      <h3>Bull vs bear</h3>
      <div class="two-col">
        <div class="metric-box"><div class="label">Bull case</div><div class="value narrative">${report.bull_case}</div></div>
        <div class="metric-box"><div class="label">Bear case</div><div class="value narrative">${report.bear_case}</div></div>
      </div>
      <h3>Network signal</h3>
      <div class="tag-row">${network}</div>
    </article>
    <section id="filedResults"></section>
    <section id="sourceWorkspace"></section>
  `;
  bindMarketButton(ticker);
  loadFiledResults(ticker);
  bindSourceWorkspace(ticker);
}

async function loadFiledResults(ticker) {
  const target = document.getElementById('filedResults');
  target.innerHTML = '<div class="empty-state">Checking for a cited quarterly-results filing…</div>';
  try {
    const results = await fetchJson(`/api/research/${encodeURIComponent(ticker)}/results`);
    if (!results.available) {
      target.innerHTML = `<div class="empty-state">${escapeHtml(results.reason)}</div>`;
      return;
    }

    const rows = Object.entries(results.metrics).map(([name, values]) => `
      <tr>
        <th>${escapeHtml(name)}</th>
        <td>${values.current.toLocaleString('en-IN')}</td>
        <td>${values.qoq_pct >= 0 ? '+' : ''}${values.qoq_pct}%</td>
        <td>${values.yoy_pct >= 0 ? '+' : ''}${values.yoy_pct}%</td>
      </tr>
    `).join('');
    const citation = `${results.source.source_url}#page=${results.source.page}`;
    target.innerHTML = `
      <article class="research-card">
        <div class="meta-row">
          <span class="badge">Filed quarterly results</span>
          <span class="demo-label">EXCHANGE-SOURCED</span>
        </div>
        <h3>${escapeHtml(results.period)}</h3>
        <p class="eyebrow">${escapeHtml(results.notice)} Values in ${escapeHtml(results.unit)}.</p>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Metric</th><th>Current</th><th>QoQ</th><th>YoY</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
        <p><a class="source-link" href="${escapeHtml(citation)}" target="_blank" rel="noopener noreferrer">${escapeHtml(results.source.title)} · p. ${results.source.page}</a></p>
      </article>
    `;
  } catch (error) {
    target.innerHTML = `<div class="empty-state">Unable to load cited quarterly results: ${escapeHtml(error.message)}</div>`;
  }
}

function bindMarketButton(ticker) {
  document.getElementById('marketButton').addEventListener('click', async () => {
    const target = document.getElementById('marketDetails');
    target.innerHTML = '<div class="empty-state">Fetching latest available end-of-day data…</div>';
    try {
      const market = await fetchJson(`/api/market/${encodeURIComponent(ticker)}`);
      target.innerHTML = `
        <div class="market-snapshot">
          <div class="meta-row">
            <span class="badge">${market.ticker} · ${market.market_date}</span>
            <span class="priority">Source: ${market.source}</span>
          </div>
          <div class="two-col">
            <div class="metric-box"><div class="label">Close</div><div class="value">₹${market.price.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</div></div>
            <div class="metric-box"><div class="label">Daily move</div><div class="value">${market.change_pct === null ? '—' : `${market.change_pct > 0 ? '+' : ''}${market.change_pct}%`}</div></div>
            <div class="metric-box"><div class="label">Volume</div><div class="value">${market.volume.toLocaleString('en-IN')}</div></div>
            <div class="metric-box"><div class="label">Vs 20-day average</div><div class="value">${market.volume_multiple === null ? 'Not available' : `${market.volume_multiple}×`}</div></div>
          </div>
        </div>
      `;
    } catch (error) {
      target.innerHTML = `<div class="empty-state">Live market data unavailable: ${escapeHtml(error.message)}. The sample portfolio figures remain illustrative.</div>`;
    }
  });
}

function bindSourceWorkspace(ticker) {
  const workspace = document.getElementById('sourceWorkspace');
  workspace.innerHTML = `
    <article class="research-card source-workspace">
      <div class="meta-row">
        <h3>Primary-source library</h3>
        <span class="demo-label">LOCAL PDF INGESTION</span>
      </div>
      <p class="muted-copy">Local builds can upload company or exchange PDFs with public source URLs. Search returns page-cited excerpts; this prototype does not generate a complete investment thesis. The hosted demo is read-only.</p>
      <form id="sourceUploadForm" class="source-form">
        <label>Document type
          <select name="doc_type" required>
            <option value="annual_report">Annual report</option>
            <option value="quarterly_results">Quarterly results filing</option>
            <option value="earnings_call_transcript">Earnings-call transcript</option>
            <option value="investor_presentation">Investor presentation</option>
          </select>
        </label>
        <label>Document title
          <input name="title" type="text" maxlength="250" required placeholder="e.g. FY2025 Annual Report">
        </label>
        <label>Public source URL
          <input name="source_url" type="url" required placeholder="https://...">
        </label>
        <label>PDF file (max 25 MB)
          <input name="file" type="file" accept="application/pdf,.pdf" required>
        </label>
        <button class="primary-btn" type="submit">Add source PDF</button>
      </form>
      <p id="sourceWriteNotice" class="muted-copy" hidden>Uploads and deletion are disabled in this hosted demo. Source documents are read-only here.</p>
      <div id="sourceUploadStatus" class="muted-copy"></div>
      <h3>Added documents</h3>
      <div id="sourceList" class="card-stack"></div>
      <form id="evidenceSearchForm" class="form-controls">
        <label class="select-wrap">Search source text
          <input name="query" type="search" maxlength="500" required placeholder="revenue guidance margin cash flow">
        </label>
        <button class="primary-btn" type="submit">Find cited passages</button>
      </form>
      <div id="evidenceResults"></div>
    </article>
  `;

  refreshSourceList(ticker);
  document.getElementById('sourceUploadForm').addEventListener('submit', async event => {
    event.preventDefault();
    const form = event.currentTarget;
    const status = document.getElementById('sourceUploadStatus');
    status.textContent = 'Extracting PDF text and storing it locally…';
    try {
      const source = await fetchJson(`/api/research/${encodeURIComponent(ticker)}/sources`, {
        method: 'POST',
        body: new FormData(form)
      });
      status.textContent = `Added ${source.title} (${source.page_count} pages).`;
      form.reset();
      await refreshSourceList(ticker);
    } catch (error) {
      status.textContent = `Could not add PDF: ${error.message}`;
    }
  });

  document.getElementById('evidenceSearchForm').addEventListener('submit', async event => {
    event.preventDefault();
    const query = new FormData(event.currentTarget).get('query');
    const target = document.getElementById('evidenceResults');
    target.innerHTML = '<div class="empty-state">Searching uploaded source documents…</div>';
    try {
      const result = await fetchJson(`/api/research/${encodeURIComponent(ticker)}/evidence?query=${encodeURIComponent(query)}`);
      target.innerHTML = renderEvidenceMatches(result.matches);
    } catch (error) {
      target.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
    }
  });
}

async function refreshSourceList(ticker) {
  const target = document.getElementById('sourceList');
  target.innerHTML = '<div class="empty-state">Loading source documents…</div>';
  try {
    const result = await fetchJson(`/api/research/${encodeURIComponent(ticker)}/sources`);
  const writesEnabled = result.writes_enabled !== false;
  document.getElementById('sourceUploadForm').hidden = !writesEnabled;
  document.getElementById('sourceWriteNotice').hidden = writesEnabled;
    if (!result.sources.length) {
      target.innerHTML = '<div class="empty-state">No primary-source PDFs have been added for this ticker yet.</div>';
      return;
    }
    target.innerHTML = result.sources.map(source => `
      <article class="source-entry">
        <div class="meta-row">
          <span class="badge">${escapeHtml(source.doc_type.replace(/_/g, ' '))}</span>
          ${writesEnabled ? `<button class="text-btn" type="button" data-delete-source="${escapeHtml(source.id)}">Delete</button>` : ''}
        </div>
        <a class="source-link" href="${escapeHtml(source.source_url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.title)}</a>
        <p class="eyebrow">${source.page_count} pages · added ${escapeHtml(source.uploaded_at)} · SHA-256 ${escapeHtml(source.sha256.slice(0, 12))}…</p>
      </article>
    `).join('');
    target.querySelectorAll('[data-delete-source]').forEach(button => {
      button.addEventListener('click', async () => {
        const sourceId = button.dataset.deleteSource;
        const response = await fetch(`/api/research/${encodeURIComponent(ticker)}/sources/${encodeURIComponent(sourceId)}`, { method: 'DELETE' });
        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          document.getElementById('sourceUploadStatus').textContent = error.detail || `Delete failed: ${response.status}`;
          return;
        }
        await refreshSourceList(ticker);
      });
    });
  } catch (error) {
    target.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
  }
}

function renderEvidenceMatches(matches) {
  if (!matches.length) {
    return '<div class="empty-state">No matching text found in the uploaded source documents.</div>';
  }
  return `<div class="card-stack">${matches.map(match => `
    <article class="source-entry">
      <div class="meta-row">
        <span class="badge">${escapeHtml(match.doc_type.replace(/_/g, ' '))}</span>
        <span class="priority">Page ${match.page}</span>
      </div>
      <a class="source-link" href="${escapeHtml(match.source_url)}#page=${match.page}" target="_blank" rel="noopener noreferrer">${escapeHtml(match.title)} · p. ${match.page}</a>
      <p>${escapeHtml(match.excerpt)}</p>
    </article>
  `).join('')}</div>`;
}

async function renderNetwork() {
  const network = await fetchJson('/api/network');
  const people = network.people.map(person => `
    <article class="network-card">
      <div class="meta-row">
        <span class="badge">${person.name}</span>
        <span class="priority">${person.strength}/100</span>
      </div>
      <h3>${person.role}</h3>
      <p><strong>Relationship:</strong> ${person.relationship}</p>
      <p>${person.why_helpful}</p>
      <div class="tag-row">
        ${person.company_overlap.map(tag => `<span class="tag">${tag}</span>`).join('')}
      </div>
    </article>
  `).join('');

  contentArea.innerHTML = `
    <div class="section-title">The Network layer <span class="demo-label">SYNTHETIC PROFILES</span></div>
    <p class="muted-copy">These fictional profiles demonstrate matching logic only. No real person's professional profile was collected.</p>
    <div class="card-stack">${people}</div>
  `;
}

async function loadView(view) {
  state.currentView = view;
  document.querySelectorAll('.nav-btn').forEach(button => {
    button.classList.toggle('active', button.dataset.view === view);
  });

  if (view === 'push') await loadPush();
  if (view === 'pull') await renderPull();
  if (view === 'network') await renderNetwork();
}

async function init() {
  const overview = await fetchJson('/api/overview');
  renderOverview(overview);
  await loadView('push');

  document.querySelectorAll('.nav-btn').forEach(button => {
    button.addEventListener('click', () => {
      loadView(button.dataset.view).catch(showError);
    });
  });
}

function showError(error) {
  const card = document.createElement('div');
  card.className = 'news-card';
  const heading = document.createElement('h3');
  heading.textContent = 'Unable to load this view';
  const message = document.createElement('p');
  message.textContent = error.message;
  card.append(heading, message);
  contentArea.replaceChildren(card);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, character => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  })[character]);
}

init().catch(showError);
