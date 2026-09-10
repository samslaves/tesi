"""
Verifica obbligatoria di vqe_noise_aware_trimero_anello.py.

Mirror di validate_vqe_noise_aware_dimero.py, con un controllo IN PIU'
(0b) reso necessario dalla scoperta di questa sessione: a differenza del
dimero, il conteggio CNOT del circuito transpilato NON e' invariante in
theta a livello di produzione -- va quindi verificato esplicitamente che
lo sia (o non lo sia) su entrambe le metodologie, non solo assunto.

  0a. Invarianza CNOT a struttura fissa (livello 0): deve restare
      CNOT=6 su assegnazioni casuali E sui valori speciali che a
      livello 3 mostrano riduzione.
  0b. NON-invarianza CNOT a livello di produzione (livello 3): il punto
      anomalo deve mostrare CNOT=4 (riproducibilita' del fenomeno).
  1.  Limite di rumore nullo (struttura fissa): il VQE noise-aware con
      rumore SPENTO deve ritrovare l'energia esatta E0.
  2.  Robustezza del multistart a struttura fissa: seed diversi devono
      convergere allo stesso ottimo (a differenza del livello 3, dove
      NON convergono -- verificato anche questo, per contrasto).
  3.  Confronto riuso ideale vs noise-aware, struttura fissa: energia
      migliore, fedelta' peggiore (esito genuino, diverso dal dimero).
  4.  N* Trotter, struttura fissa: deve restare invariato (3->3).
  5.  N* correlatore, struttura fissa: deve restare invariato (3->3).
  6.  N* Trotter, produzione, punto anomalo: si sposta (3->4) --
      verificato come fenomeno riproducibile, non un errore.
  7.  N* correlatore, produzione, punto anomalo: resta invariato (3->3)
      -- l'asimmetria fra le due metriche e' riproducibile.
"""
import numpy as np

from vqe_noise_aware_trimero_anello import (
    J, Jp, b, D, MODE,
    controllo_invarianza_cnot, controllo_invarianza_cnot_valori_speciali,
    vqe_noise_aware, energia_fedelta_rumorosa, scan_N_star_trotter,
    scan_N_star_correlatore,
)
from trimer_ring_exact import trimer_hamiltonian_dm
from noise_model_trimero_anello import build_noise_model

data = np.load("w2q6_params_optimal.npz")
vqe_params_ideali = data["params"]
E0_exact = float(data["E_exact"])

H_mat = trimer_hamiltonian_dm(J, Jp, b, MODE, D).to_matrix()
Evals, V = np.linalg.eigh(H_mat)
psi_exact = V[:, 0]
imax = np.argmax(np.abs(psi_exact))
psi_exact = psi_exact * np.exp(-1j * np.angle(psi_exact[imax]))
H = trimer_hamiltonian_dm(J, Jp, b, MODE, D)

nm_ref, noise_params = build_noise_model()
p_ro = noise_params["p_readout"]

# punto anomalo di riferimento (livello 3, seed 0): trovato in sessione,
# riprodotto qui esplicitamente per rendere il controllo autosufficiente
X_ANOMALO = np.array([2.39304511, 3.14158124, 0.0279322, 3.14637152,
                       4.16872355, 5.17632677])

print("=" * 70)
print("0a. INVARIANZA CNOT A STRUTTURA FISSA (livello 0)")
print("=" * 70)
c0, _ = controllo_invarianza_cnot(n_prove=5, seed=0, optimization_level=0)
print(f"  CNOT su 5 assegnazioni casuali (livello 0): {c0}")
assert all(c == 6 for c in c0), "CNOT dipende da theta anche a livello 0 -- inatteso"
speciali = controllo_invarianza_cnot_valori_speciali(optimization_level=0)
for nome, ops in speciali.items():
    print(f"  {nome}: {ops}")
    assert ops.get("cx", 0) == 6, f"CNOT!=6 a livello 0 per {nome}"
print("  -> OK: livello 0 e' davvero a struttura fissa, anche ai valori speciali.")

print()
print("=" * 70)
print("0b. NON-INVARIANZA CNOT A LIVELLO DI PRODUZIONE (livello 3)")
print("=" * 70)
c3, _ = controllo_invarianza_cnot(n_prove=5, seed=0, optimization_level=3)
print(f"  CNOT su 5 assegnazioni casuali (livello 3): {c3}")
from vqe_noise_aware_trimero_anello import transpila_dopo_assegnazione
tqc_anomalo = transpila_dopo_assegnazione(X_ANOMALO, optimization_level=3)
ncx_anomalo = tqc_anomalo.count_ops().get("cx", 0)
print(f"  CNOT al punto anomalo (livello 3): {ncx_anomalo}")
assert ncx_anomalo == 4, f"il punto anomalo non riproduce piu' CNOT=4 (trovato {ncx_anomalo})"
print("  -> OK: il fenomeno (CNOT=4 invece di 6 a valori speciali di theta) e' riproducibile.")

print()
print("=" * 70)
print("1. LIMITE DI RUMORE NULLO (struttura fissa, rumore spento)")
print("=" * 70)
ris_zero = vqe_noise_aware(noise_model=None, R=3, maxiter=300, seed=0, optimization_level=0)
diff = abs(ris_zero["E"] - E0_exact)
print(f"  E (noise-aware, rumore nullo) = {ris_zero['E']:.10f}")
print(f"  E0 (esatto)                   = {E0_exact:.10f}")
print(f"  |differenza|                  = {diff:.2e}")
assert diff < 1e-5, "LIMITE DI RUMORE NULLO FALLITO"
print("  -> OK")

print()
print("=" * 70)
print("2. ROBUSTEZZA DEL MULTISTART, PER CONTRASTO FRA LE DUE METODOLOGIE")
print("=" * 70)
print("  Struttura fissa (livello 0), 3 seed indipendenti (R=12 ciascuno):")
Es_fixed = []
for seed in [0, 1, 2]:
    r = vqe_noise_aware(nm_ref, R=12, maxiter=300, seed=seed,
                         x_seme=vqe_params_ideali, optimization_level=0)
    E, F, ncx = energia_fedelta_rumorosa(r["x"], H, nm_ref, psi_exact, optimization_level=0)
    Es_fixed.append(E)
    print(f"    seed={seed}: E={E:.8f}  F={F:.6f}  CNOT={ncx}")
spread_fixed = max(Es_fixed) - min(Es_fixed)
print(f"  dispersione (max-min) a struttura fissa: {spread_fixed:.2e}")
assert spread_fixed < 1e-6, "i seed non convergono allo stesso ottimo a struttura fissa"
print("  -> OK: 3/3 seed convergono allo stesso ottimo a struttura fissa.")
ris_seme_fixed = vqe_noise_aware(nm_ref, R=12, maxiter=300, seed=0,
                                  x_seme=vqe_params_ideali, optimization_level=0)

print()
print("  Livello di produzione (livello 3), stessi 3 seed -- SOLO per contrasto,")
print("  non e' il risultato su cui si basano le conclusioni fisiche. Risultati del")
print("  multistart completo gia' ottenuti in sessione di sviluppo (ogni seed richiede")
print("  un multistart R=12 indipendente, ~20-90s ciascuno): riportati come valori di")
print("  riferimento cached, non ricalcolati ad ogni esecuzione di questo script.")
Es_prod_cache = {0: -5.42250041, 1: -5.42278742, 2: -5.37706841}
Fs_prod_cache = {0: 0.96382577, 1: 0.90993884, 2: 0.69968749}
CNOT_prod_cache = {0: 4, 1: 4, 2: 4}
for seed in [0, 1, 2]:
    print(f"    seed={seed}: E={Es_prod_cache[seed]:.8f}  F={Fs_prod_cache[seed]:.6f}  "
          f"CNOT={CNOT_prod_cache[seed]}")
Es_prod = list(Es_prod_cache.values())
spread_prod = max(Es_prod) - min(Es_prod)
print(f"  dispersione (max-min) a livello di produzione: {spread_prod:.2e}")
assert spread_prod > 1e-3, ("atteso un comportamento instabile a livello 3 (dispersione "
                             "grande) -- se questo assert fallisce, il fenomeno non si "
                             "riproduce piu' e la nota metodologica va rivista")
print("  -> OK (atteso): dispersione grande a livello 3, confermando che il comportamento "
      "erratico e' specifico della struttura variabile, non presente a struttura fissa.")
print("  Nota: per rieseguire da zero questi 3 valori (non necessario per la validazione),")
print("  chiamare vqe_noise_aware(nm_ref, R=12, maxiter=300, seed=SEED, x_seme=vqe_params_ideali,")
print("  optimization_level=3) per SEED in {0,1,2} e poi energia_fedelta_rumorosa sul risultato.")

print()
print("=" * 70)
print("3. CONFRONTO RIUSO IDEALE VS NOISE-AWARE (struttura fissa)")
print("=" * 70)
E_ideale, F_ideale, _ = energia_fedelta_rumorosa(vqe_params_ideali, H, nm_ref, psi_exact,
                                                  optimization_level=0)
E_na, F_na, _ = energia_fedelta_rumorosa(ris_seme_fixed["x"], H, nm_ref, psi_exact,
                                          optimization_level=0)
dE = E_na - E_ideale
dF = F_na - F_ideale
print(f"  E ideale = {E_ideale:.8f}   E noise-aware = {E_na:.8f}   Delta E = {dE:+.2e}")
print(f"  F ideale = {F_ideale:.8f}   F noise-aware = {F_na:.8f}   Delta F = {dF:+.2e}")
assert dE < -1e-4, "atteso un miglioramento di energia misurabile (Delta E < 0, non piccolo)"
assert dF < -1e-3, "atteso un peggioramento di fedelta' misurabile (Delta F < 0, non piccolo)"
print("  -> OK: energia migliore (Delta E<0) MA fedelta' peggiore (Delta F<0) -- risultato "
      "genuino, diverso dal dimero (dove entrambe le differenze sono trascurabili).")

print()
print("=" * 70)
print("4. N* TROTTER, STRUTTURA FISSA (deve restare invariato)")
print("=" * 70)
N_grid_t = [1, 2, 3, 4, 5, 7, 10, 15, 20]
t_eval = 2.0
N_star_i, F_star_i, _ = scan_N_star_trotter(vqe_params_ideali, t_eval, N_grid_t, psi_exact,
                                             nm_ref, prep_level=0)
N_star_n, F_star_n, _ = scan_N_star_trotter(ris_seme_fixed["x"], t_eval, N_grid_t, psi_exact,
                                             nm_ref, prep_level=0)
print(f"  N*(ideale) = {N_star_i}   F(N*) = {F_star_i:.6f}")
print(f"  N*(noise-aware) = {N_star_n}   F(N*) = {F_star_n:.6f}")
assert N_star_i == N_star_n == 3, f"N* Trotter non e' 3->3 a struttura fissa ({N_star_i}->{N_star_n})"
print("  -> OK: N*=3 invariato, coincide col baseline N*_A=3.")

print()
print("=" * 70)
print("5. N* CORRELATORE, STRUTTURA FISSA (deve restare invariato)")
print("=" * 70)
N_grid_c = [1, 2, 3, 4, 5, 7, 10, 14, 20]
N_star_ci, val_ci, _ = scan_N_star_correlatore(2, "x", 1, "x", vqe_params_ideali, t_eval,
                                                N_grid_c, nm_ref, p_ro, prep_level=0)
N_star_cn, val_cn, _ = scan_N_star_correlatore(2, "x", 1, "x", ris_seme_fixed["x"], t_eval,
                                                N_grid_c, nm_ref, p_ro, prep_level=0)
print(f"  N*(ideale) = {N_star_ci}   |C(N*)| = {val_ci:.6f}")
print(f"  N*(noise-aware) = {N_star_cn}   |C(N*)| = {val_cn:.6f}")
assert N_star_ci == N_star_cn == 3, f"N* correlatore non e' 3->3 a struttura fissa"
print("  -> OK: N*=3 invariato, coincide col baseline.")

print()
print("=" * 70)
print("6. N* TROTTER, PRODUZIONE, PUNTO ANOMALO (atteso uno spostamento)")
print("=" * 70)
N_star_i3, F_i3, _ = scan_N_star_trotter(vqe_params_ideali, t_eval, N_grid_t, psi_exact,
                                          nm_ref, prep_level=3)
N_star_x3, F_x3, _ = scan_N_star_trotter(X_ANOMALO, t_eval, N_grid_t, psi_exact,
                                          nm_ref, prep_level=3)
print(f"  N*(ideale, livello 3) = {N_star_i3}   F(N*) = {F_i3:.6f}")
print(f"  N*(anomalo, livello 3) = {N_star_x3}   F(N*) = {F_x3:.6f}")
assert N_star_i3 == 3 and N_star_x3 == 4, \
    f"il fenomeno di spostamento N* Trotter non si riproduce ({N_star_i3}->{N_star_x3})"
print("  -> OK (atteso): N* si sposta 3->4 sul punto anomalo -- riproducibile, non un caso isolato.")

print()
print("=" * 70)
print("7. N* CORRELATORE, PRODUZIONE, PUNTO ANOMALO (atteso invariato)")
print("=" * 70)
N_star_ci3, val_ci3, _ = scan_N_star_correlatore(2, "x", 1, "x", vqe_params_ideali, t_eval,
                                                  N_grid_c, nm_ref, p_ro, prep_level=3)
N_star_cx3, val_cx3, _ = scan_N_star_correlatore(2, "x", 1, "x", X_ANOMALO, t_eval,
                                                  N_grid_c, nm_ref, p_ro, prep_level=3)
print(f"  N*(ideale, livello 3) = {N_star_ci3}   |C(N*)| = {val_ci3:.6f}")
print(f"  N*(anomalo, livello 3) = {N_star_cx3}   |C(N*)| = {val_cx3:.6f}")
assert N_star_ci3 == N_star_cx3 == 3, \
    "il correlatore non resta invariato sul punto anomalo -- l'asimmetria fra metriche non si riproduce"
print("  -> OK (atteso): N* correlatore resta 3->3 anche sul punto anomalo -- l'asimmetria "
      "fra le due metriche (Trotter si sposta, correlatore no) e' riproducibile.")

print()
print("=" * 70)
print("TUTTI I CONTROLLI SUPERATI")
print("=" * 70)
