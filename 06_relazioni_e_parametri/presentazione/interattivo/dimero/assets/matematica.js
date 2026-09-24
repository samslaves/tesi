/*
 * matematica.js — pannello matematico condiviso: matrici come heatmap HTML,
 * notazione di Dirac con coefficienti live, ed evidenziazione mirata quando
 * un valore cambia in conseguenza di un'azione sui controlli.
 *
 * Filosofia: niente librerie di typesetting esterne (KaTeX, MathJax...) per
 * restare fedeli al vincolo "solo un browser, nessuna dipendenza". Le formule
 * simboliche sono HTML statico scritto a mano; ciò che qui si genera
 * dinamicamente sono i NUMERI (matrici, ket, letture) e le animazioni di
 * evidenziazione.
 */
(function (global) {
  "use strict";

  function fmt(x, d) { d = d === undefined ? 3 : d; return (x >= 0 ? "+" : "") + x.toFixed(d); }
  function fmtPlain(x, d) { d = d === undefined ? 3 : d; return x.toFixed(d); }

  function fmtComplex(re, im, d) {
    d = d === undefined ? 3 : d;
    if (Math.abs(im) < 5e-4) return fmtPlain(re, d);
    return fmtPlain(re, d) + (im >= 0 ? "+" : "-") + Math.abs(im).toFixed(d) + "i";
  }

  // -------------------------------------------------------- maschere di dipendenza
  // Confronta due matrici e ritorna l'insieme di posizioni [i,j] dove differiscono
  // di piu' di una soglia: usato per sapere quali celle "appartengono" a un dato
  // parametro, senza doverle trascrivere a mano.
  function diffMask(A, B, tol) {
    tol = tol === undefined ? 1e-9 : tol;
    const out = [];
    for (let i = 0; i < A.length; i++)
      for (let j = 0; j < A.length; j++)
        if (Math.abs(A[i][j] - B[i][j]) > tol) out.push([i, j]);
    return out;
  }
  function nonzeroMask(A, tol) {
    tol = tol === undefined ? 1e-9 : tol;
    const out = [];
    for (let i = 0; i < A.length; i++)
      for (let j = 0; j < A.length; j++)
        if (Math.abs(A[i][j]) > tol) out.push([i, j]);
    return out;
  }
  function maskKey(i, j) { return i + "_" + j; }

  // ------------------------------------------------------------------ heatmap
  function heatColor(v, vMax) {
    if (vMax <= 1e-12) return "#ffffff";
    const t = Math.min(1, Math.abs(v) / vMax);
    const L = 96 - t * 38;
    const hue = v >= 0 ? 178 : 336;
    return `hsl(${hue} 55% ${L}%)`;
  }

  // Renderizza una matrice NxN reale (o complessa: passare anche Mim) come
  // tabella HTML colorata. labels: array di etichette di riga/colonna (es.
  // ["00","01","10","11"]). highlightSet: Set di "i_j" da evidenziare con un
  // anello ambra (le celle "appena cambiate" per il parametro mosso).
  function renderMatrix(container, Mre, Mim, labels, opts) {
    opts = opts || {};
    const n = Mre.length;
    let vMax = 0;
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      const mag = Mim ? Math.hypot(Mre[i][j], Mim[i][j]) : Math.abs(Mre[i][j]);
      if (mag > vMax) vMax = mag;
    }
    const hl = opts.highlight || new Set();
    let html = `<div class="mat-scroll"><table class="mat"><thead><tr><th></th>`;
    labels.forEach(l => html += `<th>${l}</th>`);
    html += `</tr></thead><tbody>`;
    for (let i = 0; i < n; i++) {
      html += `<tr><th>${labels[i]}</th>`;
      for (let j = 0; j < n; j++) {
        const re = Mre[i][j], im = Mim ? Mim[i][j] : 0;
        const mag = Math.hypot(re, im);
        const signedForColor = Mim ? mag : re; // per matrici reali il segno conta nel colore
        const bg = heatColor(signedForColor, vMax || 1);
        const cellId = maskKey(i, j);
        const cls = hl.has(cellId) ? "mcell hl" : "mcell";
        html += `<td class="${cls}" style="background:${bg}" data-cell="${cellId}">${fmtComplex(re, im, opts.decimals)}</td>`;
      }
      html += `</tr>`;
    }
    html += `</tbody></table></div>`;
    container.innerHTML = html;
  }

  // --------------------------------------------------------------- ket line
  function renderKet(container, re, im, kets, color, opts) {
    opts = opts || {};
    const tol = opts.tol === undefined ? 1e-4 : opts.tol;
    const dec = opts.decimals === undefined ? 3 : opts.decimals;
    let html = "", first = true;
    for (let n = 0; n < re.length; n++) {
      const r = re[n], i = im ? im[n] : 0;
      if (Math.hypot(r, i) < tol) continue;
      let opStr, mag;
      if (Math.abs(i) < 5e-4) {
        const neg = r < 0;
        mag = Math.abs(r).toFixed(dec);
        opStr = first ? (neg ? "&minus;" : "") : (neg ? " &minus; " : " + ");
      } else {
        mag = "(" + fmtComplex(r, i, dec) + ")";
        opStr = first ? "" : " + ";
      }
      html += `${opStr}<span style="color:${color}">${mag}</span>${kets[n]}`;
      first = false;
    }
    container.innerHTML = html || "0";
  }

  // ------------------------------------------------------------ evidenziazione
  // Aggiunge una classe di animazione e la rimuove al termine, forzando un
  // reflow cosi' che due evidenziazioni ravvicinate si vedano entrambe.
  function flashText(el) {
    if (!el) return;
    el.classList.remove("flash-text"); void el.offsetWidth;
    el.classList.add("flash-text");
  }
  function flashRing(el) {
    if (!el) return;
    el.classList.remove("flash-ring"); void el.offsetWidth;
    el.classList.add("flash-ring");
  }
  function flashCells(container, cells) {
    cells.forEach(([i, j]) => {
      const el = container.querySelector(`[data-cell="${maskKey(i,j)}"]`);
      flashRing(el);
    });
  }
  function flashAll(container) {
    container.querySelectorAll(".mcell").forEach(flashRing);
  }

  function renderStaticFormulas(root) {
    (root || document).querySelectorAll(".formula-static[data-tex]").forEach(el => {
      try { katex.render(el.dataset.tex, el, { throwOnError: false, displayMode: true }); }
      catch (e) { /* lascia il testo semplice come rete di sicurezza */ }
    });
    (root || document).querySelectorAll(".formula-inline-ktx[data-tex]").forEach(el => {
      try { katex.render(el.dataset.tex, el, { throwOnError: false, displayMode: false }); }
      catch (e) { /* idem */ }
    });
  }

  const Matematica = {
    fmt, fmtPlain, fmtComplex, diffMask, nonzeroMask, maskKey,
    heatColor, renderMatrix, renderKet, flashText, flashRing, flashCells, flashAll,
    renderStaticFormulas,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = Matematica;
  else global.Matematica = Matematica;
})(typeof window !== "undefined" ? window : globalThis);
