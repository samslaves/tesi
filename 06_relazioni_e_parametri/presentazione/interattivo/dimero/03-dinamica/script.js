/* script.js — 03-dinamica */
(function () {
  "use strict";
  const params = Staffetta.readParams();
  let bJ = Staffetta.numOr(params, "bJ", -0.18);
  let DJ = Staffetta.numOr(params, "DJ", 1.0);
  let stato = params.stato || "su";
  let ansatz = params.ansatz && Fisica.ANSATZ_INFO[params.ansatz] ? params.ansatz : "pma3";
  let N = Math.round(Staffetta.numOr(params, "N", 8));
  let tmax = Staffetta.numOr(params, "tmax", 10.0);
  let t = Math.min(Staffetta.numOr(params, "t", Math.min(6, tmax)), tmax);

  const $bJ = document.getElementById("bJ"), $DJ = document.getElementById("DJ");
  const $bJv = document.getElementById("bJv"), $DJv = document.getElementById("DJv");
  const $stato = document.getElementById("stato");
  const $N = document.getElementById("N"), $Nv = document.getElementById("Nv");
  const $tmax = document.getElementById("tmax"), $tmaxv = document.getElementById("tmaxv");
  const $t = document.getElementById("t"), $tv = document.getElementById("tv");
  $bJ.value = bJ; $DJ.value = DJ; $stato.value = stato;
  $N.value = N; $tmax.value = tmax; $t.value = t; $t.max = tmax;

  const KETS = ["|00\u27E9", "|01\u27E9", "|10\u27E9", "|11\u27E9"];
  const maskB = Matematica.diffMask(Fisica.buildH1(1), Fisica.buildH1(0));

  function forwardParams(extra) {
    return Object.assign({ bJ: bJ.toFixed(3), DJ: DJ.toFixed(3), stato, ansatz, N, t: t.toFixed(2) }, extra || {});
  }
  function updateNav() {
    Staffetta.renderTopNav(document.getElementById("topnav"), "dinamica", "../", forwardParams());
  }
  function updateProsegui() {
    document.getElementById("prosegui").href =
      Staffetta.buildUrl("../", "04-correlatori", forwardParams({ da: "dinamica" }));
  }

  function initialState() {
    if (stato === "esatto") {
      const gs = Fisica.groundState(bJ, DJ);
      return { re: gs.psi0.slice(), im: gs.psi0.map(() => 0) };
    }
    if (stato === "vqe") {
      const res = Fisica.optimizeAnsatz(ansatz, bJ, DJ, { restarts: 6, iters: 220 });
      return { re: res.state.re.slice(), im: res.state.im.slice() };
    }
    return { re: [1, 0, 0, 0], im: [0, 0, 0, 0] }; // |up up>
  }

  function updateNotaStato() {
    const el = document.getElementById("notaStato");
    if (stato === "su") {
      el.innerHTML = "|&uarr;&uarr;&rang; non &egrave; autostato n&eacute; di H&#8321; n&eacute; di H&#8322; separatamente: l'errore di Trotter resta visibile a ogni N. Uno stato che fosse gi&agrave; autostato di un pezzo lo nasconderebbe.";
    } else if (stato === "esatto") {
      el.innerHTML = "Partendo dal fondamentale esatto si isola l'errore di Trotter da quello, distinto, del VQE dello stadio precedente.";
    } else {
      el.innerHTML = `Lo stato arriva dal VQE (ansatz: ${Fisica.ANSATZ_INFO[ansatz].nome}). Se quel circuito non aveva raggiunto fidelity 1, l'imperfezione si somma qui a quella di Trotter.`;
    }
  }

  // ------------------------------------------------------------- grafico Sz(t)
  function drawSz() {
    const NT = 121;
    const psi0 = initialState();
    const ts = [], szExact = [], szTrot = [];
    const Mz2 = m => { // <Sz_tot> su uno stato {re,im}
      const gs = Fisica.buildSz();
      return Fisica.bilinearReal(gs, m.re, m.im);
    };
    for (let k = 0; k < NT; k++) {
      const tv = tmax * k / (NT - 1);
      ts.push(tv);
      szExact.push(Mz2(Fisica.exactEvolve(bJ, DJ, tv, psi0.re, psi0.im)));
      szTrot.push(Mz2(Fisica.trotterEvolve(bJ, DJ, tv, N, psi0.re, psi0.im)));
    }
    const svg = document.getElementById("szplot");
    const szAtT = Mz2(Fisica.exactEvolve(bJ, DJ, t, psi0.re, psi0.im));
    Componenti.LineChart(svg, {
      w: 700, h: 260, margin: { l: 54, r: 14, t: 10, b: 40 },
      xDomain: [0, tmax], yDomain: [-1.15, 1.15],
      xTicks: Array.from({length:6}, (_,i)=> (tmax*i/5).toFixed(1)).map(Number),
      yTicks: [-1, -0.5, 0, 0.5, 1],
      xLabel: "t  (unit\u00e0 di 1/J)", yLabel: "\u27e8S_z^tot\u27e9  (adimensionale)",
      series: [
        { x: ts, y: szExact, color: "#14273A", width: 2.4 },
        { x: ts, y: szTrot, color: "#A4306B", width: 1.8, dash: "5 3" },
      ],
      vlines: [{ x: t, color: "#A8560C", width: 1.4, dash: "2 2" }],
      points: [{ x: t, y: szAtT, color: "#A8560C", r: 4.5 }],
    });
  }

  // --------------------------------------------------------- pannello H1, H2
  function drawH1H2() {
    const H1 = Fisica.buildH1(bJ), H2 = Fisica.buildH2(DJ);
    Matematica.renderMatrix(document.getElementById("matH1"), H1, null, ["00","01","10","11"], { decimals: 2 });
    Matematica.renderMatrix(document.getElementById("matH2"), H2, null, ["00","01","10","11"], { decimals: 2 });
  }

  // ----------------------------------------------------- pannello M(tau), ket
  function drawTrotterPanel() {
    const tau = t / N;
    const M = Fisica.trotterStepMatrix(bJ, DJ, tau);
    Matematica.renderMatrix(document.getElementById("matM"), M.re, M.im, ["00","01","10","11"], { decimals: 2 });
    document.getElementById("ketTlabel").textContent = t.toFixed(2);
    const psi0 = initialState();
    const ex = Fisica.exactEvolve(bJ, DJ, t, psi0.re, psi0.im);
    const tr = Fisica.trotterEvolve(bJ, DJ, t, N, psi0.re, psi0.im);
    Matematica.renderKet(document.getElementById("ketExact"), ex.re, ex.im, KETS, "#14273A");
    Matematica.renderKet(document.getElementById("ketTrot"), tr.re, tr.im, KETS, "#A4306B");
    return { ex, tr };
  }

  // ------------------------------------------------------------- errore vs N
  function drawErrore() {
    const psi0 = initialState();
    const Uexact = Fisica.expOfSymH(Fisica.buildH(bJ, DJ), tmax);
    const exState = Fisica.matVecC(Uexact, psi0.re, psi0.im);
    const Nlist = [1,2,4,8,16,32,64,128,256].filter(n => n <= 400);
    const errFid = Nlist.map(n => {
      const tr = Fisica.trotterEvolve(bJ, DJ, tmax, n, psi0.re, psi0.im);
      const d = Fisica.vecDagVec(exState.re, exState.im, tr.re, tr.im);
      return Math.max(1e-12, 1 - (d.re*d.re + d.im*d.im));
    });
    const errOp = Nlist.map(n => {
      const tau = tmax / n;
      let M = Fisica.trotterStepMatrix(bJ, DJ, tau);
      // ||U_trotter - U_exact||_F come proxy pratico (norma di Frobenius della differenza)
      let diffSq = 0;
      // costruiamo U_trotter^N applicandolo a base canonica
      const cols = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]].map(e0 => {
        let re = e0.slice(), im = [0,0,0,0];
        for (let k=0;k<n;k++) { const o = Fisica.matVecC(M, re, im); re = o.re; im = o.im; }
        return { re, im };
      });
      for (let c=0;c<4;c++) for (let r=0;r<4;r++) {
        const dre = cols[c].re[r] - Uexact.re[r][c], dim = cols[c].im[r] - Uexact.im[r][c];
        diffSq += dre*dre + dim*dim;
      }
      return Math.sqrt(diffSq);
    });

    const svg = document.getElementById("errplot");
    Componenti.LineChart(svg, {
      w: 700, h: 220, margin: { l: 58, r: 14, t: 10, b: 40 }, logY: true, logX: true,
      xDomain: [1, 400], yDomain: [1e-8, 4],
      xTicks: [1, 10, 100], yTicks: [1e-8,1e-6,1e-4,1e-2,1],
      yFmt: v => v.toExponential(0),
      xLabel: "N, numero di passi di Trotter  (numero, adimensionale)",
      yLabel: "errore  (adimensionale)",
      series: [
        { x: Nlist, y: errOp, color: "#0E7C86", width: 2 },
        { x: Nlist, y: errFid, color: "#A4306B", width: 2 },
      ],
      points: Nlist.map((n,i)=>({x:n,y:errFid[i],color:"#A4306B",r:3})).concat(
              Nlist.map((n,i)=>({x:n,y:errOp[i],color:"#0E7C86",r:3}))),
    });

    // errore alla N corrente (readout)
    const trN = Fisica.trotterEvolve(bJ, DJ, t, N, psi0.re, psi0.im);
    const exN = Fisica.exactEvolve(bJ, DJ, t, psi0.re, psi0.im);
    const dN = Fisica.vecDagVec(exN.re, exN.im, trN.re, trN.im);
    const errNow = 1 - (dN.re*dN.re + dN.im*dN.im);
    document.getElementById("rErrN").textContent = errNow.toExponential(3);
    document.getElementById("rCnotTot").textContent = (3*N).toString();

    const cc = document.getElementById("ccTradeoff");
    if (N < 12) {
      cc.innerHTML = `Con N = ${N} l'errore (${errNow.toExponential(2)}) &egrave; ancora ben visibile nel grafico sopra, ma il costo &egrave; basso: ${3*N} CNOT in tutto.`;
    } else if (N < 60) {
      cc.innerHTML = `Con N = ${N} l'errore &egrave; sceso a ${errNow.toExponential(2)}, con ${3*N} CNOT: un compromesso ragionevole per un dispositivo NISQ.`;
    } else {
      cc.innerHTML = `Con N = ${N} l'errore algoritmico &egrave; ormai piccolissimo (${errNow.toExponential(2)}), ma il circuito costa ${3*N} CNOT: su hardware reale il rumore di gate comincerebbe a dominare su questo stesso errore che si sta riducendo.`;
    }
  }

  // ------------------------------------------------ il circuito, un periodo alla volta
  let trotterFullSteps = [], trotterIdx = -1, trotterPlayTimer = null;
  const GATI_PER_PERIODO = 11; // 5 per U1 (Rz,Rz,Rxx,Ryy,Rzz) + 6 per U2 (H,Rzz,H,H,Rzz,H)

  function stopTrotterPlay() {
    if (trotterPlayTimer) { clearTimeout(trotterPlayTimer); trotterPlayTimer = null; }
    document.getElementById("tsPlay").textContent = "Avvia";
  }

  function renderCircuitoTrotterDiagramma() {
    // un solo periodo, per esteso nelle sue 11 porte elementari; l'evidenziazione
    // segue la posizione nel periodo corrente (indice modulo la lunghezza del periodo).
    const unPeriodo = trotterFullSteps.slice(0, GATI_PER_PERIODO)
      .map(s => s.kind === "BOX" ? { kind: "BOX", wire: s.wire, label: s.label } : { kind: "SPAN", wires: s.wires, label: s.label });
    const hi = trotterIdx === -1 ? undefined : (trotterIdx % GATI_PER_PERIODO);
    Componenti.CircuitDiagram(document.getElementById("circuitoTrotter"), unPeriodo, { nWires: 2, wireLabels: ["q0","q1"], highlightIndex: hi });
    document.getElementById("notaPeriodo").textContent = `Questo periodo (le 11 porte sopra) si ripete N = ${N} volte, una dopo l'altra.`;
  }

  function renderTrotterStep() {
    renderCircuitoTrotterDiagramma();
    const psi0 = initialState();
    const st = trotterIdx === -1 ? { re: psi0.re, im: psi0.im } : trotterFullSteps[trotterIdx].state;
    const col = trotterIdx === -1 ? "#5C7288" : "#A8560C";
    Componenti.renderAmps(document.getElementById("ampsTrotterStep"), st.re, st.im, KETS, col);
    Matematica.renderKet(document.getElementById("ketTrotterStep"), st.re, st.im, KETS, col);
    Matematica.flashText(document.getElementById("ketTrotterStep"));
    document.getElementById("tsPasso").textContent = `${trotterIdx + 1} di ${trotterFullSteps.length}`;
    document.getElementById("tsBlocco").innerHTML = trotterIdx === -1 ? "&mdash; (stato iniziale)" : trotterFullSteps[trotterIdx].desc;
  }

  function computeTrotterCircuit() {
    const psi0 = initialState();
    trotterFullSteps = Fisica.trotterMicroSteps(bJ, DJ, t, N, psi0.re, psi0.im);
    trotterIdx = -1;
    stopTrotterPlay();
    renderTrotterStep();
  }

  document.getElementById("tsInizio").addEventListener("click", () => { stopTrotterPlay(); trotterIdx = -1; renderTrotterStep(); });
  document.getElementById("tsIndietro").addEventListener("click", () => { stopTrotterPlay(); trotterIdx = Math.max(-1, trotterIdx - 1); renderTrotterStep(); });
  document.getElementById("tsAvanti").addEventListener("click", () => { stopTrotterPlay(); trotterIdx = Math.min(trotterFullSteps.length - 1, trotterIdx + 1); renderTrotterStep(); });
  document.getElementById("tsFine").addEventListener("click", () => { stopTrotterPlay(); trotterIdx = trotterFullSteps.length - 1; renderTrotterStep(); });
  document.getElementById("tsPlay").addEventListener("click", () => {
    if (trotterPlayTimer) { stopTrotterPlay(); return; }
    if (trotterIdx >= trotterFullSteps.length - 1) trotterIdx = -1;
    document.getElementById("tsPlay").textContent = "Ferma";
    const delay = Math.max(35, Math.min(700, 6000 / trotterFullSteps.length));
    const tick = () => {
      trotterIdx++;
      renderTrotterStep();
      if (trotterIdx < trotterFullSteps.length - 1) trotterPlayTimer = setTimeout(tick, delay);
      else stopTrotterPlay();
    };
    tick();
  });

  function renderAll() {
    $bJv.textContent = bJ.toFixed(2);
    $DJv.textContent = DJ.toFixed(2);
    $Nv.textContent = N;
    $tmaxv.textContent = tmax.toFixed(1);
    $tv.textContent = t.toFixed(1);
    updateNotaStato();
    drawH1H2();
    drawSz();
    drawTrotterPanel();
    drawErrore();
    computeTrotterCircuit();
    updateNav();
    updateProsegui();
  }

  $bJ.addEventListener("input", e => {
    bJ = parseFloat(e.target.value); renderAll();
    Matematica.flashCells(document.getElementById("matH1"), maskB);
  });
  $DJ.addEventListener("input", e => {
    DJ = parseFloat(e.target.value); renderAll();
    Matematica.flashAll(document.getElementById("matH2"));
  });
  $stato.addEventListener("change", e => { stato = e.target.value; renderAll(); });
  $N.addEventListener("input", e => {
    N = parseInt(e.target.value, 10); renderAll();
    Matematica.flashAll(document.getElementById("matM"));
    [document.getElementById("ketExact"), document.getElementById("ketTrot")].forEach(Matematica.flashText);
  });
  $tmax.addEventListener("input", e => {
    tmax = parseFloat(e.target.value);
    if (t > tmax) { t = tmax; $t.value = t; }
    $t.max = tmax;
    renderAll();
  });
  $t.addEventListener("input", e => {
    t = parseFloat(e.target.value); renderAll();
    Matematica.flashAll(document.getElementById("matM"));
    [document.getElementById("ketExact"), document.getElementById("ketTrot")].forEach(Matematica.flashText);
  });

  Staffetta.renderHandoff(document.getElementById("handoff"), params.da,
    params.da === "vqe"
      ? `Lo stato in ingresso pu&ograve; essere quello del VQE (fidelity ${params.fid || "?"}) o l'esatto: lo sceglie dal menu qui sotto.`
      : "Punto di lavoro riportato dallo stadio precedente.");

  Matematica.renderStaticFormulas();

  renderAll();
})();
