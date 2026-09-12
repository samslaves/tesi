"""Figura documento 06 (anello) -- energia e fedelta' rumorose del VQE con
termine DM, in funzione di eps_2q."""
import os, time
import numpy as np
import matplotlib.pyplot as plt
from stile import *
from vqe_dm_rumoroso_trimero_anello import vqe_energia_fedelta_rumorosa
from noise_model_trimero_anello import build_noise_model, EPS_2Q_REF

os.makedirs("figure", exist_ok=True)
data = np.load("w2q6_params_optimal.npz")
vqe_params = data["params"]

H0 = None
from trimer_ring_exact import trimer_hamiltonian_dm
Hmat = trimer_hamiltonian_dm(1.0, 0.4, 2.4, "B", 0.15).to_matrix()
Evals, V = np.linalg.eigh(Hmat)
psi0_exact = V[:, 0]
imax = np.argmax(np.abs(psi0_exact))
psi0_exact = psi0_exact * np.exp(-1j*np.angle(psi0_exact[imax]))

eps2q_grid = np.concatenate([[0.0], np.geomspace(2e-4, 1.6e-2, 16)])
Es, Fs = [], []
t0=time.time()
for eps2q in eps2q_grid:
    nm, _ = build_noise_model(eps_2q=eps2q)
    E, F, _ = vqe_energia_fedelta_rumorosa(vqe_params, psi0_exact, noise_model=nm)
    Es.append(E); Fs.append(F)
Es, Fs = np.array(Es), np.array(Fs)
print(f"tempo: {time.time()-t0:.0f}s")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.2))
a1.plot(eps2q_grid, Es, color=C_BLU, marker="o", ms=4, lw=1.8)
a1.axvline(EPS_2Q_REF, color="0.55", ls=":", lw=1.4)
a1.set_xlabel(r"$\varepsilon_{2q}$"); a1.set_ylabel(r"$E$ (rumoroso)")
a1.set_title("Energia")
a1.ticklabel_format(axis="x", style="sci", scilimits=(0,0), useMathText=True)
a2.plot(eps2q_grid, Fs, color=C_ROSSO, marker="o", ms=4, lw=1.8)
a2.axvline(EPS_2Q_REF, color="0.55", ls=":", lw=1.4)
a2.set_xlabel(r"$\varepsilon_{2q}$"); a2.set_ylabel(r"$F$ (rumorosa)")
a2.set_title("Fedeltà")
a2.ticklabel_format(axis="x", style="sci", scilimits=(0,0), useMathText=True)
salva(fig, "fig_passo2_scan_eps2q_anello")

idx_ref = np.argmin(np.abs(eps2q_grid - EPS_2Q_REF))
print(f"al riferimento: E={Es[idx_ref]:.6f}  F={Fs[idx_ref]:.6f}")
