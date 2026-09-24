/*
 * fisica.js — motore fisico condiviso dalle 4 pagine del progetto.
 *
 * Modello:  H = J(X1X2+Y1Y2+Z1Z2) + b(Z1+Z2) + D(X1Z2-Z1X2)      [J=1 sempre]
 * Convenzione qubit: indice di base = 2*q1+q0 (little-endian, come Qiskit).
 *   q0 = sito 2 (label a destra), q1 = sito 1 (label a sinistra).
 * Tutte le matrici a 2 qubit sono hard-codate da un calcolo Qiskit di riferimento
 * (SparsePauliOp(...).to_matrix()), non ricostruite a mano: garantisce che i numeri
 * prodotti qui coincidano con quelli dei documenti .tex del progetto.
 *
 * Nessuna dipendenza esterna. Funziona sia nel browser (window.Fisica) sia in
 * Node (module.exports) per i test numerici di verifica.
 */
(function (global) {
  "use strict";

  // ---------------------------------------------------------------- costanti
  // Operatori a due qubit (tutti reali) sulla base {|00>,|01>,|10>,|11>}.
  const M_XX = [[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0]];
  const M_YY = [[0,0,0,-1],[0,0,1,0],[0,1,0,0],[-1,0,0,0]];
  const M_ZZ = [[1,0,0,0],[0,-1,0,0],[0,0,-1,0],[0,0,0,1]];
  const M_ZI = [[1,0,0,0],[0,1,0,0],[0,0,-1,0],[0,0,0,-1]];   // Z sul sito 1
  const M_IZ = [[1,0,0,0],[0,-1,0,0],[0,0,1,0],[0,0,0,-1]];   // Z sul sito 2
  const M_XZ = [[0,0,1,0],[0,0,0,-1],[1,0,0,0],[0,-1,0,0]];
  const M_ZX = [[0,1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,-1,0]];

  // Operatori di singolo sito (per i correlatori). X,Z reali; Y puramente immaginario.
  const M_XI_re = [[0,0,1,0],[0,0,0,1],[1,0,0,0],[0,1,0,0]];   // X sito 1
  const M_IX_re = [[0,1,0,0],[1,0,0,0],[0,0,0,1],[0,0,1,0]];   // X sito 2
  const M_YI_im = [[0,0,-1,0],[0,0,0,-1],[1,0,0,0],[0,1,0,0]]; // Y sito 1 (Im)
  const M_IY_im = [[0,-1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,1,0]]; // Y sito 2 (Im)
  const M_ZI_re = M_ZI, M_IZ_re = M_IZ;

  const SITE_OP = {
    "1x": { re: M_XI_re, im: zeros4() },
    "1y": { re: zeros4(), im: M_YI_im },
    "1z": { re: M_ZI_re, im: zeros4() },
    "2x": { re: M_IX_re, im: zeros4() },
    "2y": { re: zeros4(), im: M_IY_im },
    "2z": { re: M_IZ_re, im: zeros4() },
  };

  function zeros4() { return [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]; }
  function ident4() { return [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]; }
  function addM(A, B, cB) {
    const R = zeros4();
    for (let i=0;i<4;i++) for (let j=0;j<4;j++) R[i][j] = A[i][j] + (cB===undefined?B[i][j]:cB*B[i][j]);
    return R;
  }
  function scaleM(A, c) {
    const R = zeros4();
    for (let i=0;i<4;i++) for (let j=0;j<4;j++) R[i][j] = c*A[i][j];
    return R;
  }

  // ------------------------------------------------------- Hamiltoniana (J=1)
  function buildH1(bJ) {
    // scambio isotropo + campo (reale, simmetrica)
    let H = scaleM(M_XX,1);
    H = addM(H, M_YY); H = addM(H, M_ZZ);
    H = addM(H, M_ZI, bJ); H = addM(H, M_IZ, bJ);
    return H;
  }
  function buildH2(DJ) {
    // termine DM (reale, simmetrica): D*(XZ - ZX)
    return addM(scaleM(M_XZ, DJ), scaleM(M_ZX, DJ), -1);
  }
  function buildH(bJ, DJ) {
    return addM(buildH1(bJ), buildH2(DJ));
  }

  // ------------------------------------------------- diagonalizzazione (Jacobi)
  // Autovalori/autovettori di una matrice reale simmetrica 4x4, esatti a
  // precisione macchina in poche decine di rotazioni di Jacobi.
  function jacobiEigen(Ain, maxSweeps, tol) {
    maxSweeps = maxSweeps || 100; tol = tol === undefined ? 1e-14 : tol;
    const n = 4;
    const A = Ain.map(r => r.slice());
    let V = ident4();
    for (let sweep = 0; sweep < maxSweeps; sweep++) {
      let off = 0;
      for (let p=0;p<n;p++) for (let q=p+1;q<n;q++) off += A[p][q]*A[p][q];
      if (off < tol) break;
      for (let p=0;p<n;p++) {
        for (let q=p+1;q<n;q++) {
          if (Math.abs(A[p][q]) < 1e-300) continue;
          const theta = (A[q][q]-A[p][p]) / (2*A[p][q]);
          const sign = theta >= 0 ? 1 : -1;
          const t = sign / (Math.abs(theta) + Math.sqrt(theta*theta+1));
          const c = 1/Math.sqrt(t*t+1), s = t*c;
          const app=A[p][p], aqq=A[q][q], apq=A[p][q];
          A[p][p] = c*c*app - 2*s*c*apq + s*s*aqq;
          A[q][q] = s*s*app + 2*s*c*apq + c*c*aqq;
          A[p][q] = 0; A[q][p] = 0;
          for (let i=0;i<n;i++) {
            if (i!==p && i!==q) {
              const aip=A[i][p], aiq=A[i][q];
              A[i][p]=c*aip - s*aiq; A[p][i]=A[i][p];
              A[i][q]=s*aip + c*aiq; A[q][i]=A[i][q];
            }
          }
          for (let i=0;i<n;i++) {
            const vip=V[i][p], viq=V[i][q];
            V[i][p] = c*vip - s*viq;
            V[i][q] = s*vip + c*viq;
          }
        }
      }
    }
    const values = [0,1,2,3].map(i => A[i][i]);
    const order = [0,1,2,3].sort((a,b) => values[a]-values[b]);
    const sortedValues = order.map(i => values[i]);
    const sortedV = [0,1,2,3].map(row => order.map(col => V[row][col]));
    // convenzione di segno: la componente di modulo massimo dell'autovettore e' positiva
    for (let col=0; col<4; col++) {
      let best=0, bi=0;
      for (let row=0; row<4; row++) if (Math.abs(sortedV[row][col])>best){best=Math.abs(sortedV[row][col]); bi=row;}
      if (sortedV[bi][col] < 0) for (let row=0; row<4; row++) sortedV[row][col] *= -1;
    }
    return { values: sortedValues, vectors: sortedV };
  }

  function groundState(bJ, DJ) {
    const H = buildH(bJ, DJ);
    const eig = jacobiEigen(H);
    const psi0 = eig.vectors.map(row => row[0]);
    const Mz = addM(scaleM(M_ZI,0.5), scaleM(M_IZ,0.5));
    const mz0 = bilinearReal(Mz, psi0, psi0);
    return { H, E: eig.values, V: eig.vectors, psi0, mz0 };
  }

  function bilinearReal(Mre, vRe, vIm) {
    // <v|M|v> per M reale, v complesso; ritorna la parte reale.
    vIm = vIm || vRe.map(()=>0);
    let re = 0;
    for (let i=0;i<4;i++) {
      let sRe=0, sIm=0;
      for (let j=0;j<4;j++){ sRe += Mre[i][j]*vRe[j]; sIm += Mre[i][j]*vIm[j]; }
      re += vRe[i]*sRe + vIm[i]*sIm;
    }
    return re;
  }

  // ---------------------------------------------------- esponenziale di H reale
  // exp(-i H t) per H reale simmetrica, via decomposizione spettrale.
  function expOfSymH(Hre, t) {
    const eig = jacobiEigen(Hre);
    const re = zeros4(), im = zeros4();
    for (let j=0;j<4;j++) for (let k=0;k<4;k++) {
      let sre=0, sim=0;
      for (let n=0;n<4;n++) {
        const vj = eig.vectors[j][n], vk = eig.vectors[k][n];
        const ang = -eig.values[n]*t;
        sre += vj*vk*Math.cos(ang);
        sim += vj*vk*Math.sin(ang);
      }
      re[j][k]=sre; im[j][k]=sim;
    }
    return { re, im };
  }

  // ---------------------------------------------------- algebra complessa 4x4
  function matMulC(A, B) {
    const re = zeros4(), im = zeros4();
    for (let i=0;i<4;i++) for (let j=0;j<4;j++) {
      let sre=0, sim=0;
      for (let k=0;k<4;k++) {
        sre += A.re[i][k]*B.re[k][j] - A.im[i][k]*B.im[k][j];
        sim += A.re[i][k]*B.im[k][j] + A.im[i][k]*B.re[k][j];
      }
      re[i][j]=sre; im[i][j]=sim;
    }
    return { re, im };
  }
  function matVecC(A, vRe, vIm) {
    vIm = vIm || vRe.map(()=>0);
    const re=[0,0,0,0], im=[0,0,0,0];
    for (let i=0;i<4;i++) {
      let sre=0, sim=0;
      for (let j=0;j<4;j++) {
        sre += A.re[i][j]*vRe[j] - A.im[i][j]*vIm[j];
        sim += A.re[i][j]*vIm[j] + A.im[i][j]*vRe[j];
      }
      re[i]=sre; im[i]=sim;
    }
    return { re, im };
  }
  function vecDagVec(aRe, aIm, bRe, bIm) {
    // <a|b> complesso
    aIm = aIm || aRe.map(()=>0); bIm = bIm || bRe.map(()=>0);
    let re=0, im=0;
    for (let i=0;i<4;i++) {
      re += aRe[i]*bRe[i] + aIm[i]*bIm[i];
      im += aRe[i]*bIm[i] - aIm[i]*bRe[i];
    }
    return { re, im };
  }

  // ---------------------------------------------------------------- Trotter
  function trotterStepMatrix(bJ, DJ, tau) {
    const U1 = expOfSymH(buildH1(bJ), tau);
    const U2 = expOfSymH(buildH2(DJ), tau);
    return matMulC(U2, U1); // (e^{-iH2 tau} e^{-iH1 tau})
  }
  function trotterEvolve(bJ, DJ, t, N, psiRe, psiIm) {
    psiIm = psiIm || psiRe.map(()=>0);
    if (N <= 0) return { re: psiRe.slice(), im: psiIm.slice() };
    const tau = t / N;
    const M = trotterStepMatrix(bJ, DJ, tau);
    let re = psiRe.slice(), im = psiIm.slice();
    for (let k=0;k<N;k++) {
      const out = matVecC(M, re, im);
      re = out.re; im = out.im;
    }
    return { re, im };
  }
  function exactEvolve(bJ, DJ, t, psiRe, psiIm) {
    const U = expOfSymH(buildH(bJ, DJ), t);
    return matVecC(U, psiRe, psiIm || psiRe.map(()=>0));
  }

  // Il circuito di Trotter, un blocco alla volta: applica U1=e^{-iH1 tau}, poi
  // U2=e^{-iH2 tau}, ripetuto N volte. Riusa esattamente trotterStepMatrix'
  // componenti (nessuna nuova fisica), solo registrando lo stato ad ogni blocco
  // invece di restituire solo il risultato finale.
  function trotterSteps(bJ, DJ, t, N, psiRe, psiIm) {
    psiIm = psiIm || psiRe.map(()=>0);
    const tau = t / N;
    const U1 = expOfSymH(buildH1(bJ), tau);
    const U2 = expOfSymH(buildH2(DJ), tau);
    let re = psiRe.slice(), im = psiIm.slice();
    const steps = [];
    for (let k = 0; k < N; k++) {
      let o = matVecC(U1, re, im); re = o.re; im = o.im;
      steps.push({ kind: "SPAN", wires: [0,1], label: "U\u2081(\u03c4)", period: k, half: 0,
        desc: `periodo ${k+1} di ${N} \u2014 applica U\u2081(\u03c4) = e^{-iH\u2081\u03c4}`,
        state: { re: re.slice(), im: im.slice() } });
      o = matVecC(U2, re, im); re = o.re; im = o.im;
      steps.push({ kind: "SPAN", wires: [0,1], label: "U\u2082(\u03c4)", period: k, half: 1,
        desc: `periodo ${k+1} di ${N} \u2014 applica U\u2082(\u03c4) = e^{-iH\u2082\u03c4}`,
        state: { re: re.slice(), im: im.slice() } });
    }
    return steps;
  }

  // -------------------------------------------------- U1, U2 in porte elementari
  // Decomposizione ESATTA (verificata numericamente, non un'approssimazione in
  // piu'): scambio isotropo e campo commutano fra loro (norma del commutatore
  // nulla), quindi U1 si fattorizza in RZ+RXX+RYY+RZZ senza errore aggiuntivo.
  // Per U2, X1Z2 e Z1X2 commutano anch'essi: si fattorizza coniugando due RZZ
  // con Hadamard (H manda X in Z sul qubit su cui agisce).
  function embedSingleQubitGate4(qubit, gRe, gIm) {
    gIm = gIm || [[0,0],[0,0]];
    const re = zeros4(), im = zeros4();
    const mask = 1 << qubit;
    for (let idx0 = 0; idx0 < 4; idx0++) {
      if (((idx0 >> qubit) & 1) !== 0) continue;
      const idx1 = idx0 | mask;
      re[idx0][idx0] = gRe[0][0]; im[idx0][idx0] = gIm[0][0];
      re[idx0][idx1] = gRe[0][1]; im[idx0][idx1] = gIm[0][1];
      re[idx1][idx0] = gRe[1][0]; im[idx1][idx0] = gIm[1][0];
      re[idx1][idx1] = gRe[1][1]; im[idx1][idx1] = gIm[1][1];
    }
    return { re, im };
  }
  function gateRZ4(qubit, phi) {
    const c = Math.cos(phi / 2), s = Math.sin(phi / 2);
    return embedSingleQubitGate4(qubit, [[c, 0], [0, c]], [[-s, 0], [0, s]]);
  }
  function gateH4(qubit) { return embedSingleQubitGate4(qubit, GATE_H); }

  function trotterMicroSteps(bJ, DJ, t, N, psiRe, psiIm) {
    psiIm = psiIm || psiRe.map(()=>0);
    const tau = t / N;
    let re = psiRe.slice(), im = psiIm.slice();
    const steps = [];
    function apply(gate4, kind, wires, label, desc) {
      const out = matVecC(gate4, re, im);
      re = out.re; im = out.im;
      const rec = kind === "BOX" ? { kind: "BOX", wire: wires, label } : { kind: "SPAN", wires, label };
      rec.desc = desc; rec.state = { re: re.slice(), im: im.slice() };
      steps.push(rec);
    }
    for (let k = 0; k < N; k++) {
      // --- U1(tau) = RZ(2 b tau) su q0 e q1, poi RXX, RYY, RZZ (2 J tau), J=1
      apply(gateRZ4(0, 2*bJ*tau), "BOX", 0, `Rz(${(2*bJ*tau).toFixed(3)})`, `periodo ${k+1} di ${N} \u2014 Rz del campo sul qubit 0`);
      apply(gateRZ4(1, 2*bJ*tau), "BOX", 1, `Rz(${(2*bJ*tau).toFixed(3)})`, `periodo ${k+1} di ${N} \u2014 Rz del campo sul qubit 1`);
      apply(expOfSymH(scaleM(M_XX,1), tau), "SPAN", [0,1], `Rxx(${(2*tau).toFixed(3)})`, `periodo ${k+1} di ${N} \u2014 Rxx dello scambio isotropo`);
      apply(expOfSymH(scaleM(M_YY,1), tau), "SPAN", [0,1], `Ryy(${(2*tau).toFixed(3)})`, `periodo ${k+1} di ${N} \u2014 Ryy dello scambio isotropo`);
      apply(expOfSymH(scaleM(M_ZZ,1), tau), "SPAN", [0,1], `Rzz(${(2*tau).toFixed(3)})`, `periodo ${k+1} di ${N} \u2014 Rzz dello scambio isotropo (chiude U\u2081)`);
      // --- U2(tau) = H_q1 RZZ(2 D tau) H_q1  ·  H_q0 RZZ(-2 D tau) H_q0
      apply(gateH4(1), "BOX", 1, "H", `periodo ${k+1} di ${N} \u2014 apre la coniugazione per X\u2081Z\u2082 (qubit 1)`);
      apply(expOfSymH(scaleM(M_ZZ,DJ), tau), "SPAN", [0,1], `Rzz(${(2*DJ*tau).toFixed(3)})`, `periodo ${k+1} di ${N} \u2014 Rzz al posto di X\u2081Z\u2082, nella base ruotata`);
      apply(gateH4(1), "BOX", 1, "H", `periodo ${k+1} di ${N} \u2014 richiude la coniugazione sul qubit 1`);
      apply(gateH4(0), "BOX", 0, "H", `periodo ${k+1} di ${N} \u2014 apre la coniugazione per Z\u2081X\u2082 (qubit 0)`);
      apply(expOfSymH(scaleM(M_ZZ,-DJ), tau), "SPAN", [0,1], `Rzz(${(-2*DJ*tau).toFixed(3)})`, `periodo ${k+1} di ${N} \u2014 Rzz al posto di Z\u2081X\u2082, nella base ruotata (chiude U\u2082)`);
      apply(gateH4(0), "BOX", 0, "H", `periodo ${k+1} di ${N} \u2014 richiude la coniugazione sul qubit 0`);
    }
    return steps;
  }

  // ---------------------------------------------- porte quantistiche (ansatz)
  // Stato = {re:[4], im:[4]}; qubit in {0,1}; indice base = 2*q1+q0.
  function state00() { return { re: [1,0,0,0], im: [0,0,0,0] }; }
  function applyGate1(st, g, qubit) {
    // g = [[re00,re01],[re10,re11]] reale (tutte le porte dell'ansatz lo sono)
    const re = st.re.slice(), im = st.im.slice();
    const mask = 1 << qubit;
    for (let idx0=0; idx0<4; idx0++) {
      if (((idx0 >> qubit) & 1) !== 0) continue;
      const idx1 = idx0 | mask;
      const a0re=st.re[idx0], a0im=st.im[idx0], a1re=st.re[idx1], a1im=st.im[idx1];
      re[idx0] = g[0][0]*a0re + g[0][1]*a1re;
      im[idx0] = g[0][0]*a0im + g[0][1]*a1im;
      re[idx1] = g[1][0]*a0re + g[1][1]*a1re;
      im[idx1] = g[1][0]*a0im + g[1][1]*a1im;
    }
    return { re, im };
  }
  const GATE_X = [[0,1],[1,0]];
  const GATE_H = [[Math.SQRT1_2, Math.SQRT1_2],[Math.SQRT1_2, -Math.SQRT1_2]];
  function gateRY(theta) { const c=Math.cos(theta/2), s=Math.sin(theta/2); return [[c,-s],[s,c]]; }
  function applyX(st,q){ return applyGate1(st, GATE_X, q); }
  function applyH(st,q){ return applyGate1(st, GATE_H, q); }
  function applyRY(st,theta,q){ return applyGate1(st, gateRY(theta), q); }
  function applyCZ(st) {
    // amplitude nell'indice 3 (=|11>, entrambi i bit a 1) cambia segno
    const re=st.re.slice(), im=st.im.slice();
    re[3]*=-1; im[3]*=-1;
    return { re, im };
  }
  function applyCX(st, control, target) {
    const re=st.re.slice(), im=st.im.slice();
    for (let idx=0; idx<4; idx++) {
      if (((idx>>control)&1)===1) {
        const flipped = idx ^ (1<<target);
        if (flipped > idx) {
          [re[idx], re[flipped]] = [re[flipped], re[idx]];
          [im[idx], im[flipped]] = [im[flipped], im[idx]];
        }
      }
    }
    return { re, im };
  }
  function rbsBlock(st, phi) {
    st = applyH(st,0); st = applyH(st,1); st = applyCZ(st);
    st = applyRY(st, phi, 0); st = applyRY(st, -phi, 1);
    st = applyCZ(st); st = applyH(st,0); st = applyH(st,1);
    return st;
  }

  // ---------------------------------------------------------- ansatz completi
  const ANSATZ_INFO = {
    ha:      { nome: "Generico (hardware-efficient)", nparam: 6 },
    pma1:    { nome: "PMA base (1 par.)",              nparam: 1 },
    pma3:    { nome: "PMA esteso (3 par.)",             nparam: 3 },
  };

  function ansatzState(type, params, bJ) {
    let st = state00();
    if (type === "ha") {
      // R0 - CZ - R1 - CZ - R2   (Ry(p0) su q0, Ry(p1) su q1, poi CZ, ecc.)
      st = applyRY(st, params[0], 0); st = applyRY(st, params[1], 1);
      st = applyCZ(st);
      st = applyRY(st, params[2], 0); st = applyRY(st, params[3], 1);
      st = applyCZ(st);
      st = applyRY(st, params[4], 0); st = applyRY(st, params[5], 1);
      return st;
    }
    if (type === "pma1") {
      // ansatz "alla Crippa": stato iniziale scelto in base al settore + W(theta)
      if (bJ < 2.0) {
        st = applyX(st,0); st = applyH(st,0); st = applyCX(st,0,1); st = applyX(st,0); // singoletto
      } else {
        st = applyX(st,0); st = applyX(st,1); // |11>
      }
      st = applyCX(st,0,1); st = applyRY(st, params[0], 0); st = applyCX(st,0,1);
      return st;
    }
    if (type === "pma3") {
      st = applyX(st,1);
      st = rbsBlock(st, params[0]);
      st = applyRY(st, params[1], 0);
      st = applyRY(st, params[2], 1);
      return st;
    }
    throw new Error("ansatz sconosciuto: " + type);
  }

  // Come ansatzState, ma registra lo stato dopo OGNI porta elementare, insieme
  // a una descrizione della porta (per disegnare il circuito e animare la
  // trasformazione passo-passo). Le due funzioni condividono la stessa identica
  // sequenza di chiamate: se una cambia, l'altra va aggiornata di pari passo.
  // Formato di ogni porta (compatibile con Componenti.CircuitDiagram):
  //   {kind:"BOX"|"CTRL"|"DOTS"|"SPAN", ..., desc: "descrizione leggibile", state}
  function ansatzSteps(type, params, bJ) {
    let st = state00();
    const steps = [];
    function push(gate, desc) {
      st = gate.apply(st);
      const rec = Object.assign({}, gate);
      delete rec.apply;
      rec.desc = desc;
      rec.state = { re: st.re.slice(), im: st.im.slice() };
      steps.push(rec);
    }
    const g = {
      X:  (q)            => ({ kind: "BOX", wire: q, label: "X", apply: s => applyX(s, q) }),
      H:  (q)            => ({ kind: "BOX", wire: q, label: "H", apply: s => applyH(s, q) }),
      RY: (q, pIdx, val) => ({ kind: "BOX", wire: q, paramIndex: pIdx, label: `Ry(${val.toFixed(3)})`, apply: s => applyRY(s, params[pIdx], q) }),
      CZ: ()             => ({ kind: "DOTS", wires: [0,1], apply: s => applyCZ(s) }),
      CX: (c, t)         => ({ kind: "CTRL", control: c, target: t, open: false, targetLabel: "X", showAsCnot: true, apply: s => applyCX(s, c, t) }),
      RBS:(pIdx, val)    => ({ kind: "SPAN", wires: [0,1], paramIndex: pIdx, label: `RBS(${val.toFixed(3)})`, apply: s => rbsBlock(s, params[pIdx]) }),
    };
    if (type === "ha") {
      push(g.RY(0, 0, params[0]), `Ry(${params[0].toFixed(4)}) sul qubit 0`);
      push(g.RY(1, 1, params[1]), `Ry(${params[1].toFixed(4)}) sul qubit 1`);
      push(g.CZ(), "CZ fra i due qubit");
      push(g.RY(0, 2, params[2]), `Ry(${params[2].toFixed(4)}) sul qubit 0`);
      push(g.RY(1, 3, params[3]), `Ry(${params[3].toFixed(4)}) sul qubit 1`);
      push(g.CZ(), "CZ fra i due qubit");
      push(g.RY(0, 4, params[4]), `Ry(${params[4].toFixed(4)}) sul qubit 0`);
      push(g.RY(1, 5, params[5]), `Ry(${params[5].toFixed(4)}) sul qubit 1`);
    } else if (type === "pma1") {
      if (bJ < 2.0) {
        push(g.X(0), "X sul qubit 0");
        push(g.H(0), "H sul qubit 0");
        push(g.CX(0,1), "CX, controllo q0 \u2192 bersaglio q1");
        push(g.X(0), "X sul qubit 0");
      } else {
        push(g.X(0), "X sul qubit 0");
        push(g.X(1), "X sul qubit 1");
      }
      push(g.CX(0,1), "CX, controllo q0 \u2192 bersaglio q1");
      push(g.RY(0, 0, params[0]), `Ry(${params[0].toFixed(4)}) sul qubit 0`);
      push(g.CX(0,1), "CX, controllo q0 \u2192 bersaglio q1");
    } else if (type === "pma3") {
      push(g.X(1), "X sul qubit 1");
      push(g.RBS(0, params[0]), `blocco RBS(${params[0].toFixed(4)}) \u2014 rotazione di Givens`);
      push(g.RY(0, 1, params[1]), `Ry(${params[1].toFixed(4)}) sul qubit 0`);
      push(g.RY(1, 2, params[2]), `Ry(${params[2].toFixed(4)}) sul qubit 1`);
    } else {
      throw new Error("ansatz sconosciuto: " + type);
    }
    return steps;
  }

  function energyOf(H, st) { return bilinearReal(H, st.re, st.im); }
  function fidelityToVec(st, psi0) {
    // |<psi0|st>|, psi0 reale
    const d = vecDagVec(psi0, psi0.map(()=>0), st.re, st.im);
    return Math.hypot(d.re, d.im);
  }

  // ----------------------------------------------------- ottimizzatore (VQE)
  // Discesa del gradiente con differenze finite + riavvii casuali. Il problema
  // e' a bassa dimensione (<=6 parametri) e l'energia costa O(1): non serve
  // nulla di piu' sofisticato per convergere in modo affidabile.
  function optimizeAnsatz(type, bJ, DJ, opts) {
    opts = opts || {};
    const nParam = ANSATZ_INFO[type].nparam;
    const H = buildH(bJ, DJ);
    const restarts = opts.restarts || 6;
    const iters = opts.iters || 220;
    const seed = opts.seed || 12345;
    let rngState = seed;
    function rng() { rngState = (rngState*1103515245+12345)&0x7fffffff; return rngState/0x7fffffff; }

    function energyFn(p) { return energyOf(H, ansatzState(type, p, bJ)); }

    let best = { E: Infinity, params: null, trace: [] };
    for (let r=0; r<restarts; r++) {
      let p = new Array(nParam).fill(0).map(()=> (rng()*2-1)*Math.PI);
      let lr = 0.35;
      const trace = [];
      let E = energyFn(p);
      trace.push({ E, params: p.slice() });
      for (let it=0; it<iters; it++) {
        const grad = new Array(nParam).fill(0);
        const h = 1e-4;
        for (let k=0;k<nParam;k++) {
          const pPlus = p.slice(); pPlus[k]+=h;
          const pMinus = p.slice(); pMinus[k]-=h;
          grad[k] = (energyFn(pPlus)-energyFn(pMinus))/(2*h);
        }
        const pNew = p.map((v,k)=>v-lr*grad[k]);
        const ENew = energyFn(pNew);
        if (ENew < E) { p = pNew; E = ENew; }
        else { lr *= 0.7; }
        trace.push({ E, params: p.slice() });
        if (lr < 1e-6) break;
      }
      if (E < best.E) best = { E, params: p, trace };
    }
    const stFinal = ansatzState(type, best.params, bJ);
    return {
      params: best.params,
      energy: best.E,
      trace: best.trace,
      state: stFinal,
    };
  }

  // ---------------------------------------------------------- correlatori
  function applyPauli(st, site, comp) {
    const op = SITE_OP[String(site)+comp];
    return matVecC(op, st.re, st.im);
  }
  function correlator(bJ, DJ, t, evolveMode, N, i, alpha, j, beta, psi0) {
    // C_ij^{alpha,beta}(t) = <psi0| sigma_i^alpha(t) sigma_j^beta(0) |psi0>
    //                      = (U(t) psi0)^dagger sigma_i^alpha (U(t) sigma_j^beta psi0)
    const psi0c = { re: psi0.slice(), im: psi0.map(()=>0) };
    const pert = applyPauli(psi0c, j, beta);           // sigma_j^beta |psi0>
    let evPert, evPsi0;
    if (evolveMode === "trotter") {
      evPert = trotterEvolve(bJ, DJ, t, N, pert.re, pert.im);
      evPsi0 = trotterEvolve(bJ, DJ, t, N, psi0c.re, psi0c.im);
    } else {
      evPert = exactEvolve(bJ, DJ, t, pert.re, pert.im);
      evPsi0 = exactEvolve(bJ, DJ, t, psi0c.re, psi0c.im);
    }
    const sigmaChi = applyPauli(evPsi0, i, alpha);      // sigma_i^alpha (U psi0)
    return vecDagVec(sigmaChi.re, sigmaChi.im, evPert.re, evPert.im);
  }

  // --------------------------------------------------- operatori ausiliari
  function buildSz() { return addM(scaleM(M_ZI, 0.5), scaleM(M_IZ, 0.5)); }
  function buildS2() { return addM(scaleM(addM(addM(M_XX, M_YY), M_ZZ), 0.5), scaleM(ident4(), 1.5)); }
  function matMulReal(A, B) {
    const R = zeros4();
    for (let i=0;i<4;i++) for (let j=0;j<4;j++) { let s=0; for (let k=0;k<4;k++) s+=A[i][k]*B[k][j]; R[i][j]=s; }
    return R;
  }
  function frobeniusNorm(A) {
    let s = 0; for (let i=0;i<4;i++) for (let j=0;j<4;j++) s += A[i][j]*A[i][j];
    return Math.sqrt(s);
  }
  function commutatorNorm(A, B) {
    const AB = matMulReal(A, B), BA = matMulReal(B, A);
    return frobeniusNorm(addM(AB, BA, -1));
  }

  function commutatorMatrix(A, B) {
    return addM(matMulReal(A, B), matMulReal(B, A), -1);
  }

  // -------------------------------------------------------------- esportazione
  const PAULI2 = { XX: M_XX, YY: M_YY, ZZ: M_ZZ, ZI: M_ZI, IZ: M_IZ, XZ: M_XZ, ZX: M_ZX };

  const Fisica = {
    PAULI2, buildSz, buildS2, commutatorNorm, commutatorMatrix, matMulReal, frobeniusNorm,
    buildH, buildH1, buildH2, jacobiEigen, groundState, expOfSymH,
    matMulC, matVecC, vecDagVec, trotterStepMatrix, trotterEvolve, exactEvolve, trotterSteps, trotterMicroSteps,
    state00, applyX, applyH, applyRY, applyCZ, applyCX, rbsBlock,
    ANSATZ_INFO, ansatzState, ansatzSteps, energyOf, fidelityToVec, optimizeAnsatz,
    applyPauli, correlator, bilinearReal,
  };

  if (typeof module !== "undefined" && module.exports) module.exports = Fisica;
  else global.Fisica = Fisica;
})(typeof window !== "undefined" ? window : globalThis);
