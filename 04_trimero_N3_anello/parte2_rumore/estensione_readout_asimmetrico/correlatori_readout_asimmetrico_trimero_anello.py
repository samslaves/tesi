"""
Estensione (facoltativa) del Passo 4/5 -- test con readout ASIMMETRICO,
trimero ad anello. Mirror di correlatori_readout_asimmetrico.py (dimero).

Formula generale (teoria_readout_asimmetrico.tex, derivata sul dimero,
riusata qui identica -- si applica alla singola matrice di confusione
dell'ancilla, indipendente dal numero di qubit di registro, verificato
nel documento dei punti di lavoro):

    <Z>_readout = alpha * <Z>_ideale + beta,
    alpha = 1 - p01 - p10,   beta = p10 - p01.

Il limite p01=p10=p deve riprodurre esattamente il ramo simmetrico gia'
in uso in correlatori_rumorosi_trimero_anello.py (N*=3) -- primo
controllo obbligatorio.

DIFFERENZA RISPETTO AL DIMERO -- convenzione qubit dell'ancilla:
sul dimero l'ancilla e' il qubit 0 (ultimo carattere della stringa di
misura, Qiskit little-endian). Sull'anello l'ancilla e' il qubit 3
(PRIMO carattere della stringa a 4 bit) -- verificato esplicitamente con
un circuito di controllo (X solo sull'ancilla, |000> sul registro) prima
di scrivere il cross-check Monte Carlo, per non ripetere in silenzio un
errore di indicizzazione.

METODOLOGIA -- allineata allo standard ora in uso sul dimero (readout
genuinamente campionato, non solo formula analitica): il cross-check
Monte Carlo (shot veri, ReadoutError vero agganciato al NoiseModel) non
e' qui un contorno opzionale ma parte integrante della verifica, riportato
sempre insieme al risultato analitico, mai da solo.
"""
import numpy as np
from qiskit.quantum_info import DensityMatrix, SparsePauliOp
from qiskit_aer import AerSimulator
from qiskit_aer.noise import ReadoutError

from trimer_ring_exact import trimer_hamiltonian_dm
from noise_model_trimero_anello import build_noise_model
from correlatori_rumorosi_trimero_anello import (
    build_noisy_correlator_circuit, ancilla_z_gate_noisy,
    J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT, ANCILLA,
)

P_READOUT_REF = 2.3e-2  # media di riferimento, invariata rispetto al caso simmetrico

# Split illustrativo (dichiarato, non calibrazione reale di ibm_torino) --
# STESSO usato sul dimero, per confrontabilita' diretta fra le due topologie.
P01_ILLUSTRATIVO = 0.0115
P10_ILLUSTRATIVO = 0.0345


def correzione_readout(z_ideale, p01, p10):
    """<Z>_readout = alpha*<Z>_ideale + beta -- stessa formula del dimero."""
    alpha = 1.0 - p01 - p10
    beta = p10 - p01
    return alpha * z_ideale + beta


def correlator_rumoroso_asimmetrico(i, alpha, j, beta, t, N, J, Jp, b, D,
                                     ansatz_params, noise_model=None,
                                     p01=0.0, p10=0.0):
    """Come correlator_rumoroso (Stadio 4), ma con matrice di confusione
    asimmetrica (p01, p10) al posto del p_readout simmetrico."""
    qc_re = build_noisy_correlator_circuit(i, alpha, j, beta, t, N, J, Jp, b, D,
                                            "re", ansatz_params)
    qc_im = build_noisy_correlator_circuit(i, alpha, j, beta, t, N, J, Jp, b, D,
                                            "im", ansatz_params)
    z_re_ideale = ancilla_z_gate_noisy(qc_re, noise_model)
    z_im_ideale = ancilla_z_gate_noisy(qc_im, noise_model)
    z_re = correzione_readout(z_re_ideale, p01, p10)
    z_im = correzione_readout(z_im_ideale, p01, p10)
    return z_re + 1j * z_im


def trova_N_star_asimmetrico(vqe_params, t, N_grid, J, Jp, b, D, noise_model,
                              p01, p10, i=2, alpha="x", j=1, beta="x"):
    """arg max_N |C(N)| con readout asimmetrico (p01, p10)."""
    vals = []
    for N in N_grid:
        c = correlator_rumoroso_asimmetrico(i, alpha, j, beta, t, N, J, Jp, b, D,
                                             vqe_params, noise_model=noise_model,
                                             p01=p01, p10=p10)
        vals.append(abs(c))
    imax = int(np.argmax(vals))
    return N_grid[imax], vals[imax], vals


def readout_error_asimmetrico_aer(p01, p10):
    """ReadoutError di Aer con matrice di confusione ASIMMETRICA -- identica
    al dimero, per il cross-check Monte Carlo."""
    conf_matrix = [[1 - p01, p01],
                   [p10, 1 - p10]]
    return ReadoutError(conf_matrix)


def correlator_montecarlo_asimmetrico(i, alpha_op, j, beta_op, t, N, J, Jp, b, D,
                                       ansatz_params, eps_1q, eps_2q,
                                       p01, p10, shots=200_000, seed=7):
    """Cross-check Monte Carlo: stesso circuito, ma con ReadoutError VERO
    (asimmetrico) agganciato al NoiseModel e misura a shot finiti, invece
    della correzione analitica. Percorso di calcolo indipendente.

    ATTENZIONE convenzione qubit: sull'anello l'ancilla e' il qubit 3 --
    con measure_all() su 4 qubit, il bit del qubit 3 e' il PRIMO carattere
    della stringa (Qiskit ordina c3 c2 c1 c0 da sinistra a destra),
    verificato esplicitamente con un circuito di controllo (vedi log). Il
    dimero usa invece bitstr[-1] perche' li' l'ancilla e' il qubit 0 --
    qui va usato bitstr[0], NON bitstr[-1]."""
    nm_gate_only, _ = build_noise_model(eps_1q=eps_1q, eps_2q=eps_2q, p_readout=0.0)
    ro_err = readout_error_asimmetrico_aer(p01, p10)
    nm_gate_only.add_readout_error(ro_err, [ANCILLA])

    ris = {}
    for part in ("re", "im"):
        qc = build_noisy_correlator_circuit(i, alpha_op, j, beta_op, t, N,
                                             J, Jp, b, D, part, ansatz_params)
        qc = qc.copy()
        qc.measure_all()
        sim = AerSimulator(noise_model=nm_gate_only, seed_simulator=seed)
        counts = sim.run(qc, shots=shots).result().get_counts()
        # ancilla = qubit 3 -> PRIMO carattere della stringa (vedi nota sopra)
        p0 = sum(c for bitstr, c in counts.items() if bitstr[0] == "0") / shots
        p1 = sum(c for bitstr, c in counts.items() if bitstr[0] == "1") / shots
        ris[part] = p0 - p1
    return ris["re"] + 1j * ris["im"]


if __name__ == "__main__":
    data = np.load("w2q6_params_optimal.npz")
    vqe_params = data["params"]
    nm_ref, _ = build_noise_model()
    t = 2.0
    N_grid = [1, 2, 3, 4, 5, 7, 10, 14, 20]

    print("=" * 70)
    print("CONTROLLO PRELIMINARE: indicizzazione del bit dell'ancilla")
    print("=" * 70)
    from qiskit import QuantumCircuit
    qc_test = QuantumCircuit(4)
    qc_test.x(ANCILLA)
    qc_test.measure_all()
    sim_test = AerSimulator()
    counts_test = sim_test.run(qc_test, shots=100).result().get_counts()
    print(f"  X solo sull'ancilla (qubit {ANCILLA}): {counts_test}")
    assert list(counts_test.keys()) == ["1000"], "indicizzazione del bit dell'ancilla inattesa"
    print("  -> OK: il bit dell'ancilla e' il primo carattere (sinistra), come dichiarato.")

    print()
    print("=" * 70)
    print("0. LIMITE DI RUMORE NULLO (readout spento, p01=p10=0)")
    print("=" * 70)
    from correlatori_rumorosi_trimero_anello import correlator_rumoroso
    for N in [3, 5]:
        c_rif = correlator_rumoroso(2, "x", 1, "x", t, N, J_DEFAULT, JP_DEFAULT,
                                     B_DEFAULT, D_DEFAULT, vqe_params,
                                     noise_model=nm_ref, p_readout=0.0)
        c_nuovo = correlator_rumoroso_asimmetrico(2, "x", 1, "x", t, N,
                                                   J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
                                                   vqe_params, noise_model=nm_ref,
                                                   p01=0.0, p10=0.0)
        print(f"  N={N}: ramo originale={c_rif:.8f}   ramo nuovo={c_nuovo:.8f}   "
              f"|diff|={abs(c_rif-c_nuovo):.2e}")

    print()
    print("=" * 70)
    print("1. LIMITE SIMMETRICO: p01=p10=p deve riprodurre N*=3 gia' noto")
    print("=" * 70)
    p_ref = P_READOUT_REF
    N_star, val_star, vals = trova_N_star_asimmetrico(
        vqe_params, t, N_grid, J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
        nm_ref, p01=p_ref, p10=p_ref)
    print(f"  N* (p01=p10={p_ref}) = {N_star}   |C(N*)| = {val_star:.6f}")

    print()
    print("=" * 70)
    print("2. TEST ASIMMETRICO: split illustrativo (stessa media, rapporto 3x)")
    print("=" * 70)
    N_star_asym, val_star_asym, vals_asym = trova_N_star_asimmetrico(
        vqe_params, t, N_grid, J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
        nm_ref, p01=P01_ILLUSTRATIVO, p10=P10_ILLUSTRATIVO)
    print(f"  N* (asimmetrico) = {N_star_asym}   |C(N*)| = {val_star_asym:.6f}")

    print()
    print("=" * 70)
    print("3. CROSS-CHECK MONTE CARLO (ReadoutError vero, shot finiti)")
    print("=" * 70)
    for N in [3, 5]:
        c_analitico = correlator_rumoroso_asimmetrico(
            2, "x", 1, "x", t, N, J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
            vqe_params, noise_model=nm_ref,
            p01=P01_ILLUSTRATIVO, p10=P10_ILLUSTRATIVO)
        c_mc = correlator_montecarlo_asimmetrico(
            2, "x", 1, "x", t, N, J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
            vqe_params, 2.9e-4, 3.8e-3,
            p01=P01_ILLUSTRATIVO, p10=P10_ILLUSTRATIVO, shots=200_000)
        print(f"  N={N}: analitico={c_analitico:.6f}   montecarlo={c_mc:.6f}   "
              f"|diff|={abs(c_analitico-c_mc):.2e}")
