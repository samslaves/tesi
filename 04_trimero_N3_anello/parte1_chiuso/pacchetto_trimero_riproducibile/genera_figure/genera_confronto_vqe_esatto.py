import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codice"))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""Genera fig_vqe_vs_esatto_correlatore.pdf: C_21^xx(t), preparazione
esatta contro VQE, e lo scostamento in scala logaritmica."""
import numpy as np
from stile import plt, C_NERO, C_GRIGIO, C_BLU, C_ROSSO, C_VERDE

data = np.load("dati/confronto_vqe_esatto.npz")
ts, C_esatto, C_vqe = data["ts"], data["C_esatto"], data["C_vqe"]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.2))
a1.plot(ts, C_esatto.real, color=C_NERO, lw=2.2, label="Re, preparazione esatta")
a1.plot(ts, C_esatto.imag, color=C_GRIGIO, lw=2.2, label="Im, preparazione esatta")
a1.plot(ts, C_vqe.real, "o", ms=6, mfc="none", mew=1.6, color=C_BLU, label="Re, VQE (W-2q.6)")
a1.plot(ts, C_vqe.imag, "s", ms=6, mfc="none", mew=1.6, color=C_ROSSO, label="Im, VQE (W-2q.6)")
a1.set_xlabel("$t$ (unità di $1/J$)")
a1.set_ylabel(r"$C_{21}^{xx}(t)$")
a1.set_title("Preparazione esatta contro VQE")
a1.legend(loc="upper center", ncol=2, fontsize=8.5)

scarto = np.abs(C_vqe - C_esatto)
a2.semilogy(ts, scarto, "o-", color=C_VERDE, ms=6, lw=1.8)
a2.set_xlabel("$t$ (unità di $1/J$)")
a2.set_ylabel(r"$|C_{\rm VQE}-C_{\rm esatto}|$")
a2.set_title("Scostamento (scala log)")

fig.savefig("figure/fig_vqe_vs_esatto_correlatore.pdf", bbox_inches="tight")
fig.savefig("figure/fig_vqe_vs_esatto_correlatore.png", bbox_inches="tight", dpi=200)
plt.close(fig)
print("[ok] figure/fig_vqe_vs_esatto_correlatore.pdf")
