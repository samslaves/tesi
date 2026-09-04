"""Figure del documento 1 — il sistema, lo spettro, il ruolo del termine DM."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *
from dimer_exact import exact_sweep, dimer_hamiltonian

os.makedirs("figure", exist_ok=True)
J = 1.0
b = np.linspace(0.0, 4.0, 601)
r0 = exact_sweep(b, J=J, D=0.0)
rD = exact_sweep(b, J=J, D=0.2)

# ---------------------------------------------------------------- fig: spettro
fig, ax = plt.subplots(figsize=(7.2, 4.6))
etichette = [r"$|S{=}1,M{=}{+}1\rangle$", r"$|S{=}1,M{=}0\rangle$",
             r"$|S{=}0,M{=}0\rangle$", r"$|S{=}1,M{=}{-}1\rangle$"]
E_ana = {
    r"$|S{=}1,M{=}{+}1\rangle$": J + 2 * b,
    r"$|S{=}1,M{=}0\rangle$":    J + 0 * b,
    r"$|S{=}0,M{=}0\rangle$":   -3 * J + 0 * b,
    r"$|S{=}1,M{=}{-}1\rangle$": J - 2 * b,
}
colori = [C_AZZURRO, C_VERDE, C_BLU, C_ARANC]
for (lab, E), col in zip(E_ana.items(), colori):
    ax.plot(b / J, E, color=col, lw=2.0)
ax.plot(b / J, r0["gs_energy"], color=C_NERO, lw=3.4, alpha=0.9,
        label="stato fondamentale")
ax.axvline(2.0, color="0.55", ls=":", lw=1.4)

# etichette dei livelli poste sulle curve, in punti liberi verificati
ax.annotate(r"$|S{=}1,M{=}{+}1\rangle$", xy=(2.55, J + 2 * 2.55), xytext=(2.05, 7.4),
            color=C_AZZURRO, fontsize=12)
ax.annotate(r"$|S{=}1,M{=}0\rangle$", xy=(3.0, J), xytext=(2.95, 1.35),
            color=C_VERDE, fontsize=12)
ax.annotate(r"$|S{=}0,M{=}0\rangle$", xy=(0.6, -3), xytext=(0.35, -2.55),
            color=C_BLU, fontsize=12)
ax.annotate(r"$|S{=}1,M{=}{-}1\rangle$", xy=(3.2, J - 2 * 3.2), xytext=(2.35, -6.6),
            color=C_ARANC, fontsize=12)
ax.annotate("incrocio\n" + r"$B/J=2$", xy=(2.0, -3.0), xytext=(1.02, -6.2),
            fontsize=12, color="0.25",
            arrowprops=dict(arrowstyle="->", color="0.45", lw=1.2))

ax.set_xlabel(r"$B/J$")
ax.set_ylabel(r"$E/J$")
ax.set_xlim(0, 4)
ax.set_ylim(-8.2, 9.2)
ax.legend(loc="upper left", frameon=True)
salva(fig, "fig01_spettro")

# ------------------------------------------------- fig: gap e magnetizzazione
gap0 = r0["energies"][:, 1] - r0["energies"][:, 0]
gapD = rD["energies"][:, 1] - rD["energies"][:, 0]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.2))

a1.plot(b / J, gap0, color=C_NERO, lw=2.4, label=r"$D=0$")
a1.plot(b / J, gapD, color=C_ROSSO, lw=2.4, ls="--", label=r"$D/J=0.2$")
a1.axvline(2.0, color="0.55", ls=":", lw=1.2)
a1.set_xlabel(r"$B/J$"); a1.set_ylabel(r"$\Delta E_{01}/J$")
a1.set_title("Distanza fondamentale–primo eccitato")
a1.set_ylim(-0.15, 4.2)
a1.legend(loc="upper right")
i_min = np.argmin(gapD)
a1.annotate(f"minimo\n{gapD[i_min]:.2f}", xy=(b[i_min] / J, gapD[i_min]),
            xytext=(2.62, 1.95), fontsize=11.5, color=C_ROSSO,
            arrowprops=dict(arrowstyle="->", color=C_ROSSO, lw=1.1))
a1.annotate("si chiude\nesattamente", xy=(2.0, 0.02), xytext=(0.30, 0.75),
            fontsize=11.5, color="0.25",
            arrowprops=dict(arrowstyle="->", color="0.45", lw=1.1))

a2.plot(b / J, r0["gs_mz"], color=C_NERO, lw=2.4, label=r"$D=0$")
a2.plot(b / J, rD["gs_mz"], color=C_ROSSO, lw=2.4, ls="--", label=r"$D/J=0.2$")
a2.axvline(2.0, color="0.55", ls=":", lw=1.2)
a2.set_xlabel(r"$B/J$"); a2.set_ylabel(r"$\langle M_z\rangle$")
a2.set_title("Magnetizzazione dello stato fondamentale")
a2.set_ylim(-1.18, 0.35)
a2.legend(loc="center left", bbox_to_anchor=(0.0, 0.22))
a2.annotate("salto netto", xy=(2.0, -0.62), xytext=(2.45, -0.52), fontsize=11.5,
            color="0.25", arrowprops=dict(arrowstyle="->", color="0.45", lw=1.1))
a2.annotate("crossover\nliscio", xy=(1.72, -0.13), xytext=(0.55, -0.62),
            fontsize=11.5, color=C_ROSSO,
            arrowprops=dict(arrowstyle="->", color=C_ROSSO, lw=1.1))
salva(fig, "fig02_gap_magnetizzazione")

# stampa numeri citati nel testo
print("gap D=0.2 minimo  :", gapD.min(), " a B/J =", b[np.argmin(gapD)])
for bb in (1.9, 2.0, 2.1):
    k = np.argmin(np.abs(b - bb))
    print(f"B/J={bb}: gap(D=0)={gap0[k]:.3f}  gap(D=0.2)={gapD[k]:.3f}")

# commutatori (numeri citati nel testo)
from qiskit.quantum_info import SparsePauliOp
HD = SparsePauliOp(["XZ", "ZX"], [0.2, -0.2]).to_matrix()
Sz = SparsePauliOp(["ZI", "IZ"], [0.5, 0.5]).to_matrix()
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]])
Z = np.diag([1, -1]).astype(complex)
I = np.eye(2)
S2 = sum(np.kron(A, A) for A in (X, Y, Z)) / 2 + 1.5 * np.eye(4)
print("||[H_D,Sz]||_F =", np.linalg.norm(HD @ Sz - Sz @ HD))
print("||[H_D,S^2]||_F =", np.linalg.norm(HD @ S2 - S2 @ HD))
