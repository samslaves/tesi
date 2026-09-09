"""Figura del documento 9 -- N* (fedelta' di Trotter) in funzione di
eps_2q e eps_1q, scala log, l'altro parametro fissato al riferimento."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *
from scan_parametri_rumore_dimero import scan_eps2q, scan_eps1q
from noise_model_dimero import EPS_1Q_REF, EPS_2Q_REF

os.makedirs("figure", exist_ok=True)

data = np.load("ground_state_test2.npz")
vqe_params = data["vqe_params"]
psi0_exact = data["psi0_exact"]

eps2q_values = [1e-3, 2e-3, 3.8e-3, 6e-3, 1e-2, 1.5e-2, 2.5e-2]
eps1q_values = [1e-4, 2.9e-4, 1e-3, 3e-3, 1e-2, 3e-2]

res2q = scan_eps2q(vqe_params, psi0_exact, eps2q_values)
res1q = scan_eps1q(vqe_params, psi0_exact, eps1q_values)

e2, N2, _ = zip(*res2q)
e1, N1, _ = zip(*res1q)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.4, 4.4))
a1.plot(e2, N2, color=C_ROSSO, marker="o", ms=6, lw=2.0)
a1.axvline(EPS_2Q_REF, color="0.55", ls=":", lw=1.4)
a1.set_xscale("log")
a1.set_xlabel(r"$\varepsilon_{2q}$")
a1.set_ylabel(r"$N^*$")
a1.set_title(r"$N^*$ vs $\varepsilon_{2q}$")

a2.plot(e1, N1, color=C_BLU, marker="o", ms=6, lw=2.0)
a2.axvline(EPS_1Q_REF, color="0.55", ls=":", lw=1.4)
a2.set_xscale("log")
a2.set_xlabel(r"$\varepsilon_{1q}$")
a2.set_ylabel(r"$N^*$")
a2.set_title(r"$N^*$ vs $\varepsilon_{1q}$")

salva(fig, "fig_passo5_Nstar_vs_eps")

print("scan eps2q:", list(zip(e2, N2)))
print("scan eps1q:", list(zip(e1, N1)))

# =====================================================================
# Tabella invarianza da p_readout (correlatore C_11^yz), readout
# genuinamente campionato a shot finiti -- non compare in una figura,
# ma tracciata qui per riproducibilita' (usata nel testo del Documento 9).
# =====================================================================
from correlatori_shots_dimero import correlator_shots, SHOTS_DEFAULT

N_grid_corr = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 40]
for p in [0.00, 0.05, 0.20]:
    vals = [abs(correlator_shots(1, "y", 1, "z", 2.0, N, vqe_params,
                                  p01=p, p10=p, shots=SHOTS_DEFAULT, seed=1))
            for N in N_grid_corr]
    vals = np.array(vals)
    idx = int(np.argmax(vals))
    print(f"readout p={p:.2f}  N*={N_grid_corr[idx]}  |C(N*)|={vals[idx]:.4f}")
