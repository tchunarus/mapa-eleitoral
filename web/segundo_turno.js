/* Mapa Eleitoral: 2º turno presidencial de 2026 (rotas #/2turno/...).
   Lê docs/data/segundo-turno.json, gerado por coletor/segundo_turno.py. Notas, justificativas,
   evidências e classificações vêm prontas dos dados curados; aqui só se exibe, filtra e
   recalcula a média ponderada com os pesos escolhidos por quem lê (guardados só neste navegador). */
(() => {
"use strict";
const MN = window.AppEleitoral;
if (!MN) return;
const { esc, FMT, getJSON, ls } = MN.util;
const ARQ = "segundo-turno.json";
const S = { d: null, erro: null, carregando: false, f: ls.get("st-filtros", {}), pesos: ls.get("st-pesos", null), notas: ls.get("st-notas", {}) };

function dados() {
  if (S.d || S.erro) return S.d;
  if (!S.carregando) {
    S.carregando = true;
    getJSON(ARQ).then(d => { S.d = d; }).catch(e => { S.erro = e.message || String(e); }).finally(() => { S.carregando = false; MN.render(true); });
  }
  return null;
}
const salvarF = () => ls.set("st-filtros", S.f);
const R = (g, v) => ((S.d.rotulos || {})[g] || {})[v] || v || "";
const cands = () => S.d.eleicao.candidatos;
const cand = id => cands().find(c => c.id === id) || {};
const nomeAlvo = id => id === "ambos" ? "Ambos" : cand(id).nome_urna || id;
const crit = () => (S.d.criterios || []).slice().sort((a, b) => a.ordem - b.ordem);
const critPor = id => crit().find(c => c.id === id) || {};
const aval = (c, k) => (S.d.avaliacoes || []).find(a => a.criterio === c && a.candidato === k);
const evPor = id => (S.d.evidencias || []).find(e => e.id === id);

// ------------------------------------------------------------ ícones (traço simples, herdam a cor do texto)
const P = {
  briefcase: "M4 8h16v11H4zM9 8V5h6v3M4 13h16", chart: "M4 19h16M7 16v-5M12 16V7M17 16v-8", list: "M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01",
  shield: "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z", landmark: "M3 10l9-6 9 6M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18",
  handshake: "M3 12l4-4 4 3 3-3 7 6-3 3-4-3-2 2-3-3-3 3z", leaf: "M5 19C5 10 11 5 20 5c0 9-5 14-14 14zM5 19l7-7", refresh: "M20 11a8 8 0 0 0-14-5M4 4v4h4M4 13a8 8 0 0 0 14 5M20 20v-4h-4",
  doc: "M7 3h7l5 5v13H7zM14 3v5h5", ext: "M14 4h6v6M20 4l-9 9M18 14v6H4V6h6", check: "M5 12l5 5 9-10", clock: "M12 7v5l3 2M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z",
  sliders: "M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0M14 4v4M8 10v4M16 16v4", scale: "M12 4v16M5 20h14M6 8l-3 6h6zM18 8l-3 6h6zM6 8h12",
  info: "M12 8h.01M11 12h1v5h1M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z", alert: "M12 4l9 16H3zM12 10v4M12 17h.01",
};
const ico = (n, cls) => `<svg class="ico ${cls || ""}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${P[n] || P.info}"/></svg>`;

// ------------------------------------------------------------ peças
function fonte(f) {
  if (!f) return "";
  return `<li>${f.url ? `<a class="ref" href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.titulo || f.url)} ${ico("ext", "ico-s")}</a>` : esc(f.titulo || "")}
    <span class="small muted"> · ${esc(f.veiculo || "")}${f.data ? ` · ${esc(FMT(f.data))}` : ""}</span> <span class="badge">${esc(R("tipo_fonte", f.tipo_fonte))}</span></li>`;
}
const fontes = (lista) => (lista && lista.length) ? `<ul class="st-fontes">${lista.map(fonte).join("")}</ul>` : "";
const verFonte = (f) => f && f.url ? `<a class="btn quiet st-btn-fonte" href="${esc(f.url)}" target="_blank" rel="noopener">${ico("ext")} Ver fonte original</a>` : "";
const pill = (k) => { const c = cand(k); return `<span class="st-pill st-${esc(c.cor)}"><i></i>${esc(c.nome_urna)}</span>`; };
const tomSentido = { FAVORAVEL: "ok", DESFAVORAVEL: "warn", MISTO: "mid", CONTEXTO: "" };
const tomChecagem = { VERDADEIRO: "ok", PARCIALMENTE_VERDADEIRO: "mid", INCONCLUSIVO: "", DESCONTEXTUALIZADO: "warn", ENGANOSO: "warn", FALSO: "warn" };

function evidencia(e, opts) {
  const o = opts || {};
  return `<details class="st-ev" ${o.aberta ? "open" : ""}>
    <summary><span class="st-ev-top">${o.semCand ? "" : pill(e.candidato)}<span class="badge ${tomSentido[e.sentido] || ""}">${esc(R("sentido", e.sentido))}</span>
      <span class="badge">${esc(R("tipo", e.tipo))}</span><span class="badge" title="Peso probatório">peso ${esc(R("peso", e.peso_probatorio).toLowerCase())}</span>
      ${e.data_fato ? `<span class="small muted mono">${esc(FMT(e.data_fato))}</span>` : ""}</span>
      <span class="st-ev-txt">${esc(e.afirmacao)}</span><span class="st-ev-tema small muted">${esc(critPor(e.criterio).nome || "")} · ${esc(e.tema || "")}</span></summary>
    <div class="st-ev-body">
      ${e.contraponto ? `<p class="small"><b>Contraponto.</b> ${esc(e.contraponto)}</p>` : ""}
      ${e.limitacoes ? `<p class="small"><b>Limitações.</b> ${esc(e.limitacoes)}</p>` : ""}
      <p class="el-mini">Fontes</p>${fontes(e.fontes)}
      <div class="actions">${verFonte((e.fontes || [])[0])}<span class="small muted mono">${esc(e.id)}</span></div>
    </div></details>`;
}

function chips(nome, opcoes, atual, todos) {
  return `<div class="chips" role="group" aria-label="${esc(nome)}">${[["", todos || "Todos"]].concat(opcoes).map(([v, t]) =>
    `<button type="button" class="chip" data-f="${esc(nome)}" data-v="${esc(v)}" aria-pressed="${(atual || "") === v}">${esc(t)}</button>`).join("")}</div>`;
}

// ------------------------------------------------------------ pesos e médias
function pesos() {
  const p = {}; crit().forEach(c => { p[c.id] = S.pesos && S.pesos[c.id] != null ? S.pesos[c.id] : c.peso_padrao; }); return p;
}
function nota(c, k) {
  const ov = S.notas[c + "|" + k];
  if (ov != null) return ov;
  const a = aval(c, k); return a ? a.nota : null;
}
function media(k, p, soSuficientes) {
  let s = 0, w = 0;
  crit().forEach(c => { const a = aval(c.id, k); const n = nota(c.id, k);
    if (n == null || !p[c.id]) return; if (soSuficientes && a && a.suficiencia === "BAIXA") return; s += n * p[c.id]; w += p[c.id]; });
  return w ? s / w : null;
}
const f1 = n => n == null ? "s/ nota" : n.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

// gráfico de pontos pareados (0 a 10) por critério; um eixo, rótulo direto do valor, tooltip por marca
function grafico(p) {
  const ks = cands().map(c => c.id), L = 150, W = 640, H = 34, top = 26, x = v => L + (W - L - 24) * v / 10;
  const linhas = crit().map((c, i) => {
    const y = top + i * H + H / 2, ns = ks.map(k => nota(c.id, k));
    const seg = ns.every(n => n != null) ? `<line x1="${x(Math.min(...ns))}" x2="${x(Math.max(...ns))}" y1="${y}" y2="${y}" class="st-g-seg"/>` : "";
    const marcas = ks.map((k, j) => ns[j] == null ? "" : `<circle cx="${x(ns[j])}" cy="${y + (ns[0] === ns[1] ? (j ? 5 : -5) : 0)}" r="6.5" class="st-g-${cand(k).cor}" data-tip="${esc(cand(k).nome_urna)} · ${esc(c.nome)}: ${f1(ns[j])}"/>`).join("");
    const peso = p[c.id] ? "" : ` opacity=".35"`;
    return `<g${peso}><text x="${L - 12}" y="${y + 4}" text-anchor="end" class="st-g-lab">${esc(c.nome_curto || c.nome)}</text>
      <line x1="${x(0)}" x2="${x(10)}" y1="${y}" y2="${y}" class="st-g-grid"/>${seg}${marcas}<rect x="0" y="${y - H / 2}" width="${W}" height="${H}" fill="transparent"><title>${esc(c.nome)}</title></rect></g>`;
  }).join("");
  const eixo = [0, 2, 4, 6, 8, 10].map(v => `<text x="${x(v)}" y="16" text-anchor="middle" class="st-g-ax">${v}</text>`).join("");
  return `<figure class="st-fig"><figcaption class="st-leg">${cands().map(c => pill(c.id)).join("")}<span class="small muted">Nota de 0 a 10 por critério, conforme a rubrica publicada. Critérios com peso zero aparecem esmaecidos.</span></figcaption>
    <svg viewBox="0 0 ${W} ${top + crit().length * H + 8}" class="st-g" role="img" aria-label="Notas por critério">${eixo}${linhas}</svg>
    <details class="st-tabela"><summary>Ver como tabela</summary>${tabelaNotas(p)}</details></figure>`;
}
function tabelaNotas(p) {
  return `<div class="tbl-wrap"><table><thead><tr><th>Critério</th><th>Peso</th>${cands().map(c => `<th>${esc(c.nome_urna)}</th>`).join("")}</tr></thead><tbody>
    ${crit().map(c => `<tr><td>${esc(c.nome)}</td><td class="mono">${p[c.id]}</td>${cands().map(k => { const a = aval(c.id, k.id);
      return `<td class="mono">${f1(nota(c.id, k.id))}${a ? ` <span class="small muted">(${esc(R("suficiencia", a.suficiencia).toLowerCase())})</span>` : ""}</td>`; }).join("")}</tr>`).join("")}
    <tr><td><b>Média ponderada</b></td><td></td>${cands().map(k => `<td class="mono"><b>${f1(media(k.id, p))}</b></td>`).join("")}</tr></tbody></table></div>`;
}

// ------------------------------------------------------------ páginas
const SUB = [["", "Visão geral", "scale"], ["criterios", "Critérios e evidências", "list"], ["propostas", "Propostas", "doc"],
  ["tempo", "Linha do tempo", "clock"], ["checagens", "Verificação de fatos", "check"], ["simulador", "Seus pesos", "sliders"],
  ["conclusao", "Conclusão", "landmark"], ["metodologia", "Metodologia e fontes", "info"]];
function subnav(atual) {
  return `<nav class="st-sub" aria-label="Seções do 2º turno">${SUB.map(([r, t, i]) => `<a href="#/2turno${r ? "/" + r : ""}" ${atual === r ? 'aria-current="page"' : ""}>${ico(i)}<span>${esc(t)}</span></a>`).join("")}</nav>`;
}
function cabecalho(titulo, lede) {
  return `<div class="page-head reveal"><p class="crumbs"><span>Eleição presidencial de 2026</span><span>2º turno · 25/10</span></p><h2>${esc(titulo)}</h2>${lede ? `<p class="lede">${lede}</p>` : ""}</div>`;
}
function vazio(msg) { return `<div class="st-vazio">${ico("info")} ${esc(msg)}</div>`; }

function visao() {
  const d = S.d, el = d.eleicao, p = pesos(), sit = el.situacao || {};
  const cards = cands().map(c => {
    const m = media(c.id, p), nev = (d.evidencias || []).filter(e => e.candidato === c.id), nprop = (d.propostas[c.id] || []).length;
    const nchk = (d.checagens || []).filter(x => x.alvo === c.id).length;
    return `<article class="st-cand st-${esc(c.cor)} reveal">
      ${c.foto_url ? `<img class="st-foto" src="${esc(c.foto_url)}" alt="Foto de ${esc(c.nome_urna)} registrada no TSE" loading="lazy" referrerpolicy="no-referrer">` : ""}
      <div><p class="eyebrow">${esc(c.partido)} · ${esc(c.numero)}</p><h3>${esc(c.nome_urna)}</h3><p class="small muted">${esc(c.nome)}</p>
      <dl class="st-kpis"><div><dt>1º turno</dt><dd>${c.resultado_1t != null ? c.resultado_1t.toLocaleString("pt-BR") + "%" : "s/d"}</dd></div>
        <div><dt>Média (seus pesos)</dt><dd>${f1(m)}</dd></div><div><dt>Evidências</dt><dd>${nev.length}</dd></div><div><dt>Propostas</dt><dd>${nprop}</dd></div><div><dt>Checagens</dt><dd>${nchk}</dd></div></dl>
      <a class="ref small" href="#/2turno/criterios?c=${esc(c.id)}">Ver evidências de ${esc(c.nome_urna)}</a></div></article>`;
  }).join("");
  const conc = (d.conclusao || {}).resumo;
  return `${cabecalho("Lula e Flávio Bolsonaro: análise comparativa", "Evidências verificáveis, classificadas e com fonte, organizadas em oito critérios definidos antes da análise. As notas seguem uma rubrica publicada; você pode mudar os pesos e ver como suas prioridades alteram o resultado.")}
    
    <div class="st-oficial reveal">${ico("check")}<div><p><b>Situação oficial.</b> ${esc(sit.texto || "")}</p>${fontes(sit.fontes)}</div></div>
    <div class="st-cands">${cards}</div>
    ${(d.avaliacoes || []).length ? `<section class="blk"><div class="sec-head"><h2>Notas por critério</h2><a class="ref small" href="#/2turno/simulador">Ajustar pesos</a></div>${grafico(p)}</section>` :
      `<section class="blk">${vazio("As notas por critério serão publicadas depois da revisão das evidências.")}</section>`}
    ${conc ? `<section class="blk"><div class="sec-head"><h2>Em síntese</h2><a class="ref small" href="#/2turno/conclusao">Conclusão completa</a></div><p class="lede">${esc(conc)}</p></section>` : ""}
    <section class="blk"><div class="sec-head"><h2>Como ler esta análise</h2></div>
      <div class="st-guia">${[["scale", "Mesmos critérios", "O mesmo roteiro de perguntas foi aplicado aos dois candidatos; quando um tem mais ou menos evidências, isso aparece, sem equivalência forçada."],
        ["shield", "Tipos de informação", "Cada evidência é marcada como fato, dado oficial, decisão judicial (definitiva ou não), investigação, alegação, interpretação, opinião ou promessa."],
        ["sliders", "Você decide os pesos", "A média muda conforme a importância que você atribui a cada critério. Nada aqui é recomendação de voto."],
        ["alert", "Lacunas declaradas", "Cada nota indica se a evidência é suficiente, parcial ou insuficiente, e quais são as limitações."]].map(([i, t, x]) =>
        `<div class="st-guia-i">${ico(i)}<b>${esc(t)}</b><p class="small">${esc(x)}</p></div>`).join("")}</div></section>`;
}

function criterios(q) {
  const d = S.d, f = S.f;
  if (q.c) f.cand = q.c;
  const lista = crit();
  const sel = q.id || f.crit || "";
  const corpo = (sel ? lista.filter(c => c.id === sel) : lista).map(c => {
    const evs = (d.evidencias || []).filter(e => e.criterio === c.id && (!f.sentido || e.sentido === f.sentido) && (!f.tipo || e.tipo === f.tipo) && (!f.peso || e.peso_probatorio === f.peso));
    const colunas = cands().filter(k => !f.cand || f.cand === k.id).map(k => {
      const a = aval(c.id, k.id), es = evs.filter(e => e.candidato === k.id);
      const ord = { FAVORAVEL: 0, MISTO: 1, CONTEXTO: 2, DESFAVORAVEL: 3 }, pp = { ALTO: 0, MEDIO: 1, BAIXO: 2 };
      es.sort((x, y) => (pp[x.peso_probatorio] - pp[y.peso_probatorio]) || (ord[x.sentido] - ord[y.sentido]));
      const fav = es.filter(e => e.sentido === "FAVORAVEL").length, des = es.filter(e => e.sentido === "DESFAVORAVEL").length;
      return `<div class="st-col st-${esc(k.cor)}"><div class="st-col-h">${pill(k.id)}${a ? `<span class="st-nota" title="Nota pela rubrica">${f1(nota(c.id, k.id))}</span>` : ""}</div>
        ${a ? `<p class="small"><span class="badge ${a.suficiencia === "ALTA" ? "ok" : a.suficiencia === "MEDIA" ? "mid" : "warn"}">${esc(R("suficiencia", a.suficiencia))}</span></p><p class="st-just">${esc(a.justificativa)}</p>${a.limitacoes ? `<p class="small muted"><b>Limitações.</b> ${esc(a.limitacoes)}</p>` : ""}` : ""}
        <p class="st-cont small"><span class="badge ok">${fav} favoráveis</span> <span class="badge warn">${des} desfavoráveis</span> <span class="badge">${es.length - fav - des} mistas ou de contexto</span></p>
        ${es.map(e => evidencia(e, { semCand: true })).join("") || vazio("Nenhuma evidência com os filtros escolhidos.")}</div>`;
    }).join("");
    return `<section class="blk st-crit reveal" id="c-${esc(c.id)}"><div class="sec-head"><h2>${ico(c.icone)} ${esc(c.nome)}</h2><span class="badge">${c.natureza === "OBJETIVA" ? "critério predominantemente objetivo" : c.natureza === "VALORATIVA" ? "critério com forte componente valorativo" : "critério misto"}</span></div>
      <p class="lede" style="margin-top:0">${esc(c.pergunta)}</p>
      <details class="st-rub"><summary>Rubrica e indicadores</summary><ul class="small">${c.indicadores.map(i => `<li>${esc(i)}</li>`).join("")}</ul>
        <div class="tbl-wrap"><table><tbody>${c.rubrica.map(r => `<tr><td class="k mono">${esc(r.faixa)}</td><td>${esc(r.descricao)}</td></tr>`).join("")}</tbody></table></div></details>
      <div class="st-cols">${colunas}</div></section>`;
  }).join("");
  return `${cabecalho("Critérios e evidências", "Para cada critério, as evidências favoráveis e desfavoráveis a cada candidato, com a nota atribuída pela rubrica e a justificativa. Abra uma evidência para ver contraponto, limitações e fontes.")}
    
    <div class="st-filtros"><div><span class="el-mini">Critério</span>${chips("crit", lista.map(c => [c.id, c.nome_curto || c.nome]), sel)}</div>
      <div><span class="el-mini">Candidato</span>${chips("cand", cands().map(c => [c.id, c.nome_urna]), f.cand, "Ambos")}</div>
      <div><span class="el-mini">Sentido</span>${chips("sentido", Object.entries(d.rotulos.sentido), f.sentido)}</div>
      <div><span class="el-mini">Tipo</span>${chips("tipo", Object.entries(d.rotulos.tipo), f.tipo)}</div>
      <div><span class="el-mini">Peso probatório</span>${chips("peso", Object.entries(d.rotulos.peso), f.peso)}</div></div>
    ${(d.evidencias || []).length ? corpo : vazio("As evidências estão em revisão e serão publicadas em breve.")}`;
}

const AREAS = [["economia", "Economia"], ["tributacao", "Tributação"], ["saude", "Saúde"], ["educacao", "Educação"], ["seguranca", "Segurança"],
  ["meio-ambiente", "Meio ambiente"], ["mobilidade", "Mobilidade"], ["infraestrutura", "Infraestrutura"], ["habitacao", "Habitação"],
  ["administracao-publica", "Administração pública"], ["direitos-sociais", "Direitos sociais"], ["instituicoes-politicas", "Instituições"]];
const DET = { HIGH: "Detalhamento alto", MEDIUM: "Detalhamento médio", LOW: "Detalhamento baixo" };
function propostas() {
  const d = S.d, f = S.f;
  const col = k => {
    const ps = (d.propostas[k.id] || []).filter(p => !f.area || (p.temas || []).some(t => t.id === f.area));
    return `<div class="st-col st-${esc(k.cor)}"><div class="st-col-h">${pill(k.id)}<span class="small muted">${ps.length} proposta(s)</span></div>
      ${ps.map(p => `<article class="st-prop reveal"><p class="el-mini">${esc((p.temas || []).map(t => t.nome).join(" · "))}${p.subtema ? ` · ${esc(p.subtema)}` : ""}</p>
        <h4><a href="#/proposta/${esc(p.id)}">${esc(p.titulo)}</a></h4><p class="small">${esc(p.resumo)}</p>
        <div class="chips">${p.rotulo ? `<span class="badge ${p.rotulo.tom === "ok" ? "ok" : p.rotulo.tom === "warn" ? "warn" : p.rotulo.tom === "mid" ? "mid" : ""}">${esc(p.rotulo.subtitulo)}</span>` : ""}
          ${p.detalhamento ? `<span class="badge">${esc(DET[p.detalhamento])}</span>` : ""}${p.impacto_orcamentario ? `<span class="badge mid">Depende de orçamento</span>` : ""}</div>
        ${p.instrumento ? `<p class="small muted">Instrumento: ${esc(p.instrumento)}${p.dependencias.length ? ` · Participam: ${esc(p.dependencias.join(", "))}` : ""}</p>` : ""}
        ${p.trecho ? `<blockquote class="el-trecho">${esc(p.trecho)}</blockquote>` : ""}
        <div class="actions">${p.fonte && p.fonte.url ? `<a class="btn quiet st-btn-fonte" href="${esc(p.fonte.url)}" target="_blank" rel="noopener">${ico("ext")} Ver fonte original</a>` : ""}<span class="small muted">${esc(p.localizador || "")}</span></div></article>`).join("") || vazio("Sem propostas registradas nesta área.")}</div>`;
  };
  const tot = cands().reduce((s, k) => s + (d.propostas[k.id] || []).length, 0);
  return `${cabecalho("Propostas lado a lado", "Propostas extraídas dos planos de governo registrados no TSE, com o trecho literal e a página. Os selos indicam se a medida cabe à Presidência ou depende do Congresso, de outros entes ou de emenda constitucional; o selo de detalhamento mede metas, valores e prazos.")}
    
    <div class="st-filtros"><div><span class="el-mini">Área</span>${chips("area", AREAS, f.area, "Todas")}</div></div>
    ${tot ? `<div class="st-cols">${cands().map(col).join("")}</div>` : vazio("As propostas estão sendo extraídas dos planos de governo e serão publicadas em breve.")}`;
}

function tempo() {
  const d = S.d, f = S.f;
  const its = (d.linha_do_tempo || []).filter(t => (!f.tcand || t.candidato === f.tcand || t.candidato === "ambos") && (!f.tcat || t.categoria === f.tcat))
    .slice().sort((a, b) => String(a.data).localeCompare(String(b.data)));
  return `${cabecalho("Linha do tempo", "Marcos das trajetórias, dos processos e da campanha, cada um com fonte.")}
    <div class="st-filtros"><div><span class="el-mini">Candidato</span>${chips("tcand", cands().map(c => [c.id, c.nome_urna]), f.tcand, "Ambos")}</div>
      <div><span class="el-mini">Categoria</span>${chips("tcat", Object.entries(d.rotulos.categoria_tempo), f.tcat, "Todas")}</div></div>
    ${its.length ? `<ol class="st-tempo">${its.map(t => `<li class="reveal ${t.candidato === "ambos" ? "st-ambos" : "st-" + esc(cand(t.candidato).cor)}"><span class="st-t-data mono">${esc(FMT(t.data))}</span>
      <div><p class="st-t-top">${t.candidato === "ambos" ? `<span class="badge">Ambos</span>` : pill(t.candidato)} <span class="badge">${esc(R("categoria_tempo", t.categoria))}</span></p><b>${esc(t.titulo)}</b><p class="small">${esc(t.descricao || "")}</p>
      <details><summary class="small">Fontes</summary>${fontes(t.fontes)}</details></div></li>`).join("")}</ol>` : vazio("A linha do tempo será publicada após a revisão das fontes.")}`;
}

function checagens() {
  const d = S.d, f = S.f, todas = d.checagens || [];
  const its = todas.filter(x => (!f.calvo || x.alvo === f.calvo) && (!f.cclass || x.classificacao === f.cclass) && (!f.cautor || x.origem === f.cautor));
  const conta = xs => Object.keys(d.rotulos.checagem).map(c => [c, xs.filter(x => x.classificacao === c).length]).filter(x => x[1])
    .map(([c, n]) => `<span class="badge ${tomChecagem[c]}">${esc(R("checagem", c))}: ${n}</span>`).join("");
  const resumo = cands().map(k => { const proprias = todas.filter(x => x.origem === k.id), terc = todas.filter(x => x.origem === "terceiros" && (x.alvo === k.id || x.alvo === "ambos"));
    return `<div class="st-chk-res st-${esc(k.cor)}">${pill(k.id)}<p class="small"><b>${proprias.length}</b> declaração(ões) de ${esc(k.nome_urna)} checada(s)</p><div class="chips">${conta(proprias)}</div>
      <p class="small" style="margin-top:10px"><b>${terc.length}</b> conteúdo(s) de terceiros sobre ${esc(k.nome_urna)} checado(s)</p><div class="chips">${conta(terc)}</div></div>`; }).join("");
  return `${cabecalho("Verificação de fatos", "Declarações dos candidatos e conteúdos que circularam sobre eles, com a classificação das agências de checagem e o contexto. A amostra depende do que as agências escolheram verificar; contagens não medem, sozinhas, a veracidade geral de uma campanha.")}
    ${todas.length ? `<div class="st-chk-resumo">${resumo}</div>` : ""}
    <div class="st-filtros"><div><span class="el-mini">Sobre quem</span>${chips("calvo", cands().map(c => [c.id, c.nome_urna]).concat([["ambos", "Ambos"]]), f.calvo)}</div>
      <div><span class="el-mini">Classificação</span>${chips("cclass", Object.entries(d.rotulos.checagem), f.cclass, "Todas")}</div>
      <div><span class="el-mini">Autoria</span>${chips("cautor", cands().map(c => [c.id, "Dita por " + c.nome_urna]).concat([["terceiros", "Produzida por terceiros"]]), f.cautor, "Todas")}</div></div>
    ${its.length ? `<div class="st-chks">${its.map(x => `<article class="st-chk reveal"><div class="st-chk-top"><span class="badge ${tomChecagem[x.classificacao]} st-chk-cl">${esc(R("checagem", x.classificacao))}</span>${x.alvo === "ambos" ? `<span class="badge">Ambos</span>` : pill(x.alvo)}<span class="small muted mono">${esc(FMT(x.data))}</span></div>
      <blockquote class="st-chk-dec">${esc(x.declaracao)}</blockquote><p class="small muted">${esc(x.autor)} · ${esc(x.veiculo)}</p>
      ${x.contexto ? `<p class="small"><b>Contexto.</b> ${esc(x.contexto)}</p>` : ""}<p class="small"><b>Por que esta classificação.</b> ${esc(x.explicacao)}</p>
      <details><summary class="small">Fontes da verificação</summary>${fontes(x.fontes_verificacao)}</details>
      <div class="actions">${x.url_primaria ? `<a class="btn quiet st-btn-fonte" href="${esc(x.url_primaria)}" target="_blank" rel="noopener">${ico("ext")} Ver fonte original</a>` : ""}</div></article>`).join("")}</div>` : vazio(todas.length ? "Nenhuma checagem com os filtros escolhidos." : "O painel de verificação será publicado após a revisão.")}`;
}

function simulador() {
  const p = pesos(), sufi = !!S.f.sufi;
  const linhas = crit().map(c => `<div class="st-peso"><label for="w-${esc(c.id)}">${ico(c.icone)} <span>${esc(c.nome)}</span></label>
    <input type="range" min="0" max="5" step="1" id="w-${esc(c.id)}" data-peso="${esc(c.id)}" value="${p[c.id]}" aria-valuetext="peso ${p[c.id]}"><output class="mono">${p[c.id]}</output>
    <div class="st-peso-notas">${cands().map(k => { const a = aval(c.id, k.id); return `<label class="small">${pill(k.id)} <input type="number" min="0" max="10" step="0.5" data-nota="${esc(c.id)}|${esc(k.id)}" value="${nota(c.id, k.id) ?? ""}" ${a ? "" : "disabled"} aria-label="Nota de ${esc(k.nome_urna)} em ${esc(c.nome)}">${S.notas[c.id + "|" + k.id] != null ? ` <span class="badge mid">sua nota</span>` : ""}</label>`; }).join("")}</div></div>`).join("");
  const res = cands().map(k => { const m = media(k.id, p, sufi); return `<div class="st-res st-${esc(k.cor)}">${pill(k.id)}<b class="mono">${f1(m)}</b><span class="st-res-bar"><i style="width:${(m || 0) * 10}%"></i></span></div>`; }).join("");
  const iguais = {}; crit().forEach(c => { iguais[c.id] = 1; });
  return `${cabecalho("Seus pesos", "Defina quanto cada critério importa para você (0 exclui o critério). Se discordar de uma nota, você pode substituí-la; sua versão fica só neste navegador e é sinalizada.")}
    ${(S.d.avaliacoes || []).length ? `<div class="st-sim"><div class="st-sim-l">${linhas}
      <div class="actions"><button class="btn quiet" type="button" id="stReset">Restaurar pesos iguais e notas da metodologia</button>
      <label class="small"><input type="checkbox" id="stSufi" ${sufi ? "checked" : ""}> Ignorar critérios com evidência insuficiente</label></div></div>
      <aside class="st-sim-r"><div class="st-sticky"><p class="el-mini">Resultado com seus pesos</p>${res}
      <p class="small muted">Com pesos iguais: ${cands().map(k => `${esc(k.nome_urna)} ${f1(media(k.id, iguais))}`).join(" · ")}</p>
      <p class="small muted">A média resume prioridades; ela não substitui a leitura das evidências de cada critério nem indica em quem votar.</p></div></aside></div>` : vazio("O simulador ficará disponível quando as notas forem publicadas.")}`;
}

function conclusao() {
  const c = S.d.conclusao || {};
  const dims = c.dimensoes || [];
  return `${cabecalho("Conclusão por dimensão", "Onde cada candidato apresenta vantagens, fragilidades e riscos, segundo o peso das evidências em cada dimensão. Não há vencedor definido de antemão nem equivalência presumida.")}
    ${c.resumo ? `<p class="lede">${esc(c.resumo)}</p>` : ""}
    ${(c.distincoes || []).length ? `<section class="blk"><div class="sec-head"><h2>Distinções necessárias</h2></div><div class="st-guia">${c.distincoes.map(x => `<div class="st-guia-i">${ico("scale")}<b>${esc(x.titulo)}</b><p class="small">${esc(x.texto)}</p></div>`).join("")}</div></section>` : ""}
    ${dims.length ? dims.map(x => `<section class="blk reveal"><div class="sec-head"><h2>${esc(x.titulo)}</h2>${x.criterio ? `<a class="ref small" href="#/2turno/criterios/${esc(x.criterio)}">Evidências</a>` : ""}</div>
      <div class="st-cols">${cands().map(k => { const v = (x.por_candidato || {})[k.id] || {}; return `<div class="st-col st-${esc(k.cor)}"><div class="st-col-h">${pill(k.id)}</div>
        ${v.vantagens ? `<p class="small"><b>Vantagens.</b> ${esc(v.vantagens)}</p>` : ""}${v.fragilidades ? `<p class="small"><b>Fragilidades.</b> ${esc(v.fragilidades)}</p>` : ""}${v.riscos ? `<p class="small"><b>Riscos.</b> ${esc(v.riscos)}</p>` : ""}</div>`; }).join("")}</div>
      ${x.leitura ? `<p class="small"><b>Leitura do conjunto.</b> ${esc(x.leitura)}</p>` : ""}${x.insuficiencias ? `<p class="small muted"><b>Insuficiências.</b> ${esc(x.insuficiencias)}</p>` : ""}</section>`).join("") : vazio("A conclusão será publicada depois das notas.")}`;
}

function metodologia() {
  const d = S.d, todas = {};
  const add = (f, onde) => { if (!f || !f.url) return; const k = f.url; (todas[k] = todas[k] || Object.assign({ usos: 0 }, f)).usos++; };
  (d.evidencias || []).forEach(e => (e.fontes || []).forEach(f => add(f)));
  (d.checagens || []).forEach(e => (e.fontes_verificacao || []).forEach(f => add(f)));
  (d.linha_do_tempo || []).forEach(e => (e.fontes || []).forEach(f => add(f)));
  ((d.eleicao.situacao || {}).fontes || []).forEach(f => add(f));
  const lista = Object.values(todas).sort((a, b) => String(b.data).localeCompare(String(a.data)));
  const porTipo = Object.keys(d.rotulos.tipo_fonte).map(t => [t, lista.filter(f => f.tipo_fonte === t).length]);
  const porVeiculo = {}; lista.forEach(f => { porVeiculo[f.veiculo] = (porVeiculo[f.veiculo] || 0) + 1; });
  const m = d.conclusao && d.conclusao.metodologia || {};
  return `${cabecalho("Metodologia e fontes", "Como as evidências foram reunidas, classificadas e avaliadas, e a lista completa das fontes consultadas.")}
    <section class="blk"><div class="sec-head"><h2>Procedimento</h2></div><ol class="st-passos">${(m.passos || [
      "Confirmação da situação eleitoral oficial no TSE.",
      "Roteiro único de perguntas por critério, aplicado aos dois candidatos.",
      "Coleta em fontes primárias (TSE, STF, STJ, Congresso, IBGE, Banco Central, Tesouro, planos de governo) e em veículos de linhas editoriais diferentes, nacionais e internacionais.",
      "Classificação de cada evidência por tipo, sentido e peso probatório; registro de contraponto e limitações.",
      "Nota de 0 a 10 por critério segundo rubrica publicada, com justificativa que cita as evidências e grau de suficiência.",
      "Publicação automática bloqueada se faltar fonte, data ou justificativa."]).map(x => `<li>${esc(x)}</li>`).join("")}</ol>
      ${m.limites ? `<p class="small muted"><b>Limites.</b> ${esc(m.limites)}</p>` : ""}</section>
    <section class="blk"><div class="sec-head"><h2>Tipos de evidência</h2></div><dl class="kv">${Object.entries(d.rotulos.tipo).map(([k, v]) => `<dt>${esc(v)}</dt><dd class="small">${esc((m.tipos || {})[k] || "")}</dd>`).join("")}</dl></section>
    <section class="blk"><div class="sec-head"><h2>Fontes consultadas</h2><span class="sec-note">${lista.length} fontes · ${porTipo.filter(x => x[1]).map(([t, n]) => `${esc(R("tipo_fonte", t))}: ${n}`).join(" · ")}</span></div>
      <p class="small muted">Veículos: ${Object.entries(porVeiculo).sort((a, b) => b[1] - a[1]).map(([v, n]) => `${esc(v)} (${n})`).join(", ")}</p>
      ${lista.length ? `<ul class="st-fontes st-fontes-todas">${lista.map(fonte).join("")}</ul>` : vazio("Lista em preparação.")}</section>`;
}

// ------------------------------------------------------------ rotas
function render(h) {
  const d = dados();
  if (S.erro) return `<div class="empty">Não foi possível carregar a análise do 2º turno (${esc(S.erro)}).</div>`;
  if (!d) return `<p class="loading">Carregando a análise do 2º turno…</p>`;
  const [rota, qs] = h.replace(/^\/2turno\/?/, "").split("?");
  const q = {}; (qs || "").split("&").filter(Boolean).forEach(x => { const [k, v] = x.split("="); q[k] = decodeURIComponent(v || ""); });
  const [sec, id] = rota.split("/");
  if (id) q.id = id;
  MN.util.status(`<span><span class="pulse"></span>Dados de ${esc(MN.util.FMTH(d.gerado_em))}</span>`);
  return ({ "": visao, criterios, propostas, tempo, checagens, simulador, conclusao, metodologia }[sec] || visao)(q);
}
let tip = null;
function depois() {
  document.querySelectorAll("[data-f]").forEach(b => b.addEventListener("click", () => {
    const k = b.dataset.f; S.f[k] = b.dataset.v || ""; if (k === "crit" && location.hash.match(/criterios\/./)) { location.hash = "#/2turno/criterios"; }
    salvarF(); MN.render(true); }));
  document.querySelectorAll("[data-peso]").forEach(r => {
    r.addEventListener("input", () => { r.nextElementSibling.textContent = r.value; });
    r.addEventListener("change", () => { S.pesos = Object.assign(pesos(), { [r.dataset.peso]: +r.value }); ls.set("st-pesos", S.pesos); MN.render(true); }); });
  document.querySelectorAll("[data-nota]").forEach(r => r.addEventListener("change", () => {
    const v = r.value === "" ? null : Math.max(0, Math.min(10, +r.value)); const k = r.dataset.nota; const [c, cd] = k.split("|"); const a = aval(c, cd);
    if (v == null || (a && v === a.nota)) delete S.notas[k]; else S.notas[k] = v; ls.set("st-notas", S.notas); MN.render(true); }));
  const rs = document.getElementById("stReset"); if (rs) rs.addEventListener("click", () => { S.pesos = null; S.notas = {}; ls.set("st-pesos", null); ls.set("st-notas", {}); MN.render(true); });
  const sf = document.getElementById("stSufi"); if (sf) sf.addEventListener("change", () => { S.f.sufi = sf.checked; salvarF(); MN.render(true); });
  if (!tip) { tip = document.createElement("div"); tip.className = "st-tip"; tip.hidden = true; document.body.appendChild(tip); }
  document.querySelectorAll("[data-tip]").forEach(el => {
    el.addEventListener("mouseenter", ev => { tip.textContent = el.dataset.tip; tip.hidden = false; });
    el.addEventListener("mousemove", ev => { tip.style.left = ev.clientX + 12 + "px"; tip.style.top = ev.clientY + 12 + "px"; });
    el.addEventListener("mouseleave", () => { tip.hidden = true; });
  });
}
MN.registrar({ prefixo: "/2turno", render, depois });
})();
