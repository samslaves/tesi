/* script.js — 02-vqe */
(function () {
  "use strict";
  const params = Staffetta.readParams();
  let bJ = Staffetta.numOr(params, "bJ", 2.0);
  let DJ = Staffetta.numOr(params, "DJ", 0.2);
  let ansatz = params.ansatz && Fisica.ANSATZ_INFO[params.ansatz] ? params.ansatz : "pma3";

  const $bJ = document.getElementById("bJ"), $DJ = document.getElementById("DJ");
  const $bJv = document.getElementById("bJv"), $DJv = document.getElementById("DJv");
  const $ansatz = document.getElementById("ansatz");
  $bJ.value = bJ; $DJ.value = DJ; $ansatz.value = ansatz;

  const KETS = ["|00\u27E9", "|01\u27E9", "|10\u27E9", "|11\u27E9"];
  const BMAX = 4.0;
  let sweepB = [], sweepFid = [];
  let animTimer = null;
  let lastFid = null, lastState = null, lastParams = null;

  const maskB = Matematica.diffMask(Fisica.buildH1(1), Fisica.buildH1(0));
  const maskD = Matematica.nonzeroMask(Fisica.buildH2(1));

  function renderMatH() {
    const gs = Fisica.groundState(bJ, DJ);
    Matematica.renderMatrix(document.getElementById("matH"), gs.H, null, ["00","01","10","11"], { decimals: 2 });
    return gs;
  }

  function forwardParams(extra) {
    return Object.assign({ bJ: bJ.toFixed(3), DJ: DJ.toFixed(3), ansatz }, extra || {});
  }
  function updateNav() {
    Staffetta.renderTopNav(document.getElementById("topnav"), "vqe", "../", forwardParams());
  }
  function updateProseguiLinks(fid) {
    const a = document.getElementById("prosegui");
    a.href = Staffetta.buildUrl("../", "03-dinamica", forwardParams({ da: "vqe", stato: "vqe", fid: fid.toFixed(4) }));
  }

  function computeSweep() {
    const N = 25;
    sweepB = []; sweepFid = [];
    for (let k = 0; k < N; k++) {
      const bv = BMAX * k / (N - 1);
      const gs = Fisica.groundState(bv, DJ);
      const res = Fisica.optimizeAnsatz(ansatz, bv, DJ, { restarts: 4, iters: 160 });
      sweepB.push(bv);
      sweepFid.push(Fisica.fidelityToVec(res.state, gs.psi0));
    }
  }

  function drawFidCurve(markerFid) {
    const svg = document.getElementById("fidcurve");
    Componenti.LineChart(svg, {
      w: 700, h: 260, margin: { l: 54, r: 14, t: 10, b: 40 },
      xDomain: [0, BMAX], yDomain: [0.4, 1.02],
      xTicks: [0, 1, 2, 3, 4], yTicks: [0.4, 0.6, 0.8, 1.0],
      xLabel: "B / J  (adimensionale)", yLabel: "fidelity |\u27e8\u03c8_VQE|\u03c8\u2080\u27e9|  (adimensionale)",
      series: [{ x: sweepB, y: sweepFid, color: "#A4306B", width: 2.2 }],
      vlines: [{ x: 2, color: "#BDC9D7", width: 1.2, dash: "3 3" }],
      points: markerFid === undefined ? [] : [{ x: bJ, y: markerFid, color: "#A8560C", r: 5.5 }],
    });
  }

  function drawConvergenza(trace, uptoIdx) {
    const svg = document.getElementById("convergenza");
    const E0 = Fisica.groundState(bJ, DJ).E[0];
    const xs = trace.slice(0, uptoIdx + 1).map((_, i) => i);
    const ys = trace.slice(0, uptoIdx + 1).map(p => p.E);
    const yMin = Math.min(E0, ...trace.map(p => p.E)) - 0.15;
    const yMax = Math.max(...trace.map(p => p.E)) + 0.15;
    Componenti.LineChart(svg, {
      w: 700, h: 180, margin: { l: 58, r: 14, t: 10, b: 38 },
      xDomain: [0, trace.length - 1], yDomain: [yMin, yMax],
      xTicks: [0, Math.round(trace.length/2), trace.length-1],
      yTicks: [yMin, (yMin+yMax)/2, yMax], yFmt: v=>v.toFixed(2),
      xLabel: "iterazione dell'ottimizzatore  (numero, adimensionale)", yLabel: "E(\u03b8) / J  (in unit\u00e0 di J)",
      series: [{ x: xs, y: ys, color: "#0E7C86", width: 2 }],
      vlines: [], points: [{ x: uptoIdx, y: trace[uptoIdx].E, color: "#A8560C", r: 4 }],
    });
    document.getElementById("rE0").textContent = E0.toFixed(4);
  }

  function stopAnim() { if (animTimer) { clearTimeout(animTimer); animTimer = null; } }

  function runOptimization() {
    stopAnim();
    const gs = Fisica.groundState(bJ, DJ);
    const res = Fisica.optimizeAnsatz(ansatz, bJ, DJ, { restarts: 6, iters: 220 });
    const trace = res.trace;
    const FRAMES = Math.min(50, trace.length);
    const idxs = [];
    for (let f = 0; f < FRAMES; f++) idxs.push(Math.round(f * (trace.length - 1) / (FRAMES - 1)));

    let fi = 0;
    function step() {
      const idx = idxs[fi];
      const p = trace[idx].params;
      const st = Fisica.ansatzState(ansatz, p, bJ);
      const fid = Fisica.fidelityToVec(st, gs.psi0);
      document.getElementById("rIter").textContent = idx;
      document.getElementById("rE").textContent = trace[idx].E.toFixed(4);
      document.getElementById("rFid").textContent = fid.toFixed(4);
      drawConvergenza(trace, idx);
      drawFidCurve(fid);
      Componenti.renderAmps(document.getElementById("ampsVqe"), st.re, st.im, KETS, "#A4306B");
      Matematica.renderKet(document.getElementById("ketVqe"), st.re, st.im, KETS, "#A4306B");
      Matematica.flashText(document.getElementById("ketVqe"));
      fi++;
      if (fi < idxs.length) {
        animTimer = setTimeout(step, 900 / FRAMES + (fi < 5 ? 40 : 0));
      } else {
        finish(st, fid, p);
      }
    }
    step();
  }

  function finish(st, fid, p) {
    lastFid = fid; lastState = st; lastParams = p.slice();
    updateProseguiLinks(fid);
    const cc = document.getElementById("ccEsito");
    if (fid > 0.999) {
      cc.innerHTML = `Fidelity ${fid.toFixed(6)}: il circuito raggiunge lo stato esatto. Con ${Fisica.ANSATZ_INFO[ansatz].nparam} parametri, in questo punto di lavoro, basta e avanza.`;
    } else if (fid > 0.97) {
      cc.innerHTML = `Fidelity ${fid.toFixed(6)}: molto vicino ma non esatto. Provi a spostare lo slider B/J verso B/J=2 per vedere l'effetto crescere.`;
    } else {
      cc.innerHTML = `Fidelity ${fid.toFixed(6)}: qui l'ansatz non ce la fa. Non &egrave; un problema di ottimizzazione &mdash; &egrave; strutturale: lo stato fondamentale con il DM acceso esce dal settore a magnetizzazione fissata su cui questo circuito &egrave; costruito, e nessun numero di iterazioni in pi&ugrave; lo risolve.`;
    }
    computeCircuitSteps();
  }

  function onHeavyChange() { computeSweep(); drawFidCurve(lastFid === null ? undefined : lastFid); }

  // ------------------------------------------------- il circuito, porta per porta
  let circuitSteps = [], circuitIdx = -1, circuitPlayTimer = null;

  function stopCircuitPlay() {
    if (circuitPlayTimer) { clearTimeout(circuitPlayTimer); circuitPlayTimer = null; }
    document.getElementById("stepPlay").textContent = "Avvia";
  }

  function renderCircuitStep() {
    Componenti.CircuitDiagram(document.getElementById("circuito"), circuitSteps, { nWires: 2, wireLabels: ["q0","q1"], highlightIndex: circuitIdx });
    const st = circuitIdx === -1 ? { re: [1,0,0,0], im: [0,0,0,0] } : circuitSteps[circuitIdx].state;
    const col = circuitIdx === -1 ? "#5C7288" : "#A8560C";
    Componenti.renderAmps(document.getElementById("ampsCircuito"), st.re, st.im, KETS, col);
    Matematica.renderKet(document.getElementById("ketCircuito"), st.re, st.im, KETS, col);
    Matematica.flashText(document.getElementById("ketCircuito"));
    document.getElementById("rPasso").textContent = `${circuitIdx + 1} di ${circuitSteps.length}`;
    document.getElementById("rPorta").innerHTML = circuitIdx === -1 ? "&mdash; (stato iniziale |00&rang;)" : circuitSteps[circuitIdx].desc;
    document.getElementById("notaCircuito").innerHTML = lastParams
      ? ""
      : "Parametri non ancora ottimizzati per questo punto (mostrati a zero): prema &laquo;Ottimizza&raquo; qui sopra per vedere il circuito che risolve davvero il problema.";
  }

  function computeCircuitSteps() {
    const nparam = Fisica.ANSATZ_INFO[ansatz].nparam;
    const p = lastParams || new Array(nparam).fill(0);
    circuitSteps = Fisica.ansatzSteps(ansatz, p, bJ);
    circuitIdx = -1;
    stopCircuitPlay();
    renderCircuitStep();
  }

  document.getElementById("stepInizio").addEventListener("click", () => { stopCircuitPlay(); circuitIdx = -1; renderCircuitStep(); });
  document.getElementById("stepIndietro").addEventListener("click", () => { stopCircuitPlay(); circuitIdx = Math.max(-1, circuitIdx - 1); renderCircuitStep(); });
  document.getElementById("stepAvanti").addEventListener("click", () => { stopCircuitPlay(); circuitIdx = Math.min(circuitSteps.length - 1, circuitIdx + 1); renderCircuitStep(); });
  document.getElementById("stepFine").addEventListener("click", () => { stopCircuitPlay(); circuitIdx = circuitSteps.length - 1; renderCircuitStep(); });
  document.getElementById("stepPlay").addEventListener("click", () => {
    if (circuitPlayTimer) { stopCircuitPlay(); return; }
    if (circuitIdx >= circuitSteps.length - 1) circuitIdx = -1;
    document.getElementById("stepPlay").textContent = "Ferma";
    const tick = () => {
      circuitIdx++;
      renderCircuitStep();
      if (circuitIdx < circuitSteps.length - 1) circuitPlayTimer = setTimeout(tick, 750);
      else stopCircuitPlay();
    };
    tick();
  });

  function invalidaOttimizzazione() {
    lastFid = null; lastState = null; lastParams = null;
    document.getElementById("ccEsito").innerHTML = "Punto di lavoro cambiato: prema &laquo;Ottimizza&raquo; per questo punto.";
  }

  $bJ.addEventListener("input", e => {
    bJ = parseFloat(e.target.value); $bJv.textContent = bJ.toFixed(2);
    updateNav();
    invalidaOttimizzazione();
    drawFidCurve();
    renderMatH();
    Matematica.flashCells(document.getElementById("matH"), maskB);
    computeCircuitSteps();
  });
  $DJ.addEventListener("input", e => {
    DJ = parseFloat(e.target.value); $DJv.textContent = DJ.toFixed(2);
    updateNav();
    invalidaOttimizzazione();
    renderMatH();
    Matematica.flashCells(document.getElementById("matH"), maskD);
  });
  $DJ.addEventListener("change", onHeavyChange);
  $ansatz.addEventListener("change", e => {
    ansatz = e.target.value; updateNav();
    invalidaOttimizzazione();
    onHeavyChange();
    computeCircuitSteps();
  });
  document.getElementById("ottimizza").addEventListener("click", runOptimization);

  Staffetta.renderHandoff(document.getElementById("handoff"), params.da,
    "Il punto di lavoro (B/J, D/J) arriva dallo stadio 1. Scelga un ansatz e prema \u00abOttimizza\u00bb.");

  $bJv.textContent = bJ.toFixed(2);
  $DJv.textContent = DJ.toFixed(2);
  updateNav();
  computeSweep();
  drawFidCurve();
  renderMatH();
  const E0init = Fisica.groundState(bJ, DJ);
  Componenti.renderAmps(document.getElementById("ampsExact"), E0init.psi0, E0init.psi0.map(()=>0), KETS, "#0E7C86");
  document.getElementById("rE0").textContent = E0init.E[0].toFixed(4);
  document.getElementById("ccEsito").innerHTML = "Prema &laquo;Ottimizza&raquo; per far convergere l'ansatz su questo punto.";
  computeCircuitSteps();
  Matematica.renderStaticFormulas();
})();
