const API = "http://127.0.0.1:8765";

// ── State ─────────────────────────────────────────────────────────────────
let currentFile = null;
let searchTimeout = null;

// ── Elements ──────────────────────────────────────────────────────────────
const dropZone     = document.getElementById("drop-zone");
const fileInput    = document.getElementById("file-input");
const previewArea  = document.getElementById("preview-area");
const previewImg   = document.getElementById("preview-img");
const clearBtn     = document.getElementById("clear-btn");
const analyzeBtn   = document.getElementById("analyze-btn");
const resultPanel  = document.getElementById("result-panel");
const loading      = document.getElementById("loading");
const errorMsg     = document.getElementById("error-msg");
const explanation  = document.getElementById("explanation");
const actionsList  = document.getElementById("actions");
const ocrText      = document.getElementById("ocr-text");
const modelSelect  = document.getElementById("model-select");
const searchInput  = document.getElementById("search-input");
const historyList  = document.getElementById("history-list");
const historyEmpty = document.getElementById("history-empty");

// ── Tabs ──────────────────────────────────────────────────────────────────
document.querySelectorAll(".tab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"), p => p.classList.add("hidden"));
    btn.classList.add("active");
    const panel = document.getElementById(`tab-${btn.dataset.tab}`);
    panel.classList.remove("hidden");
    panel.classList.add("active");
    if (btn.dataset.tab === "history") loadHistory();
  });
});

// ── Models ────────────────────────────────────────────────────────────────
async function loadModels() {
  try {
    const res = await fetch(`${API}/analysis/models`);
    const data = await res.json();
    modelSelect.innerHTML = data.models.map(m => `<option value="${m}">${m}</option>`).join("");
  } catch {
    modelSelect.innerHTML = `<option value="llama3">llama3</option>`;
  }
}

// ── File handling ─────────────────────────────────────────────────────────
function setFile(file) {
  if (!file || !file.type.startsWith("image/")) {
    showError("Only image files are supported.");
    return;
  }
  currentFile = file;
  const url = URL.createObjectURL(file);
  previewImg.src = url;
  dropZone.classList.add("hidden");
  previewArea.classList.remove("hidden");
  analyzeBtn.classList.remove("hidden");
  hideResult();
  hideError();
}

clearBtn.addEventListener("click", () => {
  currentFile = null;
  previewImg.src = "";
  dropZone.classList.remove("hidden");
  previewArea.classList.add("hidden");
  analyzeBtn.classList.add("hidden");
  hideResult();
  hideError();
});

fileInput.addEventListener("change", e => {
  if (e.target.files[0]) setFile(e.target.files[0]);
});

dropZone.addEventListener("dragover", e => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) setFile(file);
});
dropZone.addEventListener("click", () => fileInput.click());

// ── Analyze ───────────────────────────────────────────────────────────────
analyzeBtn.addEventListener("click", async () => {
  if (!currentFile) return;
  setLoading(true);
  hideResult();
  hideError();

  try {
    const b64 = await toBase64(currentFile);
    const res = await fetch(`${API}/screenshot/analyze-b64`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image_b64: b64,
        filename: currentFile.name,
        model: modelSelect.value
      })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Analysis failed");
    }
    const data = await res.json();
    showResult(data);
  } catch (err) {
    showError(err.message || "Could not reach backend. Is it running?");
  } finally {
    setLoading(false);
  }
});

function toBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(",")[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// ── Result rendering ──────────────────────────────────────────────────────
function showResult(data) {
  explanation.textContent = data.explanation;
  actionsList.innerHTML = data.actions.map(a => `<li>${escHtml(a)}</li>`).join("");
  ocrText.textContent = data.ocr_text || "(no text extracted)";
  resultPanel.classList.remove("hidden");
}

function hideResult() { resultPanel.classList.add("hidden"); }
function setLoading(on) { loading.classList.toggle("hidden", !on); analyzeBtn.disabled = on; }
function showError(msg) { errorMsg.textContent = msg; errorMsg.classList.remove("hidden"); }
function hideError() { errorMsg.classList.add("hidden"); }

// Collapsible OCR block
document.querySelector(".collapse-toggle").addEventListener("click", function () {
  const expanded = !ocrText.classList.contains("hidden");
  ocrText.classList.toggle("hidden", expanded);
  this.textContent = expanded ? "Raw OCR text ▸" : "Raw OCR text ▾";
});

// ── History ───────────────────────────────────────────────────────────────
async function loadHistory(query = "") {
  try {
    const url = query
      ? `${API}/analysis/search?q=${encodeURIComponent(query)}&limit=50`
      : `${API}/analysis/history?limit=50`;
    const res = await fetch(url);
    const data = await res.json();
    renderHistory(data);
  } catch {
    historyList.innerHTML = "";
    historyEmpty.classList.remove("hidden");
    historyEmpty.textContent = "Could not load history.";
  }
}

function renderHistory(items) {
  historyList.innerHTML = "";
  if (!items.length) {
    historyEmpty.classList.remove("hidden");
    return;
  }
  historyEmpty.classList.add("hidden");
  items.forEach(item => {
    const li = document.createElement("li");
    li.className = "history-item";
    const date = new Date(item.created + "Z").toLocaleString();
    const actions = (item.actions || []).slice(0, 3);
    li.innerHTML = `
      <div class="hi-meta">
        <span class="hi-name">${escHtml(item.image_name || "Screenshot")}</span>
        <span>${escHtml(date)}</span>
      </div>
      <p class="hi-explanation">${escHtml(item.explanation)}</p>
      <div class="hi-actions">
        ${actions.map(a => `<span class="hi-tag">${escHtml(a)}</span>`).join("")}
        <button class="hi-delete" data-id="${item.id}">Delete</button>
      </div>`;
    li.querySelector(".hi-delete").addEventListener("click", async e => {
      e.stopPropagation();
      await fetch(`${API}/analysis/${item.id}`, { method: "DELETE" });
      loadHistory(searchInput.value.trim());
    });
    historyList.appendChild(li);
  });
}

searchInput.addEventListener("input", () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => loadHistory(searchInput.value.trim()), 300);
});

// ── Utilities ─────────────────────────────────────────────────────────────
function escHtml(str) {
  return String(str).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

// ── Init ──────────────────────────────────────────────────────────────────
loadModels();
