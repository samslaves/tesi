"""
01 -- Genera il ground state esatto e il VQE ideale per il punto di
lavoro principale ("test 2": b/J=0.35, D/J=0.80, J=1).

Eseguire DALLA RADICE del pacchetto:
    python3 01_genera_dati_vqe_ideale.py

Riproduce la stessa ottimizzazione multistart di Parte 1 (nessun
rumore). Salva in dati/ground_state_test2.npz -- prerequisito per
quasi tutto il resto del pacchetto.

RUOLO NELL'INSIEME DEL PACCHETTO: e' il PRIMO script da eseguire, in
assoluto -- ogni altro script (dati, validazioni, figure) dipende,
direttamente o indirettamente, dal file dati/ground_state_test2.npz
che questo script produce. Non definisce funzioni proprie: e' un
orchestratore lineare che chiama exact_ground(), pma_2q() e
vqe_multistart() di codice/vqe_test2.py con il punto di lavoro fissato
qui esplicitamente (a differenza del blocco __main__ di quel modulo,
che userebbe lo stesso punto ma salverebbe nella cartella corrente
invece che in dati/).
"""
import sys, os
sys.path.insert(0, "codice")
import numpy as np

from vqe_test2 import exact_ground, pma_2q, vqe_multistart
from dimer_exact import dimer_hamiltonian

J, b, D = 1.0, 0.35, 0.80

print(f"Punto di lavoro: b/J={b/J}, D/J={D/J}, J={J}")

E0_exact, psi0_exact, w, v = exact_ground(b, J, D)
print("E0 esatto:", E0_exact)

H_op = dimer_hamiltonian(b, J, D)
ansatz = pma_2q(3)
ris = vqe_multistart(ansatz, H_op, w, v, R=6, seed=0)
print("E VQE:", ris["E"], " |E-E0|=", abs(ris["E"] - E0_exact))
print("Fedeltà:", ris["fid"])
print("Parametri:", ris["x"])

os.makedirs("dati", exist_ok=True)
np.savez("dati/ground_state_test2.npz", b=b, J=J, D=D, E0_exact=E0_exact,
         psi0_exact=psi0_exact, vqe_params=ris["x"], fidelity=ris["fid"],
         E_vqe=ris["E"])
print("\n[salvato] dati/ground_state_test2.npz")

print("\nValori attesi (verificati nel lavoro originale):")
print("  E VQE ideale ~ -3.57321145, fedeltà ~ 1.0000000000")
