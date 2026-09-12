"""
Genera i dati del SECONDO punto di lavoro (b/J=-0.18, D/J=1, J=1) usato
per verificare la generalita' dei risultati dell'estensione VQE
noise-aware (vedi risultati_vqe_noise_aware_definitivo.tex, sezione
"Generalita': un secondo punto di lavoro").

Eseguire DALLA RADICE del pacchetto, DOPO 01_ e 02_:
    python3 03_genera_dati_secondo_punto.py

Questo punto era gia' usato nella documentazione narrativa per la
discussione (dimero_03_dinamica.tex, dinamica non monocromatica) --
qui si ottimizza il VQE (ideale e noise-aware) per quel punto, con lo
stesso ansatz PMA-2q.3 usato ovunque nel progetto.

Produce:
  dati/ground_state_punto2.npz       -- ground state esatto + VQE ideale
  dati/vqe_noise_aware_punto2.npz    -- VQE noise-aware allo stesso punto

RUOLO NELL'INSIEME DEL PACCHETTO: e' il terzo e ultimo script di
generazione dati -- a differenza di 01_ e 02_ (che lavorano al punto
"test 2" e producono prerequisiti per quasi tutto il resto), questo
script serve solo alla figura del secondo punto di lavoro
(fig_secondo_punto_confronto.pdf) e a nessun altro file. E' anche
l'esempio pratico, in questo pacchetto, di come lavorare correttamente
a un punto di lavoro diverso da "test 2" con vqe_noise_aware_dimero.py
-- vedi il monkey-patch esplicito di vna_module.b/D/J qualche riga
sotto, e la spiegazione completa in GUIDA_USO.md sez. 6.
"""
import sys, os
sys.path.insert(0, "codice")
import numpy as np

from vqe_test2 import exact_ground, pma_2q, vqe_multistart
from dimer_exact import dimer_hamiltonian
from noise_model_dimero import build_noise_model
import vqe_noise_aware_dimero as vna_module
from vqe_noise_aware_dimero import vqe_noise_aware, energia_fedelta_rumorosa

J, b, D = 1.0, -0.18, 1.0

# ATTENZIONE (trappola nota, verificata su questo stesso script): la
# funzione vqe_noise_aware() del modulo vqe_noise_aware_dimero.py
# costruisce internamente H = dimer_hamiltonian(b=b, J=J, D=D) leggendo
# le costanti DI MODULO (fissate a "test 2": b=0.35, D=0.80), non un
# parametro passabile. Per un punto di lavoro diverso va sovrascritto
# esplicitamente l'attributo di modulo PRIMA di chiamare la funzione --
# altrimenti l'ottimizzazione avviene silenziosamente sull'Hamiltoniana
# sbagliata. energia_fedelta_rumorosa(), usata sotto per la valutazione
# finale, non ha questo problema: prende H come parametro esplicito.
vna_module.b, vna_module.D, vna_module.J = b, D, J

print("=" * 70)
print(f"Secondo punto di lavoro: b/J={b/J:.3f}  D/J={D/J:.3f}  J={J}")
print("=" * 70)

# --- ground state esatto ---
E0_exact, psi0_exact, w, v = exact_ground(b, J, D)
print("Spettro:", np.round(w, 6))
print("E0 esatto:", E0_exact)

# --- VQE ideale, multistart su 10 seed (un solo seed non basta a questo
#     punto per la fedelta' a precisione macchina, verificato) ---
H_op = dimer_hamiltonian(b, J, D)
ansatz = pma_2q(3)
best = None
for seed in range(10):
    ris = vqe_multistart(ansatz, H_op, w, v, R=6, seed=seed)
    if best is None or ris["E"] < best["E"]:
        best = ris
    print(f"  seed={seed}: E={ris['E']:.10f}  F={ris['fid']:.10f}")
vqe_params_ideali = best["x"]
print("MIGLIORE:", best["E"], best["fid"], best["x"])

os.makedirs("dati", exist_ok=True)
np.savez("dati/ground_state_punto2.npz", b=b, J=J, D=D, E0_exact=E0_exact,
         psi0_exact=psi0_exact, vqe_params=vqe_params_ideali,
         fidelity=best["fid"], E_vqe=best["E"])
print("\n[salvato] dati/ground_state_punto2.npz")

# --- VQE noise-aware allo stesso punto ---
nm_ref, _ = build_noise_model()
H2 = dimer_hamiltonian(b=b, J=J, D=D)  # esplicito: mai i default del modulo (b=0.35,D=0.80 di "test 2")

E_ideale_su_rumore, F_ideale_su_rumore, _ = energia_fedelta_rumorosa(
    vqe_params_ideali, H2, nm_ref, psi0_exact)
print("\nRiuso ideale sotto rumore: E=", E_ideale_su_rumore,
      " F=", F_ideale_su_rumore)

ris_rumore = vqe_noise_aware(noise_model=nm_ref, R=6, maxiter=300, seed=0,
                              x_seme=vqe_params_ideali)
E_na, F_na, _ = energia_fedelta_rumorosa(ris_rumore["x"], H2, nm_ref,
                                          psi0_exact)
print("Noise-aware: E=", E_na, " F=", F_na)
print("Delta E =", E_na - E_ideale_su_rumore)
print("Delta F =", F_na - F_ideale_su_rumore)

np.savez("dati/vqe_noise_aware_punto2.npz", x_noise_aware=ris_rumore["x"],
         E_noise_aware=E_na, F_noise_aware=F_na,
         E_ideale_su_rumore=E_ideale_su_rumore,
         F_ideale_su_rumore=F_ideale_su_rumore)
print("\n[salvato] dati/vqe_noise_aware_punto2.npz")
