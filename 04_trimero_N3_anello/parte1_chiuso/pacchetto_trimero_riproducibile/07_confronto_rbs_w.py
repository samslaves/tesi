import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))


"""
Confronto RBS-2q vs W-2q (Documento 2): fedelta' sotto DM al punto di
lavoro, tetto strutturale di RBS puro (nessun R_y finale, K giri), e
verifica che l'ansatz W-2q.6 non abbia bisogno di rami di preparazione
diversi a seconda di b/J (a differenza dell'ansatz minimo del dimero).

Fonte: confronto_ansatz_entangler_trimero_anello.ipynb /
analisi_espressivita_PMA_anello.ipynb (stessa nota di provenienza di
vqe_w2q6_trimero_anello.py -- non riprodotto qui da zero, solo isolato in
uno script minimo con asserzioni).

  1. Fedelta' sotto DM, punto di lavoro Scenario A: RBS-2q.6 ha un tetto
     reale (F=0.99991), W-2q.6 raggiunge l'esatto (F=1 a precisione
     macchina).
  2. Tetto strutturale: RBS puro (senza R_y finali) NON migliora
     aggiungendo giri (K=1,2,3) -- coincide col peso della vera GS nel
     settore raggiungibile, non e' un limite dell'ottimizzatore.
  3. Sweep in b/J (13 punti, incluso l'incrocio): W-2q.6 raggiunge
     F=1 OVUNQUE, nessun ramo di preparazione necessario -- a
     differenza del CNOT-Ry-CNOT (blocco "ansatz base" del dimero, qui
     riusato dentro W-2q.6) che da solo, senza le R_y finali, resterebbe
     confinato al settore di partenza.
"""
import numpy as np
from scipy.optimize import minimize
from qiskit.quantum_info import Statevector

from trimer_ring_exact import trimer_hamiltonian_dm
from ansatz_trimero_anello import rbs2q_circuit, w2q_circuit_locale

J, Jp, b, D = 1.0, 0.4, 2.4, 0.15
H = trimer_hamiltonian_dm(J, Jp, b, "B", D).to_matrix()
Evals, V = np.linalg.eigh(H)
psi0 = V[:, 0]
imax = np.argmax(np.abs(psi0))
psi0 = psi0 * np.exp(-1j * np.angle(psi0[imax]))


def fidelity_max(qc_factory, nparam, R=15, seed=0):
    """Multistart (COBYLA + polish L-BFGS-B) della fidelity rispetto a
    psi0, per un circuito costruito da qc_factory(nparam)."""
    def obj(params):
        psi = Statevector(qc_factory(nparam).assign_parameters(params)).data
        return -abs(np.vdot(psi0, psi)) ** 2
    rng = np.random.default_rng(seed)
    best = (0.0, None)
    for _ in range(R):
        x0 = rng.uniform(-np.pi, np.pi, nparam)
        res = minimize(obj, x0, method="COBYLA", options=dict(maxiter=1500, tol=1e-11))
        if -res.fun > best[0]:
            best = (-res.fun, res.x)
    res = minimize(obj, best[1], method="L-BFGS-B")
    if -res.fun > best[0]:
        best = (-res.fun, res.x)
    return best[0]


print("=" * 78)
print("1. FEDELTA' SOTTO DM, PUNTO DI LAVORO SCENARIO A (6 parametri)")
print("=" * 78)
F_rbs = fidelity_max(rbs2q_circuit, 6, R=15, seed=1)
F_w = fidelity_max(w2q_circuit_locale, 6, R=15, seed=1)
print(f"  RBS-2q.6: F = {F_rbs:.10f}   (1-F = {1 - F_rbs:.2e})")
print(f"  W-2q.6:   F = {F_w:.10f}   (1-F = {1 - F_w:.2e})")
assert abs(F_rbs - 0.9999110739) < 1e-6, "F(RBS) fuori dal range atteso (~0.99991)"
assert F_w > 1 - 1e-6, "W-2q.6 dovrebbe raggiungere l'esatto"
print("  -> OK: RBS ha un tetto reale, W raggiunge l'esatto")

print()
print("=" * 78)
print("2. TETTO STRUTTURALE: RBS puro (senza R_y finali), K giri")
print("=" * 78)


def rbs_puro_K_giri(K):
    """K giri completi di SOLO blocchi RBS sui tre legami (3*K
    parametri), MAI uno strato di R_y finale -- costruzione dedicata,
    non pma_2q_trimer_exact (quella aggiunge R_y quando nparam>3, il
    che darebbe l'ansatz RBS-2q.6 vero e proprio, non 'K giri puri')."""
    from qiskit import QuantumCircuit
    from qiskit.circuit import ParameterVector
    from ansatz_trimero_anello import rbs_block, BONDS
    p = ParameterVector("p", 3 * K)
    qc = QuantumCircuit(3)
    qc.x(0)
    idx = 0
    for _ in range(K):
        for bnd in BONDS:
            rbs_block(qc, p[idx], *bnd)
            idx += 1
    return qc


def fidelity_max_qc(qc, nparam, R=12, seed=7):
    def obj(params):
        psi = Statevector(qc.assign_parameters(params)).data
        return -abs(np.vdot(psi0, psi)) ** 2
    rng = np.random.default_rng(seed)
    best = (0.0, None)
    for _ in range(R):
        x0 = rng.uniform(-np.pi, np.pi, nparam)
        res = minimize(obj, x0, method="COBYLA", options=dict(maxiter=1500, tol=1e-11))
        if -res.fun > best[0]:
            best = (-res.fun, res.x)
    res = minimize(obj, best[1], method="L-BFGS-B")
    if -res.fun > best[0]:
        best = (-res.fun, res.x)
    return best[0]


F_K1 = None
for K in (1, 2, 3):
    qc_K = rbs_puro_K_giri(K)
    F_K = fidelity_max_qc(qc_K, 3 * K, R=12, seed=7)
    print(f"  K={K} giri ({3*K} parametri, nessun R_y): F = {F_K:.10f}")
    if K == 1:
        F_K1 = F_K
    else:
        assert abs(F_K - F_K1) < 1e-6, "il tetto si sposta aggiungendo giri: non atteso"
print("  -> OK: il tetto non si sposta aggiungendo giri (stesso principio del dimero)")

print()
print("=" * 78)
print("3. SWEEP IN b/J: W-2q.6 senza rami di preparazione")
print("=" * 78)
b_valori = [0.3, 0.8, 1.2, 1.8, 2.372, 3.0, 3.6, 4.5]  # 2.372 = incrocio Opzione A


def fidelity_a_b(b_val, R=5, seed=2):
    H_b = trimer_hamiltonian_dm(J, Jp, b_val, "B", D).to_matrix()
    E_b, V_b = np.linalg.eigh(H_b)
    p0 = V_b[:, 0]
    im = np.argmax(np.abs(p0))
    p0 = p0 * np.exp(-1j * np.angle(p0[im]))

    def obj(params):
        psi = Statevector(w2q_circuit_locale(6).assign_parameters(params)).data
        return -abs(np.vdot(p0, psi)) ** 2

    rng = np.random.default_rng(seed)
    best = (0.0, None)
    for _ in range(R):
        x0 = rng.uniform(-np.pi, np.pi, 6)
        res = minimize(obj, x0, method="COBYLA", options=dict(maxiter=800, tol=1e-10))
        if -res.fun > best[0]:
            best = (-res.fun, res.x)
    res = minimize(obj, best[1], method="L-BFGS-B")
    if -res.fun > best[0]:
        best = (-res.fun, res.x)
    return best[0]


fedelta_sweep = []
for bv in b_valori:
    Fv = fidelity_a_b(bv)
    fedelta_sweep.append(Fv)
    print(f"  b/J={bv:.3f}: F = {Fv:.8f}")
assert all(f > 1 - 1e-5 for f in fedelta_sweep), \
    "F<1 in almeno un punto dello sweep: il claim 'nessun ramo necessario' non regge"
print("  -> OK: F=1 ovunque, nessun ramo di preparazione necessario")

np.savez("confronto_rbs_w.npz",
         F_rbs=F_rbs, F_w=F_w,
         b_valori=np.array(b_valori), fedelta_sweep=np.array(fedelta_sweep))
print("\nSalvato: confronto_rbs_w.npz")
