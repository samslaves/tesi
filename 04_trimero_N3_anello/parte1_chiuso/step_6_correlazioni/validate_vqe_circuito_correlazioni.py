"""Validazione: il circuito dei correlatori con preparazione VQE reale
(ansatz W-2q.6, parametri ottimali da w2q6_params_optimal.npz) riproduce le
81 combinazioni C_ij^{alpha,beta}(t) ottenute con la preparazione esatta
delle ampiezze (prepare_state), entro un errore consistente con la
fidelity F=0.99999999999961 dell'ansatz al punto di lavoro.
"""
import itertools
import numpy as np

from circuito_correlazioni_trimero_anello import (
    ground_state, correlator_from_circuit,
)

J, Jp, b, D = 1.0, 0.4, 2.4, 0.15
T = 1.3
N = 200

SITES = (1, 2, 3)
COMPS = ('x', 'y', 'z')

data = np.load("w2q6_params_optimal.npz")
params = data["params"]
print(f"fidelity ansatz (da vqe_w2q6_trimero_anello.py) = {float(data['fidelity']):.14f}")

psi0, _ = ground_state(J, Jp, b, D)

max_err = 0.0
sum_err = 0.0
n = 0
worst = None
for i, al in itertools.product(SITES, COMPS):
    for j, be in itertools.product(SITES, COMPS):
        c_exact = correlator_from_circuit(i, al, j, be, T, N, J, Jp, b, D, psi0)
        c_vqe = correlator_from_circuit(i, al, j, be, T, N, J, Jp, b, D,
                                         ansatz_params=params)
        err = abs(c_vqe - c_exact)
        sum_err += err
        n += 1
        if err > max_err:
            max_err = err
            worst = (i, al, j, be, c_exact, c_vqe)

print(f"\nCombinazioni confrontate: {n}")
print(f"errore medio |C_vqe - C_exact| = {sum_err / n:.3e}")
print(f"errore massimo                = {max_err:.3e}")
i, al, j, be, c_exact, c_vqe = worst
print(f"  peggiore: C_{i}{j}^{al}{be}  esatto={c_exact:.10f}  vqe={c_vqe:.10f}")