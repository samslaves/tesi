"""Figure del documento 1 (trimero ad anello) — il sistema, lo spettro, il ruolo del DM."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *
from trimer_ring_exact import (trimer_hamiltonian, exact_sweep, critical_field,
                                exact_sweep_dm, dm_min_gap)

os.makedirs("figure", exist_ok=True)
J, Jp = 1.0, 0.4
bc = critical_field(J, Jp)
print(f"b_c = {bc}")

b = np.linspace(0.0, 4.0, 601)
r0 = exact_sweep(b, J=J, Jp=Jp)

# ---------------------------------------------------------------- fig: spettro
fig, ax = plt.subplots(figsize=(7.4, 4.8))
E_A = J + 2*Jp + 2*b*np.array([1.5, 0.5, -0.5, -1.5])[:, None]
E_B = J - 4*Jp + 2*b*np.array([0.5, -0.5])[:, None]
E_C = -3*J + 2*b*np.array([0.5, -0.5])[:, None]

for k, EE in enumerate(E_A):
    ax.plot(b/J, EE, color=C_ARANC, lw=1.6, alpha=0.85,
             label=("blocco A ($S{=}3/2$)" if k == 0 else None))
for k, EE in enumerate(E_B):
    ax.plot(b/J, EE, color=C_VERDE, lw=1.6, alpha=0.85,
             label=("blocco B ($S{=}1/2$)" if k == 0 else None))
for k, EE in enumerate(E_C):
    ax.plot(b/J, EE, color=C_BLU, lw=1.6, alpha=0.85,
             label=("blocco C ($S{=}1/2$)" if k == 0 else None))
ax.plot(b/J, r0["gs_energy"], color=C_NERO, lw=3.2, alpha=0.9,
        label="stato fondamentale")
ax.axvline(bc, color="0.55", ls=":", lw=1.4)
ax.annotate(f"incrocio\n$b_c/J={bc:.1f}$", xy=(bc, -3.0), xytext=(1.0, -6.3),
            fontsize=11.5, color="0.25",
            arrowprops=dict(arrowstyle="->", color="0.45", lw=1.1))
ax.set_xlabel(r"$b/J$"); ax.set_ylabel(r"$E/J$")
ax.set_xlim(0, 4); ax.set_ylim(-8.2, 9.2)
ax.set_title("Spettro del trimero isoscele ($J'/J=0.4$), $D=0$")
ax.legend(loc="upper left", fontsize=10.5)
salva(fig, "fig01_spettro_anello")

# ------------------------------------------------- fig: gap, entrambe le opzioni DM
D_test = 0.15
b_fine = np.linspace(bc - 1.0, bc + 1.0, 401)
gap0 = []
gapA = []
gapB = []
from trimer_ring_exact import trimer_hamiltonian_dm
for bb in b_fine:
    H0 = trimer_hamiltonian(J, Jp, bb).to_matrix()
    E0 = np.sort(np.linalg.eigvalsh(H0))
    gap0.append(E0[1]-E0[0])
    HA = trimer_hamiltonian_dm(J, Jp, bb, "A", D_test).to_matrix()
    EA = np.sort(np.linalg.eigvalsh(HA))
    gapA.append(EA[1]-EA[0])
    HB = trimer_hamiltonian_dm(J, Jp, bb, "B", D_test).to_matrix()
    EB = np.sort(np.linalg.eigvalsh(HB))
    gapB.append(EB[1]-EB[0])
gap0, gapA, gapB = map(np.array, (gap0, gapA, gapB))

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.4, 4.3))
a1.plot(b_fine/J, gap0, color=C_NERO, lw=2.2, label=r"$D=0$")
a1.plot(b_fine/J, gapA, color=C_VERDE, lw=2.2, ls="-.", label=r"Opzione A, $D/J=0.15$")
a1.plot(b_fine/J, gapB, color=C_ROSSO, lw=2.2, ls="--", label=r"Opzione B, $D/J=0.15$")
a1.axvline(bc, color="0.55", ls=":", lw=1.2)
a1.set_xlabel(r"$b/J$"); a1.set_ylabel(r"$\Delta E_{01}/J$")
a1.set_title("Distanza fondamentale-primo eccitato")
a1.legend(loc="upper right", fontsize=9.5)
gapB_min, bB_min = dm_min_gap(J, Jp, "B", D_test)
a1.annotate(f"minimo vero\n{gapB_min:.3f}", xy=(bB_min, gapB_min), xytext=(2.75, 0.62),
            fontsize=10.5, color=C_ROSSO,
            arrowprops=dict(arrowstyle="->", color=C_ROSSO, lw=1.1))
a1.annotate("Opzione A:\nresta chiuso", xy=(bc, 0.02), xytext=(1.15, 0.75),
            fontsize=10.5, color=C_VERDE,
            arrowprops=dict(arrowstyle="->", color=C_VERDE, lw=1.1))

a2.plot(b/J, r0["gs_mz"], color=C_NERO, lw=2.4, label=r"$D=0$")
rB = exact_sweep_dm(b, J, Jp, "B", D_test)
a2.plot(b/J, rB["gs_mz"], color=C_ROSSO, lw=2.2, ls="--", label=r"Opzione B, $D/J=0.15$")
a2.axvline(bc, color="0.55", ls=":", lw=1.2)
a2.set_xlabel(r"$b/J$"); a2.set_ylabel(r"$\langle M_z\rangle$")
a2.set_title("Magnetizzazione dello stato fondamentale")
a2.legend(loc="center right", fontsize=9.5)
salva(fig, "fig02_gap_magnetizzazione_anello")

print(f"gap a b_c: D=0 -> {gap0[np.argmin(np.abs(b_fine-bc))]:.6f}")
print(f"gap minimo vero: Opzione A -> {dm_min_gap(J,Jp,'A',D_test)[0]:.3e}, "
      f"Opzione B -> {gapB_min:.4f} a b={bB_min:.4f}")

# commutatori (numeri citati nel testo)
from qiskit.quantum_info import SparsePauliOp
S12sq = SparsePauliOp(["III","XXI","YYI","ZZI"], [1.5,0.5,0.5,0.5]).to_matrix()
HA_op = trimer_hamiltonian_dm(J, Jp, bc, "A", D_test).to_matrix()
HB_op = trimer_hamiltonian_dm(J, Jp, bc, "B", D_test).to_matrix()
H0_op = trimer_hamiltonian(J, Jp, bc).to_matrix()
commA = np.linalg.norm((HA_op-H0_op) @ S12sq - S12sq @ (HA_op-H0_op))
commB = np.linalg.norm((HB_op-H0_op) @ S12sq - S12sq @ (HB_op-H0_op))
print(f"||[H_DM_A, S12^2]|| = {commA:.3e}")
print(f"||[H_DM_B, S12^2]|| = {commB:.3f}")
