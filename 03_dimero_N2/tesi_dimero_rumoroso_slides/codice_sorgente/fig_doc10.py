"""Figure del documento 10 -- VQE noise-aware. Sette figure, tutte
ricalcolate dai moduli fisici verificati della pipeline (nessun dato
raster/preview riusato)."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *

from qiskit import transpile
from vqe_test2 import pma_2q, dimer_hamiltonian
from noise_model_dimero import build_noise_model, BASIS_GATES
from vqe_noise_aware_dimero import (
    vqe_noise_aware, energia_fedelta_rumorosa, controllo_N_star_correlatore,
    verifica_secondo_punto_lavoro, transpila_dopo_assegnazione,
)
from vqe_dm_rumoroso_dimero import vqe_energia_fedelta_rumorosa
from trotter_rumoroso_dimero import fedelta_trotter_rumoroso
from correlatori_rumorosi_dimero import correlator_rumoroso, J_DEFAULT, b_DEFAULT, D_DEFAULT
from scan_parametri_rumore_dimero import trova_N_star
from verifica_passo5_noise_aware import verifica_griglia_completa, N_star_correlatore

os.makedirs("figure", exist_ok=True)

data = np.load("ground_state_test2.npz")
vqe_params_ideali = data["vqe_params"]
psi_exact = data["psi0_exact"]
J, b, D = 1.0, 0.35, 0.80
H = dimer_hamiltonian(b=b, J=J, D=D)
nm_ref, _ = build_noise_model()

# =====================================================================
# 1. fig_bug_conteggio_gate -- transpilare prima o dopo l'assegnazione
# =====================================================================
x_demo = vqe_params_ideali
ansatz_sym = pma_2q(3)
tqc_prima = transpile(ansatz_sym, basis_gates=BASIS_GATES,
                       optimization_level=3, seed_transpiler=7)
tqc_prima = tqc_prima.assign_parameters(x_demo)
ops_prima = tqc_prima.count_ops()

tqc_dopo = transpila_dopo_assegnazione(x_demo)
ops_dopo = tqc_dopo.count_ops()

gates = ["rz", "sx", "cx"]
vals_prima = [ops_prima.get(g, 0) for g in gates]
vals_dopo = [ops_dopo.get(g, 0) for g in gates]

fig, ax = plt.subplots(figsize=(5.6, 4.2))
x = np.arange(len(gates))
w = 0.35
ax.bar(x - w / 2, vals_prima, width=w, color=C_ROSSO, label="transpila poi assegna")
ax.bar(x + w / 2, vals_dopo, width=w, color=C_VERDE, label="assegna poi transpila")
ax.set_xticks(x); ax.set_xticklabels([r"\texttt{rz}", r"\texttt{sx}", r"\texttt{cx}"])
ax.set_ylabel("conteggio")
ax.set_title("Costo in gate: ordine di transpilazione/assegnazione")
ax.legend(loc="upper right")
salva(fig, "fig_bug_conteggio_gate")
print("prima:", ops_prima, " dopo:", ops_dopo)

# =====================================================================
# 2. VQE noise-aware: risultato principale (R=6 + seme)
# =====================================================================
ris_na = vqe_noise_aware(noise_model=nm_ref, R=6, maxiter=300, seed=0,
                          x_seme=vqe_params_ideali)
x_na = ris_na["x"]
E_na, F_na, ncx_na = energia_fedelta_rumorosa(x_na, H, nm_ref, psi_exact)
E_id, F_id, ncx_id = vqe_energia_fedelta_rumorosa(vqe_params_ideali, psi_exact,
                                                    noise_model=nm_ref)
print(f"E_id={E_id:.8f} F_id={F_id:.8f}  E_na={E_na:.8f} F_na={F_na:.8f}")

# =====================================================================
# 3. fig_scan_eps2q_confronto -- energia/fedelta' vs eps2q, riuso vs noise-aware
# =====================================================================
eps2q_grid = np.concatenate([[0.0], np.geomspace(2e-4, 1.6e-2, 18)])
E_id_scan, F_id_scan, E_na_scan, F_na_scan = [], [], [], []
for eps2q in eps2q_grid:
    nm, _ = build_noise_model(eps_2q=eps2q)
    Ei, Fi, _ = vqe_energia_fedelta_rumorosa(vqe_params_ideali, psi_exact, noise_model=nm)
    En, Fn, _ = energia_fedelta_rumorosa(x_na, H, nm, psi_exact)
    E_id_scan.append(Ei); F_id_scan.append(Fi)
    E_na_scan.append(En); F_na_scan.append(Fn)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.2))
a1.plot(eps2q_grid, E_id_scan, color=C_BLU, lw=2.2, label=r"riuso $\theta^*_\mathrm{ideale}$")
a1.plot(eps2q_grid, E_na_scan, color=C_ARANC, lw=1.6, ls="--", label="noise-aware")
a1.set_xlabel(r"$\varepsilon_{2q}$"); a1.set_ylabel("Energia")
a1.legend(loc="lower left")
a1.ticklabel_format(axis="x", style="sci", scilimits=(0, 0), useMathText=True)
a2.plot(eps2q_grid, F_id_scan, color=C_BLU, lw=2.2, label=r"riuso $\theta^*_\mathrm{ideale}$")
a2.plot(eps2q_grid, F_na_scan, color=C_ARANC, lw=1.6, ls="--", label="noise-aware")
a2.set_xlabel(r"$\varepsilon_{2q}$"); a2.set_ylabel("Fedelt\u00e0")
a2.legend(loc="lower left")
a2.ticklabel_format(axis="x", style="sci", scilimits=(0, 0), useMathText=True)
salva(fig, "fig_scan_eps2q_confronto")

# =====================================================================
# 4. fig_robustezza_multistart
# =====================================================================
ris_r6 = vqe_noise_aware(noise_model=nm_ref, R=6, maxiter=300, seed=1)
ris_r6seme = ris_na
ris_r20 = vqe_noise_aware(noise_model=nm_ref, R=20, maxiter=300, seed=2)
E_ottimo = min(ris_r6seme["finals"].min(), ris_r20["finals"].min())

fig, ax = plt.subplots(figsize=(6.2, 4.6))
groups = [("R=6\n(no seme)", ris_r6["finals"], C_ROSSO),
          ("R=6+seme", ris_r6seme["finals"], C_BLU),
          ("R=20\n(no seme)", ris_r20["finals"], C_ARANC)]
for k, (lbl, finals, col) in enumerate(groups):
    xs = np.full(len(finals), k) + np.random.default_rng(0).uniform(-0.08, 0.08, len(finals))
    ax.scatter(xs, finals, color=col, s=28, zorder=3)
ax.axhline(E_ottimo, color="0.4", ls="--", lw=1.2, label=f"ottimo noto $E={E_ottimo:.6f}$")
ax.set_xticks(range(3)); ax.set_xticklabels([g[0] for g in groups])
ax.set_ylabel(r"$E$ finale (per singolo restart COBYLA)")
ax.set_title("Dispersione degli esiti del multistart (rumore acceso)")
ax.legend(loc="upper right", fontsize=10)
salva(fig, "fig_robustezza_multistart")

# =====================================================================
# 5. fig_F_vs_N_confronto -- fedelta' di Trotter, ideale vs noise-aware
# =====================================================================
N_grid_t = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 60, 80, 120, 160]
F_id_t, F_na_t = [], []
for N in N_grid_t:
    Fi, _ = fedelta_trotter_rumoroso(vqe_params_ideali, psi_exact, 2.0, N, noise_model=nm_ref)
    Fn, _ = fedelta_trotter_rumoroso(x_na, psi_exact, 2.0, N, noise_model=nm_ref)
    F_id_t.append(Fi); F_na_t.append(Fn)
F_id_t, F_na_t = np.array(F_id_t), np.array(F_na_t)
Nstar_t = N_grid_t[int(np.argmax(F_na_t))]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.2))
a1.plot(N_grid_t, F_id_t, color=C_BLU, marker="o", ms=4, lw=1.8, label=r"$\theta^*_\mathrm{ideale}$")
a1.plot(N_grid_t, F_na_t, color=C_ARANC, marker="s", ms=4, lw=1.4, ls="--", label="noise-aware")
a1.axvline(Nstar_t, color="0.55", ls=":", lw=1.2)
a1.set_xlabel(r"$N$"); a1.set_ylabel(r"$F(N)$"); a1.legend(loc="lower right")
a2.plot(N_grid_t, F_na_t - F_id_t, color=C_ROSSO, marker="o", ms=4, lw=1.6)
a2.set_xlabel(r"$N$"); a2.set_ylabel(r"noise-aware $-$ ideale")
salva(fig, "fig_F_vs_N_confronto")
print("N* Trotter (na) =", Nstar_t)

# =====================================================================
# 6. fig_correlatore_noise_aware_confronto
# =====================================================================
ris_corr = controllo_N_star_correlatore(vqe_params_ideali, x_na, nm_ref)
Ng = ris_corr["N_grid"]
vi = np.array(ris_corr["vals_ideale"])
vn = np.array(ris_corr["vals_na"])

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.2))
a1.plot(Ng, vi, color=C_BLU, marker="o", ms=4, lw=1.8, label=r"$\theta^*_\mathrm{ideale}$")
a1.plot(Ng, vn, color=C_ARANC, marker="s", ms=4, lw=1.4, ls="--", label="noise-aware")
a1.axvline(ris_corr["N_star_ideale"], color="0.55", ls=":", lw=1.2)
a1.set_xlabel(r"$N$"); a1.set_ylabel(r"$|C(N)|$"); a1.legend(loc="lower right")
a2.plot(Ng, vn - vi, color=C_ROSSO, marker="o", ms=4, lw=1.6)
a2.set_xlabel(r"$N$"); a2.set_ylabel(r"noise-aware $-$ ideale")
salva(fig, "fig_correlatore_noise_aware_confronto")
print("N* corr ideale/na:", ris_corr["N_star_ideale"], ris_corr["N_star_na"])

# =====================================================================
# 7. fig_secondo_punto_confronto
# =====================================================================
ris2 = verifica_secondo_punto_lavoro(nm_ref, R=6, maxiter=300, seed=0)
Ng2t = ris2["N_grid_trotter"]; Fi2 = np.array(ris2["F_trotter_ideale"]); Fn2 = np.array(ris2["F_trotter_na"])
Ng2c = ris2["N_grid_corr"]; vi2 = np.array(ris2["vals_corr_ideale"]); vn2 = np.array(ris2["vals_corr_na"])

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.2))
a1.plot(Ng2t, Fi2, color=C_BLU, marker="o", ms=4, lw=1.8, label=r"$\theta^*_\mathrm{ideale}$")
a1.plot(Ng2t, Fn2, color=C_ARANC, marker="s", ms=4, lw=1.4, ls="--", label="noise-aware")
a1.axvline(ris2["N_star_trotter_ideale"], color="0.55", ls=":", lw=1.2)
a1.set_xlabel(r"$N$"); a1.set_ylabel(r"$F(N)$")
a1.set_title("Fedelt\u00e0 di Trotter, secondo punto")
a1.legend(loc="lower right")
a2.plot(Ng2c, vi2, color=C_BLU, marker="o", ms=4, lw=1.8, label=r"$\theta^*_\mathrm{ideale}$")
a2.plot(Ng2c, vn2, color=C_ARANC, marker="s", ms=4, lw=1.4, ls="--", label="noise-aware")
a2.axvline(ris2["N_star_corr_ideale"], color="0.55", ls=":", lw=1.2)
a2.set_xlabel(r"$N$"); a2.set_ylabel(r"$|C(N)|$")
a2.set_title("Correlatore, secondo punto")
a2.legend(loc="lower right")
salva(fig, "fig_secondo_punto_confronto")
print("secondo punto N* trotter:", ris2["N_star_trotter_ideale"], ris2["N_star_trotter_na"])
print("secondo punto N* corr:", ris2["N_star_corr_ideale"], ris2["N_star_corr_na"])

np.savez("vqe_noise_aware_result.npz", x_noise_aware=x_na,
         E_noise_aware=E_na, F_noise_aware=F_na,
         E_ideale_su_rumore=E_id, F_ideale_su_rumore=F_id)

# =====================================================================
# 8. fig_passo5_griglia_completa
# =====================================================================
righe = verifica_griglia_completa(vqe_params_ideali, x_na, psi_exact)
trotter_eps2q = [(v, Ni, Nn) for (m, p, v, Ni, Nn, ok) in righe if m == "Trotter" and p == "eps_2q"]
corr_eps2q = [(v, Ni, Nn) for (m, p, v, Ni, Nn, ok) in righe if m == "Correlatore" and p == "eps_2q"]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.2))
v, Ni, Nn = zip(*trotter_eps2q)
a1.plot(v, Ni, color=C_BLU, marker="o", ms=6, lw=1.8, label=r"$\theta^*_\mathrm{ideale}$")
a1.plot(v, Nn, color=C_ARANC, marker="s", ms=5, lw=1.2, ls="--", label="noise-aware")
a1.set_xscale("log"); a1.set_xlabel(r"$\varepsilon_{2q}$"); a1.set_ylabel(r"$N^*$")
a1.set_title("Fedelt\u00e0 di Trotter"); a1.legend(loc="upper right")
v, Ni, Nn = zip(*corr_eps2q)
a2.plot(v, Ni, color=C_BLU, marker="o", ms=6, lw=1.8, label=r"$\theta^*_\mathrm{ideale}$")
a2.plot(v, Nn, color=C_ARANC, marker="s", ms=5, lw=1.2, ls="--", label="noise-aware")
a2.set_xscale("log"); a2.set_xlabel(r"$\varepsilon_{2q}$"); a2.set_ylabel(r"$N^*$")
a2.set_title("Correlatore"); a2.legend(loc="upper right")
salva(fig, "fig_passo5_griglia_completa")

n_ok = sum(1 for r in righe if r[5])
print(f"{n_ok}/{len(righe)} punti della griglia con N* invariato.")
