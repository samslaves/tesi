"""Sweep sistematico degli ansatz per il trimero a catena aperta — Fase 5.

Un solo sweep che include da subito RBS e W, D=0 e DM acceso (come da piano
concordato: non due tappe separate come per l'anello, perche' l'ipotesi da
testare e' gia' nota -- ma va VERIFICATA sui dati della catena, non assunta).

Punto di lavoro DM confermato al checkpoint 1: J=1, b_c=3J=3.0, D=0.15.
Il DM e' acceso su TUTTA la griglia in b (non solo a b_c), per vedere dove
la differenza fra le famiglie emerge.

Cache incrementale: rilanciabile senza ricalcolare.
"""

import os
import json
import time

import numpy as np
from scipy.optimize import minimize
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import Statevector

from trimer_chain_exact import (
    trimer_hamiltonian, trimer_hamiltonian_dm, critical_field,
    exact_sweep, exact_sweep_dm,
    ground_state_projector, ground_state_projector_dm,
)
from ansatz_catena import build_ansatze

J = 1.0
D_DM = 0.15
BC = critical_field(J)                       # 3.0
B_GRID = sorted(set(np.linspace(0.05, 2 * BC, 9).round(3).tolist() + [BC]))
CACHE_PATH = "trimer_chain_dm_sweep_cache.json"

ANSATZE = build_ansatze()
ESTIMATOR = StatevectorEstimator()


def _energy(params, ansatz, H_matrix):
    """Valore di aspettazione esatto via prodotto matriciale.

    Equivalente a StatevectorEstimator (verificato: max scarto 1.8e-15 su
    15 ansatz x 3 punti casuali) ma senza l'overhead del primitive.
    """
    sv = Statevector(ansatz.assign_parameters(params)).data
    return float(np.real(sv.conj() @ H_matrix @ sv))


def run_vqe(ansatz, b, D, n_restarts=2, seed=42):
    """VQE su energia, poi fidelity contro il proiettore sul fondamentale."""
    rng = np.random.default_rng(seed)
    if D != 0.0:
        hamiltonian = trimer_hamiltonian_dm(J, b, D).to_matrix()
        e_exact = float(exact_sweep_dm(np.array([b]), J, D)["gs_energy"][0])
        P0, _, deg = ground_state_projector_dm(J, b, D)
    else:
        hamiltonian = trimer_hamiltonian(J, b).to_matrix()
        e_exact = float(exact_sweep(np.array([b]), J=J)["gs_energy"][0])
        P0, _, deg = ground_state_projector(J, b)

    best_e, best_params = np.inf, None
    for _ in range(n_restarts):
        x0 = rng.uniform(-np.pi, np.pi, ansatz.num_parameters)
        r1 = minimize(_energy, x0, args=(ansatz, hamiltonian),
                      method="COBYLA", options={"maxiter": 2000, "tol": 1e-10})
        r2 = minimize(_energy, r1.x, args=(ansatz, hamiltonian),
                      method="L-BFGS-B", options={"maxiter": 2000, "ftol": 1e-14})
        if r2.fun < best_e:
            best_e, best_params = r2.fun, r2.x

    sv = Statevector(ansatz.assign_parameters(best_params)).data
    fid = float(np.real(sv.conj() @ P0 @ sv))
    return {"e_vqe": best_e, "e_exact": e_exact, "delta_e": best_e - e_exact,
            "fidelity": fid, "n_params": int(ansatz.num_parameters),
            "degeneracy": int(deg)}


def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=1)


def main():
    cache = load_cache()
    n_attesi = len(ANSATZE) * len(B_GRID) * 2
    print(f"b_c = {BC},  D_DM = {D_DM}")
    print(f"griglia ({len(B_GRID)} punti): {B_GRID}")
    print(f"ansatz: {len(ANSATZE)}   punti attesi: {n_attesi}")

    t0 = time.time()
    n_new = 0
    for name, ansatz in ANSATZE.items():
        for b in B_GRID:
            for tag, D in [("D0", 0.0), ("DM", D_DM)]:
                key = f"{tag}|{name}|{b}"
                if key in cache:
                    continue
                cache[key] = run_vqe(ansatz, b, D)
                n_new += 1
                save_cache(cache)
                if n_new % 5 == 0:
                    print(f"  ... {n_new} nuovi, {time.time()-t0:.0f}s",
                          flush=True)
    save_cache(cache)
    print(f"[ok] {n_new} punti nuovi in {time.time()-t0:.0f}s "
          f"({len(cache)} in cache)")


if __name__ == "__main__":
    main()
