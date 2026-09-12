"""Correlatori dinamici rumorosi con readout GENUINAMENTE campionato a shot
finiti, trimero ad anello -- mirror di correlatori_shots_dimero.py (Parte 2
del dimero, Documenti 8-11): nessuna formula analitica di correzione, solo
misura vera (ReadoutError di Aer agganciato al NoiseModel, measure_all,
shot finiti).

Convenzione qubit: ancilla = qubit 3 (non 0 come sul dimero) -- il bit
dell'ancilla e' il PRIMO carattere della stringa di misura a 4 bit,
verificato esplicitamente (vedi correlatori_readout_asimmetrico_trimero_
anello.py, dove lo stesso controllo e' gia' stato fatto per l'estensione
readout asimmetrico)."""
import numpy as np
from qiskit_aer import AerSimulator
from qiskit_aer.noise import ReadoutError

from noise_model_trimero_anello import build_noise_model
from correlatori_rumorosi_trimero_anello import (
    build_noisy_correlator_circuit, ANCILLA,
    J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
)

SHOTS_DEFAULT = 100_000


def correlator_shots(i, alpha, j, beta, t, N, ansatz_params,
                      p01=0.023, p10=0.023, eps_1q=2.9e-4, eps_2q=3.8e-3,
                      J=J_DEFAULT, Jp=JP_DEFAULT, b=B_DEFAULT, D=D_DEFAULT,
                      shots=SHOTS_DEFAULT, seed=0):
    """Re/Im di C_ij^{alpha,beta}(t), misura vera a shot finiti: rumore di
    gate (eps_1q, eps_2q) piu' ReadoutError vero (p01, p10) sulla sola
    ancilla, nessuna correzione analitica applicata a posteriori."""
    nm, _ = build_noise_model(eps_1q=eps_1q, eps_2q=eps_2q, p_readout=0.0)
    if p01 > 0 or p10 > 0:
        conf_matrix = [[1 - p01, p01], [p10, 1 - p10]]
        nm.add_readout_error(ReadoutError(conf_matrix), [ANCILLA])

    ris = {}
    sim = AerSimulator(noise_model=nm, seed_simulator=seed)
    for part in ("re", "im"):
        qc = build_noisy_correlator_circuit(i, alpha, j, beta, t, N, J, Jp, b, D,
                                             part, ansatz_params)
        qc = qc.copy()
        qc.measure_all()
        counts = sim.run(qc, shots=shots).result().get_counts()
        # ancilla = qubit 3 -> PRIMO carattere della stringa a 4 bit
        p0 = sum(c for bitstr, c in counts.items() if bitstr[0] == "0") / shots
        p1 = sum(c for bitstr, c in counts.items() if bitstr[0] == "1") / shots
        ris[part] = p0 - p1
    return ris["re"] + 1j * ris["im"]


if __name__ == "__main__":
    data = np.load("w2q6_params_optimal.npz")
    vqe_params = data["params"]

    print("=" * 70)
    print("CONTROLLO: indicizzazione ancilla, coerenza col rumore nullo")
    print("=" * 70)
    from correlatori_rumorosi_trimero_anello import correlator_rumoroso
    nm_ref, _ = build_noise_model()
    for N in [3, 5]:
        c_formula = correlator_rumoroso(2, "x", 1, "x", 2.0, N, J_DEFAULT, JP_DEFAULT,
                                         B_DEFAULT, D_DEFAULT, vqe_params,
                                         noise_model=nm_ref, p_readout=0.023)
        c_shots = correlator_shots(2, "x", 1, "x", 2.0, N, vqe_params,
                                    p01=0.023, p10=0.023, shots=200_000, seed=0)
        print(f"  N={N}: formula analitica={c_formula:.4f}   shot finiti={c_shots:.4f}   "
              f"|diff|={abs(c_formula-c_shots):.2e}")
