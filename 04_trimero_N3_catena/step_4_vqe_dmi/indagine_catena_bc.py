"""Indagine dedicata al punto critico, con molti restart -- mirror di
analisi_espressivita_PMA_anello.ipynb, per distinguere un vero tetto
strutturale da un artefatto dei 2 restart dello sweep sistematico."""

import numpy as np
from scipy.optimize import minimize
from qiskit.quantum_info import Statevector

from trimer_chain_exact import critical_field, ground_state_projector_dm
from ansatz_catena import build_ansatze

A = build_ansatze()
J, D = 1.0, 0.15
bc = critical_field(J)
P0, E0, deg = ground_state_projector_dm(J, bc, D)
print(f"b_c = {bc}, D = {D}, degenerazione fondamentale = {deg}")


def max_fidelity(qc, P0, n_restarts, seed=3):
    def neg_fid(params):
        sv = Statevector(qc.assign_parameters(params)).data
        return -np.real(sv.conj() @ P0 @ sv)
    rng = np.random.default_rng(seed)
    best = 0.0
    for _ in range(n_restarts):
        x0 = rng.uniform(-np.pi, np.pi, qc.num_parameters)
        r = minimize(neg_fid, x0, method="COBYLA", options={"maxiter": 600, "tol": 1e-12})
        r2 = minimize(neg_fid, r.x, method="L-BFGS-B", options={"maxiter": 600, "ftol": 1e-16})
        best = max(best, -r2.fun)
    return best


CANDIDATI = ["W-2q.8", "W-2qC.K1", "W-1q.6", "W-1q.9"]

print(f"{'ansatz':14s} {'par':>4s} {'fid (60 restart)':>18s}")
for name in CANDIDATI:
    qc = A[name]
    best = max_fidelity(qc, P0, n_restarts=60)
    print(f"{name:14s} {qc.num_parameters:4d} {best:18.10f}")
