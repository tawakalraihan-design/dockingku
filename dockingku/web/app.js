const TRACK = { protein: "Jalur protein", ligand: "Jalur ligan", merge: "Gabungan" };
let viewer;

async function api(path, opts) {
  const res = await fetch(path, opts);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function loadSteps() {
  const steps = await api("/api/steps");
  const nav = document.getElementById("steps");
  steps.forEach((s, i) => {
    const b = document.createElement("button");
    b.className = "step";
    b.innerHTML = `${i + 1}. ${s.title}<small>${TRACK[s.track]} · ${s.modules.join(", ")}</small>`;
    b.onclick = () => openStep(s, b);
    nav.appendChild(b);
  });
}

function openStep(step, btn) {
  document.querySelectorAll(".step").forEach(x => x.classList.remove("active"));
  btn.classList.add("active");
  document.getElementById("step-title").textContent = step.title;
  const body = document.getElementById("step-body");
  if (step.key === "target") {
    body.innerHTML = `<input id="q" placeholder="mis. EGFR kinase" class="input"> <button class="pill" id="go">Cari di RCSB</button><div id="hits"></div>`;
    document.getElementById("go").onclick = searchRcsb;
  } else {
    body.textContent = "Belum diimplementasikan. Modul: " + step.modules.join(", ");
  }
}

async function searchRcsb() {
  const q = document.getElementById("q").value;
  const hits = await api("/api/rcsb/search?q=" + encodeURIComponent(q));
  document.getElementById("hits").innerHTML = hits.map(h =>
    `<p><a href="#" data-id="${h.id}">${h.id}</a> · ${h.resolution ?? "?"} Å · ${h.title ?? ""}</p>`).join("");
  document.querySelectorAll("#hits a").forEach(a => a.onclick = e => { e.preventDefault(); show(a.dataset.id); });
}

async function show(pdbId) {
  await viewer.plugin.clear();
  await viewer.loadPdb(pdbId);
}

async function loadStatus() {
  const s = await api("/api/status");
  document.getElementById("modules").innerHTML = s.modules.map(m =>
    `<li><b>${m.title}</b> <span class="${m.missing.length ? "warn" : "ok"}">${m.missing.length ? "kurang: " + m.missing.join(", ") : "siap"}</span><br><small class="muted">menggantikan ${m.replaces}</small></li>`).join("");
}

async function init() {
  viewer = await molstar.Viewer.create("viewer", { layoutIsExpanded: false, layoutShowControls: false, layoutShowSequence: false, layoutShowLog: false });
  await Promise.all([loadSteps(), loadStatus()]);
}
init();
