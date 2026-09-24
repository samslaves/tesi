/*
 * staffetta.js — passaggio dei parametri fra le 4 pagine via query string
 * dell'URL. Nessun localStorage, nessun server: funziona anche aprendo i
 * file con un doppio click (file://).
 */
(function (global) {
  "use strict";

  const STAGES = [
    { key: "sistema",      num: "1", nome: "Sistema",      dir: "01-sistema" },
    { key: "vqe",          num: "2", nome: "VQE",           dir: "02-vqe" },
    { key: "dinamica",     num: "3", nome: "Dinamica",      dir: "03-dinamica" },
    { key: "correlatori",  num: "4", nome: "Correlatori",   dir: "04-correlatori" },
  ];

  function readParams() {
    const p = new URLSearchParams(window.location.search);
    const out = {};
    for (const [k, v] of p.entries()) out[k] = v;
    return out;
  }

  function numOr(params, key, fallback) {
    const v = params[key];
    if (v === undefined || v === null || v === "") return fallback;
    const n = parseFloat(v);
    return Number.isFinite(n) ? n : fallback;
  }

  function buildUrl(relBase, targetDir, params) {
    const qs = new URLSearchParams(params).toString();
    return relBase + targetDir + "/index.html" + (qs ? "?" + qs : "");
  }

  // relBase: "../" se siamo dentro una sottocartella, "" se siamo nell'indice
  function renderTopNav(container, currentKey, relBase, forwardParams) {
    relBase = relBase === undefined ? "../" : relBase;
    forwardParams = forwardParams || {};
    const home = relBase === "../" ? "../index.html" : "index.html";
    const manuale = relBase === "../" ? "../manuale.html" : "manuale.html";
    let html = `<span class="brand">tesi dimero &middot;</span>`;
    html += `<a class="navbtn" href="${home}">&#8962; indice</a>`;
    STAGES.forEach(S => {
      const cur = S.key === currentKey;
      const href = cur ? "#" : buildUrl(relBase, S.dir, forwardParams);
      html += `<a class="navbtn${cur ? " current" : ""}" href="${href}"><span class="num">${S.num}</span> ${S.nome}</a>`;
    });
    html += `<a class="navbtn" href="${manuale}" style="margin-left:auto">&#128214; guida</a>`;
    container.innerHTML = html;
  }

  function renderHandoff(container, fromKey, html) {
    if (!fromKey) { container.innerHTML = ""; return; }
    const S = STAGES.find(s => s.key === fromKey);
    const nome = S ? (S.num + " &middot; " + S.nome) : fromKey;
    container.innerHTML = `<div class="box"><b>In ingresso da ${nome}.</b> ${html}</div>`;
  }

  global.Staffetta = { STAGES, readParams, numOr, buildUrl, renderTopNav, renderHandoff };
})(typeof window !== "undefined" ? window : globalThis);
