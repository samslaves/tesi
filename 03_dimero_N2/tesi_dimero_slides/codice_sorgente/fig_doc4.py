"""Figure del documento 4 — correlatori dinamici misurati con l'ancilla."""
import os
import itertools
import numpy as np
import scipy.linalg as sla
import matplotlib.pyplot as plt
from qiskit.quantum_info import SparsePauliOp
from stile import *
from dimer_exact import dimer_hamiltonian
from circuito_correlazioni_dimero import ground_state, correlator_from_circuit

os.makedirs("figure", exist_ok=True)

J, b, D = 1.0, 0.35, 0.80          # punto di lavoro "test 2"
H = dimer_hamiltonian(b=b, J=J, D=D).to_matrix()
E, V = np.linalg.eigh(H)
psi0, _ = ground_state(b, J, D)

PAULI = {"x": "X", "y": "Y", "z": "Z"}

def op_sito(sito, alpha):
    """sigma_alpha sul sito indicato, convenzione di dimer_exact.py
    (sito 1 -> qubit 1, sito 2 -> qubit 0 in notazione little-endian)."""
    lab = ["I", "I"]
    lab[0 if sito == 1 else 1] = PAULI[alpha]   # stringa scritta q1 q0
    return SparsePauliOp("".join(lab)).to_matrix()

def C_esatto(i, alpha, j, beta, ts):
    """Riferimento classico via esponenziale di matrice (metodo indipendente
    dalla formula spettrale)."""
    Vop, Wop = op_sito(i, alpha), op_sito(j, beta)
    out = []
    for t in ts:
        U = sla.expm(-1j * H * t)
        out.append(psi0.conj() @ U.conj().T @ Vop @ U @ Wop @ psi0)
    return np.array(out)

# ------------------------------------------- validazione circuito vs esatto
ts_fine = np.linspace(0, 6, 241)
ts_circ = np.linspace(0, 6, 13)
i, al, j, be = 2, "x", 1, "x"
C_ref = C_esatto(i, al, j, be, ts_fine)
C_cir = np.array([correlator_from_circuit(i, al, j, be, t, 200, J, b, D, psi0=psi0)
                  for t in ts_circ])
C_ref_at = C_esatto(i, al, j, be, ts_circ)
res = np.abs(C_cir - C_ref_at)
print(f"[validazione] C_{i}{j}^{al}{be}: residuo medio {res.mean():.2e}, "
      f"massimo {res.max():.2e}  (N=200 passi)")

fig, ax = plt.subplots(figsize=(8.0, 4.6))
ax.plot(ts_fine, C_ref.real, color=C_NERO, lw=2.4, label="Re, riferimento esatto")
ax.plot(ts_fine, C_ref.imag, color=C_GRIGIO, lw=2.4, ls="-", label="Im, riferimento esatto")
ax.plot(ts_circ, C_cir.real, "o", ms=8, mfc="none", mew=2, color=C_BLU,
        label="Re, misura via circuito")
ax.plot(ts_circ, C_cir.imag, "s", ms=8, mfc="none", mew=2, color=C_ROSSO,
        label="Im, misura via circuito")
ax.set_xlabel(r"$t$  (unità di $1/J$)")
ax.set_ylabel(rf"$C_{{{i}{j}}}^{{{al}{be}}}(t)$")
ax.set_title("Il circuito con l'ancilla riproduce il calcolo classico")
ax.set_xlim(-0.15, 6.15)
ax.set_ylim(-1.18, 1.72)
ax.legend(loc="upper center", ncol=2)
salva(fig, "fig07_correlatore_validazione")

# --------------------------------------------- scan delle 36 combinazioni
siti = [1, 2]
comp = ["x", "y", "z"]
ts_scan = np.linspace(0, 8, 161)
ampiezza = np.zeros((6, 6))
istante0 = np.zeros((6, 6))
righe, colonne = [], []
dati = {}
for a_idx, (i_, al_) in enumerate(itertools.product(siti, comp)):
    righe.append(rf"$\sigma_{{{i_}}}^{{{al_}}}(t)$")
    for b_idx, (j_, be_) in enumerate(itertools.product(siti, comp)):
        if a_idx == 0:
            colonne.append(rf"$\sigma_{{{j_}}}^{{{be_}}}(0)$")
        c = C_esatto(i_, al_, j_, be_, ts_scan)
        dati[(i_, al_, j_, be_)] = c
        ampiezza[a_idx, b_idx] = np.abs(c).max()
        istante0[a_idx, b_idx] = abs(c[0])

fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(13.6, 6.0))
for ax, M, titolo in ((ax0, istante0, r"$|C_{ij}^{\alpha\beta}(0)|$   (istante iniziale)"),
                      (ax1, ampiezza, r"$\max_t\,|C_{ij}^{\alpha\beta}(t)|$   su $t\in[0,8]$")):
    im = ax.imshow(M, cmap="viridis", vmin=0, vmax=1.0)
    ax.set_xticks(range(6), colonne, fontsize=11)
    ax.set_yticks(range(6), righe, fontsize=11)
    for r in range(6):
        for c in range(6):
            val = M[r, c]
            ax.text(c, r, "0" if val < 1e-12 else f"{val:.2f}",
                    ha="center", va="center", fontsize=11,
                    color="white" if val < 0.6 else "black")
    ax.set_title(titolo, fontsize=13.5)
    ax.grid(False)
cb = fig.colorbar(im, ax=(ax0, ax1), shrink=0.8)
cb.set_label(r"modulo del correlatore")
salva(fig, "fig08_scan36")

# ---------------------------------------------- esempio ricco / esempio piatto
chiavi = list(dati.keys())
varianza = {k: np.std(np.real(dati[k])) + np.std(np.imag(dati[k])) for k in chiavi}
ricco = max(varianza, key=varianza.get)
piatto = min(varianza, key=varianza.get)
print(f"[scan] combinazione piu' strutturata: {ricco}   (std={varianza[ricco]:.3f})")
print(f"[scan] combinazione piu' piatta:      {piatto}  (std={varianza[piatto]:.3f})")
print(f"[scan] ampiezza minima e massima nella griglia: "
      f"{ampiezza.min():.3f} / {ampiezza.max():.3f}")
print("[scan] combinazioni nulle a t=0:",
      [k for k in chiavi if abs(dati[k][0]) < 1e-12])

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.4, 4.3), sharey=True)
for ax, k, titolo in ((a1, ricco, "segnale ricco"), (a2, piatto, "segnale povero")):
    i_, al_, j_, be_ = k
    ax.plot(ts_scan, np.real(dati[k]), color=C_BLU, lw=2.2, label="parte reale")
    ax.plot(ts_scan, np.imag(dati[k]), color=C_ARANC, lw=2.2, ls="--",
            label="parte immaginaria")
    ax.set_xlabel(r"$t$  (unità di $1/J$)")
    ax.set_title(rf"{titolo}:  $C_{{{i_}{j_}}}^{{{al_}{be_}}}(t)$")
    ax.set_xlim(0, 8)
a1.set_ylabel("correlatore")
a1.set_ylim(-1.25, 1.55)
a1.legend(loc="upper center", ncol=2)
salva(fig, "fig09_ricco_piatto")

# ---------------------------------------------- contenuto spettrale
def righe_spettrali(k):
    i_, al_, j_, be_ = k
    Vop, Wop = op_sito(i_, al_), op_sito(j_, be_)
    g = V[:, 0]
    pesi, freq = [], []
    for n in range(4):
        a_n = V[:, n].conj() @ Vop @ g
        b_n = V[:, n].conj() @ Wop @ g
        pesi.append(abs(np.conj(a_n) * b_n))
        freq.append(E[n] - E[0])
    return np.array(freq), np.array(pesi)

fig, ax = plt.subplots(figsize=(7.8, 4.4))
larg = 0.045
for off, (k, col, lab) in enumerate((
        (ricco,  C_BLU,   "ricco"),
        (piatto, C_ARANC, "povero"))):
    f_, p_ = righe_spettrali(k)
    i_, al_, j_, be_ = k
    ax.bar(f_[1:] + (off - 0.5) * 2 * larg, p_[1:], width=2 * larg, color=col,
           label=rf"$C_{{{i_}{j_}}}^{{{al_}{be_}}}$  ({lab})")
f_all, _ = righe_spettrali(ricco)
ax.set_xticks(f_all[1:], [f"{x:.2f}" for x in f_all[1:]])
ax.set_xlim(3.9, 5.85)
ax.set_xlabel(r"frequenza  $E_k-E_0$   (unità di $J$)")
ax.set_ylabel("peso della riga")
ax.set_title("Quali transizioni contribuiscono al segnale")
ax.legend(loc="upper right")
salva(fig, "fig10_spettro_righe")

for k in (ricco, piatto):
    f_, p_ = righe_spettrali(k)
    print(f"[righe] {k}: frequenze {np.round(f_,4)}  pesi {np.round(p_,4)}")
