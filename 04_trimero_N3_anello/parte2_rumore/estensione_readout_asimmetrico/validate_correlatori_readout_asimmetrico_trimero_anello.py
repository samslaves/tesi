"""
Verifica obbligatoria di correlatori_readout_asimmetrico_trimero_anello.py.

Mirror di validate_correlatori_readout_asimmetrico.py (dimero), con un
controllo IN PIU' (0) reso necessario dalla diversa convenzione qubit
dell'anello (ancilla = qubit 3, non 0): l'indicizzazione del bit
dell'ancilla nella stringa di misura va verificata esplicitamente, non
assunta per analogia dal dimero.

  0. Indicizzazione del bit dell'ancilla: con X solo sull'ancilla e
     measure_all(), il risultato deve essere '1000' (bit in prima
     posizione), non '0001' come sarebbe se si applicasse per errore la
     convenzione del dimero.
  1. Limite di rumore nullo: il ramo asimmetrico con p01=p10=0 deve
     coincidere esattamente col ramo originale (correlator_rumoroso con
     p_readout=0).
  2. Limite simmetrico: p01=p10=p deve riprodurre N*=3, il baseline
     dello Stadio 4.
  3. Test asimmetrico (split illustrativo, rapporto 3x, stessa media):
     N* deve restare 3.
  4. Cross-check Monte Carlo: la formula analitica e la misura a shot
     finiti (ReadoutError vero) devono coincidere entro l'errore
     statistico atteso.
  5. Stress test: N* deve restare 3 su tutti i rapporti fino a 50x.
"""
import numpy as np

from correlatori_readout_asimmetrico_trimero_anello import (
    correlator_rumoroso_asimmetrico, trova_N_star_asimmetrico,
    correlator_montecarlo_asimmetrico, P_READOUT_REF,
    P01_ILLUSTRATIVO, P10_ILLUSTRATIVO,
    J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT, ANCILLA,
)
from correlatori_rumorosi_trimero_anello import correlator_rumoroso
from noise_model_trimero_anello import build_noise_model

data = np.load("w2q6_params_optimal.npz")
vqe_params = data["params"]
nm_ref, _ = build_noise_model()
t = 2.0
N_grid = [1, 2, 3, 4, 5, 7, 10, 14, 20]

print("=" * 70)
print("0. INDICIZZAZIONE DEL BIT DELL'ANCILLA (qubit 3, non 0 come sul dimero)")
print("=" * 70)
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
qc_test = QuantumCircuit(4)
qc_test.x(ANCILLA)
qc_test.measure_all()
counts = AerSimulator().run(qc_test, shots=100).result().get_counts()
print(f"  X solo sull'ancilla (qubit {ANCILLA}), 100 shot: {counts}")
assert list(counts.keys()) == ["1000"], \
    "indicizzazione errata: atteso '1000' (bit ancilla in prima posizione)"
print("  -> OK: bit dell'ancilla in prima posizione, come dichiarato nel modulo.")

print()
print("=" * 70)
print("1. LIMITE DI RUMORE NULLO (p01=p10=0 deve coincidere col ramo originale)")
print("=" * 70)
max_diff = 0.0
for N in [1, 3, 5, 10]:
    c_rif = correlator_rumoroso(2, "x", 1, "x", t, N, J_DEFAULT, JP_DEFAULT,
                                 B_DEFAULT, D_DEFAULT, vqe_params,
                                 noise_model=nm_ref, p_readout=0.0)
    c_nuovo = correlator_rumoroso_asimmetrico(2, "x", 1, "x", t, N,
                                               J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
                                               vqe_params, noise_model=nm_ref,
                                               p01=0.0, p10=0.0)
    diff = abs(c_rif - c_nuovo)
    max_diff = max(max_diff, diff)
    print(f"  N={N}: |diff| = {diff:.2e}")
assert max_diff < 1e-12, "il ramo asimmetrico non coincide col ramo originale a readout spento"
print("  -> OK: coincidenza esatta a precisione macchina.")

print()
print("=" * 70)
print("2. LIMITE SIMMETRICO: p01=p10=p deve riprodurre N*=3")
print("=" * 70)
N_star, val_star, _ = trova_N_star_asimmetrico(
    vqe_params, t, N_grid, J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
    nm_ref, p01=P_READOUT_REF, p10=P_READOUT_REF)
print(f"  N* (p01=p10={P_READOUT_REF}) = {N_star}   |C(N*)| = {val_star:.6f}")
assert N_star == 3, f"N* nel limite simmetrico non e' 3 (trovato {N_star})"
print("  -> OK: coincide col baseline dello Stadio 4.")

print()
print("=" * 70)
print("3. TEST ASIMMETRICO (split illustrativo, rapporto 3x)")
print("=" * 70)
N_star_asym, val_star_asym, _ = trova_N_star_asimmetrico(
    vqe_params, t, N_grid, J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
    nm_ref, p01=P01_ILLUSTRATIVO, p10=P10_ILLUSTRATIVO)
print(f"  N* (asimmetrico) = {N_star_asym}   |C(N*)| = {val_star_asym:.6f}")
assert N_star_asym == 3, f"N* asimmetrico non e' 3 (trovato {N_star_asym})"
print("  -> OK: N* invariato rispetto al caso simmetrico.")

print()
print("=" * 70)
print("4. CROSS-CHECK MONTE CARLO (formula analitica vs shot veri)")
print("=" * 70)
max_diff_mc = 0.0
for N in [3, 5]:
    c_analitico = correlator_rumoroso_asimmetrico(
        2, "x", 1, "x", t, N, J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
        vqe_params, noise_model=nm_ref, p01=P01_ILLUSTRATIVO, p10=P10_ILLUSTRATIVO)
    c_mc = correlator_montecarlo_asimmetrico(
        2, "x", 1, "x", t, N, J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
        vqe_params, 2.9e-4, 3.8e-3,
        p01=P01_ILLUSTRATIVO, p10=P10_ILLUSTRATIVO, shots=200_000)
    diff = abs(c_analitico - c_mc)
    max_diff_mc = max(max_diff_mc, diff)
    print(f"  N={N}: analitico={c_analitico:.6f}  montecarlo={c_mc:.6f}  |diff|={diff:.2e}")
# soglia statistica attesa per 200k shot: ~ 1/sqrt(200000) ~ 2.2e-3 per componente,
# margine x3 per tenere conto di entrambe le componenti (re, im) e fluttuazione
assert max_diff_mc < 8e-3, f"scostamento Monte Carlo oltre la soglia statistica attesa"
print("  -> OK: entro l'errore statistico atteso per 200k shot.")

print()
print("=" * 70)
print("5. STRESS TEST: rapporti p10:p01 fino a 50x")
print("=" * 70)
for r in [1, 3, 5, 10, 20, 50]:
    tot = 2 * P_READOUT_REF
    p01_r = tot / (1 + r)
    p10_r = r * p01_r
    Nr, valr, _ = trova_N_star_asimmetrico(
        vqe_params, t, N_grid, J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
        nm_ref, p01=p01_r, p10=p10_r)
    print(f"  rapporto={r:3d}  N*={Nr}  |C(N*)|={valr:.4f}")
    assert Nr == 3, f"N* si sposta al rapporto {r}x (trovato {Nr})"
print("  -> OK: N*=3 invariato su tutto lo stress test.")

print()
print("=" * 70)
print("TUTTI I CONTROLLI SUPERATI")
print("=" * 70)
