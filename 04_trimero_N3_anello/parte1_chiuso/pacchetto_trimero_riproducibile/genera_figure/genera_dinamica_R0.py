import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codice"))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""
Genera le figure del Documento 3 al punto di lavoro R0 (b/J=0.05,
D/J=1.93, dichiarato provvisorio in Parte 1) -- assenti dalla prima
versione di questo pacchetto, che valida trotter_trimero_anello.py solo
con parametri casuali (self-test generico, non al punto di lavoro
specifico usato nei documenti).

  fig_trotter_sz_anello.pdf/.png: <Sz_tot>(t), stato iniziale |000>,
      esatto contro Trotter a N=50,150,500.
  fig_trotter_errore_anello.pdf/.png: errore a t=6 in scala log-log,
      Trotter contro N, con retta di riferimento ~1/N^2 (fidelity).
  circ_trotter_anello.pdf/.png: diagramma del singolo passo esterno di
      Trotter (scambio, campo, DM).
"""
import numpy as np
from qiskit.quantum_info import Statevector
from stile import plt, C_NERO, C_ARANC, C_VERDE, C_ROSSO, C_GRIGIO

from trotter_trimero_anello import trotter_circuit, U_exact, PSI0, sz_tot

J, Jp, b, D = 1.0, 0.4, 0.05, 1.93  # punto R0

# ---------------------------------------------------------------------
# Figura: <Sz_tot>(t), esatto vs Trotter a N=50,150,500
# ---------------------------------------------------------------------
ts = np.linspace(0.0, 12.0, 121)
sz_esatto = []
for t in ts:
    psi_t = U_exact(J, Jp, b, D, t) @ PSI0.data
    sz_esatto.append(sz_tot(psi_t))
sz_esatto = np.array(sz_esatto)

fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.plot(ts, sz_esatto, color=C_NERO, lw=2.4, label="esatta", zorder=5)

colori_N = {50: C_ARANC, 150: "#c9a000", 500: C_VERDE}
stili_N = {50: "--", 150: "-.", 500: ":"}
for N in (50, 150, 500):
    sz_N = []
    for t in ts:
        qc = trotter_circuit(J, Jp, b, D, t, N)
        psi = Statevector(qc).data
        sz_N.append(sz_tot(psi))
    ax.plot(ts, sz_N, color=colori_N[N], lw=1.6, ls=stili_N[N], label=f"Trotter, $N={N}$")

ax.set_xlabel("$t$ (unità di $1/J$)")
ax.set_ylabel(r"$\langle S_z^{\rm tot}\rangle(t)$")
ax.set_title(r"Magnetizzazione nel tempo, stato iniziale $|000\rangle$ (punto $R_0$)")
ax.legend(loc="best", fontsize=9)
fig.savefig("figure/fig_trotter_sz_anello.pdf", bbox_inches="tight")
fig.savefig("figure/fig_trotter_sz_anello.png", bbox_inches="tight", dpi=200)
plt.close(fig)
print("[ok] figure/fig_trotter_sz_anello.pdf")

# ---------------------------------------------------------------------
# Figura: errore a t=6, scala log-log, con retta di riferimento
# ---------------------------------------------------------------------
t_fix = 6.0
psi_ref = U_exact(J, Jp, b, D, t_fix) @ PSI0.data
Ns = [5, 10, 20, 40, 80, 160, 320]
errs = []
for N in Ns:
    qc = trotter_circuit(J, Jp, b, D, t_fix, N)
    psi = Statevector(qc).data
    infid = 1 - abs(np.vdot(psi_ref, psi)) ** 2
    errs.append(infid)
errs = np.array(errs)

fig, ax = plt.subplots(figsize=(6.0, 4.4))
ax.loglog(Ns, errs, "o-", color=C_ROSSO, label="infedeltà (circuito)")
ref = errs[0] * (Ns[0] / np.array(Ns)) ** 2
ax.loglog(Ns, ref, "--", color=C_GRIGIO, label=r"$\propto 1/N^2$")
ax.set_xlabel("$N$ (passi di Trotter)")
ax.set_ylabel(r"$1-|\langle\psi_{\rm esatto}|\psi_{\rm Trotter}\rangle|^2$")
ax.set_title(f"Errore a $t={t_fix:.0f}$ (punto $R_0$), scala doppio-logaritmica")
ax.legend()
fig.savefig("figure/fig_trotter_errore_anello.pdf", bbox_inches="tight")
fig.savefig("figure/fig_trotter_errore_anello.png", bbox_inches="tight", dpi=200)
plt.close(fig)
print("[ok] figure/fig_trotter_errore_anello.pdf")

pendenza_coda = np.polyfit(np.log(Ns[-3:]), np.log(errs[-3:]), 1)[0]
pendenza_testa = np.polyfit(np.log(Ns[:3]), np.log(errs[:3]), 1)[0]
print(f"Pendenza nella coda asintotica (N=80,160,320): {pendenza_coda:.2f}  (atteso ~-2)")
print(f"Pendenza a N piccolo (N=5,10,20): {pendenza_testa:.2f}  "
      f"(lontano da -2: regime non ancora asintotico, coerente con la "
      f"convergenza molto piu' lenta del dimero gia' documentata)")

# ---------------------------------------------------------------------
# Figura: diagramma del circuito, un singolo passo esterno
# ---------------------------------------------------------------------
qc_step = trotter_circuit(J, Jp, b, D, t=1.0, N=1)
fig_c = qc_step.draw("mpl", style="iqp", fold=-1, scale=0.9)
fig_c.savefig("figure/circ_trotter_anello.pdf", bbox_inches="tight")
fig_c.savefig("figure/circ_trotter_anello.png", bbox_inches="tight", dpi=200)
plt.close(fig_c)
print("[ok] figure/circ_trotter_anello.pdf")
