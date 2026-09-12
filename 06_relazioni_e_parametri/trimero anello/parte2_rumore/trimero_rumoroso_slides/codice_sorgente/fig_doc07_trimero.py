"""Figure documento 07 (anello) -- fedelta' F(N) sotto rumore, Scenario A e R0."""
import os, time
import numpy as np
import matplotlib.pyplot as plt
from stile import *
from trotter_rumoroso_trimero_anello import fedelta_trotter_rumoroso, PUNTO_VQE, PUNTO_R0
from noise_model_trimero_anello import build_noise_model
from trimer_ring_exact import trimer_hamiltonian_dm

os.makedirs("figure", exist_ok=True)
data = np.load("w2q6_params_optimal.npz")
vqe_params = data["params"]
nm_ref, _ = build_noise_model()
t = 2.0

# Scenario A -- preparazione VQE
HA = trimer_hamiltonian_dm(PUNTO_VQE["J"], PUNTO_VQE["Jp"], PUNTO_VQE["b"], "B", PUNTO_VQE["D"]).to_matrix()
EA, VA = np.linalg.eigh(HA)
psi0_A = VA[:, 0]
imax = np.argmax(np.abs(psi0_A)); psi0_A = psi0_A * np.exp(-1j*np.angle(psi0_A[imax]))

N_grid = [1,2,3,4,5,6,7,8,10,12,15,20,30,40,60,80]
t0=time.time()
F_A = []
for N in N_grid:
    F,_ = fedelta_trotter_rumoroso(**PUNTO_VQE, t=t, N=N, psi0=psi0_A, noise_model=nm_ref, vqe_params=vqe_params)
    F_A.append(F)
F_A = np.array(F_A)
NstarA = N_grid[int(np.argmax(F_A))]
print(f"Scenario A: N*={NstarA}  F(N*)={F_A.max():.6f}  (t={time.time()-t0:.0f}s)")

# Scenario B (R0) -- da |000>
psi0_000 = np.zeros(8, dtype=complex); psi0_000[0]=1.0
N_grid_B = [1,2,3,4,5,6,7,8,9,10,12,15,20,30,40,60,80,120,160]
t0=time.time()
F_B = []
for N in N_grid_B:
    F,_ = fedelta_trotter_rumoroso(**PUNTO_R0, t=t, N=N, psi0=psi0_000, noise_model=nm_ref, vqe_params=None)
    F_B.append(F)
F_B = np.array(F_B)
NstarB = N_grid_B[int(np.argmax(F_B))]
print(f"Scenario B (R0): N*={NstarB}  F(N*)={F_B.max():.6f}  (t={time.time()-t0:.0f}s)")

fig, (a1,a2) = plt.subplots(1,2, figsize=(11.4,4.4))
a1.plot(N_grid, F_A, color=C_ROSSO, marker="o", ms=5, lw=2.0)
a1.axvline(NstarA, color="0.55", ls=":", lw=1.4)
a1.annotate(f"$N^*={NstarA}$", xy=(NstarA, F_A.max()), xytext=(NstarA+3, F_A.max()-0.12),
            fontsize=11, color=C_ROSSO, arrowprops=dict(arrowstyle="->", color=C_ROSSO))
a1.set_xlabel(r"$N$"); a1.set_ylabel(r"$F(N)$")
a1.set_title("Scenario A (preparazione VQE)")

a2.plot(N_grid_B, F_B, color=C_VERDE, marker="s", ms=5, lw=2.0)
a2.axvline(NstarB, color="0.55", ls=":", lw=1.4)
a2.annotate(f"$N^*={NstarB}$", xy=(NstarB, F_B.max()), xytext=(NstarB+5, F_B.max()-0.1),
            fontsize=11, color=C_VERDE, arrowprops=dict(arrowstyle="->", color=C_VERDE))
a2.set_xlabel(r"$N$"); a2.set_ylabel(r"$F(N)$")
a2.set_title(r"Scenario B ($R_0$, da $|000\rangle$)")
salva(fig, "fig_passo3_F_vs_N_anello")
