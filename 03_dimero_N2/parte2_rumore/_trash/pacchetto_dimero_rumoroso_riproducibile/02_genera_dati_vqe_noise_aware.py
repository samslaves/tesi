"""
02 -- Genera il VQE noise-aware (ottimizzato di nuovo sotto rumore, non
riusando i parametri ideali) per il punto "test 2".

Eseguire DALLA RADICE del pacchetto, DOPO 01_genera_dati_vqe_ideale.py:
    python3 02_genera_dati_vqe_noise_aware.py

Salva in dati/vqe_noise_aware_result.npz.

RUOLO NELL'INSIEME DEL PACCHETTO: e' il secondo script della sequenza --
dipende da dati/ground_state_test2.npz (prodotto da 01_) e produce a sua
volta dati/vqe_noise_aware_result.npz, prerequisito per gli script di
figura dell'estensione VQE noise-aware e per 03_genera_dati_secondo_punto.py
(che ne riusa il pattern, non i dati). Orchestra, in un unico posto,
tutti e quattro i controlli principali dell'estensione: invarianza CNOT,
riuso ideale sotto rumore, ottimizzazione noise-aware vera e propria, e
il controllo diretto su N* del correlatore.
"""
import sys, os
sys.path.insert(0, "codice")
import numpy as np

from dimer_exact import dimer_hamiltonian
from noise_model_dimero import build_noise_model
from vqe_noise_aware_dimero import (
    vqe_noise_aware, energia_fedelta_rumorosa, controllo_invarianza_cnot,
    controllo_N_star_correlatore,
)
from vqe_dm_rumoroso_dimero import vqe_energia_fedelta_rumorosa

data = np.load("dati/ground_state_test2.npz")
vqe_params_ideali = data["vqe_params"]
psi0_exact = data["psi0_exact"]

nm_ref, _ = build_noise_model()

# 1. controllo invarianza CNOT (premessa fisica dell'argomento)
conteggi, dettagli = controllo_invarianza_cnot(n_prove=5, seed=0)
print("Invarianza CNOT su 5 prove:", conteggi)
assert len(set(conteggi)) == 1, "il conteggio CNOT dipende da theta!"

# 2. riuso ideale sotto rumore (gia' noto da Passo 2)
E_ideale_su_rumore, F_ideale_su_rumore, _ = vqe_energia_fedelta_rumorosa(
    vqe_params_ideali, psi0_exact, noise_model=nm_ref)
print("Riuso ideale sotto rumore: E=", E_ideale_su_rumore,
      " F=", F_ideale_su_rumore)

# 3. VQE noise-aware vero e proprio
ris_rumore = vqe_noise_aware(noise_model=nm_ref, R=6, maxiter=300, seed=0,
                              x_seme=vqe_params_ideali)
H = dimer_hamiltonian(b=0.35, J=1.0, D=0.80)
E_na, F_na, _ = energia_fedelta_rumorosa(ris_rumore["x"], H, nm_ref, psi0_exact)
print("Noise-aware: E=", E_na, " F=", F_na)
print("Delta E =", E_na - E_ideale_su_rumore)
print("Delta F =", F_na - F_ideale_su_rumore)

# 4. controllo diretto sul correlatore (Passo 4), non per analogia
ris_corr = controllo_N_star_correlatore(vqe_params_ideali, ris_rumore["x"], nm_ref)
print("N* correlatore: ideale=", ris_corr["N_star_ideale"],
      " noise-aware=", ris_corr["N_star_na"])

os.makedirs("dati", exist_ok=True)
np.savez("dati/vqe_noise_aware_result.npz",
         x_noise_aware=ris_rumore["x"],
         E_noise_aware=E_na, F_noise_aware=F_na,
         E_ideale_su_rumore=E_ideale_su_rumore,
         F_ideale_su_rumore=F_ideale_su_rumore,
         cnot_invarianza=conteggi,
         N_grid_corr=ris_corr["N_grid"],
         vals_corr_ideale=ris_corr["vals_ideale"],
         vals_corr_na=ris_corr["vals_na"],
         N_star_corr_ideale=ris_corr["N_star_ideale"],
         N_star_corr_na=ris_corr["N_star_na"])
print("\n[salvato] dati/vqe_noise_aware_result.npz")

print("\nValori attesi (verificati nel lavoro originale):")
print("  Delta E ~ -1.16e-07, Delta F ~ +1.76e-08")
print("  N* correlatore: 5 -> 5")
