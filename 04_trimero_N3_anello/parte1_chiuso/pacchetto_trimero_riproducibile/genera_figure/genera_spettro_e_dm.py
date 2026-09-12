import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codice"))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""
Genera le due figure del Documento 1 nella forma effettivamente usata
nella documentazione dei risultati -- diverse da dati/trimer_ring_exact.png
(quella, generata dal self-test di trimer_ring_exact.py, colora SOLO la
curva del fondamentale per blocco; qui si colora l'INTERO spettro a otto
livelli per blocco di Kambe, e si aggiunge il confronto con le due
opzioni DM, assente dal self-test).

  fig_spettro_anello.pdf/.png: tutti e otto i livelli, colorati per
      blocco (A, B, C secondo la decomposizione di Kambe), D=0.
  fig_gap_magnetizzazione_anello.pdf/.png: distanza fondamentale-primo
      eccitato e magnetizzazione, D=0 contro le due opzioni DM
      (D/J=0.15), zoomati attorno all'incrocio -- il confronto centrale
      del Documento 1, mai generato nella prima versione di questo
      pacchetto.
"""
import numpy as np
from stile import plt, C_NERO, C_ARANC, C_VERDE, C_ROSSO, C_GRIGIO

from trimer_ring_exact import kambe_energy, critical_field, trimer_hamiltonian_dm, dm_min_gap

J, Jp, D = 1.0, 0.4, 0.15
bc = critical_field(J, Jp)
b_grid = np.linspace(0.0, 4.0, 400)

# ---------------------------------------------------------------------
# Figura 1: spettro completo a 8 livelli, colorato per blocco di Kambe
# ---------------------------------------------------------------------
livelli = []  # (blocco, M, colore)
for M in (1.5, 0.5, -0.5, -1.5):
    livelli.append(("A", M, C_ARANC))
for M in (0.5, -0.5):
    livelli.append(("B", M, C_VERDE))
for M in (0.5, -0.5):
    livelli.append(("C", M, C_GRIGIO))

fig, ax = plt.subplots(figsize=(7.0, 4.8))
etichette_fatte = set()
for blocco, M, colore in livelli:
    E = kambe_energy(J, Jp, b_grid, blocco, M)
    lab = f"blocco {blocco}" if blocco not in etichette_fatte else None
    etichette_fatte.add(blocco)
    ax.plot(b_grid / J, E, color=colore, lw=1.6, label=lab)

# stato fondamentale in nero, spesso, sopra tutto
E_C = kambe_energy(J, Jp, b_grid, "C", -0.5)
E_A = kambe_energy(J, Jp, b_grid, "A", -1.5)
gs = np.minimum(E_C, E_A)
ax.plot(b_grid / J, gs, color=C_NERO, lw=2.6, label="stato fondamentale", zorder=5)
ax.axvline(bc / J, color="0.4", ls=":", lw=1)
ax.annotate(f"incrocio\n$b_c/J={bc/J:.2g}$", xy=(bc / J, gs[np.searchsorted(b_grid, bc)]),
            xytext=(bc / J - 1.1, gs.min() * 0.55), fontsize=9, color="0.3",
            arrowprops=dict(arrowstyle="->", color="0.5"))
ax.set_xlabel("$b/J$"); ax.set_ylabel("$E/J$")
ax.set_title("Spettro del trimero isoscele ($J'/J=0.4$), $D=0$")
ax.legend(loc="upper left", fontsize=9)
fig.savefig("figure/fig_spettro_anello.pdf", bbox_inches="tight")
fig.savefig("figure/fig_spettro_anello.png", bbox_inches="tight", dpi=200)
plt.close(fig)
print("[ok] figure/fig_spettro_anello.pdf")

# ---------------------------------------------------------------------
# Figura 2: gap e magnetizzazione, D=0 vs Opzione A vs Opzione B
# ---------------------------------------------------------------------
b_zoom = np.linspace(bc - 1.2, bc + 1.2, 300)


def gap_curve(mode, D_val):
    gaps = []
    for b in b_zoom:
        H = trimer_hamiltonian_dm(J, Jp, b, mode, D_val).to_matrix()
        w = np.sort(np.linalg.eigvalsh(H))
        gaps.append(w[1] - w[0])
    return np.array(gaps)


g0 = gap_curve(None, 0.0)
gA = gap_curve("A", D)
gB = gap_curve("B", D)

gap_A_min, b_A_min = dm_min_gap(J, Jp, "A", D)
gap_B_min, b_B_min = dm_min_gap(J, Jp, "B", D)
print(f"Opzione A: gap minimo vero = {gap_A_min:.3e}  a b/J={b_A_min:.4f}")
print(f"Opzione B: gap minimo vero = {gap_B_min:.4f}  a b/J={b_B_min:.4f}")

fig, ax = plt.subplots(figsize=(6.6, 4.6))
ax.plot(b_zoom / J, g0, color=C_NERO, lw=2.0, label="$D=0$")
ax.plot(b_zoom / J, gA, color=C_VERDE, lw=2.0, ls="-.", label="Opzione A")
ax.plot(b_zoom / J, gB, color=C_ROSSO, lw=2.0, ls="--", label="Opzione B")
ax.axvline(bc / J, color="0.6", ls=":", lw=1)
ax.annotate("Opzione A:\nresta chiuso", xy=(b_A_min, gap_A_min),
            xytext=(b_A_min - 1.0, 0.55), fontsize=9, color=C_VERDE,
            arrowprops=dict(arrowstyle="->", color=C_VERDE))
ax.annotate(f"minimo vero\n{gap_B_min:.3f}", xy=(b_B_min, gap_B_min),
            xytext=(b_B_min + 0.15, gap_B_min + 0.5), fontsize=9, color=C_ROSSO,
            arrowprops=dict(arrowstyle="->", color=C_ROSSO))
ax.set_xlabel("$b/J$"); ax.set_ylabel(r"$\Delta E_{01}/J$")
ax.set_title(f"Distanza fondamentale-primo eccitato, $D/J={D}$")
ax.legend(loc="upper center")
fig.savefig("figure/fig_gap_magnetizzazione_anello.pdf", bbox_inches="tight")
fig.savefig("figure/fig_gap_magnetizzazione_anello.png", bbox_inches="tight", dpi=200)
plt.close(fig)
print("[ok] figure/fig_gap_magnetizzazione_anello.pdf")
