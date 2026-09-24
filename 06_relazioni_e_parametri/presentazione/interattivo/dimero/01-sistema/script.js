/* script.js — 01-sistema */
(function () {
  "use strict";
  const params = Staffetta.readParams();
  let bJ = Staffetta.numOr(params, "bJ", 1.2);
  let DJ = Staffetta.numOr(params, "DJ", 0.2);

  const $bJ = document.getElementById("bJ"), $DJ = document.getElementById("DJ");
  const $bJv = document.getElementById("bJv"), $DJv = document.getElementById("DJv");
  $bJ.value = bJ; $DJ.value = DJ;

  const KETS = ["|00\u27E9", "|01\u27E9", "|10\u27E9", "|11\u27E9"];
  const BMAX = 4.0;
  let sweep = null; // {b:[...], E:[[4]...]}

  // maschere di dipendenza: quali celle di H cambiano per b, quali per D
  const maskB = Matematica.diffMask(Fisica.buildH1(1), Fisica.buildH1(0));
  const maskD = Matematica.nonzeroMask(Fisica.buildH2(1));

  function computeSweep() {
    const N = 161, b = [], E = [];
    for (let k = 0; k < N; k++) {
      const bv = BMAX * k / (N - 1);
      b.push(bv);
      E.push(Fisica.groundState(bv, DJ).E);
    }
    sweep = { b, E };
  }

  function forwardParams() { return { bJ: bJ.toFixed(3), DJ: DJ.toFixed(3) }; }
  function updateNav() {
    Staffetta.renderTopNav(document.getElementById("topnav"), "sistema", "../", forwardParams());
    document.getElementById("prosegui").href = Staffetta.buildUrl("../", "02-vqe", Object.assign(forwardParams(), { da: "sistema" }));
  }

  function drawSpettro() {
    const svg = document.getElementById("spettro");
    const series = [0, 1, 2, 3].map(lvl => ({
      x: sweep.b, y: sweep.b.map((_, k) => sweep.E[k][lvl]), color: "#8FA2B5", width: 1.2,
    }));
    const gsCurve = { x: sweep.b, y: sweep.b.map((_, k) => sweep.E[k][0]), color: "#14273A", width: 2.6 };
    const gs = Fisica.groundState(bJ, DJ);
    Componenti.LineChart(svg, {
      w: 700, h: 320, margin: { l: 54, r: 14, t: 10, b: 40 },
      xDomain: [0, BMAX], yDomain: [-8, 9],
      xTicks: [0, 1, 2, 3, 4], yTicks: [-8, -6, -4, -2, 0, 2, 4, 6, 8],
      xLabel: "B / J  (adimensionale)", yLabel: "E / J  (energia, in unit\u00e0 di J)",
      series: series.concat([gsCurve]),
      vlines: [{ x: 2, color: "#BDC9D7", width: 1.2, dash: "3 3" }],
      points: [{ x: bJ, y: gs.E[0], color: "#A8560C", r: 5.5 }],
    });
  }

  function render() {
    $bJv.textContent = bJ.toFixed(2);
    $DJv.textContent = DJ.toFixed(2);
    drawSpettro();
    const gs = Fisica.groundState(bJ, DJ);
    document.getElementById("rE0").textContent = gs.E[0].toFixed(4);
    document.getElementById("rGap").textContent = (gs.E[1] - gs.E[0]).toFixed(4);
    document.getElementById("rMz").textContent = gs.mz0.toFixed(4);

    Matematica.renderMatrix(document.getElementById("matH"), gs.H, null, KETS.map(k=>k.replace(/[|\u27E9]/g,"")), { decimals: 2 });
    Matematica.renderKet(document.getElementById("ketPsi0"), gs.psi0, gs.psi0.map(() => 0), KETS, "#0E7C86");

    const H2 = Fisica.buildH2(DJ);
    const comSz = Fisica.commutatorNorm(H2, Fisica.buildSz());
    const comS2 = Fisica.commutatorNorm(H2, Fisica.buildS2());
    document.getElementById("rComSz").textContent = comSz.toFixed(4);
    document.getElementById("rComS2").textContent = comS2.toFixed(4);
    const comM = Fisica.commutatorMatrix(H2, Fisica.buildSz());
    Matematica.renderMatrix(document.getElementById("matCom"), comM, null, KETS.map(k=>k.replace(/[|\u27E9]/g,"")), { decimals: 3 });

    const cc = document.getElementById("ccDM");
    if (DJ < 1e-6) {
      cc.innerHTML = "Con D/J = 0 il commutatore &egrave; esattamente nullo: la magnetizzazione &egrave; conservata, e a B/J = 2 il gap si chiude del tutto. Provi ad alzare lo slider D/J.";
    } else {
      cc.innerHTML = `Con D/J = ${DJ.toFixed(2)} il commutatore vale ${comSz.toFixed(4)}: diverso da zero, quindi la magnetizzazione non &egrave; pi&ugrave; conservata. Il gap a B/J = 2 resta finito (lo vede nel grafico sopra) invece di annullarsi.`;
    }

    Componenti.renderAmps(document.getElementById("amps"), gs.psi0, gs.psi0.map(() => 0), KETS, "#0E7C86");
    updateNav();
    return gs;
  }

  function flashForB() {
    Matematica.flashCells(document.getElementById("matH"), maskB);
    [document.getElementById("rE0"), document.getElementById("rGap"), document.getElementById("rMz")].forEach(Matematica.flashText);
    Matematica.flashText(document.getElementById("ketPsi0"));
  }
  function flashForD() {
    Matematica.flashCells(document.getElementById("matH"), maskD);
    Matematica.flashAll(document.getElementById("matCom"));
    [document.getElementById("rComSz"), document.getElementById("rComS2")].forEach(Matematica.flashText);
    Matematica.flashText(document.getElementById("ketPsi0"));
  }

  function onDJChange() { computeSweep(); render(); flashForD(); }

  $bJ.addEventListener("input", e => { bJ = parseFloat(e.target.value); render(); flashForB(); });
  $DJ.addEventListener("input", e => { DJ = parseFloat(e.target.value); onDJChange(); });

  // cassetto di ingresso (solo se si arriva da un'altra pagina con "da")
  Staffetta.renderHandoff(document.getElementById("handoff"), params.da,
    "Il punto di lavoro (B/J, D/J) &egrave; stato riportato da dove si trovava. Pu&ograve; modificarlo qui e proseguire di nuovo.");

  Matematica.renderStaticFormulas();

  computeSweep();
  render();
})();
