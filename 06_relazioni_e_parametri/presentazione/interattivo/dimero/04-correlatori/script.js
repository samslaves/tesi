/* script.js — 04-correlatori */
(function () {
  "use strict";
  const params = Staffetta.readParams();
  let bJ = Staffetta.numOr(params, "bJ", 0.35);
  let DJ = Staffetta.numOr(params, "DJ", 0.80);
  let evo = "esatto";
  let N = Math.round(Staffetta.numOr(params, "N", 40));
  let tmax = Staffetta.numOr(params, "tmax", 12.0);
  let stato = ["su", "esatto", "vqe"].includes(params.stato) ? params.stato : "esatto";
  let ansatz = params.ansatz && Fisica.ANSATZ_INFO[params.ansatz] ? params.ansatz : "pma3";
  let site1 = 2, comp1 = "x", site2 = 1, comp2 = "x";
  let ti = 40, stage = 0, playing = false, trail = [], playTimer = null;

  const $bJ = document.getElementById("bJ"), $DJ = document.getElementById("DJ");
  const $bJv = document.getElementById("bJv"), $DJv = document.getElementById("DJv");
  const $stato = document.getElementById("stato");
  const $evo = document.getElementById("evo"), $N = document.getElementById("N"), $Nv = document.getElementById("Nv");
  const $site1 = document.getElementById("site1"), $comp1 = document.getElementById("comp1");
  const $site2 = document.getElementById("site2"), $comp2 = document.getElementById("comp2");
  const $ts = document.getElementById("ts"), $tv = document.getElementById("tv"), $tmax = document.getElementById("tmax");
  $bJ.value = bJ; $DJ.value = DJ; $stato.value = stato; $N.value = N; $tmax.value = tmax;

  const KETS = ["|00\u27E9", "|01\u27E9", "|10\u27E9", "|11\u27E9"];
  const SIXLAB = ["1x", "1y", "1z", "2x", "2y", "2z"];
  const maskB = Matematica.diffMask(Fisica.buildH1(1), Fisica.buildH1(0));
  const maskD = Matematica.nonzeroMask(Fisica.buildH2(1));

  let TS = [], ReC = [], ImC = [];
  let psi0Cache = null; // evita di rilanciare l'ottimizzatore VQE ad ogni fotogramma

  function invalidatePsi0() { psi0Cache = null; }

  function getPsi0() {
    if (psi0Cache) return psi0Cache;
    if (stato === "vqe") {
      const res = Fisica.optimizeAnsatz(ansatz, bJ, DJ, { restarts: 6, iters: 220 });
      const gs = Fisica.groundState(bJ, DJ);
      psi0Cache = { vec: res.state.re.slice(), fidelity: Fisica.fidelityToVec(res.state, gs.psi0) };
    } else if (stato === "su") {
      psi0Cache = { vec: [1, 0, 0, 0], fidelity: null };
    } else {
      psi0Cache = { vec: Fisica.groundState(bJ, DJ).psi0.slice(), fidelity: 1.0 };
    }
    return psi0Cache;
  }
  function psi0Vec() { return getPsi0().vec; }

  function sigmaLabel(site, comp) { return `&sigma;<sub>${site}</sub><sup>${comp}</sup>`; }

  function forwardParams(extra) {
    return Object.assign({ bJ: bJ.toFixed(3), DJ: DJ.toFixed(3), N, tmax: tmax.toFixed(1), stato, ansatz }, extra || {});
  }
  function updateNav() { Staffetta.renderTopNav(document.getElementById("topnav"), "correlatori", "../", forwardParams()); }

  function updateNotaStato() {
    const el = document.getElementById("notaStato");
    const p = getPsi0();
    if (stato === "su") {
      el.innerHTML = "|&uarr;&uarr;&rang; non &egrave; il fondamentale: &egrave; comunque uno stato lecito su cui misurare C(t), ma i valori non coincidono con quelli \"a riposo\" mostrati altrove.";
    } else if (stato === "esatto") {
      el.innerHTML = "Fondamentale esatto: la scelta standard per un correlatore dinamico. Nota: il tempo t di questa pagina evolve lo stato <em>dentro</em> il circuito &mdash; non c'entra con l'eventuale istante scelto nello stadio 3.";
    } else {
      el.innerHTML = `Stato dal VQE (ansatz: ${Fisica.ANSATZ_INFO[ansatz].nome}), fidelity ${p.fidelity.toFixed(6)} rispetto al fondamentale esatto. Se la fidelity non &egrave; 1, C(t) qui misurato differisce leggermente da quello "vero".`;
    }
  }
  function evolve(tv, re, im) {
    return evo === "trotter" ? Fisica.trotterEvolve(bJ, DJ, tv, N, re, im) : Fisica.exactEvolve(bJ, DJ, tv, re, im);
  }
  function corrAt(tv) {
    return Fisica.correlator(bJ, DJ, tv, evo === "trotter" ? "trotter" : "esatto", N, site1, comp1, site2, comp2, psi0Vec());
  }

  // ------------------------------------------------------------- traccia C(t)
  function computeTraces() {
    const NT = 121;
    TS = []; ReC = []; ImC = [];
    for (let k = 0; k < NT; k++) {
      const tv = tmax * k / (NT - 1);
      TS.push(tv);
      const c = corrAt(tv);
      ReC.push(c.re); ImC.push(c.im);
    }
  }

  // -------------------------------------------------------------- stadi 0-4
  function branchesAt(tv) {
    const psi0 = psi0Vec();
    const psi0c = { re: psi0.slice(), im: psi0.map(() => 0) };
    const pert = Fisica.applyPauli(psi0c, site2, comp2);
    const evPsi0 = evolve(tv, psi0c.re, psi0c.im);
    const evPert = evolve(tv, pert.re, pert.im);
    const Afinal = Fisica.applyPauli(evPsi0, site1, comp1);
    return { psi0c, pert, evPsi0, evPert, Afinal };
  }

  function stageKet(b) {
    const s2b = sigmaLabel(site2, comp2), s1a = sigmaLabel(site1, comp1);
    switch (stage) {
      case 0: return `|0&rang;<sub>a</sub> &otimes; |&psi;&#8320;&rang;`;
      case 1: return `<span class="br0">|0&rang;<sub>a</sub>|&psi;&#8320;&rang;</span> + <span class="br1">|1&rang;<sub>a</sub>|&psi;&#8320;&rang;</span>  (&divide;&radic;2)`;
      case 2: return `<span class="br0">|0&rang;<sub>a</sub>|&psi;&#8320;&rang;</span> + <span class="br1">|1&rang;<sub>a</sub> ${s2b}|&psi;&#8320;&rang;</span>  (&divide;&radic;2)`;
      case 3: return `<span class="br0">|0&rang;<sub>a</sub> U(t)|&psi;&#8320;&rang;</span> + <span class="br1">|1&rang;<sub>a</sub> U(t)${s2b}|&psi;&#8320;&rang;</span>  (&divide;&radic;2)`;
      default: return `<span class="br0">|0&rang;<sub>a</sub>|A&rang;</span> + <span class="br1">|1&rang;<sub>a</sub>|B&rang;</span>  (&divide;&radic;2)`;
    }
  }
  function stageWhat() {
    const s2b = sigmaLabel(site2, comp2), s1a = sigmaLabel(site1, comp1);
    switch (stage) {
      case 0: return "Il registro porta lo stato fondamentale esatto. L'ancilla \u00e8 inerte in |0\u27e9: non rappresenta nessuno spin fisico, \u00e8 solo lo strumento che user\u00e0 l'interferenza.";
      case 1: return "L'Hadamard apre due rami coerenti, identici: al dimero non \u00e8 ancora successo nulla. Da qui in poi si possono far accadere cose diverse nei due rami.";
      case 2: return `Il controllo pieno applica ${s2b.replace(/<[^>]+>/g,"")} solo nel ramo |1\u27e9: \u00e8 la perturbazione al tempo 0. I due rami ora differiscono.`;
      case 3: return "U(t) agisce su entrambi i rami, senza controllo: l'evoluzione del dimero \u00e8 fisica e non dipende dall'ancilla.";
      default: return `L'anti-controllo applica ${s1a.replace(/<[^>]+>/g,"")} solo nel ramo |0\u27e9, dopo l'evoluzione. Ora \u27e8A|B\u27e9 \u00e8 esattamente C(t).`;
    }
  }
  function branchForStage(br) {
    switch (stage) {
      case 0: return { A: br.psi0c, B: null };
      case 1: return { A: br.psi0c, B: br.psi0c };
      case 2: return { A: br.psi0c, B: br.pert };
      case 3: return { A: br.evPsi0, B: br.evPert };
      default: return { A: br.Afinal, B: br.evPert };
    }
  }

  function wireForSite(site) { return site === 1 ? 2 : 1; } // wire 0=ancilla, 1=q0 (sito2), 2=q1 (sito1)
  function sigmaPlain(comp) { return "\u03c3^" + comp; }

  function renderStage() {
    const tv = tmax * ti / 120;
    const br = branchesAt(tv);
    const disp = branchForStage(br);
    document.getElementById("ket").innerHTML = stageKet();
    document.getElementById("what").textContent = stageWhat();
    Componenti.renderAmps(document.getElementById("ampsA"), disp.A ? disp.A.re : null, disp.A ? disp.A.im : null, KETS, "#0E7C86");
    Componenti.renderAmps(document.getElementById("ampsB"), disp.B ? disp.B.re : null, disp.B ? disp.B.im : null, KETS, "#A4306B", "ramo non ancora presente");
    [...document.querySelectorAll(".stagebtn")].forEach((btn, k) => btn.setAttribute("aria-selected", k === stage));

    Matematica.renderKet(document.getElementById("ketA"), br.Afinal.re, br.Afinal.im, KETS, "#0E7C86");
    Matematica.renderKet(document.getElementById("ketB"), br.evPert.re, br.evPert.im, KETS, "#A4306B");
  }

  // ---------------------------------------------- sezione 4: il circuito, porta per porta
  const GATI_PER_PERIODO_CORR = 11; // stessa decomposizione esatta usata in Dinamica
  let ccSteps = [], ccIdx = -1, ccPlayTimer = null;

  function computeCircuitoPortaPerPorta() {
    const tv = tmax * ti / 120;
    const psi0 = psi0Vec();
    const psi0c = { re: psi0.slice(), im: psi0.map(() => 0) };
    const pert = Fisica.applyPauli(psi0c, site2, comp2);
    const steps = [];

    steps.push({
      kind: "BOX", wire: 0, label: "H",
      desc: "Hadamard sull'ancilla: apre i due rami, ancora identici",
      A: { re: psi0c.re.slice(), im: psi0c.im.slice() }, B: { re: psi0c.re.slice(), im: psi0c.im.slice() },
    });
    steps.push({
      kind: "CTRL", control: 0, target: wireForSite(site2), open: false, targetLabel: comp2.toUpperCase(), showAsCnot: comp2 === "x",
      desc: `controlled-${sigmaPlain(comp2)} sul ramo |1&rang;: applica la perturbazione a t=0`,
      A: { re: psi0c.re.slice(), im: psi0c.im.slice() }, B: { re: pert.re.slice(), im: pert.im.slice() },
    });

    if (evo === "trotter") {
      const microA = Fisica.trotterMicroSteps(bJ, DJ, tv, N, psi0c.re, psi0c.im);
      const microB = Fisica.trotterMicroSteps(bJ, DJ, tv, N, pert.re, pert.im);
      for (let k = 0; k < microA.length; k++) {
        steps.push({
          kind: microA[k].kind,
          wire: microA[k].wire !== undefined ? microA[k].wire + 1 : undefined,
          wires: microA[k].wires ? microA[k].wires.map(w => w + 1) : undefined,
          label: microA[k].label,
          desc: "U(t): " + microA[k].desc,
          A: microA[k].state, B: microB[k].state,
        });
      }
    } else {
      const evA = Fisica.exactEvolve(bJ, DJ, tv, psi0c.re, psi0c.im);
      const evB = Fisica.exactEvolve(bJ, DJ, tv, pert.re, pert.im);
      steps.push({
        kind: "SPAN", wires: [1,2], label: "U(t) esatta",
        desc: "U(t) agisce su entrambi i rami, senza controllo (evoluzione esatta, non Trotter)",
        A: evA, B: evB,
      });
    }

    const lastState = steps[steps.length - 1];
    const Afinal = Fisica.applyPauli(lastState.A, site1, comp1);
    steps.push({
      kind: "CTRL", control: 0, target: wireForSite(site1), open: true, targetLabel: comp1.toUpperCase(), showAsCnot: comp1 === "x",
      desc: `anti-controlled-${sigmaPlain(comp1)} sul ramo |0&rang;: ora &lang;A|B&rang; = C(t)`,
      A: Afinal, B: { re: lastState.B.re.slice(), im: lastState.B.im.slice() },
    });
    return steps;
  }

  function renderCircuitoTemplate() {
    const template = [
      { kind: "BOX", wire: 0, label: "H" },
      { kind: "CTRL", control: 0, target: wireForSite(site2), open: false, targetLabel: comp2.toUpperCase(), showAsCnot: comp2 === "x" },
    ];
    if (evo === "trotter") {
      const oneUPeriod = ccSteps.slice(2, 2 + GATI_PER_PERIODO_CORR);
      oneUPeriod.forEach(s => template.push(s.kind === "BOX" ? { kind: "BOX", wire: s.wire, label: s.label } : { kind: "SPAN", wires: s.wires, label: s.label }));
    } else {
      template.push({ kind: "SPAN", wires: [1,2], label: "U(t)" });
    }
    template.push({ kind: "CTRL", control: 0, target: wireForSite(site1), open: true, targetLabel: comp1.toUpperCase(), showAsCnot: comp1 === "x" });

    let hi;
    if (ccIdx === -1) hi = undefined;
    else if (ccIdx === 0) hi = 0;
    else if (ccIdx === 1) hi = 1;
    else if (ccIdx === ccSteps.length - 1) hi = template.length - 1;
    else if (evo === "trotter") hi = 2 + ((ccIdx - 2) % GATI_PER_PERIODO_CORR);
    else hi = 2;

    Componenti.CircuitDiagram(document.getElementById("circuitoCorr"), template, { nWires: 3, wireLabels: ["a","q0","q1"], highlightIndex: hi });
    document.getElementById("notaCircuitoCorr").innerHTML = evo === "trotter"
      ? `Il blocco U(t) mostrato &egrave; un solo periodo di Trotter: si ripete N = ${N} volte. Dopo l'ultima porta, l'ancilla verrebbe richiusa con un'altra H e misurata.`
      : "Con evoluzione esatta, U(t) non ha una scomposizione elementare (non commuta a pezzi separabili): resta un unico blocco. Scelga Trotter in sezione 1 per espanderlo.";
  }

  function stopCcPlay() {
    if (ccPlayTimer) { clearTimeout(ccPlayTimer); ccPlayTimer = null; }
    document.getElementById("ccPlay").textContent = "Avvia";
  }

  function renderCcStep() {
    renderCircuitoTemplate();
    const st = ccIdx === -1
      ? { A: { re: psi0Vec(), im: psi0Vec().map(() => 0) }, B: null }
      : { A: ccSteps[ccIdx].A, B: ccSteps[ccIdx].B };
    Componenti.renderAmps(document.getElementById("ampsCircA"), st.A.re, st.A.im, KETS, "#0E7C86");
    Componenti.renderAmps(document.getElementById("ampsCircB"), st.B ? st.B.re : null, st.B ? st.B.im : null, KETS, "#A4306B", "ramo non ancora presente");
    Matematica.renderKet(document.getElementById("ketCircA"), st.A.re, st.A.im, KETS, "#0E7C86");
    if (st.B) Matematica.renderKet(document.getElementById("ketCircB"), st.B.re, st.B.im, KETS, "#A4306B");
    else document.getElementById("ketCircB").textContent = "\u2014";
    document.getElementById("ccPasso").textContent = `${ccIdx + 1} di ${ccSteps.length}`;
    document.getElementById("ccPorta").innerHTML = ccIdx === -1 ? "&mdash; (stato iniziale, un solo ramo)" : ccSteps[ccIdx].desc;
  }

  function computeCcCircuit() {
    ccSteps = computeCircuitoPortaPerPorta();
    ccIdx = -1;
    stopCcPlay();
    renderCcStep();
  }

  document.getElementById("ccInizio").addEventListener("click", () => { stopCcPlay(); ccIdx = -1; renderCcStep(); });
  document.getElementById("ccIndietro").addEventListener("click", () => { stopCcPlay(); ccIdx = Math.max(-1, ccIdx - 1); renderCcStep(); });
  document.getElementById("ccAvanti").addEventListener("click", () => { stopCcPlay(); ccIdx = Math.min(ccSteps.length - 1, ccIdx + 1); renderCcStep(); });
  document.getElementById("ccFine").addEventListener("click", () => { stopCcPlay(); ccIdx = ccSteps.length - 1; renderCcStep(); });
  document.getElementById("ccPlay").addEventListener("click", () => {
    if (ccPlayTimer) { stopCcPlay(); return; }
    if (ccIdx >= ccSteps.length - 1) ccIdx = -1;
    document.getElementById("ccPlay").textContent = "Ferma";
    const delay = Math.max(20, Math.min(700, 6000 / ccSteps.length));
    const tick = () => {
      ccIdx++;
      renderCcStep();
      if (ccIdx < ccSteps.length - 1) ccPlayTimer = setTimeout(tick, delay);
      else stopCcPlay();
    };
    tick();
  });

  const STAGE_NAMES = ["preparazione", "H sull'ancilla", "controlled-W", "evoluzione U(t)", "anti-controlled-V"];
  document.getElementById("stagebar").innerHTML = STAGE_NAMES.map((nome, k) =>
    `<button class="stagebtn" role="tab" aria-selected="${k===0}" data-k="${k}">${k} &middot; ${nome}</button>`).join("");
  document.getElementById("stagebar").addEventListener("click", e => {
    const b = e.target.closest(".stagebtn"); if (!b) return;
    stage = +b.dataset.k; renderStage();
  });

  // ------------------------------------------------------------------ dial
  const CX = 210, CY = 210, RAD = 150;
  function renderDial() {
    const re = ReC[ti], im = ImC[ti];
    const x = CX + re * RAD, y = CY - im * RAD;
    const ticks = [...Array(8)].map((_, k) => { const a = k * Math.PI / 4;
      return `<line x1="${CX+Math.cos(a)*RAD}" y1="${CY-Math.sin(a)*RAD}" x2="${CX+Math.cos(a)*(RAD-8)}" y2="${CY-Math.sin(a)*(RAD-8)}" stroke="#BDC9D7" stroke-width="1"/>`; }).join("");
    const path = trail.length > 1 ? `<polyline points="${trail.map(p=>`${(CX+p[0]*RAD).toFixed(1)},${(CY-p[1]*RAD).toFixed(1)}`).join(" ")}" fill="none" stroke="#A8560C" stroke-width="1.2" opacity="0.42"/>` : "";
    document.getElementById("dial").innerHTML = `
      <circle cx="${CX}" cy="${CY}" r="${RAD}" fill="#fff" stroke="#8FA2B5" stroke-width="1.4"/>
      <circle cx="${CX}" cy="${CY}" r="${RAD*0.5}" fill="none" stroke="#D5DEE8" stroke-width="1" stroke-dasharray="3 4"/>
      ${ticks}
      <line x1="${CX-RAD-14}" y1="${CY}" x2="${CX+RAD+14}" y2="${CY}" stroke="#5C7288" stroke-width="1"/>
      <line x1="${CX}" y1="${CY-RAD-14}" x2="${CX}" y2="${CY+RAD+14}" stroke="#5C7288" stroke-width="1"/>
      <text x="${CX+RAD+2}" y="${CY-9}" font-family="ui-monospace,monospace" font-size="11" fill="#0E7C86">Re C (adim.)</text>
      <text x="${CX+7}" y="${CY-RAD-4}" font-family="ui-monospace,monospace" font-size="11" fill="#A4306B">Im C (adim.)</text>
      ${path}
      <line x1="${x.toFixed(1)}" y1="${y.toFixed(1)}" x2="${x.toFixed(1)}" y2="${CY}" stroke="#0E7C86" stroke-width="1" stroke-dasharray="3 3"/>
      <line x1="${x.toFixed(1)}" y1="${y.toFixed(1)}" x2="${CX}" y2="${y.toFixed(1)}" stroke="#A4306B" stroke-width="1" stroke-dasharray="3 3"/>
      <line x1="${CX}" y1="${CY}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#14273A" stroke-width="2.4"/>
      <circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="5" fill="#A8560C" stroke="#fff" stroke-width="1.4"/>`;
    document.getElementById("vre").textContent = (re>=0?"+":"")+re.toFixed(4);
    document.getElementById("vim").textContent = (im>=0?"+":"")+im.toFixed(4);
    document.getElementById("vmod").textContent = Math.hypot(re,im).toFixed(4);
  }

  function renderTraces() {
    const W=980,H=260,L=64,R=16,T=14,B=46, pw=W-L-R, ph=H-T-B;
    const X=i=>L+pw*i/(TS.length-1), Y=v=>T+ph*(1-(v+1)/2);
    const line=(arr,c)=>`<polyline points="${arr.map((v,i)=>`${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join(" ")}" fill="none" stroke="${c}" stroke-width="1.7"/>`;
    const grid=[-1,-0.5,0,0.5,1].map(v=>`<line x1="${L}" y1="${Y(v)}" x2="${W-R}" y2="${Y(v)}" stroke="${v===0?'#8FA2B5':'#D5DEE8'}" stroke-width="1"/><text x="${L-8}" y="${Y(v)+4}" text-anchor="end" font-family="ui-monospace,monospace" font-size="10" fill="#5C7288">${v}</text>`).join("");
    const NXT = 6;
    const xticks = Array.from({length:NXT}, (_,k)=>{
      const idx = Math.round(k*(TS.length-1)/(NXT-1));
      return `<text x="${X(idx).toFixed(1)}" y="${H-B+16}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="10" fill="#5C7288">${TS[idx].toFixed(1)}</text>`;
    }).join("");
    const xLabel = `<text x="${L+pw/2}" y="${H-4}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="11" fill="#5C7288">t  (unit\u00e0 di 1/J)</text>`;
    const yLabelX = 14, yLabelY = T+ph/2;
    const yLabel = `<text x="${yLabelX}" y="${yLabelY}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="11" fill="#5C7288" transform="rotate(-90 ${yLabelX} ${yLabelY})">C(t)  (adimensionale)</text>`;
    document.getElementById("traces").setAttribute("viewBox", `0 0 ${W} ${H}`);
    document.getElementById("traces").innerHTML = `${grid}${xticks}${xLabel}${yLabel}
      ${line(ReC,"#0E7C86")}${line(ImC,"#A4306B")}
      <line x1="${X(ti).toFixed(1)}" y1="${T}" x2="${X(ti).toFixed(1)}" y2="${T+ph}" stroke="#A8560C" stroke-width="1.4"/>
      <circle cx="${X(ti).toFixed(1)}" cy="${Y(ReC[ti]).toFixed(1)}" r="4" fill="#0E7C86" stroke="#fff" stroke-width="1.3"/>
      <circle cx="${X(ti).toFixed(1)}" cy="${Y(ImC[ti]).toFixed(1)}" r="4" fill="#A4306B" stroke="#fff" stroke-width="1.3"/>`;
  }

  // ------------------------------------------------------ heatmap 36 combinazioni
  function computeHeat36() {
    const M = [];
    const psi0 = psi0Vec();
    const tv = tmax * ti / 120;
    const mode = evo === "trotter" ? "trotter" : "esatto";
    for (let r = 0; r < 6; r++) {
      const row = [];
      const [si, al] = [SIXLAB[r][0], SIXLAB[r][1]];
      for (let c = 0; c < 6; c++) {
        const [sj, be] = [SIXLAB[c][0], SIXLAB[c][1]];
        const cc = Fisica.correlator(bJ, DJ, tv, mode, N, si, al, sj, be, psi0);
        row.push(Math.hypot(cc.re, cc.im));
      }
      M.push(row);
    }
    return M;
  }
  function renderHeat36() {
    const M = computeHeat36();
    Matematica.renderMatrix(document.getElementById("heat36"), M, null, SIXLAB, { decimals: 2 });
  }

  document.getElementById("heat36").addEventListener("click", e => {
    const td = e.target.closest("td.mcell"); if (!td) return;
    const [r, c] = td.dataset.cell.split("_").map(Number);
    site1 = Number(SIXLAB[r][0]); comp1 = SIXLAB[r][1];
    site2 = Number(SIXLAB[c][0]); comp2 = SIXLAB[c][1];
    $site1.value = site1; $comp1.value = comp1; $site2.value = site2; $comp2.value = comp2;
    heavyRefresh();
  });

  // -------------------------------------------------------------- matH panel
  function renderMatH() {
    const gs = Fisica.groundState(bJ, DJ);
    Matematica.renderMatrix(document.getElementById("matH"), gs.H, null, ["00","01","10","11"], { decimals: 2 });
  }

  // ---------------------------------------------------------------- refresh
  let heat36Timer = null, ccTimer = null;
  function scheduleHeavyish() {
    clearTimeout(heat36Timer); heat36Timer = setTimeout(renderHeat36, 90);
    clearTimeout(ccTimer); ccTimer = setTimeout(computeCcCircuit, 90);
  }
  function lightRefresh() {
    $bJv.textContent = bJ.toFixed(2); $DJv.textContent = DJ.toFixed(2); $Nv.textContent = N;
    $tv.textContent = (tmax * ti / 120).toFixed(2);
    renderStage(); renderDial(); renderTraces(); updateNav();
    scheduleHeavyish();
  }
  function heavyRefresh() {
    computeTraces(); renderMatH(); lightRefresh();
    clearTimeout(heat36Timer); renderHeat36();
    clearTimeout(ccTimer); computeCcCircuit();
  }

  $bJ.addEventListener("input", e => { bJ = parseFloat(e.target.value); invalidatePsi0(); computeTraces(); renderMatH(); lightRefresh(); updateNotaStato();
    Matematica.flashCells(document.getElementById("matH"), maskB); });
  $DJ.addEventListener("input", e => { DJ = parseFloat(e.target.value); invalidatePsi0(); computeTraces(); renderMatH(); lightRefresh(); updateNotaStato();
    Matematica.flashCells(document.getElementById("matH"), maskD); });
  $stato.addEventListener("change", e => { stato = e.target.value; invalidatePsi0(); updateNotaStato(); heavyRefresh(); });
  $evo.addEventListener("change", e => { evo = e.target.value; document.getElementById("ctlN").style.display = evo==="trotter"?"":"none"; heavyRefresh(); });
  $N.addEventListener("change", e => { N = parseInt(e.target.value, 10); heavyRefresh(); });
  [$site1,$comp1,$site2,$comp2].forEach(sel => sel.addEventListener("change", () => {
    site1=Number($site1.value); comp1=$comp1.value; site2=Number($site2.value); comp2=$comp2.value;
    heavyRefresh();
  }));
  $tmax.addEventListener("input", e => { document.getElementById("tmaxv").textContent = parseFloat(e.target.value).toFixed(1); });
  $tmax.addEventListener("change", e => { tmax = parseFloat(e.target.value); heavyRefresh(); });
  $ts.addEventListener("input", e => { ti=+e.target.value;
    trail.push([ReC[ti],ImC[ti]]); if(trail.length>260) trail.shift(); lightRefresh(); });
  document.getElementById("clear").addEventListener("click", () => { trail=[]; renderDial(); });
  document.getElementById("play").addEventListener("click", () => {
    playing = !playing; document.getElementById("play").textContent = playing?"Ferma":"Avvia";
    if (playing) { const step=()=>{ if(!playing) return; ti=(ti+1)%121; $ts.value=ti;
        trail.push([ReC[ti],ImC[ti]]); if(trail.length>260) trail.shift(); lightRefresh();
        playTimer=setTimeout(step,55); }; step(); }
    else clearTimeout(playTimer);
  });

  $evo.value = evo; document.getElementById("ctlN").style.display = "none";
  Staffetta.renderHandoff(document.getElementById("handoff"), params.da,
    "Il punto di lavoro e la scelta dello stato (esatto o VQE) arrivano dallo stadio precedente, gi\u00e0 impostati qui sotto. Pu\u00f2 cambiarli liberamente.");

  $N.value = N; $tmax.value = tmax;
  document.getElementById("tmaxv").textContent = tmax.toFixed(1);
  $bJv.textContent = bJ.toFixed(2); $DJv.textContent = DJ.toFixed(2);
  updateNotaStato();
  heavyRefresh();
  Matematica.renderStaticFormulas();
})();
