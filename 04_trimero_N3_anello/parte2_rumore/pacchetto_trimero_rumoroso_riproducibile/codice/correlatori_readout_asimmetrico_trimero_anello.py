"""
Parte 2, Stadio 6bis -- READOUT ASIMMETRICO (trimero ad anello):
p_01 != p_10, invece del readout simmetrico usato altrove nel pacchetto.

RUOLO NELL'INSIEME DEL PACCHETTO: estensione facoltativa, analoga a
`correlatori_readout_asimmetrico_dimero.py`. Riusa interamente la
costruzione del circuito e la misura a shot finiti di
`correlatori_shots_trimero_anello.py` (Stadio 4bis) -- l'UNICA differenza
e' il ReadoutError agganciato al NoiseModel, qui costruito con una
matrice di confusione generale (non necessariamente simmetrica) invece
che con la matrice simmetrica di `build_noise_model` (Stadio 1).

Perche' l'asimmetria e' fisicamente motivata: sull'hardware reale il
rilassamento T1 agisce durante la misura stessa -- un qubit preparato in
|1> ha probabilita' non nulla di decadere a |0> proprio mentre lo si
legge, rendendo p_10 (leggere 0 quando lo stato vero era 1) tipicamente
maggiore di p_01 (l'eccitazione spontanea durante la misura e' molto
meno probabile). Split illustrativo usato qui, stessa convenzione del
dimero: rapporto p_10/p_01 = 3, stessa media p_readout=2.3e-2 del caso
simmetrico (P_READOUT_REF), per confrontabilita' diretta.

Nota sul registro (verificata esplicitamente, non assunta): il circuito
misura UN SOLO bit classico (l'ancilla) -- la correzione di readout
asimmetrico si applica a quella singola misura, non al numero di qubit
del registro. Il registro a 3 qubit (contro i 2 del dimero) non introduce
quindi nessuna complicazione nuova.
"""
import numpy as np
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

from noise_model_trimero_anello import BASIS_GATES, eps_to_lambda, EPS_1Q_REF, EPS_2Q_REF
from correlatori_shots_trimero_anello import (
    _circuito_con_misura, ancilla_z_shots,
    J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT, SHOTS_DEFAULT,
)


def build_noise_model_asimmetrico(p01, p10, eps_1q=EPS_1Q_REF, eps_2q=EPS_2Q_REF):
    """Stesso NoiseModel di build_noise_model (Stadio 1) per i canali di
    gate, ma con ReadoutError a matrice di confusione GENERALE
    (p01 != p10 permesso) al posto della matrice simmetrica.

    RUOLO NEL MODULO: unica differenza rispetto al caso simmetrico.
    RUOLO NELL'INSIEME: usata al posto di build_noise_model ovunque in
    questa estensione -- i canali di gate (depolarizzante 1q/2q) sono
    IDENTICI, cambia solo la matrice di confusione del readout."""
    lam_1q, lam_2q = eps_to_lambda(eps_1q, eps_2q)
    nm = NoiseModel(basis_gates=BASIS_GATES)
    if lam_1q > 0:
        nm.add_all_qubit_quantum_error(depolarizing_error(lam_1q, 1), ["rz", "sx", "x"])
    if lam_2q > 0:
        nm.add_all_qubit_quantum_error(depolarizing_error(lam_2q, 2), ["cx"])
    conf_matrix = [[1 - p01, p01],
                   [p10, 1 - p10]]
    nm.add_all_qubit_readout_error(ReadoutError(conf_matrix))
    return nm


def correlator_shots_asimmetrico(i, alpha, j, beta, t, N, J, Jp, b, D,
                                  ansatz_params, p01, p10,
                                  eps_1q=EPS_1Q_REF, eps_2q=EPS_2Q_REF,
                                  shots=SHOTS_DEFAULT, seed_simulator=0):
    """Mirror di correlator_shots (Stadio 4bis), con readout asimmetrico
    al posto di quello simmetrico. Stessa logica di misura a shot finiti
    -- solo il NoiseModel cambia."""
    from qiskit_aer import AerSimulator
    nm = build_noise_model_asimmetrico(p01, p10, eps_1q, eps_2q)
    qc_re = _circuito_con_misura(i, alpha, j, beta, t, N, J, Jp, b, D, "re", ansatz_params)
    qc_im = _circuito_con_misura(i, alpha, j, beta, t, N, J, Jp, b, D, "im", ansatz_params)
    z_re = ancilla_z_shots(qc_re, nm, shots, seed_simulator)
    z_im = ancilla_z_shots(qc_im, nm, shots, seed_simulator + 1)
    return z_re + 1j * z_im


if __name__ == "__main__":
    data = np.load("w2q6_params_optimal.npz")
    vqe_params = data["params"]

    P_MEDIO = 0.023  # media = P_READOUT_REF del caso simmetrico (Stadio 1)
    RAPPORTO = 3.0
    # p01 + p10 = 2*P_MEDIO, p10 = RAPPORTO*p01
    p01 = 2 * P_MEDIO / (1 + RAPPORTO)
    p10 = RAPPORTO * p01
    print(f"Split illustrativo: p01={p01:.4f}  p10={p10:.4f}  (media={(p01+p10)/2:.4f})")

    print("\nVerifica di convenzione: X solo sull'ancilla, registro |000>,")
    print("il bit dell'ancilla deve essere il PRIMO carattere della stringa:")
    from qiskit import QuantumCircuit, ClassicalRegister
    from qiskit_aer import AerSimulator
    qc = QuantumCircuit(4, 1)
    qc.x(3)  # ANCILLA
    qc.measure(3, 0)
    sim = AerSimulator()
    counts = sim.run(qc, shots=100).result().get_counts()
    print(f"  conteggi: {counts}  (atteso: solo '1' con 100 conteggi)")

    print("\nConfronto simmetrico vs asimmetrico, N=3, t=2:")
    c_sim = correlator_shots_asimmetrico(2, "x", 1, "x", 2.0, 3,
                                          J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
                                          vqe_params, p01=P_MEDIO, p10=P_MEDIO)
    c_asym = correlator_shots_asimmetrico(2, "x", 1, "x", 2.0, 3,
                                           J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
                                           vqe_params, p01=p01, p10=p10)
    print(f"  simmetrico  (p01=p10={P_MEDIO}): |C| = {abs(c_sim):.4f}")
    print(f"  asimmetrico (3x):               |C| = {abs(c_asym):.4f}")

    print("\nStress test: N* al variare del rapporto p10/p01 (media fissa):")
    for rap in [1, 3, 5, 10, 20, 50]:
        p01_r = 2 * P_MEDIO / (1 + rap)
        p10_r = rap * p01_r
        vals = []
        Ns = [1, 2, 3, 4, 5, 6, 8, 10]
        for N in Ns:
            c = correlator_shots_asimmetrico(2, "x", 1, "x", 2.0, N,
                                              J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
                                              vqe_params, p01=p01_r, p10=p10_r,
                                              shots=80_000)
            vals.append(abs(c))
        Nstar = Ns[int(np.argmax(vals))]
        print(f"  rapporto {rap:3d}x: N* = {Nstar}")
