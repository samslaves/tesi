"""
VQE per il trimero di spin-1/2 (N=3), anello/triangolo isoscele -- versione
con gate W_ij(theta) (mirror diretto di vqe_dimer.py, senza RBS).

Ansatz disponibili:
    HA  — hardware-efficient: n_local (Ry + CZ), reps=2, 12 parametri
    PMA — physically motivated "originale" (Crippa et al. 2021, come in
          vqe_dimer.py, NON la versione PMA-2q.3 con Ry indipendenti):
              gate W_ij(theta) = CNOT . (Ry(theta) x I) . CNOT
              stato iniziale dipendente dal campo (branching esplicito):
                b < b_c  -> stato di Kambe del blocco a bassa energia (B o C)
                b >= b_c -> stato di Kambe del blocco A, M=-3/2 (|111>)
              layer di W_ij su ciascuno dei 3 legami (12, 23, 31): 3K parametri

Convenzione sito<->qubit: IDENTICA a trimer_ring_exact.py e vqe_trimer_ring.py
    site1 -> qubit 2, site2 -> qubit 1, site3 -> qubit 0
Bond fisici: bond12=(2,1), bond23=(1,0), bond31=(0,2).

QUESTO E' IL MIRROR DIRETTO, PER IL TRIMERO, DEL PMA "ORIGINALE" DEL DIMERO
(vqe_dimer.py) -- serve come termine di paragone per il confronto successivo
con la versione RBS (vqe_trimer_ring.py, gia' validata) e con l'eventuale
versione "PMA-2q.3-like" senza branching (da esplorare in un notebook
separato, sul modello di confronto_ansatz_entangler.ipynb).

Dipende da trimer_ring_exact.py.
"""

import numpy as np
from scipy.optimize import minimize
from qiskit.primitives import StatevectorEstimator
from qiskit.circuit.library import n_local
from qiskit.circuit import QuantumCircuit, ParameterVector
from qiskit.quantum_info import Statevector

from trimer_ring_exact import (
    trimer_hamiltonian, exact_sweep, critical_field,
    magnetization_operator, kambe_states, ground_state_projector,
    trimer_hamiltonian_dm, exact_sweep_dm, ground_state_projector_dm,
)

BOND12 = (2, 1)   # sigma1.sigma2 — bond base
BOND23 = (1, 0)   # sigma2.sigma3 — bond laterale
BOND31 = (0, 2)   # sigma3.sigma1 — bond laterale


# ================================================================== HA ansatz

def make_ha_ansatz(reps=2):
    """Ansatz hardware-efficient: Ry + CZ, 3*(reps+1) parametri."""
    return n_local(
        num_qubits=3,
        rotation_blocks="ry",
        entanglement_blocks="cz",
        entanglement="full",
        reps=reps,
        insert_barriers=False,
    )


# ================================================================== blocco W
# Mirror diretto di vqe_dimer.py: W_ij(theta) = CNOT . Ry(theta) . CNOT,
# NON il blocco RBS. Un solo parametro per blocco (contro i 2 impliciti nella
# rotazione di Givens di RBS).

def w_block(qc, theta, q0, q1):
    qc.cx(q0, q1)
    qc.ry(theta, q0)
    qc.cx(q0, q1)


# ============================================================ stato iniziale
# Stesse funzioni di selezione del blocco di vqe_trimer_ring.py (fisica
# identica: quale multipletto di Kambe e' il fondamentale a questo b),
# riprodotte qui per rendere questo modulo autosufficiente dal punto di
# vista dell'ansatz (solo l'ansatz cambia, non la teoria del trimero).

def _select_target_block(J, Jp, b):
    bc = critical_field(J, Jp)
    E_B, E_C = J - 4 * Jp, -3 * J
    low_field_block = "C" if E_C <= E_B else "B"
    if b < bc:
        return low_field_block, -0.5
    return "A", -1.5


def _prepare_initial_state(qc, block, M):
    """Preparazione banale (X, singoletto) per C e A-estremo; generica
    (prepare_state) per B e A-intermedio -- stessa logica di
    vqe_trimer_ring.py."""
    q_site1, q_site2, q_site3 = 2, 1, 0

    if block == "C":
        qc.x(q_site1); qc.h(q_site1); qc.cx(q_site1, q_site2); qc.x(q_site1)
        if M == -0.5:
            qc.x(q_site3)
        return "banale (X,H,CNOT,X + eventuale X)"

    if block == "A" and M == -1.5:
        qc.x(q_site1); qc.x(q_site2); qc.x(q_site3)
        return "banale (solo X)"

    if block == "A" and M == 1.5:
        return "banale (nessuna porta, |000>)"

    vec = kambe_states()[(block, M)]
    qc.prepare_state(vec.tolist(), [0, 1, 2])
    return "generica (prepare_state, non gate-ottimizzata)"


# ================================================================== PMA ansatz

def make_pma_ansatz(J, Jp, b, K=1):
    """Ansatz PMA "originale" (mirror del dimero, gate W, con branching).

    Struttura:
        |Kambe(blocco,M)> -> [W_12(a_k), W_23(b_k), W_31(c_k)]_{k=1..K}

    Numero di parametri: 3K (nessun layer finale di Ry indipendenti --
    a differenza della versione RBS in vqe_trimer_ring.py).
    """
    block, M = _select_target_block(J, Jp, b)
    theta = ParameterVector("th", 3 * K)
    qc = QuantumCircuit(3)

    _prepare_initial_state(qc, block, M)

    idx = 0
    for _ in range(K):
        w_block(qc, theta[idx], *BOND12); idx += 1
        w_block(qc, theta[idx], *BOND23); idx += 1
        w_block(qc, theta[idx], *BOND31); idx += 1

    return qc


def make_pma_ansatz_forced(branch, K=1):
    """Come make_pma_ansatz, ma il ramo iniziale e' fissato indipendentemente
    da b (serve per l'esperimento "cosa succede se si forza un ramo ovunque",
    mirror dell'analogo esperimento nel notebook del dimero)."""
    theta = ParameterVector("th", 3 * K)
    qc = QuantumCircuit(3)
    q_site1, q_site2, q_site3 = 2, 1, 0

    if branch == "basso":
        qc.x(q_site1); qc.h(q_site1); qc.cx(q_site1, q_site2); qc.x(q_site1)
        qc.x(q_site3)
    else:  # "alto" -> |111>
        qc.x(q_site1); qc.x(q_site2); qc.x(q_site3)

    idx = 0
    for _ in range(K):
        w_block(qc, theta[idx], *BOND12); idx += 1
        w_block(qc, theta[idx], *BOND23); idx += 1
        w_block(qc, theta[idx], *BOND31); idx += 1
    return qc


# ================================================================== funzioni VQE

def _energy(params, ansatz, hamiltonian, estimator):
    pub = (ansatz, hamiltonian, [params])
    result = estimator.run([pub]).result()
    return float(result[0].data.evs.item())


def run_vqe(J, Jp, b, ansatz_type="PMA", reps=2, K=1,
            n_restarts=6, seed=42, dm_mode=None, D=0.0):
    """VQE a un singolo punto (J,J',b), con termine DM opzionale.
    Stessa interfaccia di vqe_trimer_ring.run_vqe, ansatz PMA sostituito
    con la versione a gate W (mirror del dimero)."""
    rng = np.random.default_rng(seed)
    hamiltonian = trimer_hamiltonian_dm(J, Jp, b, dm_mode, D)
    estimator = StatevectorEstimator()

    if ansatz_type == "HA":
        ansatz = make_ha_ansatz(reps)
    else:
        ansatz = make_pma_ansatz(J, Jp, b, K)

    n_params = ansatz.num_parameters

    if dm_mode is not None and D != 0:
        res_exact = exact_sweep_dm([b], J, Jp, dm_mode, D)
        P0, _, deg = ground_state_projector_dm(J, Jp, b, dm_mode, D)
    else:
        res_exact = exact_sweep([b], J=J, Jp=Jp)
        P0, _, deg = ground_state_projector(J, Jp, b)
    e_exact = float(res_exact["gs_energy"][0])
    mz_exact = float(res_exact["gs_mz"][0])
    Mz_mat = magnetization_operator().to_matrix()

    best_e, best_params, converged = np.inf, None, False
    for _ in range(n_restarts):
        x0 = rng.uniform(-np.pi, np.pi, n_params)
        res1 = minimize(
            _energy, x0, args=(ansatz, hamiltonian, estimator),
            method="COBYLA", options={"maxiter": 2000, "tol": 1e-10},
        )
        res2 = minimize(
            _energy, res1.x, args=(ansatz, hamiltonian, estimator),
            method="L-BFGS-B", options={"maxiter": 2000, "ftol": 1e-14},
        )
        if res2.fun < best_e:
            best_e = res2.fun
            best_params = res2.x
            converged = res2.success

    sv = Statevector(ansatz.assign_parameters(best_params)).data
    mz_vqe = float(np.real(sv.conj() @ Mz_mat @ sv))
    fid = float(np.real(sv.conj() @ P0 @ sv))

    return {
        "J": J, "Jp": Jp, "b": b, "e_vqe": best_e, "e_exact": e_exact,
        "delta_e": best_e - e_exact,
        "fidelity": fid, "mz_vqe": mz_vqe, "mz_exact": mz_exact,
        "n_params": n_params, "degeneracy": deg,
        "ansatz_type": ansatz_type, "converged": converged,
        "dm_mode": dm_mode, "D": D,
    }


def run_vqe_forced(J, Jp, b, branch, K=1, n_restarts=4, seed=42):
    """VQE con ramo PMA forzato (non switch automatico) -- mirror di
    run_vqe_forced nel notebook del dimero."""
    rng = np.random.default_rng(seed)
    hamiltonian = trimer_hamiltonian(J, Jp, b)
    estimator = StatevectorEstimator()
    ansatz = make_pma_ansatz_forced(branch, K)

    best_e = np.inf
    for _ in range(n_restarts):
        x0 = rng.uniform(-np.pi, np.pi, ansatz.num_parameters)
        res1 = minimize(_energy, x0, args=(ansatz, hamiltonian, estimator),
                         method="COBYLA", options={"maxiter": 2000, "tol": 1e-10})
        res2 = minimize(_energy, res1.x, args=(ansatz, hamiltonian, estimator),
                         method="L-BFGS-B", options={"maxiter": 2000, "ftol": 1e-14})
        best_e = min(best_e, res2.fun)
    return best_e


def vqe_sweep(b_values, J=1.0, Jp=0.4, ansatz_type="PMA", reps=2, K=1,
              n_restarts=6, seed=42, dm_mode=None, D=0.0, verbose=True):
    results = []
    for i, b in enumerate(b_values):
        r = run_vqe(J, Jp, b, ansatz_type=ansatz_type, reps=reps, K=K,
                     n_restarts=n_restarts, seed=seed + i, dm_mode=dm_mode, D=D)
        results.append(r)
        if verbose:
            print(f"  b/J={b/J:5.2f}  E={r['e_vqe']:8.4f}  "
                  f"dE={r['delta_e']:+.2e}  F={r['fidelity']:.4f}"
                  f"  <Mz>={r['mz_vqe']:+.3f}  (deg={r['degeneracy']})")
    return results


def _plot_row(axes, results, J, row_label, color):
    b_arr = np.array([r["b"] for r in results])
    e_vqe = np.array([r["e_vqe"] for r in results])
    e_exact = np.array([r["e_exact"] for r in results])
    delta_e = np.array([r["delta_e"] for r in results])
    fid = np.array([r["fidelity"] for r in results])
    mz_vqe = np.array([r["mz_vqe"] for r in results])
    mz_exact = np.array([r["mz_exact"] for r in results])
    n_par = results[0]["n_params"]

    kw = dict(color=color, lw=1.5, ms=4)

    ax = axes[0]
    ax.plot(b_arr / J, e_exact, "k-", lw=2, label="Esatto")
    ax.plot(b_arr / J, e_vqe, "--o", label=f"VQE ({n_par} par)", **kw)
    ax.set_ylabel("E / J"); ax.set_title("Energia")
    ax.legend(fontsize=7); ax.set_xlabel("b / J")

    ax = axes[1]
    ax.semilogy(b_arr / J, np.clip(delta_e, 1e-16, None), "-o", **kw)
    ax.set_ylabel(r"$\Delta E$ (log)"); ax.set_title("Errore energetico")
    ax.set_xlabel("b / J")

    ax = axes[2]
    ax.plot(b_arr / J, fid, "-o", **kw)
    ax.set_ylim(-0.05, 1.05)
    ax.set_ylabel(r"$\mathcal{F}$ (proiettore)"); ax.set_title("Fidelity")
    ax.set_xlabel("b / J")

    ax = axes[3]
    ax.plot(b_arr / J, mz_exact, "k-", lw=2, label="Esatto")
    ax.plot(b_arr / J, mz_vqe, "--o", label="VQE", **kw)
    ax.set_ylabel(r"$\langle M_z\rangle$"); ax.set_title("Magnetizzazione")
    ax.legend(fontsize=7); ax.set_xlabel("b / J")

    axes[0].annotate(row_label, xy=(-0.35, 0.5), xycoords="axes fraction",
                      fontsize=8, fontweight="bold", va="center", ha="right",
                      rotation=90)
