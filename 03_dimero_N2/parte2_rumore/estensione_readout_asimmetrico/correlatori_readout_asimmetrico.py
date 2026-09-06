"""
Estensione (facoltativa) del Passo 4/5 -- test con readout ASIMMETRICO.

Applica la formula generale derivata in teoria_readout_asimmetrico.tex,

    <Z>_readout = alpha * <Z>_ideale + beta,
    alpha = 1 - p01 - p10,   beta = p10 - p01,

al posto della correzione simmetrica (1-2p) gia' in uso in
correlatori_rumorosi_dimero.py. Il limite p01=p10=p deve riprodurre
esattamente il ramo simmetrico gia' verificato -- primo controllo
obbligatorio prima di guardare il caso asimmetrico.

Scope dichiarato: verificare se N*=5 (Passo 4, correlatori rumorosi) si
sposta quando il readout smette di essere simmetrico -- test esplicitamente
richiesto dal relatore come opzionale ("parti simmetrico, poi vedi se hai
tempo di fare un test asimmetrico, ma senza perderci troppo tempo",
domande_relatore.md sez. 12).

Valori numerici usati per il test, dichiarati ILLUSTRATIVI (non uno split
reale registrato per ibm_torino -- la fonte di calibrazione gia' citata,
arXiv:2504.15187, riporta solo la mediana simmetrica): rapporto p10:p01=3
(nel mezzo dell'intervallo 2-3.5x osservato su calibrazioni IBM reali
citabili, vedi tabella nel documento dei risultati), stessa media gia'
in uso p_readout=2.3e-2 -- cosi' il test isola l'effetto dell'asimmetria,
non introduce anche un cambiamento della scala complessiva del rumore.
"""
import numpy as np
from qiskit.quantum_info import DensityMatrix, SparsePauliOp
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError

from dimer_exact import dimer_hamiltonian
from noise_model_dimero import build_noise_model, BASIS_GATES
from correlatori_rumorosi_dimero import (
    build_noisy_correlator_circuit, ancilla_z_gate_noisy,
    J_DEFAULT, b_DEFAULT, D_DEFAULT,
)

P_READOUT_REF = 2.3e-2  # media di riferimento, invariata rispetto al caso simmetrico

# Split illustrativo (dichiarato, non calibrazione reale di ibm_torino):
# rapporto p10:p01 = 3, stessa media 2.3e-2 del caso simmetrico.
P01_ILLUSTRATIVO = 0.0115   # prob_meas1_prep0 (P(misuro 1 | preparato 0))
P10_ILLUSTRATIVO = 0.0345   # prob_meas0_prep1 (P(misuro 0 | preparato 1))


def correzione_readout(z_ideale, p01, p10):
    """<Z>_readout = alpha*<Z>_ideale + beta (Eq. generale,
    teoria_readout_asimmetrico.tex, Eq. 10)."""
    alpha = 1.0 - p01 - p10
    beta = p10 - p01
    return alpha * z_ideale + beta


def correlator_rumoroso_asimmetrico(i, alpha, j, beta, t, N, J, b, D,
                                     ansatz_params, noise_model=None,
                                     p01=0.0, p10=0.0):
    """Come correlator_rumoroso, ma con matrice di confusione asimmetrica
    (p01, p10) al posto del singolo p_readout simmetrico."""
    qc_re = build_noisy_correlator_circuit(i, alpha, j, beta, t, N, J, b, D,
                                            "re", ansatz_params)
    qc_im = build_noisy_correlator_circuit(i, alpha, j, beta, t, N, J, b, D,
                                            "im", ansatz_params)
    z_re_ideale = ancilla_z_gate_noisy(qc_re, noise_model)
    z_im_ideale = ancilla_z_gate_noisy(qc_im, noise_model)
    z_re = correzione_readout(z_re_ideale, p01, p10)
    z_im = correzione_readout(z_im_ideale, p01, p10)
    return z_re + 1j * z_im


def trova_N_star_asimmetrico(vqe_params, t, N_grid, J, b, D, noise_model,
                              p01, p10, i=2, alpha="x", j=1, beta="x"):
    """arg max_N |C(N)| con readout asimmetrico (p01, p10)."""
    vals = []
    for N in N_grid:
        c = correlator_rumoroso_asimmetrico(i, alpha, j, beta, t, N, J, b, D,
                                             vqe_params, noise_model=noise_model,
                                             p01=p01, p10=p10)
        vals.append(abs(c))
    imax = int(np.argmax(vals))
    return N_grid[imax], vals[imax], vals


def readout_error_asimmetrico_aer(p01, p10):
    """ReadoutError di Aer con matrice di confusione ASIMMETRICA, per il
    cross-check Monte Carlo (shot reali) indipendente dal percorso
    analitico principale."""
    conf_matrix = [[1 - p01, p01],
                   [p10, 1 - p10]]
    return ReadoutError(conf_matrix)


def correlator_montecarlo_asimmetrico(i, alpha_op, j, beta_op, t, N, J, b, D,
                                       ansatz_params, eps_1q, eps_2q,
                                       p01, p10, shots=200_000, seed=7):
    """Cross-check Monte Carlo: stesso circuito, ma con ReadoutError VERO
    (asimmetrico) agganciato al NoiseModel e misura a shot finiti, invece
    della correzione analitica. Percorso di calcolo indipendente.

    Costruisce il NoiseModel da zero con SOLO il rumore di gate (eps_1q,
    eps_2q) piu' il readout asimmetrico sulla sola ancilla (qubit 0) --
    non riusa un NoiseModel con readout simmetrico gia' agganciato, per
    evitare qualunque ambiguita' su quale readout venga applicato dove."""
    nm_gate_only, _ = build_noise_model(eps_1q=eps_1q, eps_2q=eps_2q, p_readout=0.0)
    ro_err = readout_error_asimmetrico_aer(p01, p10)
    nm_gate_only.add_readout_error(ro_err, [0])  # solo l'ancilla

    ris = {}
    for part in ("re", "im"):
        qc = build_noisy_correlator_circuit(i, alpha_op, j, beta_op, t, N,
                                             J, b, D, part, ansatz_params)
        qc = qc.copy()
        qc.measure_all()
        sim = AerSimulator(noise_model=nm_gate_only, seed_simulator=seed)
        counts = sim.run(qc, shots=shots).result().get_counts()
        # <Z> sull'ancilla = qubit meno significativo nella stringa di Qiskit
        # (ordine little-endian: l'ultimo carattere e' il qubit 0)
        p0 = sum(c for bitstr, c in counts.items() if bitstr[-1] == "0") / shots
        p1 = sum(c for bitstr, c in counts.items() if bitstr[-1] == "1") / shots
        ris[part] = p0 - p1
    return ris["re"] + 1j * ris["im"]


if __name__ == "__main__":
    data = np.load("ground_state_test2.npz")
    vqe_params = data["vqe_params"]
    nm_ref, _ = build_noise_model()
    t = 2.0
    N_grid = list(range(1, 21))

    print("=" * 70)
    print("0. LIMITE DI RUMORE NULLO (readout spento, p01=p10=0)")
    print("=" * 70)
    from correlatori_rumorosi_dimero import correlator_rumoroso
    for N in [5, 8]:
        c_rif = correlator_rumoroso(2, "x", 1, "x", t, N, J_DEFAULT, b_DEFAULT,
                                     D_DEFAULT, vqe_params, noise_model=nm_ref,
                                     p_readout=0.0)
        c_nuovo = correlator_rumoroso_asimmetrico(2, "x", 1, "x", t, N,
                                                   J_DEFAULT, b_DEFAULT, D_DEFAULT,
                                                   vqe_params, noise_model=nm_ref,
                                                   p01=0.0, p10=0.0)
        print(f"  N={N}: ramo originale={c_rif:.8f}   ramo nuovo={c_nuovo:.8f}   "
              f"|diff|={abs(c_rif-c_nuovo):.2e}")

    print()
    print("=" * 70)
    print("1. LIMITE SIMMETRICO: p01=p10=p deve riprodurre N*=5 gia' noto")
    print("=" * 70)
    p_ref = P_READOUT_REF
    N_star, val_star, vals = trova_N_star_asimmetrico(
        vqe_params, t, N_grid, J_DEFAULT, b_DEFAULT, D_DEFAULT,
        nm_ref, p01=p_ref, p10=p_ref)
    print(f"  N* (p01=p10={p_ref}) = {N_star}   |C(N*)| = {val_star:.6f}")

    print()
    print("=" * 70)
    print("2. TEST ASIMMETRICO: split illustrativo (stessa media, rapporto 3x)")
    print("=" * 70)
    print(f"  p01={P01_ILLUSTRATIVO}, p10={P10_ILLUSTRATIVO}  "
          f"(media={0.5*(P01_ILLUSTRATIVO+P10_ILLUSTRATIVO):.4f}, "
          f"rapporto={P10_ILLUSTRATIVO/P01_ILLUSTRATIVO:.2f})")
    N_star_asym, val_star_asym, vals_asym = trova_N_star_asimmetrico(
        vqe_params, t, N_grid, J_DEFAULT, b_DEFAULT, D_DEFAULT,
        nm_ref, p01=P01_ILLUSTRATIVO, p10=P10_ILLUSTRATIVO)
    print(f"  N* (asimmetrico) = {N_star_asym}   |C(N*)| = {val_star_asym:.6f}")
    print(f"  N* (simmetrico, riferimento) = 5")

    print()
    print("=" * 70)
    print("3. CROSS-CHECK MONTE CARLO (ReadoutError vero, shot finiti)")
    print("=" * 70)
    for N in [5, 8]:
        c_analitico = correlator_rumoroso_asimmetrico(
            2, "x", 1, "x", t, N, J_DEFAULT, b_DEFAULT, D_DEFAULT,
            vqe_params, noise_model=nm_ref,
            p01=P01_ILLUSTRATIVO, p10=P10_ILLUSTRATIVO)
        c_mc = correlator_montecarlo_asimmetrico(
            2, "x", 1, "x", t, N, J_DEFAULT, b_DEFAULT, D_DEFAULT,
            vqe_params, 2.9e-4, 3.8e-3,
            p01=P01_ILLUSTRATIVO, p10=P10_ILLUSTRATIVO, shots=200_000)
        print(f"  N={N}: analitico={c_analitico:.6f}   montecarlo={c_mc:.6f}   "
              f"|diff|={abs(c_analitico-c_mc):.2e}")

    print()
    print("=" * 70)
    print("4. STRESS TEST: rapporti p10:p01 oltre il range realistico")
    print("=" * 70)
    rapporti = [1, 3, 5, 10, 20, 50]
    N_star_vs_rapporto = []
    for r in rapporti:
        tot = 2 * P_READOUT_REF
        p01_r = tot / (1 + r)
        p10_r = r * p01_r
        Nr, valr, _ = trova_N_star_asimmetrico(
            vqe_params, t, N_grid, J_DEFAULT, b_DEFAULT, D_DEFAULT,
            nm_ref, p01=p01_r, p10=p10_r)
        N_star_vs_rapporto.append((r, p01_r, p10_r, Nr, valr))
        print(f"  rapporto={r:3d}  p01={p01_r:.4f} p10={p10_r:.4f}  "
              f"N*={Nr}  |C(N*)|={valr:.4f}")

    np.savez("scan_N_asimmetrico.npz",
             N_grid=np.array(N_grid),
             vals_simmetrico=np.array(vals),
             vals_asimmetrico=np.array(vals_asym),
             N_star_simmetrico=N_star, N_star_asimmetrico=N_star_asym,
             rapporti=np.array([r[0] for r in N_star_vs_rapporto]),
             N_star_vs_rapporto=np.array([r[3] for r in N_star_vs_rapporto]))
    print("\n[salvato] scan_N_asimmetrico.npz")

