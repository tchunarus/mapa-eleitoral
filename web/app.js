/* Mapa Eleitoral: casca da página (roteamento por hash, abas, tema e utilitários).
   O conteúdo de cada rota vem do módulo registrado em web/eleitoral.js. */
(() => {
"use strict";
const DATA = (document.querySelector('meta[name="mapa-dados"]') || {}).content || "data/";
const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const norm = s => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const FMT = d => { if (!d) return ""; const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(d); return m ? `${m[3]}/${m[2]}/${m[1]}` : d; };
const FMTH = d => { if (!d) return ""; const t = new Date(d); if (isNaN(t)) return FMT(d); return t.toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" }); };
const ls = { get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }, set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} } };
async function getJSON(p) { const r = await fetch(DATA + p, { cache: "no-cache" }); if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); }
const app = $("#app");
let mod = null;

function renderAbas() {
  const F = window.MapaEleitoralFiltros, r = F.parseRota(location.hash) || { v: "inicio" };
  const demo = r.v === "eleicao" && r.eleicao === "demonstracao" || r.v === "cargo" && r.eleicao === "demonstracao";
  const abas = [["#/", "Eleições 2026", !demo && ["inicio", "eleicao", "cargo", "candidato", "proposta"].includes(r.v)],
    ["#/propostas", "Propostas", r.v === "propostas"], ["#/municipios/florianopolis", "Municípios", r.v === "municipio"],
    ["#/demonstracao", "Demonstração", demo], ["#/admin", "Painel", r.v === "admin"]];
  $("#tabs").innerHTML = abas.map(([h, t, ativo]) => `<a class="tab" href="${h}" ${ativo ? 'aria-current="page"' : ""}>${t}</a>`).join("");
}
function render(soft) {
  if (!mod) return;
  const y = window.scrollY; let html = "";
  try { html = mod.render(location.hash.replace(/^#/, "")); }
  catch (e) { console.error(e); html = `<div class="empty">Não foi possível montar esta página (${esc(e.message)}).</div>`; }
  app.innerHTML = html; renderAbas();
  if (soft) window.scrollTo(0, y); else window.scrollTo(0, 0);
  if (mod.depois) try { mod.depois(); } catch (e) { console.error(e); }
}
function status(html) { $("#status").innerHTML = html; }
function initTheme() {
  const saved = ls.get("theme", null); if (saved) document.documentElement.setAttribute("data-theme", saved);
  $("#themeBtn").addEventListener("click", () => { const cur = document.documentElement.getAttribute("data-theme") || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
    const n = cur === "light" ? "dark" : "light"; document.documentElement.setAttribute("data-theme", n); ls.set("theme", n); });
}
window.AppEleitoral = { registrar(m) { mod = m; render(); }, render, util: { esc, norm, FMT, FMTH, ls, getJSON, status } };
window.addEventListener("hashchange", () => render());
initTheme();
})();
