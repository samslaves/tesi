"""
Verifica obbligatoria di correlatori_readout_asimmetrico.py.

  1. Limite di rumore nullo: p01=p10=0 deve riprodurre esattamente (a
     precisione macchina) il ramo originale (p_readout=0) gia' verificato.
  2. Limite simmetrico: p01=p10=p deve riprodurre esattamente N*=5 e gli
     stessi valori |C(N)| gia' registrati per il caso simmetrico
     (correlatori_rumorosi_dimero.py).
  3. Cross-check Monte Carlo: la formula analitica (alpha*<Z>+beta) deve
     coincidere, entro l'errore statistico atteso a shot finiti, con un
     ReadoutError vero e asimmetrico agganciato ad Aer -- due cammini di
     calcolo indipendenti per lo stesso risultato.
  4. Risultato centrale: N*=5 non si sposta con lo split illustrativo
     (rapporto 3x, stessa media), ne' con rapporti molto piu' estremi
     (fino a 50x) del range realistico osservato su hardware IBM reale.
"""
import numpy as np

from correlatori_readout_asimmetrico import (
    correlator_rumoroso_asimmetrico, correlator_montecarlo_asimmetrico,
    trova_N_star_asimmetrico, P_READOUT_REF, P01_ILLUSTRATIVO, P10_ILLUSTRATIVO,
)
from correlatori_rumorosi_dimero import (
    correlator_rumoroso, J_DEFAULT, b_DEFAULT, D_DEFAULT,
)
from noise_model_dimero import build_noise_model

data = np.load("ground_state_test2.npz")
vqe_params = data["vqe_params"]
nm_ref, _ = build_noise_model()
t = 2.0
N_grid = list(range(1, 21))

print("=" * 70)
print("1. LIMITE DI RUMORE NULLO (p01=p10=0)")
print("=" * 70)
max_diff = 0.0
for N in [1, 5, 8, 20]:
    c_rif = correlator_rumoroso(2, "x", 1, "x", t, N, J_DEFAULT, b_DEFAULT,
                                 D_DEFAULT, vqe_params, noise_model=nm_ref,
                                 p_readout=0.0)
    c_nuovo = correlator_rumoroso_asimmetrico(2, "x", 1, "x", t, N,
                                               J_DEFAULT, b_DEFAULT, D_DEFAULT,
                                               vqe_params, noise_model=nm_ref,
                                               p01=0.0, p10=0.0)
    diff = abs(c_rif - c_nuovo)
    max_diff = max(max_diff, diff)
    print(f"  N={N:2d}: |diff| = {diff:.2e}")
assert max_diff < 1e-12, "limite di rumore nullo fallito"
print(f"  -> OK: coincidenza a precisione macchina (max |diff| = {max_diff:.2e}).")

print()
print("=" * 70)
print("2. LIMITE SIMMETRICO: N*=5 e valori |C(N)| gia' noti")
print("=" * 70)
N_star, val_star, vals = trova_N_star_asimmetrico(
    vqe_params, t, N_grid, J_DEFAULT, b_DEFAULT, D_DEFAULT,
    nm_ref, p01=P_READOUT_REF, p10=P_READOUT_REF)
print(f"  N* (p01=p10={P_READOUT_REF}) = {N_star}")
assert N_star == 5, f"regressione: N*={N_star} invece di 5 nel limite simmetrico"
# confronto diretto col ramo originale (simmetrico) su alcuni N
for N in [5, 8]:
    c_orig = correlator_rumoroso(2, "x", 1, "x", t, N, J_DEFAULT, b_DEFAULT,
                                  D_DEFAULT, vqe_params, noise_model=nm_ref,
                                  p_readout=P_READOUT_REF)
    c_new = correlator_rumoroso_asimmetrico(2, "x", 1, "x", t, N,
                                             J_DEFAULT, b_DEFAULT, D_DEFAULT,
                                             vqe_params, noise_model=nm_ref,
                                             p01=P_READOUT_REF, p10=P_READOUT_REF)
    diff = abs(c_orig - c_new)
    print(f"  N={N}: ramo originale={c_orig:.8f}  ramo nuovo (p01=p10)={c_new:.8f}  |diff|={diff:.2e}")
    assert diff < 1e-12, "il ramo simmetrico del nuovo modulo non coincide con l'originale"
print("  -> OK: N*=5 riprodotto, coincidenza a precisione macchina col ramo originale.")

print()
print("=" * 70)
print("3. CROSS-CHECK MONTE CARLO (ReadoutError vero, asimmetrico)")
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
    diff = abs(c_analitico - c_mc)
    print(f"  N={N}: analitico={c_analitico:.6f}  montecarlo={c_mc:.6f}  |diff|={diff:.2e}")
    assert diff < 1e-2, "scostamento oltre l'errore statistico atteso a 200k shot"
print("  -> OK: formula analitica confermata da un cammino di calcolo indipendente"
      " (ReadoutError vero, shot finiti), entro l'errore statistico atteso.")

print()
print("=" * 70)
print("4. RISULTATO CENTRALE: N*=5 non si sposta")
print("=" * 70)
N_star_asym, val_star_asym, _ = trova_N_star_asimmetrico(
    vqe_params, t, N_grid, J_DEFAULT, b_DEFAULT, D_DEFAULT,
    nm_ref, p01=P01_ILLUSTRATIVO, p10=P10_ILLUSTRATIVO)
print(f"  N* (split illustrativo, rapporto 3x) = {N_star_asym}")
assert N_star_asym == 5, f"N*={N_star_asym}: si e' spostato rispetto al riferimento simmetrico"

# stress test oltre il range realistico
for r in [5, 10, 20, 50]:
    tot = 2 * P_READOUT_REF
    p01_r, p10_r = tot / (1 + r), r * tot / (1 + r)
    Nr, _, _ = trova_N_star_asimmetrico(
        vqe_params, t, N_grid, J_DEFAULT, b_DEFAULT, D_DEFAULT,
        nm_ref, p01=p01_r, p10=p10_r)
    print(f"  rapporto={r:3d}: N* = {Nr}")
    assert Nr == 5, f"N* si sposta a rapporto={r} (oltre il range realistico)"
print("  -> OK: N*=5 robusto anche ben oltre il range di asimmetria realistico"
      " (fino a rapporto 50x), non solo al punto illustrativo.")

print()
print("=" * 70)
print("TUTTI I CONTROLLI SUPERATI")
print("=" * 70)
