"""
VQE per il trimero di spin-1/2 (N=3), anello/triangolo isoscele.

Ansatz disponibili:
    HA  — hardware-efficient: n_local (Ry + CZ), reps=2, 12 parametri
    PMA — physically motivated, generalizzazione a 3 qubit di PMA-2q.3
          (blocco RBS raccomandato — vedi scelta_ansatz_RBS_vs_W.md — non
          il gate W_ij(theta) di Crippa et al., piu' costoso e ridondante
          per H reale):
              stato iniziale = stato di Kambe (blocco, M) del settore che
                                contiene il fondamentale a quel (J,J',b)
              + K layer di RBS indipendenti sui tre bond (12,23,31)
              + 1 layer finale di Ry indipendenti sui tre qubit
          parametri: 3K + 3

Convenzione sito<->qubit: IDENTICA a trimer_ring_exact.py
    site1 -> qubit 2, site2 -> qubit 1, site3 -> qubit 0
Bond fisici (coppie di qubit): bond12=(2,1), bond23=(1,0), bond31=(0,2).

Stato iniziale: preparazione a costo minimo (solo porte X) per i blocchi
C e A-estremo (banali, vedi Tabella 2 di derivazione_stati_kambe_trimero.pdf);
per i blocchi A-intermedio e B (stati di tipo W, non banali) si usa
QuantumCircuit.prepare_state come implementazione di riferimento — CORRETTA
ma non gate-ottimizzata; un circuito nativo a basso costo per questi due
casi resta lavoro futuro (rilevante solo per la Parte 2, rumore).

NOTA — questo ansatz e' una PRIMA GENERALIZZAZIONE ragionevole di PMA-2q.3
a N=3, non (ancora) dimostrata a conteggio minimo di parametri come nel
caso N=2 (S^3=3). La determinazione del minimo teorico per N=3 resta aperta.

Pattern Qiskit 2.x: StatevectorEstimator, n_local, QuantumCircuit,
scipy.optimize.minimize.

Metodologia di ottimizzazione (mandato del relatore): multistart R=6,
reinizializzazione nel ciclo ESTERNO, COBYLA + polish L-BFGS-B finale.

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
)

# bond fisici (coppie di qubit), convenzione site1->q2, site2->q1, site3->q0
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


# ================================================================== blocco RBS
# Stessa implementazione unica gia' validata per N=2 (self-test errore
# ~1e-16 in confronto_ansatz_entangler.ipynb): rotazione di Givens reale nel
# settore {|01>,|10>} della coppia di qubit (q0,q1).

def rbs_block(qc, phi, q0, q1):
    sub = QuantumCircuit(2, name="RBS")
    sub.h(0); sub.h(1); sub.cz(0, 1)
    sub.ry(phi, 0); sub.ry(-phi, 1)
    sub.cz(0, 1); sub.h(0); sub.h(1)
    qc.append(sub.to_gate(label="RBS"), [q0, q1])


# ================================================================== stato iniziale

def _select_target_block(J, Jp, b):
    """Sceglie (blocco, M) del fondamentale a questo (J,J',b).

    Per b>0 il ramo energeticamente favorito e' sempre quello a M piu'
    negativo del blocco fondamentale (E = E_blocco + 2bM, b>0):
      b < b_c  -> blocco di bassa energia a b=0 (B o C, mappa dei segni),
                  M = -1/2
      b >= b_c -> blocco A, M = -3/2 (stato prodotto |111>)
    """
    bc = critical_field(J, Jp)
    E_B, E_C = J - 4 * Jp, -3 * J
    low_field_block = "C" if E_C <= E_B else "B"
    if b < bc:
        return low_field_block, -0.5
    return "A", -1.5


def _prepare_initial_state(qc, block, M):
    """Circuito di preparazione dello stato di Kambe (blocco, M).

    Banale (solo X) per C e A-estremo; generico (prepare_state, corretto
    ma non gate-ottimizzato) per B e A-intermedio — vedi nota nel docstring
    del modulo.
    """
    q_site1, q_site2, q_site3 = 2, 1, 0

    if block == "C":
        # singoletto su (site1,site2) = (q2,q1): X,H,CNOT,X (stesso schema del dimero)
        qc.x(q_site1); qc.h(q_site1); qc.cx(q_site1, q_site2); qc.x(q_site1)
        if M == -0.5:
            qc.x(q_site3)
        return "banale (X,H,CNOT,X + eventuale X)"

    if block == "A" and M == -1.5:
        qc.x(q_site1); qc.x(q_site2); qc.x(q_site3)
        return "banale (solo X)"

    if block == "A" and M == 1.5:
        return "banale (nessuna porta, |000>)"

    # B, oppure A a M=+-1/2: stato di tipo W, preparazione generica
    vec = kambe_states()[(block, M)]
    qc.prepare_state(vec.tolist(), [0, 1, 2])
    return "generica (prepare_state, non gate-ottimizzata)"


# ================================================================== PMA ansatz

def make_pma_ansatz(J, Jp, b, K=1):
    """Ansatz fisicamente motivato per il trimero ad anello (N=3, K layer).

    Struttura:
        |Kambe(blocco,M)> -> [RBS_12(a_k), RBS_23(b_k), RBS_31(c_k)]_{k=1..K}
                           -> Ry indipendenti sui 3 qubit (layer finale)

    Numero di parametri: 3K + 3.
    """
    block, M = _select_target_block(J, Jp, b)
    theta = ParameterVector("th", 3 * K + 3)
    qc = QuantumCircuit(3)

    _prepare_initial_state(qc, block, M)

    idx = 0
    for _ in range(K):
        rbs_block(qc, theta[idx], *BOND12); idx += 1
        rbs_block(qc, theta[idx], *BOND23); idx += 1
        rbs_block(qc, theta[idx], *BOND31); idx += 1
    for q in range(3):
        qc.ry(theta[idx], q); idx += 1

    return qc


# ================================================================== funzioni VQE

def _energy(params, ansatz, hamiltonian, estimator):
    """Funzione obiettivo per scipy.optimize.minimize."""
    pub = (ansatz, hamiltonian, [params])
    result = estimator.run([pub]).result()
    return float(result[0].data.evs.item())


def run_vqe(J, Jp, b, ansatz_type="PMA", reps=2, K=1,
            n_restarts=6, seed=42):
    """VQE a un singolo punto (J,J',b).

    Ottimizzazione a due stadi (mandato del relatore): per ciascun
    restart, COBYLA seguito da polish L-BFGS-B; il migliore fra gli
    R restart (reinizializzazione nel ciclo esterno) viene tenuto.

    Ritorna dict con: b, e_vqe, e_exact, delta_e, fidelity (proiettore sul
    multipletto fondamentale, robusta a degenerazione), mz_vqe, mz_exact,
    n_params, degenerazione, ansatz_type, converged.
    """
    rng = np.random.default_rng(seed)
    hamiltonian = trimer_hamiltonian(J, Jp, b)
    estimator = StatevectorEstimator()

    if ansatz_type == "HA":
        ansatz = make_ha_ansatz(reps)
    else:
        ansatz = make_pma_ansatz(J, Jp, b, K)

    n_params = ansatz.num_parameters

    # benchmark esatto
    res_exact = exact_sweep([b], J=J, Jp=Jp)
    e_exact = float(res_exact["gs_energy"][0])
    mz_exact = float(res_exact["gs_mz"][0])
    Mz_mat = magnetization_operator().to_matrix()
    P0, _, deg = ground_state_projector(J, Jp, b)

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
    }


def vqe_sweep(b_values, J=1.0, Jp=0.4, ansatz_type="PMA", reps=2, K=1,
              n_restarts=6, seed=42, verbose=True):
    """VQE su griglia di campi b, a (J,J') fissati. Ritorna lista di dict."""
    results = []
    for i, b in enumerate(b_values):
        r = run_vqe(J, Jp, b, ansatz_type=ansatz_type, reps=reps, K=K,
                    n_restarts=n_restarts, seed=seed + i)
        results.append(r)
        if verbose:
            print(f"  b/J={b/J:5.2f}  E={r['e_vqe']:8.4f}  "
                  f"dE={r['delta_e']:+.2e}  F={r['fidelity']:.4f}"
                  f"  <Mz>={r['mz_vqe']:+.3f}  (deg={r['degeneracy']})")
    return results


# ================================================================== self-test

def _self_test():
    """Verifica strutturale dell'ansatz PMA prima di ogni ottimizzazione."""
    print("=" * 70)
    print("[self-test] ansatz PMA a parametri nulli == stato di Kambe iniziale")
    J, Jp = 1.0, 0.4
    max_err = 0.0
    for b in [0.5, 1.5, 3.0]:   # un punto per regione (basso campo, alto campo)
        block, M = _select_target_block(J, Jp, b)
        ansatz = make_pma_ansatz(J, Jp, b, K=1)
        sv0 = Statevector(ansatz.assign_parameters(
            np.zeros(ansatz.num_parameters))).data
        target = kambe_states()[(block, M)]
        # confronto a meno di fase globale (irrilevante fisicamente):
        # F=1 <=> |<sv0|target>|=1
        overlap = np.vdot(sv0, target)
        err = abs(abs(overlap) - 1.0)
        max_err = max(max_err, err)
        print(f"    b={b}: blocco target=({block},{M:+.1f}), "
              f"||ansatz(0) - Kambe|| = {err:.2e}")
    print(f"    errore massimo = {max_err:.3e}")
    assert max_err < 1e-10, "l'ansatz a parametri nulli non riproduce lo stato iniziale atteso"
    print("=" * 70)


# ================================================================== plot

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


def plot_grid(all_results, J=1.0, base_path="vqe_trimer_ring"):
    import matplotlib.pyplot as plt

    rows = [("HA", "tab:blue"), ("PMA", "tab:green")]

    fig, axes = plt.subplots(2, 4, figsize=(18, 7))
    fig.suptitle("VQE trimero anello N=3 — HA vs PMA", fontsize=12)

    for row_idx, (label, color) in enumerate(rows):
        _plot_row(axes[row_idx], all_results[row_idx], J, label, color)

    fig.tight_layout(rect=[0, 0, 1, 0.96])

    for ext in ["png", "pdf"]:
        path = f"{base_path}.{ext}"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"[ok] salvato: {path}")


# ================================================================== main

if __name__ == "__main__":
    _self_test()

    J, Jp = 1.0, 0.4      # punto di lavoro proposto (in attesa di conferma)
    reps_HA = 2           # 9 parametri
    K_PMA = 1             # 6 parametri (3K+3)
    n_b = 10
    n_rest = 6            # mandato del relatore

    bc = critical_field(J, Jp)
    b_values = np.linspace(0.05, 2 * bc, n_b)   # attraversa b_c (blocco C -> A)

    configs = [("HA", reps_HA, K_PMA), ("PMA", reps_HA, K_PMA)]

    all_results = []
    for ansatz_type, reps, K in configs:
        print(f"\n{'=' * 70}\nRun: {ansatz_type}\n{'=' * 70}")
        res = vqe_sweep(b_values, J=J, Jp=Jp, ansatz_type=ansatz_type,
                         reps=reps, K=K, n_restarts=n_rest, verbose=True)
        all_results.append(res)

    plot_grid(all_results, J=J, base_path="vqe_trimer_ring")
