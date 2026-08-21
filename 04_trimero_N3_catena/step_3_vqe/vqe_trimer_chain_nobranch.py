"""
Ansatz PMA per il trimero a catena aperta SENZA branching (mirror di
pma_2q del dimero, confronto_ansatz_entangler.ipynb, e di
vqe_trimer_ring_nobranch.py per l'anello) -- stato iniziale FISSO,
indipendente da (J,b): la scelta del ramo/settore emerge
dall'ottimizzazione dei parametri, non da una preparazione diversa a
seconda del campo.

Struttura (K cicli):
    |000> -> X(q0) -> [RBS_12(a_k), RBS_23(b_k), Ry(c_k,q0),
                        Ry(d_k,q1), Ry(e_k,q2)]_{k=1..K}
Parametri: 5K (contro i 6K dell'anello: un blocco RBS in meno per ciclo,
coerente con l'assenza del bond 31 nella catena).

Confrontato con la versione a branching (vqe_trimer_chain.py, RBS+branching,
2K+3 parametri; vqe_trimer_chain_W.py, W+branching, 2K parametri):
    - NESSUNA logica if b<b_c: un solo circuito, sempre lo stesso
    - RBS ripetuto ad OGNI ciclo (famiglia "ciclica", mirror esatto di
      vqe_trimer_ring_nobranch.py) -- diversa dalla famiglia "esatta"
      gia' esplorata in confronto_ansatz_entangler_trimero_catena.ipynb
      (PMA-2q.x, RBS fatto una sola volta, poi solo Ry aggiuntivi)

Verificato numericamente (non solo teoria), D=0, b=1.0 (< b_c=3):
    K=1 (5 par)  -> F=0.826612, vicino al tetto strutturale ~5/6 gia'
                    scoperto per la famiglia "esatta" (vedi sez. 5 di
                    confronto_ansatz_entangler_trimero_catena.ipynb)
    K=2 (10 par) -> F=1.000000 esatto: ripetere il blocco RBS (non solo
                    i Ry) supera il tetto -- stesso pattern gia' visto
                    per l'anello (PMA-2qC.K2 batte PMA-2qC.K1 sotto DM)

SCOPE: solo D=0, nessun termine DM -- vedi nota di scope in
vqe_trimer_chain_W.py. I file relativi al VQE con DM per la catena
verranno prodotti separatamente e non condizionano le scelte fatte qui.

Dipende da trimer_chain_exact.py.
"""

import numpy as np
from scipy.optimize import minimize
from qiskit.primitives import StatevectorEstimator
from qiskit.circuit import QuantumCircuit, ParameterVector
from qiskit.quantum_info import Statevector

from trimer_chain_exact import (
    trimer_hamiltonian, exact_sweep, ground_state_projector,
    magnetization_operator, critical_field,
)

BOND12 = (2, 1)
BOND23 = (1, 0)
# nessun BOND31: non esiste nella catena


def rbs_block(qc, phi, q0, q1):
    """Stesso blocco RBS gia' validato in vqe_trimer_chain.py."""
    sub = QuantumCircuit(2, name="RBS")
    sub.h(0); sub.h(1); sub.cz(0, 1)
    sub.ry(phi, 0); sub.ry(-phi, 1)
    sub.cz(0, 1); sub.h(0); sub.h(1)
    qc.append(sub.to_gate(label="RBS"), [q0, q1])


def make_ha_ansatz(reps=2):
    from qiskit.circuit.library import n_local
    return n_local(num_qubits=3, rotation_blocks="ry", entanglement_blocks="cz",
                    entanglement="full", reps=reps, insert_barriers=False)


def pma_2q_trimer_nobranch(K=1):
    """PMA senza branching: stato iniziale fisso (X su q0), K cicli di
    [RBS sui 2 bond fisici] + [Ry indipendenti sui 3 qubit]. 5K parametri."""
    nparam = 5 * K
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(3)
    qc.x(0)  # stato iniziale FISSO -- non dipende da J, b

    idx = 0
    for _ in range(K):
        rbs_block(qc, p[idx], *BOND12); idx += 1
        rbs_block(qc, p[idx], *BOND23); idx += 1
        qc.ry(p[idx], 0); idx += 1
        qc.ry(p[idx], 1); idx += 1
        qc.ry(p[idx], 2); idx += 1
    return qc


def _energy(params, ansatz, hamiltonian, estimator):
    pub = (ansatz, hamiltonian, [params])
    return float(estimator.run([pub]).result()[0].data.evs.item())


def run_vqe(J, b, K=1, n_restarts=5, seed=42):
    """VQE con l'ansatz senza branching. Interfaccia analoga a run_vqe degli
    altri moduli, ma senza ansatz_type/reps (qui c'e' solo questo PMA)."""
    rng = np.random.default_rng(seed)
    hamiltonian = trimer_hamiltonian(J, b)
    estimator = StatevectorEstimator()
    ansatz = pma_2q_trimer_nobranch(K)
    n_params = ansatz.num_parameters

    res_exact = exact_sweep([b], J=J)
    P0, _, deg = ground_state_projector(J, b)
    e_exact = float(res_exact["gs_energy"][0])
    mz_exact = float(res_exact["gs_mz"][0])
    Mz_mat = magnetization_operator().to_matrix()

    best_e, best_params = np.inf, None
    for _ in range(n_restarts):
        x0 = rng.uniform(-np.pi, np.pi, n_params)
        r1 = minimize(_energy, x0, args=(ansatz, hamiltonian, estimator),
                      method="COBYLA", options={"maxiter": 3000, "tol": 1e-10})
        r2 = minimize(_energy, r1.x, args=(ansatz, hamiltonian, estimator),
                      method="L-BFGS-B", options={"maxiter": 3000, "ftol": 1e-14})
        if r2.fun < best_e:
            best_e, best_params = r2.fun, r2.x

    sv = Statevector(ansatz.assign_parameters(best_params)).data
    mz_vqe = float(np.real(sv.conj() @ Mz_mat @ sv))
    fid = float(np.real(sv.conj() @ P0 @ sv))

    return {
        "J": J, "b": b, "e_vqe": best_e, "e_exact": e_exact,
        "delta_e": best_e - e_exact, "fidelity": fid,
        "mz_vqe": mz_vqe, "mz_exact": mz_exact,
        "n_params": n_params, "degeneracy": deg,
    }


def vqe_sweep(b_values, J=1.0, K=1, n_restarts=5, seed=42, verbose=True):
    results = []
    for i, b in enumerate(b_values):
        r = run_vqe(J, b, K=K, n_restarts=n_restarts, seed=seed + i)
        results.append(r)
        if verbose:
            print(f"  b={b:5.2f}  E={r['e_vqe']:9.4f}  dE={r['delta_e']:+.2e}  "
                  f"F={r['fidelity']:.6f}  (deg={r['degeneracy']})")
    return results
