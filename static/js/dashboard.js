/**
 * AegisFraud Analytics - Dashboard Manager
 * Manages KPI metrics, tab events, and responsive Plotly chart rendering.
 */

let activeDivision = "division_1";
let divisionDataCache = {};

document.addEventListener("DOMContentLoaded", function () {
    loadKpis();
    loadOverviewData();
    loadDivisionCharts(activeDivision);
    initDivisionButtons();
    initMobileSidebar();
    initDbConfigModal();

    document.getElementById("refreshAllBtn").addEventListener("click", function () {
        const icon = this.querySelector("i");
        icon.classList.add("spin-icon");
        divisionDataCache = {};
        Promise.all([loadKpis(), loadOverviewData(), loadDivisionCharts(activeDivision)]).finally(() => {
            setTimeout(() => icon.classList.remove("spin-icon"), 600);
        });
    });

    // Resize Plotly charts when switching tabs
    const tabButtons = document.querySelectorAll('#sidebarTabs button[data-bs-toggle="pill"]');
    tabButtons.forEach(btn => {
        btn.addEventListener("shown.bs.tab", function (e) {
            if (e.target.id === "tab-graphs-btn") {
                resizeAllPlots();
            }
        });
    });

    window.addEventListener("resize", debounce(resizeAllPlots, 200));
});

// Load KPI metrics
async function loadKpis() {
    try {
        const res = await fetch("/api/kpis");
        const json = await res.json();
        if (json.success && json.data) {
            const d = json.data;
            document.getElementById("kpiTotalUsers").textContent = Number(d.total_users).toLocaleString();
            document.getElementById("kpiTotalCards").textContent = Number(d.total_cards).toLocaleString();
            document.getElementById("kpiTotalTxns").textContent = Number(d.total_transactions).toLocaleString();
            document.getElementById("kpiTotalAmt").textContent = d.total_amount_formatted || `$${(d.total_amount/1e6).toFixed(2)}M`;
            document.getElementById("kpiFraudTxns").textContent = Number(d.fraudulent_transactions).toLocaleString();
            document.getElementById("kpiFraudRate").textContent = d.fraud_rate_formatted || `${d.fraud_rate}%`;
            document.getElementById("kpiFraudExposure").textContent = d.fraud_amount_formatted || `$${(d.fraud_amount/1e6).toFixed(2)}M`;
        }
    } catch (err) {
        console.error("Failed to load KPIs:", err);
    }
}

// Load Overview Briefing
async function loadOverviewData() {
    try {
        const res = await fetch("/api/overview");
        const json = await res.json();
        if (json.success && json.data && json.data.briefing) {
            document.getElementById("overviewBriefingText").textContent = json.data.briefing.summary;
        }
    } catch (err) {
        console.error("Failed to load Overview data:", err);
    }
}

// Initialize Division Switcher Buttons
function initDivisionButtons() {
    const btnGroup = document.getElementById("divisionButtonGroup");
    if (!btnGroup) return;

    btnGroup.querySelectorAll("button").forEach(btn => {
        btn.addEventListener("click", function () {
            btnGroup.querySelectorAll("button").forEach(b => b.classList.remove("active"));
            this.classList.add("active");
            activeDivision = this.getAttribute("data-division");
            loadDivisionCharts(activeDivision);
        });
    });
}

// Load Charts for Chosen Division
async function loadDivisionCharts(divisionId) {
    const container = document.getElementById("chartsGridContainer");
    if (!container) return;

    if (divisionDataCache[divisionId]) {
        renderCharts(divisionDataCache[divisionId]);
        return;
    }

    container.innerHTML = `
        <div class="col-12 text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <div class="text-muted mt-2">Loading ${divisionId.replace('_', ' ')} visualizations...</div>
        </div>
    `;

    try {
        const res = await fetch(`/api/charts/division/${divisionId}`);
        const json = await res.json();
        if (json.success && json.data) {
            divisionDataCache[divisionId] = json.data;
            renderCharts(json.data);
        } else {
            container.innerHTML = `<div class="col-12 alert alert-danger">Failed to load charts.</div>`;
        }
    } catch (err) {
        console.error("Failed to load division charts:", err);
        container.innerHTML = `<div class="col-12 alert alert-danger">Error connecting to server.</div>`;
    }
}

// Render Plotly Charts with exact layout requested (5 charts in Div 1: 3 in row 1, 2 in row 2; 4 charts in Div 2 & 3: 2 in row 1, 2 in row 2)
function renderCharts(divisionData) {
    const container = document.getElementById("chartsGridContainer");
    if (!container) return;

    document.getElementById("divisionHeaderTitle").textContent = divisionData.title;
    document.getElementById("divisionHeaderDesc").textContent = divisionData.description;

    container.innerHTML = "";
    const isDivision1 = divisionData.id === "division_1";

    divisionData.charts.forEach((chart, index) => {
        const col = document.createElement("div");

        if (isDivision1) {
            // Division 1: First 3 charts -> col-xl-4 (3 per row); next 2 charts -> col-xl-6 (2 per row)
            if (index < 3) {
                col.className = "col-12 col-md-6 col-xl-4";
            } else {
                col.className = "col-12 col-xl-6";
            }
        } else {
            // Division 2 & 3: 2 charts per row (2x2 grid) -> col-xl-6
            col.className = "col-12 col-xl-6";
        }

        const chartDivId = `chart_${chart.id}_${index}`;
        col.innerHTML = `
            <div class="chart-box">
                <div id="${chartDivId}" style="width: 100%; height: 390px;"></div>
            </div>
        `;
        container.appendChild(col);

        if (chart.data) {
            Plotly.newPlot(chartDivId, chart.data.data, chart.data.layout, {
                responsive: true,
                displayModeBar: false
            });
        } else if (chart.error) {
            document.getElementById(chartDivId).innerHTML = `
                <div class="text-danger small p-3">Error rendering chart: ${chart.error}</div>
            `;
        }
    });
}

function resizeAllPlots() {
    const plots = document.querySelectorAll(".chart-box > div");
    plots.forEach(div => {
        if (div && div.data) {
            Plotly.Plots.resize(div);
        }
    });
}

function initMobileSidebar() {
    const toggle = document.getElementById("mobileSidebarToggle");
    const sidebar = document.getElementById("sidebarMenu");
    if (toggle && sidebar) {
        toggle.addEventListener("click", () => {
            sidebar.classList.toggle("d-none");
        });
    }
}

function initDbConfigModal() {
    const saveBtn = document.getElementById("saveDbConfigBtn");
    if (saveBtn) {
        saveBtn.addEventListener("click", async () => {
            const host = document.getElementById("dbHost").value;
            const port = document.getElementById("dbPort").value;
            const database = document.getElementById("dbDatabase").value;
            const user = document.getElementById("dbUser").value;
            const password = document.getElementById("dbPassword").value;
            const statusBox = document.getElementById("dbTestStatus");

            statusBox.innerHTML = '<span class="spinner-border spinner-border-sm text-primary me-2"></span> Testing connection...';
            try {
                const res = await fetch("/api/db/config", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ host, port, database, user, password })
                });
                const json = await res.json();
                if (json.status === "connected") {
                    statusBox.innerHTML = `<span class="text-success fw-bold">✓ Connected!</span> Version: ${json.version}, Database: ${json.database}`;
                    document.getElementById("dbStatusBadge").textContent = `${json.host}:${json.port} [${json.database}]`;
                    loadKpis();
                } else {
                    statusBox.innerHTML = `<span class="text-danger fw-bold">✕ Error:</span> ${json.error}`;
                }
            } catch (err) {
                statusBox.innerHTML = `<span class="text-danger">Failed to connect: ${err.message}</span>`;
            }
        });
    }
}

function debounce(fn, delay) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}
