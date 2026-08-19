"""
VQE per il dimero di spin-1/2 (N=2).

Ansatz disponibili:
    HA  — hardware-efficient: n_local (Ry + CZ), reps=2, 6 parametri
    PMA — physically motivated (Crippa et al. 2021):
          gate W_ij(theta) = CNOT . (Ry(theta) x I) . CNOT
          stato iniziale dipendente da B/J:
            B/J < 2  -> singoletto locale (|01>-|10>)/sqrt(2)
            B/J >= 2 -> |11>
          2 parametri (K=1)

Pattern Qiskit 2.x (>= 2.1):
    - StatevectorEstimator  (qiskit.primitives)
    - n_local               (qiskit.circuit.library)  per HA
    - QuantumCircuit         (qiskit)                  per PMA
    - scipy.optimize.minimize

Output: griglia 4 righe x 4 pannelli (HA D=0, HA D=0.2, PMA D=0, PMA D=0.2)
        salvata come .png (raster) e .pdf (vettoriale, zoomabile).

Dipende da dimer_exact.py.
"""

import numpy as np
from scipy.optimize import minimize
from qiskit.primitives import StatevectorEstimator
from qiskit.circuit.library import n_local
from qiskit.circuit import QuantumCircuit, ParameterVector
from qiskit.quantum_info import Statevector

from dimer_exact import dimer_hamiltonian, exact_sweep, analytic_eigenvalues
from dimer_exact import magnetization_operator


# ================================================================== HA ansatz

def make_ha_ansatz(reps=2):
    """Ansatz hardware-efficient: Ry + CZ, 2*(reps+1) parametri."""
    return n_local(
        num_qubits=2,
        rotation_blocks="ry",
        entanglement_blocks="cz",
        entanglement="full",
        reps=reps,
        insert_barriers=False,
    )


# ================================================================== PMA ansatz
# Riferimento: Crippa et al., Magnetochemistry 7, 117 (2021), eq. (6)-(9)
#
# Gate W_ij(theta):
#   CNOT(ctrl=0, tgt=1) -> Ry(theta) su qubit 0 -> CNOT(ctrl=0, tgt=1)
#
# Stato iniziale:
#   B/J < 2  : singoletto (|01>-|10>)/sqrt(2)  preparato con X,H,CNOT,X
#   B/J >= 2 : |11>  preparato con X,X

def make_pma_ansatz(b, J=1.0, K=1):
    """Ansatz fisicamente motivato per il dimero (N=2, K layer).

    Struttura:
        |psi0(b/J)> -> [W_01(theta_k)]_{k=1..K}

    Stato iniziale:
        B/J < 2  -> singoletto locale
        B/J >= 2 -> |11>

    Numero di parametri: K.
    """
    theta = ParameterVector("th", K)
    qc = QuantumCircuit(2)

    # --- stato iniziale
    if b / J < 2.0:
        # singoletto: (|01> - |10>) / sqrt(2)
        # preparazione: X q0 -> H q0 -> CNOT(0->1) -> X q0
        qc.x(0)
        qc.h(0)
        qc.cx(0, 1)
        qc.x(0)
    else:
        # |11>
        qc.x(0)
        qc.x(1)

    # --- layer W_ij(theta)
    for k in range(K):
        # W_01(theta_k) = CNOT . Ry(theta) . CNOT
        qc.cx(0, 1)
        qc.ry(theta[k], 0)
        qc.cx(0, 1)

    return qc


# ================================================================== funzioni VQE

def _energy(params, ansatz, hamiltonian, estimator):
    """Funzione obiettivo per scipy.optimize.minimize."""
    pub = (ansatz, hamiltonian, [params])
    result = estimator.run([pub]).result()
    return float(result[0].data.evs.item())


def run_vqe(b, J=1.0, D=0.0, ansatz_type="HA", reps=2, K=1,
            n_restarts=3, method="L-BFGS-B", seed=42):
    """VQE a un singolo valore di campo b.

    Parametri
    ---------
    ansatz_type : 'HA' oppure 'PMA'
    reps        : layer ansatz HA (ignorato per PMA)
    K           : layer ansatz PMA (ignorato per HA)

    Ritorna dict con: b, e_vqe, e_exact, delta_e, fidelity,
                      mz_vqe, mz_exact, n_params, ansatz_type, converged.
    """
    rng = np.random.default_rng(seed)
    hamiltonian = dimer_hamiltonian(b, J, D)
    estimator   = StatevectorEstimator()

    if ansatz_type == "HA":
        ansatz = make_ha_ansatz(reps)
    else:
        ansatz = make_pma_ansatz(b, J, K)

    n_params = ansatz.num_parameters

    # benchmark esatto
    res_exact = exact_sweep([b], J=J, D=D)
    e_exact   = float(res_exact["gs_energy"][0])
    gs_exact  = res_exact["gs_state"][0]
    mz_exact  = float(res_exact["gs_mz"][0])
    Mz_mat    = magnetization_operator().to_matrix()

    best_e, best_params, converged = np.inf, None, False
    for _ in range(n_restarts):
        x0 = rng.uniform(-np.pi, np.pi, n_params)
        res = minimize(
            _energy, x0,
            args=(ansatz, hamiltonian, estimator),
            method=method,
            options={"maxiter": 2000, "ftol": 1e-12},
        )
        if res.fun < best_e:
            best_e      = res.fun
            best_params = res.x
            converged   = res.success

    sv     = Statevector(ansatz.assign_parameters(best_params)).data
    mz_vqe = float(np.real(sv.conj() @ Mz_mat @ sv))
    fid    = float(np.abs(sv.conj() @ gs_exact))

    return {
        "b": b, "e_vqe": best_e, "e_exact": e_exact,
        "delta_e": best_e - e_exact,
        "fidelity": fid, "mz_vqe": mz_vqe, "mz_exact": mz_exact,
        "n_params": n_params, "ansatz_type": ansatz_type, "converged": converged,
    }


def vqe_sweep(b_values, J=1.0, D=0.0, ansatz_type="HA", reps=2, K=1,
              n_restarts=3, method="L-BFGS-B", seed=42, verbose=True):
    """VQE su griglia di campi b. Ritorna lista di dict."""
    results = []
    for i, b in enumerate(b_values):
        r = run_vqe(b, J=J, D=D, ansatz_type=ansatz_type, reps=reps, K=K,
                    n_restarts=n_restarts, method=method, seed=seed + i)
        results.append(r)
        if verbose:
            print(f"  b/J={b/J:5.2f}  E={r['e_vqe']:8.4f}  "
                  f"dE={r['delta_e']:+.2e}  F={r['fidelity']:.4f}"
                  f"  <Mz>={r['mz_vqe']:+.3f}")
    return results


# ================================================================== plot griglia

def _plot_row(axes, results, J, row_label, color):
    """Disegna una riga della griglia 4x4."""
    import matplotlib.pyplot as plt

    b_arr    = np.array([r["b"]        for r in results])
    e_vqe    = np.array([r["e_vqe"]    for r in results])
    e_exact  = np.array([r["e_exact"]  for r in results])
    delta_e  = np.array([r["delta_e"]  for r in results])
    fid      = np.array([r["fidelity"] for r in results])
    mz_vqe   = np.array([r["mz_vqe"]  for r in results])
    mz_exact = np.array([r["mz_exact"] for r in results])
    n_par    = results[0]["n_params"]

    kw = dict(color=color, lw=1.5, ms=4)

    # col 0: energia
    ax = axes[0]
    ax.plot(b_arr / J, e_exact, "k-", lw=2, label="Esatto")
    ax.plot(b_arr / J, e_vqe, "--o", label=f"VQE ({n_par} par)", **kw)
    ax.axvline(2.0, color="0.75", ls=":", lw=0.8)
    ax.set_ylabel("E / J"); ax.set_title("Energia")
    ax.legend(fontsize=7); ax.set_xlabel("B / J")

    # col 1: errore log
    ax = axes[1]
    ax.semilogy(b_arr / J, np.clip(delta_e, 1e-16, None), "-o", **kw)
    ax.axvline(2.0, color="0.75", ls=":", lw=0.8)
    ax.set_ylabel(r"$\Delta E$ (log)"); ax.set_title("Errore energetico")
    ax.set_xlabel("B / J")

    # col 2: fidelity
    ax = axes[2]
    ax.plot(b_arr / J, fid, "-o", **kw)
    ax.axvline(2.0, color="0.75", ls=":", lw=0.8)
    ax.set_ylim(-0.05, 1.05)
    ax.set_ylabel(r"$\mathcal{F}$"); ax.set_title("Fidelity")
    ax.set_xlabel("B / J")

    # col 3: magnetizzazione
    ax = axes[3]
    ax.plot(b_arr / J, mz_exact, "k-", lw=2, label="Esatto")
    ax.plot(b_arr / J, mz_vqe, "--o", label="VQE", **kw)
    ax.axvline(2.0, color="0.75", ls=":", lw=0.8)
    ax.set_ylim(-1.15, 0.15)
    ax.set_ylabel(r"$\langle M_z\rangle$"); ax.set_title("Magnetizzazione")
    ax.legend(fontsize=7); ax.set_xlabel("B / J")

    # etichetta riga
    axes[0].annotate(row_label, xy=(-0.35, 0.5), xycoords="axes fraction",
                     fontsize=8, fontweight="bold", va="center", ha="right",
                     rotation=90)


def plot_grid(all_results, J=1.0, base_path="vqe_dimer"):
    """Griglia 4 righe x 4 colonne. Salva .png e .pdf."""
    import matplotlib.pyplot as plt

    rows = [
        ("HA  D=0",   "tab:blue"),
        ("HA  D=0.2", "tab:orange"),
        ("PMA D=0",   "tab:green"),
        ("PMA D=0.2", "tab:red"),
    ]

    fig, axes = plt.subplots(4, 4, figsize=(18, 14))
    fig.suptitle("VQE dimero N=2 — confronto HA vs PMA, D=0 vs D=0.2", fontsize=12)

    for row_idx, (label, color) in enumerate(rows):
        _plot_row(axes[row_idx], all_results[row_idx], J, label, color)

    fig.tight_layout(rect=[0, 0, 1, 0.97])

    for ext in ["png", "pdf"]:
        path = f"{base_path}.{ext}"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"[ok] salvato: {path}")

    plt.show()


# ================================================================== main

if __name__ == "__main__":
    import sys

    J       = 1.0
    reps_HA = 2       # 6 parametri
    K_PMA   = 1       # 2 parametri (K=1, Crippa eq.7)
    n_b     = 20
    n_rest  = 3

    # verifica API
    print("=" * 55)
    print("Verifica API Qiskit 2.x")
    ok = True
    for mod, name in [
        ("qiskit.primitives.StatevectorEstimator", "StatevectorEstimator"),
        ("qiskit.circuit.library.n_local",         "n_local"),
    ]:
        try:
            parts = mod.rsplit(".", 1)
            getattr(__import__(parts[0], fromlist=[parts[1]]), parts[1])
            print(f"  {name:<28}: OK")
        except Exception as e:
            print(f"  {name:<28}: ERRORE — {e}"); ok = False
    if not ok:
        sys.exit(1)
    print("=" * 55)

    b_values = np.linspace(0.0, 5.0, n_b)

    configs = [
        ("HA",  0.0,  reps_HA, K_PMA),
        ("HA",  0.2,  reps_HA, K_PMA),
        ("PMA", 0.0,  reps_HA, K_PMA),
        ("PMA", 0.2,  reps_HA, K_PMA),
    ]

    all_results = []
    for ansatz_type, D, reps, K in configs:
        label = f"{ansatz_type}  D={D}"
        print(f"\n{'='*55}")
        print(f"Run: {label}")
        n_par = (make_ha_ansatz(reps).num_parameters if ansatz_type == "HA"
                 else make_pma_ansatz(b_values[0], J, K).num_parameters)
        print(f"Parametri ansatz: {n_par}")
        print(f"{'='*55}")
        res = vqe_sweep(b_values, J=J, D=D, ansatz_type=ansatz_type,
                        reps=reps, K=K, n_restarts=n_rest, verbose=True)
        all_results.append(res)

    # confronto finale con formula chiusa (D=0)
    print("\n--- Confronto con formula chiusa (D=0, HA e PMA) ---")
    for row_idx, (ansatz_type, D, _, _) in enumerate(configs):
        if D != 0.0:
            continue
        print(f"\n  {ansatz_type}:")
        for r in all_results[row_idx]:
            e_an = analytic_eigenvalues(r["b"], J)[0]
            print(f"    b/J={r['b']/J:5.2f}  |dE_analitico|={abs(r['e_vqe']-e_an):.2e}")

    plot_grid(all_results, J=J, base_path="vqe_dimer")
