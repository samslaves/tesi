"""Documento 4 (anello) — ricco/piatto e contenuto spettrale."""
import os
import numpy as np
import scipy.linalg as sla
import matplotlib.pyplot as plt
from stile import *
from qiskit.quantum_info import SparsePauliOp
from trimer_ring_exact import trimer_hamiltonian_dm
from trotter_trimero_anello import Q

os.makedirs("figure", exist_ok=True)
J, Jp, b, D = 1.0, 0.4, 2.4, 0.15
H = trimer_hamiltonian_dm(J, Jp, b, "B", D).to_matrix()
E, V = np.linalg.eigh(H)
psi0 = V[:,0]

PAULI = {"x":"X","y":"Y","z":"Z"}
def op_sito(sito, alpha):
    lab = ["I","I","I"]; lab[2-Q[sito]] = PAULI[alpha]
    return SparsePauliOp("".join(lab)).to_matrix()

def C_esatto(i,al,j,be,ts):
    Vop, Wop = op_sito(i,al), op_sito(j,be)
    out=[]
    for t in ts:
        U = sla.expm(-1j*H*t)
        out.append(psi0.conj() @ U.conj().T @ Vop @ U @ Wop @ psi0)
    return np.array(out)

ts = np.linspace(0,8,321)
piatto = (3,"y",3,"y")
ricco  = (1,"z",1,"z")
C_piatto = C_esatto(*piatto, ts)
C_ricco  = C_esatto(*ricco, ts)

fig,(a1,a2) = plt.subplots(1,2,figsize=(11.4,4.3), sharey=True)
for ax,c,k,titolo in ((a1,C_ricco,ricco,"segnale ricco"), (a2,C_piatto,piatto,"segnale monocromatico")):
    i_,al_,j_,be_ = k
    ax.plot(ts, np.real(c), color=C_BLU, lw=2.0, label="parte reale")
    ax.plot(ts, np.imag(c), color=C_ARANC, lw=2.0, ls="--", label="parte immaginaria")
    ax.set_xlabel(r"$t$ (unità di $1/J$)")
    ax.set_title(rf"{titolo}: $C_{{{i_}{j_}}}^{{{al_}{be_}}}(t)$")
    ax.set_xlim(0,8)
a1.set_ylabel("correlatore")
a1.legend(loc="upper right", ncol=1, fontsize=9.5)
salva(fig, "fig09_ricco_piatto_anello")

def righe_spettrali(i_,al_,j_,be_,nmax=6):
    Vop, Wop = op_sito(i_,al_), op_sito(j_,be_)
    g = V[:,0]
    pesi, freq = [], []
    for n in range(1, nmax+1):
        a_n = V[:,n].conj() @ Vop @ g
        b_n = V[:,n].conj() @ Wop @ g
        pesi.append(abs(np.conj(a_n)*b_n))
        freq.append(E[n]-E[0])
    return np.array(freq), np.array(pesi)

fig, ax = plt.subplots(figsize=(8.5,4.5))
larg=0.055
for off,(k,col,lab) in enumerate(((ricco,C_BLU,"ricco"),(piatto,C_ARANC,"monocromatico"))):
    f_,p_ = righe_spettrali(*k)
    i_,al_,j_,be_ = k
    ax.bar(f_+(off-0.5)*2*larg, p_, width=2*larg, color=col,
           label=rf"$C_{{{i_}{j_}}}^{{{al_}{be_}}}$ ({lab})")
ax.set_xlabel(r"frequenza $E_n-E_0$ (unità di $J$)")
ax.set_ylabel("peso della riga")
ax.set_title("Quali transizioni contribuiscono al segnale")
ax.legend(loc="upper right")
salva(fig, "fig10_spettro_righe_anello")

f_r,p_r = righe_spettrali(*ricco)
f_p,p_p = righe_spettrali(*piatto)
print(f"ricco {ricco}: freq={np.round(f_r,3)} pesi={np.round(p_r,4)}")
print(f"piatto {piatto}: freq={np.round(f_p,3)} pesi={np.round(p_p,4)}")
