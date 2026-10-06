"use strict";

const $ = (id) => document.getElementById(id);
const results = $("results");

/* ---------- tiny DOM helper (uses textContent, so resume text can never inject HTML) ---------- */
function el(tag, attrs = {}, ...kids) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else node.setAttribute(k, v);
  }
  for (const kid of kids.flat()) {
    if (kid == null) continue;
    node.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return node;
}
/* chips with a staggered entrance (each gets --j for animation-delay) */
const chips = (items, cls = "") =>
  el("div", { class: "chips" }, items.map((s, j) => el("span", { class: "chip " + cls, style: `--j:${j}` }, s)));
/* top-level result cards get --i so they cascade in one after another */
let cardIndex = 0;
const card = (title, ...body) => el("div", { class: "card", style: `--i:${cardIndex++}` }, el("h3", {}, title), ...body);
const scoreColor = (n) => (n >= 65 ? "#0e7c7b" : n >= 45 ? "#e8a317" : "#b5382f");

/* ---------- tabs ---------- */
for (const [tab, form] of [["tab-analyze", "form-analyze"], ["tab-rank", "form-rank"]]) {
  $(tab).addEventListener("click", () => {
    for (const [t, f] of [["tab-analyze", "form-analyze"], ["tab-rank", "form-rank"]]) {
      $(t).setAttribute("aria-selected", String(t === tab));
      $(f).hidden = f !== form;
    }
  });
}

/* ---------- file name labels ---------- */
$("resume").addEventListener("change", (e) => {
  const drop = e.target.closest(".drop");
  const name = e.target.files[0]?.name;
  $("resume-name").textContent = name || "Choose your resume (PDF)";
  drop.classList.toggle("has-file", !!name);
});
$("resumes").addEventListener("change", (e) => {
  const drop = e.target.closest(".drop");
  const n = e.target.files.length;
  $("resumes-name").textContent = n ? `${n} file${n > 1 ? "s" : ""} selected` : "Choose two or more resumes (PDF)";
  drop.classList.toggle("has-file", n > 0);
});

/* ---------- drag & drop onto the drop zones ---------- */
for (const drop of document.querySelectorAll(".drop")) {
  const input = drop.querySelector("input[type=file]");
  ["dragenter", "dragover"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("drag"); }));
  ["dragleave", "drop"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("drag"); }));
  drop.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files && files.length) { input.files = files; input.dispatchEvent(new Event("change")); }
  });
}

$("sample-jd").addEventListener("click", () => {
  $("jd").value = "Python Developer\n\nWe are looking for a Python developer with experience in Python, SQL, Django or Flask, Machine Learning basics, Git, Docker and REST API design. Good communication and problem solving skills are required.";
  $("jd").focus();
});

/* ---------- API ---------- */
async function post(url, formData) {
  const res = await fetch(url, { method: "POST", body: formData });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Something went wrong. Please try again.");
  return data;
}

function show(...nodes) {
  cardIndex = 0;
  results.replaceChildren(...nodes);
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}
function busy(form, on, label) {
  const b = form.querySelector("button.primary");
  b.disabled = on;
  b.classList.toggle("loading", on);
  b.replaceChildren(...(on ? [el("span", { class: "spinner" }), "Working..."] : [label]));
}

$("form-analyze").addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = $("resume").files[0];
  if (!file) return show(el("div", { class: "error" }, "Choose a PDF resume first."));
  const fd = new FormData();
  fd.append("resume", file);
  fd.append("job_description", $("jd").value);
  busy(e.target, true);
  try { renderAnalysis(await post("/api/analyze", fd)); }
  catch (err) { show(el("div", { class: "error" }, err.message)); }
  finally { busy(e.target, false, "Analyze resume"); }
});

$("form-rank").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData();
  for (const f of $("resumes").files) fd.append("resumes", f);
  fd.append("job_description", $("jd-rank").value);
  busy(e.target, true);
  try { renderRanking((await post("/api/rank", fd)).ranking); }
  catch (err) { show(el("div", { class: "error" }, err.message)); }
  finally { busy(e.target, false, "Rank candidates"); }
});

/* ---------- renderers ---------- */
function renderAnalysis(d) {
  const out = [];

  if (d.match) {
    const m = d.match;
    const ring = el("div", { class: "ring", style: `--ring-color:${scoreColor(m.score)}` },
      el("div", {}, el("strong", {}, m.score + "%"), el("span", {}, "ATS score")));
    out.push(el("div", { class: "card", style: `--i:${cardIndex++}` }, el("div", { class: "lens" }, ring,
      el("div", { class: "lens-text" },
        el("h3", {}, m.label),
        el("p", {}, `Keyword coverage ${m.keyword_coverage}%`),
        el("p", {}, `Text similarity ${m.text_similarity}%`))),
      el("div", { class: "group" }, el("h4", {}, "Skills the job asks for that you have"),
        m.matched_skills.length ? chips(m.matched_skills, "ok") : el("p", {}, "None found.")),
      el("div", { class: "group" }, el("h4", {}, "Missing from your resume"),
        m.missing_skills.length ? chips(m.missing_skills, "miss") : el("p", {}, "Nothing missing. Nice."))));
    // animate the ring fill in on the next paint
    requestAnimationFrame(() => requestAnimationFrame(() => ring.style.setProperty("--p", m.score)));
  }

  const i = d.info;
  const rows = [["Name", i.name], ["Email", i.email], ["Phone", i.phone], ["LinkedIn", i.linkedin],
    ["GitHub", i.github], ["Education", i.education.join("; ")], ["Projects", i.projects.join("; ")]]
    .filter(([, v]) => v);
  out.push(card("What we extracted",
    rows.length ? el("dl", { class: "kv" }, rows.flatMap(([k, v]) => [el("dt", {}, k), el("dd", {}, v)]))
                : el("p", {}, "No structured details found."),
    el("div", { class: "group" }, el("h4", {}, `Detected skills (${d.skills.length})`),
      d.skills.length ? chips(d.skills) : el("p", {}, "No known skills detected."))));

  out.push(el("div", { class: "grid2" },
    card(`Resume quality: ${d.quality.score}%`,
      el("ul", { class: "checks" }, d.quality.checks.map((c, j) => el("li", { class: c.ok ? "" : "bad", style: `--j:${j}` }, c.name)))),
    card("How to improve",
      d.suggestions.length ? el("ul", { class: "plain" }, d.suggestions.map((s) => el("li", {}, s)))
                           : el("p", {}, "No major issues found."))));

  out.push(card("Careers that fit your skills",
    d.careers.length ? d.careers.map((c, j) => el("div", { class: "career", style: `--j:${j}` },
      el("div", { class: "career-head" }, el("span", {}, c.career), el("span", {}, c.match + "%")),
      el("div", { class: "bar" }, el("i", { "data-w": c.match })),
      c.missing_skills.length ? el("p", { style: "margin:.3rem 0 0;color:var(--muted);font-size:.9rem" }, "To grow: " + c.missing_skills.join(", ")) : null))
    : el("p", {}, "Add more technical skills to get career matches.")));

  if (d.interview_questions.length) {
    out.push(card("Interview questions to practice",
      el("ul", { class: "plain" }, d.interview_questions.map((q) => el("li", {}, el("strong", {}, q.topic + ": "), q.question)))));
  }
  show(...out);
  // animate every career bar from 0 to its width
  requestAnimationFrame(() => requestAnimationFrame(() => {
    for (const bar of results.querySelectorAll(".bar i")) bar.style.width = bar.dataset.w + "%";
  }));
}

function renderRanking(rows) {
  const table = el("table", {},
    el("thead", {}, el("tr", {}, ["Rank", "Candidate", "Score", "Missing skills"].map((h) => el("th", {}, h)))),
    el("tbody", {}, rows.map((r, j) => el("tr", { style: `--j:${j}` },
      el("td", {}, r.rank),
      el("td", {}, r.name, r.name !== r.file ? el("div", { style: "color:var(--muted);font-size:.85rem" }, r.file) : null),
      el("td", {}, r.error ? "Unreadable" : `${r.score}% (${r.label})`),
      el("td", {}, r.error || r.missing_skills.join(", ") || "None")))));
  show(card("Candidate ranking", el("div", { class: "table-wrap" }, table)));
}
