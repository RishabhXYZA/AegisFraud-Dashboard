/**
 * AegisFraud Analytics - SQL Query Explorer ("The Big Shot")
 * Manages enterprise SQL modules, live MySQL execution, metrics, and CSV export.
 */

let allModules = [];
let currentResults = null;

document.addEventListener("DOMContentLoaded", function () {
    initSqlExplorer();
});

async function initSqlExplorer() {
    await loadSqlModules();

    const moduleSelect = document.getElementById("sqlModuleSelect");
    const querySelect = document.getElementById("sqlQuerySelect");
    const executeBtn = document.getElementById("executeSqlBtn");
    const copyBtn = document.getElementById("copySqlBtn");
    const exportBtn = document.getElementById("exportCsvBtn");

    if (moduleSelect) {
        moduleSelect.addEventListener("change", function () {
            populateQueriesForModule(this.value);
        });
    }

    if (querySelect) {
        querySelect.addEventListener("change", function () {
            displaySelectedQuery(this.value);
        });
    }

    if (executeBtn) {
        executeBtn.addEventListener("click", executeCurrentSql);
    }

    if (copyBtn) {
        copyBtn.addEventListener("click", copySqlToClipboard);
    }

    if (exportBtn) {
        exportBtn.addEventListener("click", exportResultsToCsv);
    }
}

async function loadSqlModules() {
    try {
        const res = await fetch("/api/sql/modules");
        const json = await res.json();
        if (json.success && json.modules) {
            allModules = json.modules;
            const moduleSelect = document.getElementById("sqlModuleSelect");
            if (!moduleSelect) return;

            moduleSelect.innerHTML = "";
            allModules.forEach(mod => {
                const opt = document.createElement("option");
                opt.value = mod.id;
                opt.textContent = `${mod.name} (${mod.queries.length} Queries)`;
                moduleSelect.appendChild(opt);
            });

            if (allModules.length > 0) {
                populateQueriesForModule(allModules[0].id);
            }
        }
    } catch (err) {
        console.error("Failed to load SQL modules:", err);
    }
}

function populateQueriesForModule(moduleId) {
    const querySelect = document.getElementById("sqlQuerySelect");
    if (!querySelect) return;

    querySelect.innerHTML = "";
    const mod = allModules.find(m => m.id === moduleId);
    if (mod && mod.queries.length > 0) {
        mod.queries.forEach(q => {
            const opt = document.createElement("option");
            opt.value = q.id;
            opt.textContent = q.name;
            querySelect.appendChild(opt);
        });
        displaySelectedQuery(mod.queries[0].id);
    }
}

function displaySelectedQuery(queryId) {
    for (const mod of allModules) {
        const q = mod.queries.find(item => item.id === queryId);
        if (q) {
            document.getElementById("queryDescText").textContent = q.description;
            document.getElementById("sqlCodeEditor").value = q.sql;
            break;
        }
    }
}

async function executeCurrentSql() {
    const sqlText = document.getElementById("sqlCodeEditor").value.trim();
    if (!sqlText) {
        alert("Please enter or select a SQL query to execute.");
        return;
    }

    const executeBtn = document.getElementById("executeSqlBtn");
    const execStatus = document.getElementById("execStatus");
    const execRuntime = document.getElementById("execRuntime");
    const execRowCount = document.getElementById("execRowCount");
    const exportBtn = document.getElementById("exportCsvBtn");
    const thead = document.getElementById("sqlTableHead");
    const tbody = document.getElementById("sqlTableBody");

    executeBtn.disabled = true;
    executeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Executing...';
    execStatus.className = "text-warning";
    execStatus.textContent = "Running query in MySQL...";

    try {
        const res = await fetch("/api/sql/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sql: sqlText })
        });
        const result = await res.json();
        currentResults = result;

        if (result.success) {
            execStatus.className = "text-success";
            execStatus.textContent = "Success";
            execRuntime.textContent = `${result.execution_time_ms} ms`;
            execRowCount.textContent = Number(result.row_count).toLocaleString();
            exportBtn.disabled = !(result.rows && result.rows.length > 0);

            // Render Table Headers
            thead.innerHTML = "<tr>" + result.columns.map(c => `<th class="text-nowrap">${c}</th>`).join("") + "</tr>";

            // Render Table Rows
            if (result.rows && result.rows.length > 0) {
                tbody.innerHTML = result.rows.map(row => {
                    return "<tr>" + result.columns.map(c => {
                        const val = row[c];
                        const displayVal = (val === null || val === undefined) ? '<span class="text-muted fst-italic">NULL</span>' : val;
                        return `<td class="text-nowrap">${displayVal}</td>`;
                    }).join("") + "</tr>";
                }).join("");
            } else {
                tbody.innerHTML = `<tr><td colspan="${result.columns.length}" class="text-center text-muted py-3">No rows returned by query.</td></tr>`;
            }
        } else {
            execStatus.className = "text-danger";
            execStatus.textContent = "Execution Error";
            execRuntime.textContent = `${result.execution_time_ms || 0} ms`;
            execRowCount.textContent = "0";
            exportBtn.disabled = true;
            thead.innerHTML = '<tr><th class="text-danger">MySQL Execution Error</th></tr>';
            tbody.innerHTML = `<tr><td class="text-danger font-monospace p-3">${result.error}</td></tr>`;
        }
    } catch (err) {
        console.error("SQL Run Error:", err);
        execStatus.className = "text-danger";
        execStatus.textContent = "Network Error";
        tbody.innerHTML = `<tr><td class="text-danger p-3">${err.message}</td></tr>`;
    } finally {
        executeBtn.disabled = false;
        executeBtn.innerHTML = '<i class="bi bi-play-fill fs-5"></i><span>Execute Query</span>';
    }
}

function copySqlToClipboard() {
    const sqlText = document.getElementById("sqlCodeEditor").value;
    navigator.clipboard.writeText(sqlText).then(() => {
        const copyBtn = document.getElementById("copySqlBtn");
        const originalHtml = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="bi bi-check2 text-success me-1"></i> Copied!';
        setTimeout(() => { copyBtn.innerHTML = originalHtml; }, 1800);
    });
}

function exportResultsToCsv() {
    if (!currentResults || !currentResults.rows || currentResults.rows.length === 0) return;

    const cols = currentResults.columns;
    const rows = currentResults.rows;

    let csvContent = cols.map(c => `"${c}"`).join(",") + "\n";
    rows.forEach(r => {
        const rowLine = cols.map(c => {
            let v = r[c];
            if (v === null || v === undefined) v = "";
            v = String(v).replace(/"/g, '""');
            return `"${v}"`;
        }).join(",");
        csvContent += rowLine + "\n";
    });

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `fraud_query_export_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
