DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading AI LIVE | LLM Baseline</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0b0f19;
            --card-bg: #161b2a;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.2);
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --green: #10b981;
            --red: #ef4444;
            --border: #1e293b;
        }

        body {
            margin: 0;
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }

        header {
            background: var(--card-bg);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        h1 {
            margin: 0;
            font-size: 1.25rem;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        h1::before { content: "📈"; }

        .controls {
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        button {
            background: var(--accent);
            color: var(--bg);
            border: none;
            padding: 0.5rem 1.25rem;
            border-radius: 0.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        button:hover { opacity: 0.9; transform: translateY(-1px); }

        button#resetBtn {
            background: transparent;
            color: var(--accent);
            border: 1px solid var(--accent);
        }

        select {
            background: var(--card-bg);
            color: var(--text);
            border: 1px solid var(--border);
            padding: 0.5rem;
            border-radius: 0.5rem;
            cursor: pointer;
        }

        main {
            flex: 1;
            padding: 1.5rem;
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 1.5rem;
            overflow-y: auto;
        }

        .dashboard-grid { display: flex; flex-direction: column; gap: 1.5rem; }

        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
        }

        .metric-card {
            background: var(--card-bg);
            padding: 1.25rem;
            border-radius: 1rem;
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .metric-label { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; }
        .metric-value { font-size: 1.5rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

        .charts {
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 250px 250px;
            gap: 1.5rem;
        }

        .chart-container {
            background: var(--card-bg);
            padding: 1rem;
            border-radius: 1rem;
            border: 1px solid var(--border);
            position: relative;
        }

        .log-container {
            background: var(--card-bg);
            border-radius: 1rem;
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            height: 100%;
        }

        .log-header { padding: 1rem; border-bottom: 1px solid var(--border); font-weight: 600; }
        .log-body { flex: 1; overflow-y: auto; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; }

        table { width: 100%; border-collapse: collapse; }
        th { position: sticky; top: 0; background: var(--card-bg); text-align: left; padding: 0.5rem 1rem; border-bottom: 1px solid var(--border); }
        td { padding: 0.5rem 1rem; border-bottom: 1px solid var(--border); }

        .action-BUY { color: var(--green); }
        .action-SELL { color: var(--red); }
        .action-HOLD { color: var(--text-muted); }
        .pos { color: var(--green); }
        .neg { color: var(--red); }
    </style>
</head>
<body>
    <header>
        <h1>TRADING AI LIVE | LLM BASELINE</h1>
        <div class="controls">
            <select id="speedSel">
                <option value="1000">Slow</option>
                <option value="200" selected>Normal</option>
                <option value="50">Fast</option>
            </select>
            <button id="runBtn">▶ RUN</button>
            <button id="resetBtn">🔄 RESET</button>
        </div>
    </header>

    <main>
        <div class="dashboard-grid">
            <div class="metrics">
                <div class="metric-card">
                    <span class="metric-label">Portfolio Value</span>
                    <span class="metric-value" id="m-pv">$10,000</span>
                    <div class="metric-sub" id="m-pnl">+$0.00 (0.00%)</div>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Steps Taken</span>
                    <span class="metric-value" id="m-steps">0</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Total Trades</span>
                    <span class="metric-value" id="m-trades">0</span>
                </div>
            </div>

            <div class="charts">
                <div class="chart-container"><canvas id="chart-pv"></canvas></div>
                <div class="chart-container"><canvas id="chart-reward"></canvas></div>
                <div class="chart-container"><canvas id="chart-actions"></canvas></div>
                <div class="chart-container"><canvas id="chart-cum-reward"></canvas></div>
            </div>
        </div>

        <aside class="log-container">
            <div class="log-header">Live Session Logs</div>
            <div class="log-body">
                <table id="logTable">
                    <thead><tr><th>Step</th><th>Action</th><th>Reward</th><th>Value</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </aside>
    </main>

    <script>
        let running = false;
        let timer = null;
        let currentStep = 0;
        let baseline = 10000;
        let data = { pv: [], rewards: [], cumRewards: [], actions: [0, 0, 0], logs: [] };

        const ctxPv = document.getElementById('chart-pv').getContext('2d');
        const chartPv = new Chart(ctxPv, {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'Portfolio', data: [], borderColor: '#38bdf8', fill: true, backgroundColor: 'rgba(56, 189, 248, 0.1)' }]},
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display:false } }}
        });

        const chartReward = new Chart(document.getElementById('chart-reward').getContext('2d'), {
            type: 'bar',
            data: { labels: [], datasets: [{ data: [], backgroundColor: [] }]},
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display:false } }}
        });

        const chartActions = new Chart(document.getElementById('chart-actions').getContext('2d'), {
            type: 'doughnut',
            data: { labels: ['BUY', 'HOLD', 'SELL'], datasets: [{ data: [0,0,0], backgroundColor: ['#10b981', '#94a3b8', '#ef4444'] }]},
            options: { responsive: true, maintainAspectRatio: false }
        });

        const chartCumReward = new Chart(document.getElementById('chart-cum-reward').getContext('2d'), {
            type: 'line',
            data: { labels: [], datasets: [{ data: [], borderColor: '#10b981' }]},
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display:false } }}
        });

        async function resetEnv() {
            const res = await fetch('./reset', { method: 'POST' });
            const obs = await res.json();
            baseline = obs.portfolio_value;
            clearData();
            updateUI(obs);
        }

        function clearData() {
            currentStep = 0;
            data = { pv: [], rewards: [], cumRewards: [], actions: [0, 0, 0], logs: [] };
            chartPv.data.labels = []; chartPv.data.datasets[0].data = []; chartPv.update();
        }

        async function stepEnv() {
            if (!running) return;
            // Demo mode: Random Walk (since server only exposes environment now)
            const action = Math.floor(Math.random() * 3);
            const res = await fetch('./step', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: action })
            });
            const obs = await res.json();
            updateData(obs, action);
            updateUI(obs);
            if (obs.done) stop();
            else timer = setTimeout(stepEnv, parseInt(document.getElementById('speedSel').value));
        }

        function updateData(obs, action) {
            currentStep++;
            data.pv.push(obs.portfolio_value);
            data.rewards.push(obs.reward);
            data.cumRewards.push((data.cumRewards[data.cumRewards.length-1] || 0) + obs.reward);
            data.actions[action]++;
            data.logs.unshift({ step: currentStep, action: ['HOLD', 'BUY', 'SELL'][action], reward: obs.reward, pv: obs.portfolio_value });
        }

        function updateUI(obs) {
            document.getElementById('m-pv').innerText = `$${obs.portfolio_value.toFixed(2)}`;
            document.getElementById('m-steps').innerText = currentStep;
            document.getElementById('m-trades').innerText = data.actions[1] + data.actions[2];
            
            const labels = Array.from({length: data.pv.length}, (_, i) => i);
            chartPv.data.labels = labels; chartPv.data.datasets[0].data = data.pv; chartPv.update('none');
            
            const tbody = document.querySelector('#logTable tbody');
            tbody.innerHTML = data.logs.slice(0, 10).map(log => `
                <tr><td>${log.step}</td><td class="action-${log.action}">${log.action}</td><td class="${log.reward >= 0 ? 'pos' : 'neg'}">${log.reward.toFixed(4)}</td><td>$${log.pv.toFixed(2)}</td></tr>
            `).join('');
        }

        function stop() { running = false; document.getElementById('runBtn').innerText = '▶ RUN'; }
        function start() { running = true; document.getElementById('runBtn').innerText = '⏸ PAUSE'; stepEnv(); }

        document.getElementById('runBtn').addEventListener('click', () => running ? stop() : start());
        document.getElementById('resetBtn').addEventListener('click', () => { stop(); resetEnv(); });
        window.addEventListener('load', resetEnv);
    </script>
</body>
</html>
"""
