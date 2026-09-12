"""
VQE per il ground state del dimero al punto di lavoro del test 2
(relazione_test_parametri.md): b/J = 0.35, D/J = 0.80, J = 1.

Riusa la convenzione dell'Hamiltoniana di dimer_exact.py e l'ansatz
PMA-2q.3 + metodologia multistart validati in confronto_ansatz_entangler.ipynb.
Nessuna scelta nuova qui: solo applicazione a un singolo punto (b, J, D).

Obiettivo: |psi_0^VQE> da usare come stato iniziale nel prossimo stadio
(correlazioni dinamiche con ancilla) al posto di |00>.

RUOLO NELL'INSIEME DEL PACCHETTO: e' il secondo "mattone" (dopo
dimer_exact.py) su cui si appoggia tutta la pipeline di Parte 2 --
fornisce sia l'ansatz variazionale (pma_2q, rbs_block) sia la routine di
ottimizzazione (vqe_multistart) usati identici in ogni stadio a valle
(VQE sotto rumore, VQE ottimizzato di nuovo, Trotter, correlatori). Nota
di trasparenza: questo file ridefinisce una propria dimer_hamiltonian()
invece di importarla da dimer_exact.py -- stessa formula, stessa
convenzione (verificato: coincidono a precisione macchina), ma due
implementazioni indipendenti per storia del progetto, non un'unica
sorgente condivisa come dichiarato nel docstring di dimer_exact.py per
il resto della pipeline.
"""

import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import SparsePauliOp, Statevector, Operator

# --------------------------------------------------------------------------
# 1. Hamiltoniana — stessa convenzione di dimer_exact.py / confronto_ansatz
# --------------------------------------------------------------------------

def dimer_hamiltonian(b, J=1.0, D=0.0):
    """H = J(XX+YY+ZZ) + b(ZI+IZ) + D(XZ-ZX), come SparsePauliOp.

    Ruolo nel modulo: fornisce l'operatore su cui vqe_multistart() ottimizza
    l'aspettazione, sia nel blocco __main__ sia quando altri moduli
    importano dimer_hamiltonian da qui invece che da dimer_exact.py.
    Ruolo nell'insieme: e' la versione "storica" dell'Hamiltoniana usata
    dai moduli di Parte 1/Parte 2 che importano da vqe_test2 (per esempio
    circuito_correlazioni_dimero.py) -- funzionalmente identica a quella
    di dimer_exact.py, vedi nota di trasparenza nel docstring di modulo.
    """
    return SparsePauliOp.from_list([
        ("XX", J), ("YY", J), ("ZZ", J),
        ("ZI", b), ("IZ", b),
        ("XZ", D), ("ZX", -D),
    ])


def magnetization_operator():
    """Costruisce Mz = (Z1+Z2)/2, come SparsePauliOp.

    Ruolo nel modulo: usato nel blocco __main__ per riportare <Mz> sia
    sullo stato esatto sia su quello VQE, come controllo incrociato oltre
    all'energia (due stati con la stessa energia potrebbero comunque
    avere magnetizzazione diversa se ci fosse un errore di convenzione).
    Ruolo nell'insieme: puramente diagnostico, nessun modulo a valle lo
    importa da qui per calcoli propri.
    """
    return SparsePauliOp.from_list([("ZI", 0.5), ("IZ", 0.5)])


def exact_ground(b, J=1.0, D=0.0):
    """Diagonalizza H(b,J,D) e ritorna (E0, psi0, autovalori, autovettori).

    Ruolo nel modulo: fornisce il riferimento esatto (w, v) usato sia dal
    blocco __main__ sia da ground_fidelity() per valutare quanto lo stato
    VQE si avvicini al vero ground state.
    Ruolo nell'insieme: e' la funzione che TUTTI gli script di questo
    pacchetto che lavorano a un punto di lavoro diverso da "test 2"
    (es. 03_genera_dati_secondo_punto.py) richiamano per ottenere lo
    stato esatto di riferimento a quel nuovo punto -- il vero "punto di
    ingresso" del modulo per un punto di lavoro generico, non solo test 2.

    Ritorna: (E0, psi0, w, v) dove w,v sono l'intero spettro/autobase
    (serve a ground_fidelity per gestire correttamente eventuali
    degenerazioni del livello fondamentale).
    """
    H = dimer_hamiltonian(b, J, D).to_matrix()
    w, v = np.linalg.eigh(H)
    return w[0], v[:, 0], w, v


def ground_fidelity(psi, w, v, tol=1e-6):
    """Fidelity verso il sottospazio fondamentale (robusta a degenerazioni).

    Ruolo nel modulo: usata da vqe_multistart() per riportare quanto bene
    il circuito ottimizzato approssimi il vero ground state -- non solo
    l'energia (che potrebbe accidentalmente coincidere anche con uno
    stato diverso, in presenza di degenerazione) ma la sovrapposizione
    quantistica vera e propria.
    Ruolo nell'insieme: e' la metrica di controllo qualita' usata
    ovunque nel pacchetto per certificare un'ottimizzazione VQE come
    riuscita (tipicamente si richiede fedelta' entro 1e-9/1e-11 dal
    valore 1, non solo un'energia vicina a quella esatta).
    """
    E0 = w[0]
    idx = np.where(np.abs(w - E0) < tol)[0]
    return float(np.sum([np.abs(np.vdot(v[:, i], psi)) ** 2 for i in idx]))


# --------------------------------------------------------------------------
# 2. Ansatz PMA-2q.3 (blocco RBS + rotazioni Ry indipendenti sui due qubit)
#    Identico a quello di confronto_ansatz_entangler.ipynb — PMA_RECOMMENDED.
# --------------------------------------------------------------------------

def rbs_block(qc, phi, q0=0, q1=1):
    """Blocco M-conservante (Reconfigurable Beam Splitter):
    H-CZ-Ry(phi)/Ry(-phi)-CZ-H, appeso in-place al circuito qc.

    Ruolo nel modulo: e' il "cuore" dell'ansatz PMA-2q -- il blocco a
    due qubit che genera l'entanglement conservando il numero totale di
    eccitazioni (simmetria U(1) del modello di Heisenberg), verificato
    da _self_test_rbs() qui sotto.
    Ruolo nell'insieme: questo stesso blocco (in forma concettualmente
    identica, adattata al numero di qubit) e' il mattone di base anche
    degli ansatz per il trimero (anello e catena, W-2q.6 e W-2qC.K2) --
    e' il pattern di ansatz canonico di tutto il progetto, non solo del
    dimero.
    """
    sub = QuantumCircuit(2, name="RBS")
    sub.h(0); sub.h(1); sub.cz(0, 1)
    sub.ry(phi, 0); sub.ry(-phi, 1)
    sub.cz(0, 1); sub.h(0); sub.h(1)
    qc.append(sub.to_gate(label="RBS"), [q0, q1])


def pma_2q(nparam=3):
    """Costruisce l'ansatz PMA-2q completo:
    X(q1) . RBS(p0) . Ry(p1)_0 . Ry(p2)_1 (3 parametri di default,
    fedelta'=1 dal minimo teorico gia' verificato in Parte 1).

    Ruolo nel modulo: e' l'ansatz che vqe_multistart() ottimizza nel
    blocco __main__ -- il circuito parametrico vero e proprio, costruito
    componendo rbs_block() con le rotazioni Ry indipendenti sui due qubit.
    Ruolo nell'insieme: e' l'ansatz usato IDENTICO in ogni stadio della
    pipeline di rumore sul dimero (Parte 2) e in entrambe le estensioni
    (VQE ottimizzato di nuovo, readout asimmetrico) -- ogni modulo che
    lavora sul dimero importa pma_2q da qui, mai una propria copia.
    """
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(2)
    qc.x(1)
    rbs_block(qc, p[0])
    i = 1
    while i < nparam:
        qc.ry(p[i], 0); qc.ry(p[i + 1], 1)
        i += 2
    return qc


def _self_test_rbs():
    """Verifica che rbs_block() riproduca esattamente la rotazione di
    Givens G(phi) attesa, a precisione macchina.

    Ruolo nel modulo: eseguito in apertura del blocco __main__, prima di
    qualunque ottimizzazione VQE -- se questo test fallisse, l'intero
    ansatz sarebbe costruito su un blocco RBS sbagliato e ogni risultato
    successivo (qui e in tutta la pipeline che riusa questo ansatz)
    sarebbe inaffidabile.
    Ruolo nell'insieme: e' l'unico controllo di correttezza sul blocco
    RBS condiviso da tutto il progetto (dimero e trimero) -- un singolo
    punto di verifica per un componente riusato ovunque.
    """
    def givens(phi):
        c, s = np.cos(phi), np.sin(phi)
        G = np.eye(4, dtype=complex)
        G[1, 1] = c; G[1, 2] = -s; G[2, 1] = s; G[2, 2] = c
        return G
    for phi in [0.3, 0.7, -0.5]:
        qc = QuantumCircuit(2)
        rbs_block(qc, phi)
        err = np.max(np.abs(Operator(qc).data - givens(phi)))
        assert err < 1e-12, f"RBS self-test fallito a phi={phi}: err={err:.2e}"
    print("[self-test] blocco RBS conforme a G(phi), precisione macchina.")


# --------------------------------------------------------------------------
# 3. VQE multistart — stessa metodologia: R=6, reinizializzazione nel ciclo
#    esterno, COBYLA (confronto_ansatz_entangler.ipynb, mandato del relatore)
# --------------------------------------------------------------------------

def vqe_multistart(ansatz, H_op, w, v, R=6, maxiter=300, seed=0):
    """Ottimizzazione VQE con R riavvii casuali (COBYLA) seguiti da un
    affinamento finale (L-BFGS-B) dal miglior punto trovato.

    Ruolo nel modulo: e' la routine di ottimizzazione vera e propria,
    chiamata dal blocco __main__ sul punto di lavoro "test 2" -- prende
    un ansatz parametrico e un'Hamiltoniana, ritorna i parametri
    ottimali insieme a diagnostica sulla dispersione dei riavvii.
    Ruolo nell'insieme: e' la funzione di ottimizzazione "ideale" (nessun
    rumore) di riferimento per tutta la pipeline -- i moduli di Parte 2
    che riottimizzano SOTTO rumore (vqe_noise_aware_dimero.py) replicano
    la stessa struttura (multistart COBYLA + polish L-BFGS-B) ma con
    l'energia valutata su un simulatore rumoroso invece che su uno
    statevector esatto come qui.

    Ritorna un dict con energia migliore, parametri, fedelta' rispetto
    al ground state esatto, dispersione dei risultati dei singoli
    riavvii (utile a stimare la difficolta' del paesaggio di
    ottimizzazione) e lo statevector finale.
    """
    rng = np.random.default_rng(seed)
    n = ansatz.num_parameters
    finals = []
    best = (np.inf, None, None)
    for _ in range(R):
        x0 = rng.uniform(0.0, 2 * np.pi, n)

        def obj(x):
            sv = Statevector(ansatz.assign_parameters(x))
            return float(np.real(sv.expectation_value(H_op)))

        res = minimize(obj, x0, method="COBYLA", options={"maxiter": maxiter})
        finals.append(res.fun)
        if res.fun < best[0]:
            best = (res.fun, res.x, res.nfev)
    Ebest, xbest, nfev = best

    # polish finale: L-BFGS-B dal miglior punto COBYLA, per scendere a
    # precisione macchina (COBYLA da solo lascia un residuo ~1e-5/1e-6)
    def obj(x):
        sv = Statevector(ansatz.assign_parameters(x))
        return float(np.real(sv.expectation_value(H_op)))

    res_polish = minimize(obj, xbest, method="L-BFGS-B")
    if res_polish.fun < Ebest:
        Ebest, xbest = res_polish.fun, res_polish.x

    sv = Statevector(ansatz.assign_parameters(xbest))
    fid = ground_fidelity(sv.data, w, v)
    return {"E": Ebest, "x": xbest, "fid": fid, "nfev": nfev,
            "finals": np.array(finals), "spread": np.ptp(finals),
            "statevector": sv}


# --------------------------------------------------------------------------
# 4. Applicazione al punto di lavoro del test 2
# --------------------------------------------------------------------------

if __name__ == "__main__":
    _self_test_rbs()

    J = 1.0
    b = 0.35 * J     # test 2: b/J = 0.35
    D = 0.80 * J     # test 2: D/J = 0.80

    print(f"\nPunto di lavoro (test 2): b/J={b/J:.3f}  D/J={D/J:.3f}  J={J}")

    # --- benchmark esatto ---
    E0_exact, psi0_exact, w, v = exact_ground(b, J, D)
    Mz_op = magnetization_operator()
    Mz_exact = float(np.real(psi0_exact.conj() @ Mz_op.to_matrix() @ psi0_exact))

    print(f"\nSpettro esatto: {np.round(w, 6)}")
    print(f"E0 (esatto)   = {E0_exact:.8f}")
    print(f"<Mz> (esatto) = {Mz_exact:.6f}")
    print("Ampiezze del ground state esatto (base |00>,|01>,|10>,|11>):")
    for lbl, amp in zip(["00", "01", "10", "11"], psi0_exact):
        print(f"  |{lbl}>: {amp: .6f}")

    # --- VQE con PMA-2q.3 ---
    H_op = dimer_hamiltonian(b, J, D)
    ansatz = pma_2q(3)
    print(f"\nAnsatz: PMA-2q.3, {ansatz.num_parameters} parametri, multistart R=6")

    result = vqe_multistart(ansatz, H_op, w, v, R=6, seed=0)

    print(f"\nE (VQE)       = {result['E']:.8f}")
    print(f"|E_VQE - E0|  = {abs(result['E'] - E0_exact):.2e}")
    print(f"Fidelity      = {result['fid']:.8f}")
    print(f"Dispersione 6 restart (max-min energia finale) = {result['spread']:.2e}")

    sv_vqe = result["statevector"].data
    Mz_vqe = float(np.real(sv_vqe.conj() @ Mz_op.to_matrix() @ sv_vqe))
    print(f"<Mz> (VQE)    = {Mz_vqe:.6f}")

    print("\nParametri ottimali (rad):", np.round(result["x"], 6))
    print("\nStato VQE (base |00>,|01>,|10>,|11>):")
    for lbl, amp in zip(["00", "01", "10", "11"], sv_vqe):
        print(f"  |{lbl}>: {amp: .6f}")

    # overlap di fase con l'esatto (utile per verificare che non ci sia
    # solo una fase globale relativa arbitraria da fissare a valle)
    overlap = np.vdot(psi0_exact, sv_vqe)
    print(f"\n<psi_exact|psi_VQE> = {overlap:.6f}  (|.|={abs(overlap):.8f})")

    np.savez("ground_state_test2.npz",
             b=b, J=J, D=D,
             E0_exact=E0_exact, E_vqe=result["E"], fidelity=result["fid"],
             psi0_exact=psi0_exact, psi0_vqe=sv_vqe,
             vqe_params=result["x"])
    print("\n[salvato] ground_state_test2.npz (stato per lo stadio successivo: correlazioni)")
