"""Validazione: il circuito dei correlatori con preparazione VQE reale
(ansatz W-2qC.K2) riproduce le 81 combinazioni C_ij^{alpha,beta}(t)
ottenute con la preparazione esatta delle ampiezze (prepare_state), entro
un errore consistente con la fidelity dell'ansatz. Mirror di
validate_vqe_circuito_correlazioni.py (anello), eseguito su ENTRAMBI i
punti di lavoro.
"""
import itertools
import numpy as np

from circuito_correlazioni_trimero_catena import ground_state, correlator_from_circuit

SITES = (1, 2, 3)
COMPS = ('x', 'y', 'z')
T = 1.3
N = 200


def validate_point(J, b, D, npz_file, label):
    data = np.load(npz_file)
    params = data["params"]
    fidelity = float(data["fidelity"])
    print("=" * 78)
    print(f"Punto: {label}  (J={J}, b={b}, D={D})")
    print(f"fidelity ansatz W-2qC.K2 (da {npz_file}) = {fidelity:.14f}")

    psi0, _ = ground_state(J, b, D)

    max_err = 0.0
    sum_err = 0.0
    n = 0
    worst = None
    for i, al in itertools.product(SITES, COMPS):
        for j, be in itertools.product(SITES, COMPS):
            c_exact = correlator_from_circuit(i, al, j, be, T, N, J, b, D, psi0)
            c_vqe = correlator_from_circuit(i, al, j, be, T, N, J, b, D,
                                             ansatz_params=params)
            err = abs(c_vqe - c_exact)
            sum_err += err
            n += 1
            if err > max_err:
                max_err = err
                worst = (i, al, j, be, c_exact, c_vqe)

    print(f"Combinazioni confrontate: {n}")
    print(f"errore medio |C_vqe - C_exact| = {sum_err / n:.3e}")
    print(f"errore massimo                = {max_err:.3e}")
    print(f"riferimento sqrt(1-F)         = {np.sqrt(max(0, 1 - fidelity)):.3e}")
    i, al, j, be, c_exact, c_vqe = worst
    print(f"  peggiore: C_{i}{j}^{al}{be}  esatto={c_exact:.10f}  vqe={c_vqe:.10f}")
    print()


def main():
    validate_point(1.0, 3.0, 0.15, "w2qC_k2_params_vqedm.npz", "VQE-DM (b_c)")
    validate_point(1.0, 3.0073414, 0.3, "w2qC_k2_params_S0.npz", "S0 (Trotter)")


if __name__ == "__main__":
    main()
