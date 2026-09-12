import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))


"""
Verifica obbligatoria di correlatori_readout_asimmetrico_trimero_anello.py
(Stadio 6bis) prima di considerarlo concluso. Mirror concettuale di
validate_correlatori_readout_asimmetrico_dimero.py.

  1. Caso simmetrico (p01=p10) deve coincidere con lo Stadio 4bis
     (correlatori_shots_trimero_anello), entro l'errore statistico --
     verifica che il modulo generale si riduca correttamente al caso
     particolare gia' validato.
  2. N* invariante rispetto al rapporto p10/p01, su tutto un range
     realistico ed oltre (1x-50x), media fissa.
"""
import numpy as np

from correlatori_shots_trimero_anello import correlator_shots, SHOTS_DEFAULT
from correlatori_readout_asimmetrico_trimero_anello import correlator_shots_asimmetrico
from noise_model_trimero_anello import build_noise_model, P_READOUT_REF

data = np.load("w2q6_params_optimal.npz")
vqe_params = data["params"]

print("=" * 70)
print("1. CASO SIMMETRICO: il modulo generale deve ridursi al caso gia' validato")
print("=" * 70)
nm_ref, _ = build_noise_model()
c_stadio4bis = correlator_shots(2, "x", 1, "x", 2.0, 3, 1.0, 0.4, 2.4, 0.15,
                                 vqe_params, noise_model=nm_ref, shots=SHOTS_DEFAULT)
c_generale_simmetrico = correlator_shots_asimmetrico(
    2, "x", 1, "x", 2.0, 3, 1.0, 0.4, 2.4, 0.15, vqe_params,
    p01=P_READOUT_REF, p10=P_READOUT_REF, shots=SHOTS_DEFAULT)
scarto = abs(c_stadio4bis - c_generale_simmetrico)
atteso = 2 / np.sqrt(SHOTS_DEFAULT)  # due stime indipendenti, tolleranza raddoppiata
print(f"  Stadio 4bis (readout simmetrico dedicato): {c_stadio4bis:.4f}")
print(f"  Qui, p01=p10={P_READOUT_REF} (caso generale): {c_generale_simmetrico:.4f}")
print(f"  |scarto| = {scarto:.2e}  (atteso ~{atteso:.2e})")
assert scarto < 5 * atteso
print("  -> OK")

print()
print("=" * 70)
print("2. N* INVARIANTE RISPETTO AL RAPPORTO p10/p01 (media fissa)")
print("=" * 70)
P_MEDIO = P_READOUT_REF
N_grid = [1, 2, 3, 4, 5, 6, 8, 10]
rapporti = [1, 3, 5, 10, 20, 50]
Nstars = []
for rap in rapporti:
    p01 = 2 * P_MEDIO / (1 + rap)
    p10 = rap * p01
    vals = [abs(correlator_shots_asimmetrico(2, "x", 1, "x", 2.0, N, 1.0, 0.4, 2.4, 0.15,
                                              vqe_params, p01=p01, p10=p10, shots=80_000))
             for N in N_grid]
    Nstar = N_grid[int(np.argmax(vals))]
    Nstars.append(Nstar)
    print(f"  rapporto p10/p01 = {rap:3d}x: N* = {Nstar}")

assert all(n == 3 for n in Nstars), f"N* non invariante: {Nstars}"
print("  -> OK: N*=3 su tutto il range testato, 1x-50x")

np.savez("readout_asimmetrico_validato.npz",
         rapporti=np.array(rapporti), Nstars=np.array(Nstars))
print("\nSalvato: readout_asimmetrico_validato.npz")
