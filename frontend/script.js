const API_URL = "http://127.0.0.1:5000";
const HISTORY_KEY = "ai-business-analyst-history";

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".nav-item").forEach(button => button.addEventListener("click", () => showPage(button.dataset.page)));
  document.querySelectorAll("[data-go-to]").forEach(button => button.addEventListener("click", () => showPage(button.dataset.goTo)));
  document.querySelectorAll(".suggestion").forEach(button => button.addEventListener("click", () => setQuestion(button.dataset.question)));
  document.getElementById("askButton").addEventListener("click", askQuestion);
  document.getElementById("question").addEventListener("keydown", event => { if (event.key === "Enter" && event.ctrlKey) askQuestion(); });
  document.getElementById("menuButton").addEventListener("click", toggleSidebar);
  document.getElementById("sidebarOverlay").addEventListener("click", toggleSidebar);
  initializePowerBiViewer();
  renderHistory();
});

function initializePowerBiViewer() {
  const reportImage = document.getElementById("powerbiReportImage"), reportTitle = document.getElementById("reportTitle"), modal = document.getElementById("reportModal"), modalImage = document.getElementById("modalReportImage"), modalTitle = document.getElementById("modalReportTitle");
  const closeModal = () => modal.classList.add("hidden");
  document.querySelectorAll(".report-tab").forEach(tab => tab.addEventListener("click", () => {
    document.querySelectorAll(".report-tab").forEach(item => { const active = item === tab; item.classList.toggle("active", active); item.setAttribute("aria-selected", String(active)); });
    const { reportTitle: title, reportImage: image } = tab.dataset;
    reportImage.src = image; reportImage.alt = `${title} Power BI report preview`; reportTitle.textContent = title;
  }));
  document.getElementById("fullscreenButton").addEventListener("click", () => { modalImage.src = reportImage.src; modalImage.alt = reportImage.alt; modalTitle.textContent = reportTitle.textContent; modal.classList.remove("hidden"); document.getElementById("modalCloseButton").focus(); });
  document.getElementById("modalCloseButton").addEventListener("click", closeModal);
  modal.querySelector("[data-close-report-modal]").addEventListener("click", closeModal);
  document.addEventListener("keydown", event => { if (event.key === "Escape" && !modal.classList.contains("hidden")) closeModal(); });
}

function showPage(name) {
  document.querySelectorAll(".page").forEach(page => page.classList.toggle("active", page.id === `${name}-page`));
  document.querySelectorAll(".nav-item").forEach(button => button.classList.toggle("active", button.dataset.page === name));
  document.getElementById("sidebar").classList.remove("open"); document.getElementById("sidebarOverlay").classList.remove("show");
  if (name === "history") renderHistory();
  window.scrollTo({ top: 0, behavior: "smooth" });
}
function toggleSidebar() { document.getElementById("sidebar").classList.toggle("open"); document.getElementById("sidebarOverlay").classList.toggle("show"); }
function setQuestion(question) { document.getElementById("question").value = question; showPage("analyst"); setTimeout(() => document.getElementById("question").focus(), 100); }

async function askQuestion() {
  const input = document.getElementById("question"), question = input.value.trim(), button = document.getElementById("askButton");
  if (!question) return showError("Please enter a business question before asking the AI Analyst.");
  hide("errorBox"); hide("resultSection"); hide("emptyAnalysis"); show("loading"); button.disabled = true; document.getElementById("buttonText").textContent = "Analyzing...";
  try {
    const response = await fetch(`${API_URL}/ask`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question }) });
    let result; try { result = await response.json(); } catch { throw new Error("The AI service returned an unreadable response."); }
    if (!response.ok || !result.success) throw new Error(result.error || "Unable to analyze your question.");
    document.getElementById("answerBox").textContent = result.answer || "No answer was returned for this question.";
    document.getElementById("sqlBox").textContent = result.sql || "SQL not available.";
    renderData(result.data, document.getElementById("dataBox")); show("resultSection"); saveHistory(question, result.answer || "No answer returned.");
  } catch (error) { showError(safeError(error)); }
  finally { hide("loading"); button.disabled = false; document.getElementById("buttonText").textContent = "Ask AI"; }
}
function show(id) { document.getElementById(id).classList.remove("hidden"); } function hide(id) { document.getElementById(id).classList.add("hidden"); }
function showError(message) { const box = document.getElementById("errorBox"); box.textContent = `Unable to analyze your question. ${message}`; show("errorBox"); }
function safeError(error) { const message = error?.message || "Please check that the local AI service is running and try again."; return message.replace(/(?:traceback|at \S+\(|file ".*)/ig, "").slice(0, 300); }
function renderData(data, container) {
  container.innerHTML = ""; if (!Array.isArray(data) || !data.length) { container.textContent = "No database rows returned."; return; }
  const columns = [...new Set(data.flatMap(row => row && typeof row === "object" ? Object.keys(row) : []))]; if (!columns.length) { container.textContent = "No tabular database rows returned."; return; }
  const table = document.createElement("table"); table.className = "data-table"; const thead = document.createElement("thead"), header = document.createElement("tr");
  columns.forEach(key => { const th = document.createElement("th"); th.textContent = formatColumnName(key); header.appendChild(th); }); thead.appendChild(header); table.appendChild(thead);
  const body = document.createElement("tbody"); data.forEach(row => { const tr = document.createElement("tr"); columns.forEach(key => { const td = document.createElement("td"); td.textContent = formatValue(row?.[key]); tr.appendChild(td); }); body.appendChild(tr); }); table.appendChild(body); container.appendChild(table);
}
function formatColumnName(column) { return String(column).replaceAll("_", " ").replace(/\b\w/g, char => char.toUpperCase()); }
function formatValue(value) { if (value === null || value === undefined) return "—"; if (typeof value === "number") return value.toLocaleString("en-US", { maximumFractionDigits: 2 }); if (typeof value === "object") return JSON.stringify(value); return String(value); }
function saveHistory(question, answer) { const history = getHistory(); history.unshift({ question, answer, timestamp: new Date().toISOString() }); localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, 20))); }
function getHistory() { try { const stored = JSON.parse(localStorage.getItem(HISTORY_KEY)); return Array.isArray(stored) ? stored : []; } catch { return []; } }
function renderHistory() { const container = document.getElementById("historyList"); const history = getHistory(); container.innerHTML = ""; if (!history.length) { container.innerHTML = '<div class="empty-state history-empty"><span class="empty-icon">◷</span><h3>No query history available yet.</h3><p>Questions asked in this browser will appear here.</p></div>'; return; } history.forEach(item => { const card = document.createElement("article"); card.className = "history-item"; const title = document.createElement("h3"), answer = document.createElement("p"), date = document.createElement("small"); title.textContent = item.question; answer.textContent = item.answer; date.textContent = new Date(item.timestamp).toLocaleString(); card.append(title, answer, date); container.appendChild(card); }); }
