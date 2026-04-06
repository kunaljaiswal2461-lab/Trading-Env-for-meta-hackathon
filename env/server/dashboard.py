DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RL Trading Dashboard v2.1 | Kj2461</title>
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

        h1::before {
            content: "📈";
        }

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

        button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }

        button:disabled {
            background: var(--text-muted);
            cursor: not-allowed;
        }

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

        .tabs {
            display: flex;
            background: var(--bg);
            padding: 0.25rem;
            border-radius: 0.75rem;
            border: 1px solid var(--border);
        }

        .tab {
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.875rem;
            color: var(--text-muted);
        }

        .tab.active {
            background: var(--card-bg);
            color: var(--accent);
            font-weight: 600;
        }

        main {
            flex: 1;
            padding: 1.5rem;
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 1.5rem;
            overflow-y: auto;
        }

        .dashboard-grid {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

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

        .metric-label {
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
        }

        .metric-sub {
            font-size: 0.75rem;
            display: flex;
            gap: 0.5rem;
        }

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
            max-height: calc(100vh - 120px);
        }

        .log-header {
            padding: 1rem;
            border-bottom: 1px solid var(--border);
            font-weight: 600;
            font-size: 0.875rem;
        }

        .log-body {
            flex: 1;
            overflow-y: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            padding: 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th {
            position: sticky;
            top: 0;
            background: var(--card-bg);
            text-align: left;
            padding: 0.5rem 1rem;
            color: var(--text-muted);
            font-weight: 500;
            border-bottom: 1px solid var(--border);
        }

        td {
            padding: 0.5rem 1rem;
            border-bottom: 1px solid var(--border);
        }

        .action-BUY { color: var(--green); }
        .action-SELL { color: var(--red); }
        .action-HOLD { color: var(--text-muted); }

        .pos { color: var(--green); }
        .neg { color: var(--red); }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg); }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    </style>
</head>
<body>
    <header>
        <h1>TRADING AI LIVE</h1>
        <div class="tabs">
            <div class="tab active" data-steps="250">EASY</div>
            <div class="tab" data-steps="500">MID-MEDIUM</div>
            <div class="tab" data-steps="750">MEDIUM</div>
            <div class="tab" data-steps="968">HARD</div>
        </div>
        <div class="controls">
            <select id="speedSel">
                <option value="1000">Slow</option>
                <option value="200" selected>Normal</option>
                <option value="50">Fast</option>
                <option value="0">Max Speed</option>
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
                    <span class="metric-label">Current Score</span>
                    <span class="metric-value" id="m-score">0.000</span>
                    <span class="metric-label" style="font-size: 0.6rem">Normalized Range</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Win Rate</span>
                    <span class="metric-value" id="m-winrate">0%</span>
                    <div class="metric-sub" id="m-winratio">0 / 0 steps</div>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Drawdown</span>
                    <span class="metric-value neg" id="m-dd">0.00%</span>
                    <span class="metric-label" id="m-peak" style="font-size: 0.6rem">Peak: $10,000</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Total Trades</span>
                    <span class="metric-value" id="m-trades">0</span>
                    <span class="metric-label" id="m-steps" style="font-size: 0.6rem">Steps: 0</span>
                </div>
            </div>

            <div class="charts">
                <div class="chart-container">
                    <canvas id="chart-pv"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="chart-reward"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="chart-actions"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="chart-cum-reward"></canvas>
                </div>
            </div>
        </div>

        <aside class="log-container">
            <div class="log-header">Live Step Logs</div>
            <div class="log-body">
                <table id="logTable">
                    <thead>
                        <tr>
                            <th>Step</th>
                            <th>Action</th>
                            <th>Reward</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </aside>
    </main>

    <script>
        let running = false;
        let timer = null;
        let stepsLimit = 250;
        let currentStep = 0;
        let baseline = 10000;
        let lastObs = null;
        let data = {
            pv: [],
            rewards: [],
            cumRewards: [],
            actions: [0, 0, 0], // BUY, HOLD, SELL
            logs: []
        };

        const ctxPv = document.getElementById('chart-pv').getContext('2d');
        const ctxReward = document.getElementById('chart-reward').getContext('2d');
        const ctxActions = document.getElementById('chart-actions').getContext('2d');
        const ctxCumReward = document.getElementById('chart-cum-reward').getContext('2d');

        const chartPv = new Chart(ctxPv, {
            type: 'line',
            data: { labels: [], datasets: [
                { label: 'Portfolio Value', data: [], borderColor: '#38bdf8', borderWidth: 2, radius: 0, fill: true, backgroundColor: 'rgba(56, 189, 248, 0.1)' },
                { label: 'Baseline', data: [], borderColor: '#1e293b', borderDash: [5, 5], radius: 0 }
            ]},
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { grid: { color: '#1e293b' } } } }
        });

        const chartReward = new Chart(ctxReward, {
            type: 'bar',
            data: { labels: [], datasets: [{ label: 'Reward', data: [], backgroundColor: [] }]},
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { grid: { color: '#1e293b' } } } }
        });

        const chartActions = new Chart(ctxActions, {
            type: 'doughnut',
            data: { labels: ['BUY', 'HOLD', 'SELL'], datasets: [{ data: [0, 0, 0], backgroundColor: ['#10b981', '#94a3b8', '#ef4444'], borderWidth: 0 }]},
            options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', boxWidth: 10 } } } }
        });

        const chartCumReward = new Chart(ctxCumReward, {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'Cumulative Reward', data: [], borderColor: '#10b981', borderWidth: 2, radius: 0 }]},
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { grid: { color: '#1e293b' } } } }
        });

        async function resetEnv() {
            try {
                const res = await fetch('./reset', { method: 'POST' });
                const obs = await res.json();
                console.log("Environment Reset:", obs);
                lastObs = obs;
                baseline = obs.portfolio_value;
                clearData();
                updateUI(obs);
                return obs;
            } catch (e) { console.error("Reset failed", e); }
        }

        function clearData() {
            currentStep = 0;
            data = { pv: [], rewards: [], cumRewards: [], actions: [0, 0, 0], logs: [] };
            chartPv.data.labels = []; chartPv.data.datasets[0].data = []; chartPv.data.datasets[1].data = [];
            chartReward.data.labels = []; chartReward.data.datasets[0].data = []; chartReward.data.datasets[0].backgroundColor = [];
            chartCumReward.data.labels = []; chartCumReward.data.datasets[0].data = [];
            chartActions.data.datasets[0].data = [0, 0, 0];
            chartPv.update(); chartReward.update(); chartCumReward.update(); chartActions.update();
            document.querySelector('#logTable tbody').innerHTML = '';
        }

        async function getAction(obs) {
            try {
                const resp = await fetch('./predict', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(obs)
                });
                const data = await resp.json();
                return data.action;
            } catch(e) {
                console.error("Prediction failed:", e);
                return 0; // fallback HOLD
            }
        }

        async function stepEnv() {
            if (!running || currentStep >= stepsLimit) {
                stop();
                return;
            }

            try {
                // [1] GET PROFESSIONAL ACTION FROM AGENT
                const action = await getAction(lastObs);
                
                // [2] EXECUTE STEP
                const res = await fetch('./step', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: action })
                });
                const obs = await res.json();
                lastObs = obs;
                updateData(obs, action);
                updateUI(obs);
                
                if (obs.done || currentStep >= stepsLimit) stop();
                else {
                    const speed = parseInt(document.getElementById('speedSel').value);
                    timer = setTimeout(stepEnv, speed);
                }
            } catch (e) { console.error("Inference step failed", e); stop(); }
        }

        function updateData(obs, action) {
            currentStep++;
            data.pv.push(obs.portfolio_value);
            data.rewards.push(obs.reward);
            const lastCum = data.cumRewards.length > 0 ? data.cumRewards[data.cumRewards.length - 1] : 0;
            data.cumRewards.push(lastCum + obs.reward);
            
            // 0=HOLD, 1=BUY, 2=SELL
            if (action === 1) data.actions[0]++;
            else if (action === 0) data.actions[1]++;
            else if (action === 2) data.actions[2]++;

            const actionNames = ['HOLD', 'BUY', 'SELL'];
            data.logs.unshift({
                step: currentStep,
                action: actionNames[action],
                reward: obs.reward,
                pv: obs.portfolio_value
            });
            if (data.logs.length > 50) data.logs.pop();
        }

        function updateUI(obs) {
            // Metrics
            document.getElementById('m-pv').innerText = `$${obs.portfolio_value.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}`;
            const pnl = obs.portfolio_value - baseline;
            const pnlPct = (pnl / baseline) * 100;
            const pnlEl = document.getElementById('m-pnl');
            pnlEl.innerText = `${pnl >= 0 ? '+' : ''}$${pnl.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})} (${pnlPct.toFixed(2)}%)`;
            pnlEl.className = `metric-sub ${pnl >= 0 ? 'pos' : 'neg'}`;

            document.getElementById('m-steps').innerText = `Steps: ${currentStep}`;
            document.getElementById('m-score').innerText = (obs.reward * 10).toFixed(3); // Mock score visualization
            
            const winCount = data.rewards.filter(r => r > 0).length;
            const winRate = currentStep > 0 ? (winCount / currentStep * 100).toFixed(1) : 0;
            document.getElementById('m-winrate').innerText = `${winRate}%`;
            document.getElementById('m-winratio').innerText = `${winCount} / ${currentStep} steps`;

            // Charts update logic
            const labels = Array.from({length: data.pv.length}, (_, i) => i);
            chartPv.data.labels = labels;
            chartPv.data.datasets[0].data = data.pv;
            chartPv.data.datasets[1].data = new Array(data.pv.length).fill(baseline);
            chartPv.update('none');

            chartReward.data.labels = labels;
            chartReward.data.datasets[0].data = data.rewards;
            chartReward.data.datasets[0].backgroundColor = data.rewards.map(r => r >= 0 ? '#10b981' : '#ef4444');
            chartReward.update('none');

            chartCumReward.data.labels = labels;
            chartCumReward.data.datasets[0].data = data.cumRewards;
            chartCumReward.update('none');

            chartActions.data.datasets[0].data = data.actions;
            chartActions.update('none');

            // Log table
            const tbody = document.querySelector('#logTable tbody');
            tbody.innerHTML = data.logs.map(log => `
                <tr>
                    <td>${log.step}</td>
                    <td class="action-${log.action}">${log.action}</td>
                    <td class="${log.reward >= 0 ? 'pos' : 'neg'}">${log.reward.toFixed(4)}</td>
                    <td>$${log.pv.toFixed(2)}</td>
                </tr>
            `).join('');

            // Max Drawdown (Calculated from peaks in data.pv)
            let maxPv = baseline;
            let maxDd = 0;
            for(let v of data.pv) {
                if(v > maxPv) maxPv = v;
                let dd = (maxPv - v) / maxPv;
                if(dd > maxDd) maxDd = dd;
            }
            document.getElementById('m-dd').innerText = `${(maxDd * 100).toFixed(2)}%`;
            document.getElementById('m-peak').innerText = `Peak: $${maxPv.toLocaleString(undefined, {maximumFractionDigits:0})}`;
            
            // Total Trades - we'll infer it from obs.current_step and self.trades if environment exposes it. 
            // In our current TradingState it is 'trades', but obs doesn't have it.
            // Let's count BUY/SELL actions from our data.actions
            document.getElementById('m-trades').innerText = data.actions[0] + data.actions[2];
        }

        function stop() {
            running = false;
            if (timer) clearTimeout(timer);
            document.getElementById('runBtn').innerText = '▶ RUN';
        }

        function start() {
            if (currentStep >= stepsLimit) {
                alert("Difficulty limit reached. Reset to run again.");
                return;
            }
            running = true;
            document.getElementById('runBtn').innerText = '⏸ PAUSE';
            stepEnv();
        }

        // Event Listeners
        document.getElementById('runBtn').addEventListener('click', () => {
            if (running) stop();
            else start();
        });

        document.getElementById('resetBtn').addEventListener('click', () => {
            stop();
            resetEnv();
        });

        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                stepsLimit = parseInt(tab.dataset.steps);
                stop();
                resetEnv();
            });
        });

        // Init
        window.addEventListener('load', () => {
            resetEnv();
        });
    </script>
</body>
</html>
"""
