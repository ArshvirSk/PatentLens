document.addEventListener('DOMContentLoaded', () => {
    // ─── Tab Navigation ──────────────────────────────────────
    const tabs = document.querySelectorAll('.nav-tab');
    const panels = document.querySelectorAll('.tab-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`panel-${tab.dataset.tab}`).classList.add('active');

            // Lazy-load stats on first visit
            if (tab.dataset.tab === 'explorer' && !statsLoaded) {
                loadStats();
            }
        });
    });

    // ─── Weight Sliders ──────────────────────────────────────
    const zones = ['claims', 'title', 'abstract', 'description'];
    zones.forEach(z => {
        const slider = document.getElementById(`w-${z}`);
        const valEl = document.getElementById(`w-${z}-val`);
        slider.addEventListener('input', () => {
            valEl.textContent = parseFloat(slider.value).toFixed(2);
        });
    });

    function getWeights() {
        return {
            claims: parseFloat(document.getElementById('w-claims').value),
            title: parseFloat(document.getElementById('w-title').value),
            abstract: parseFloat(document.getElementById('w-abstract').value),
            description: parseFloat(document.getElementById('w-description').value),
        };
    }

    // ─── Search ──────────────────────────────────────────────
    const searchBtn = document.getElementById('search-btn');
    const queryInput = document.getElementById('search-query');
    const loading = document.getElementById('loading');
    const searchResults = document.getElementById('search-results');
    const resultsList = document.getElementById('results-list');
    const resultsHeading = document.getElementById('results-heading');
    const resultsMeta = document.getElementById('results-meta');

    searchBtn.addEventListener('click', performSearch);
    queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); performSearch(); }
    });

    async function performSearch() {
        const query = queryInput.value.trim();
        if (!query) return;

        searchResults.style.display = 'none';
        loading.style.display = 'flex';
        resultsList.innerHTML = '';

        const cpcFilter = document.getElementById('filter-cpc').value;
        const topK = parseInt(document.getElementById('filter-topk').value) || 20;

        try {
            const res = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query,
                    weights: getWeights(),
                    top_k: topK,
                    cpc_filter: cpcFilter || null,
                }),
            });
            const data = await res.json();
            renderResults(data);
        } catch (err) {
            resultsList.innerHTML = `<p style="color:var(--rose)">Search failed. Ensure the backend is running.</p>`;
            searchResults.style.display = 'block';
        } finally {
            loading.style.display = 'none';
        }
    }

    function renderResults(data) {
        const { results, total, time_ms } = data;
        resultsHeading.textContent = `Top ${total} Results`;
        resultsMeta.textContent = `${time_ms}ms`;

        if (results.length === 0) {
            resultsList.innerHTML = `<p style="color:var(--text-2)">No matching patents found. Try a different query or relax your filters.</p>`;
        } else {
            // Find max zone score for bar scaling
            let maxZone = 0;
            results.forEach(r => {
                Object.values(r.zone_scores).forEach(v => { if (v > maxZone) maxZone = v; });
            });
            if (maxZone === 0) maxZone = 1;

            results.forEach((r, i) => {
                const matchHtml = Object.entries(r.matched_terms || {})
                    .filter(([, terms]) => terms.length > 0)
                    .map(([zone, terms]) => `<strong>${zone}:</strong> ${terms.join(', ')}`)
                    .join(' &nbsp;·&nbsp; ');

                const abstractText = r.abstract
                    ? r.abstract.substring(0, 180) + (r.abstract.length > 180 ? '…' : '')
                    : '';

                const card = `
                <div class="result-card" style="animation-delay:${i * 0.06}s" data-patent-id="${r.id}">
                    <div class="result-top">
                        <div class="result-title">${r.title || 'Untitled Patent'}</div>
                        <div class="result-score-badge">${r.score.toFixed(4)}</div>
                    </div>
                    <div class="result-meta">
                        <span>${r.id}</span>
                        <span>${r.cpc}</span>
                        <span>${r.date}</span>
                        ${r.assignee ? `<span>${r.assignee}</span>` : ''}
                    </div>
                    ${abstractText ? `<div class="result-abstract">${abstractText}</div>` : ''}
                    <div class="zone-bars">
                        ${zones.map(z => {
                            const val = r.zone_scores[z] || 0;
                            const pct = (val / maxZone * 100).toFixed(1);
                            return `
                            <div class="zone-bar ${z}">
                                <div class="zone-bar-label"><span>${capitalize(z)}</span><span>${val.toFixed(4)}</span></div>
                                <div class="zone-bar-track"><div class="zone-bar-fill" style="width:${pct}%"></div></div>
                            </div>`;
                        }).join('')}
                    </div>
                    ${matchHtml ? `<div class="matched-terms">${matchHtml}</div>` : ''}
                </div>`;
                resultsList.insertAdjacentHTML('beforeend', card);
            });

            // Attach click-to-detail
            resultsList.querySelectorAll('.result-card').forEach(card => {
                card.addEventListener('click', () => openPatentModal(card.dataset.patentId));
            });
        }
        searchResults.style.display = 'block';
    }

    // ─── Patent Detail Modal ─────────────────────────────────
    const modal = document.getElementById('patent-modal');
    const modalContent = document.getElementById('modal-content');
    document.getElementById('modal-close-btn').addEventListener('click', () => modal.style.display = 'none');
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });

    async function openPatentModal(patentId) {
        modal.style.display = 'flex';
        modalContent.innerHTML = `<div class="loading"><div class="spinner"></div></div>`;

        try {
            const res = await fetch(`/api/patent/${patentId}`);
            const p = await res.json();
            modalContent.innerHTML = `
                <div class="modal-title">${p.title}</div>
                <div class="modal-meta">
                    <span>${p.id}</span>
                    <span>${p.cpc}</span>
                    <span>${p.date}</span>
                    ${p.assignee ? `<span>${p.assignee}</span>` : ''}
                </div>
                <div class="modal-section"><h4>Abstract</h4><p>${p.abstract || 'N/A'}</p></div>
                <div class="modal-section"><h4>Claims</h4><p>${p.claims || 'N/A'}</p></div>
                <div class="modal-section"><h4>Description</h4><p>${p.description || 'N/A'}</p></div>
                ${p.citations && p.citations.length > 0
                    ? `<div class="modal-section"><h4>Citations</h4><p>${p.citations.join(', ')}</p></div>`
                    : ''}
            `;
        } catch {
            modalContent.innerHTML = `<p style="color:var(--rose)">Failed to load patent details.</p>`;
        }
    }

    // ─── Evaluation ──────────────────────────────────────────
    const runEvalBtn = document.getElementById('run-eval-btn');
    const evalLoading = document.getElementById('eval-loading');
    const evalResults = document.getElementById('eval-results');

    runEvalBtn.addEventListener('click', runEvaluation);

    async function runEvaluation() {
        runEvalBtn.style.display = 'none';
        evalResults.style.display = 'none';
        evalLoading.style.display = 'flex';

        try {
            const res = await fetch('/api/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ weights: getWeights() }),
            });
            const data = await res.json();
            renderEvaluation(data);
        } catch {
            evalResults.innerHTML = `<p style="color:var(--rose)">Evaluation failed.</p>`;
            evalResults.style.display = 'block';
        } finally {
            evalLoading.style.display = 'none';
            runEvalBtn.style.display = 'inline-flex';
        }
    }

    function renderEvaluation(data) {
        const kValues = Object.keys(data.aggregate).sort((a, b) => +a - +b);

        // Summary cards
        let summaryHtml = `<div class="eval-summary">
            <div class="eval-metric-card">
                <div class="metric-value" style="color:var(--accent)">${data.map.toFixed(4)}</div>
                <div class="metric-label">MAP (Mean Avg Precision)</div>
            </div>
            <div class="eval-metric-card">
                <div class="metric-value" style="color:var(--green)">${data.num_queries}</div>
                <div class="metric-label">Queries Evaluated</div>
            </div>`;

        kValues.forEach(k => {
            const agg = data.aggregate[k];
            summaryHtml += `
            <div class="eval-metric-card">
                <div class="metric-value" style="color:var(--amber)">${agg.avg_precision.toFixed(4)}</div>
                <div class="metric-label">Avg Precision@${k}</div>
            </div>`;
        });
        summaryHtml += `</div>`;

        // Aggregate table
        let aggTableHtml = `
        <h3 style="margin-bottom:0.75rem">Aggregate Metrics by K</h3>
        <div class="eval-table-wrap"><table class="eval-table">
            <thead><tr>
                <th>K</th><th class="num">Avg Precision</th><th class="num">Avg Recall</th><th class="num">Avg F1</th>
            </tr></thead><tbody>`;
        kValues.forEach(k => {
            const a = data.aggregate[k];
            aggTableHtml += `<tr>
                <td>${k}</td>
                <td class="num">${a.avg_precision.toFixed(4)}</td>
                <td class="num">${a.avg_recall.toFixed(4)}</td>
                <td class="num">${a.avg_f1.toFixed(4)}</td>
            </tr>`;
        });
        aggTableHtml += `</tbody></table></div>`;

        // Per-query table
        let perQueryHtml = `
        <h3 style="margin:1.5rem 0 0.75rem">Per-Query Results</h3>
        <div class="eval-table-wrap"><table class="eval-table">
            <thead><tr>
                <th>Query ID</th><th>Query (truncated)</th><th class="num">Relevant</th><th class="num">Retrieved</th><th class="num">AP</th>
            </tr></thead><tbody>`;
        data.per_query.forEach(q => {
            perQueryHtml += `<tr>
                <td>${q.query_id}</td>
                <td>${q.query_text}</td>
                <td class="num">${q.num_relevant}</td>
                <td class="num">${q.num_retrieved}</td>
                <td class="num">${q.average_precision.toFixed(4)}</td>
            </tr>`;
        });
        perQueryHtml += `</tbody></table></div>`;

        evalResults.innerHTML = summaryHtml + aggTableHtml + perQueryHtml;
        evalResults.style.display = 'block';
    }

    // ─── Index Explorer ──────────────────────────────────────
    let statsLoaded = false;
    const statsLoading = document.getElementById('stats-loading');
    const statsContent = document.getElementById('stats-content');

    async function loadStats() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();
            renderStats(data);
            statsLoaded = true;
        } catch {
            statsContent.innerHTML = `<p style="color:var(--rose)">Failed to load stats.</p>`;
            statsContent.style.display = 'block';
        } finally {
            statsLoading.style.display = 'none';
        }
    }

    const CPC_COLORS = {
        'G06F': 'var(--accent)',
        'H04W': 'var(--green)',
        'G06N': 'var(--violet)',
        'H04L': 'var(--amber)',
        'A61B': 'var(--rose)',
        'B60W': '#fb923c',
        'G06T': '#2dd4bf',
    };

    function renderStats(data) {
        const totalVocab = Object.values(data.vocabulary_sizes).reduce((a, b) => a + b, 0);
        const maxCpc = Math.max(...Object.values(data.cpc_distribution));

        let html = `<div class="stats-grid">
            <div class="stat-card"><div class="stat-value" style="color:var(--accent)">${data.doc_count.toLocaleString()}</div><div class="stat-label">Total Patents Indexed</div></div>
            <div class="stat-card"><div class="stat-value" style="color:var(--green)">${totalVocab.toLocaleString()}</div><div class="stat-label">Total Unique Terms</div></div>
            <div class="stat-card"><div class="stat-value" style="color:var(--amber)">${Object.keys(data.cpc_distribution).length}</div><div class="stat-label">CPC Classes</div></div>
            <div class="stat-card"><div class="stat-value" style="color:var(--violet)">${data.zones.length}</div><div class="stat-label">Index Zones</div></div>
        </div>`;

        // Vocabulary per zone
        html += `<div class="stats-grid">`;
        data.zones.forEach(z => {
            html += `<div class="stat-card"><div class="stat-value" style="color:var(--text-2)">${data.vocabulary_sizes[z].toLocaleString()}</div><div class="stat-label">Vocab — ${capitalize(z)}</div></div>`;
        });
        html += `</div>`;

        // CPC bar chart
        html += `<div class="cpc-chart"><h3>CPC Class Distribution</h3>`;
        Object.entries(data.cpc_distribution)
            .sort((a, b) => b[1] - a[1])
            .forEach(([cpc, count]) => {
                const pct = (count / maxCpc * 100).toFixed(1);
                const color = CPC_COLORS[cpc] || 'var(--text-3)';
                html += `<div class="cpc-bar-row">
                    <div class="cpc-bar-label">${cpc}</div>
                    <div class="cpc-bar-track"><div class="cpc-bar-fill" style="width:${pct}%;background:${color}"></div></div>
                    <div class="cpc-bar-count">${count}</div>
                </div>`;
            });
        html += `</div>`;

        statsContent.innerHTML = html;
        statsContent.style.display = 'block';
    }

    // ─── Helpers ─────────────────────────────────────────────
    function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
});
