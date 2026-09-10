import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codice"))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""
Genera fig_Nstar_vs_eps_trimero_anello.pdf: N* in funzione di eps_2q
(sinistra) ed eps_1q (destra), per entrambi gli scenari A e B.
"""
import numpy as np
from stile import plt, C_BLU, C_ARANC

data = np.load("dati/scan_parametri_rumore_trimero_anello.npz")

EPS_2Q_REF = 3.8e-3
EPS_1Q_REF = 2.9e-4

fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))

ax = axes[0]
ax.plot(data["A_eps2q"] * 1e3, data["A_Nstar2q"], "o-", color=C_BLU, label="Scenario A (VQE)")
ax.plot(data["B_eps2q"] * 1e3, data["B_Nstar2q"], "s--", color=C_ARANC, label="Scenario B ($R_0$)")
ax.axvline(EPS_2Q_REF * 1e3, color="0.5", ls=":", lw=1.3)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel(r"$\varepsilon_{2q}$ $\times10^{-3}$")
ax.set_ylabel("$N^*$")
ax.set_title(r"$N^*$ vs $\varepsilon_{2q}$ ($\varepsilon_{1q}$ di riferimento)")
ax.legend()

ax = axes[1]
ax.plot(data["A_eps1q"] * 1e4, data["A_Nstar1q"], "o-", color=C_BLU, label="Scenario A (VQE)")
ax.plot(data["B_eps1q"] * 1e4, data["B_Nstar1q"], "s--", color=C_ARANC, label="Scenario B ($R_0$)")
ax.axvline(EPS_1Q_REF * 1e4, color="0.5", ls=":", lw=1.3)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel(r"$\varepsilon_{1q}$ $\times10^{-4}$")
ax.set_ylabel("$N^*$")
ax.set_title(r"$N^*$ vs $\varepsilon_{1q}$ ($\varepsilon_{2q}$ di riferimento)")
ax.legend()

fig.suptitle("Scan sui parametri di rumore: come si sposta $N^*$", fontsize=13.5)
fig.tight_layout()

fig.savefig("figure/fig_Nstar_vs_eps_trimero_anello.pdf", bbox_inches="tight")
fig.savefig("figure/fig_Nstar_vs_eps_trimero_anello.png", bbox_inches="tight", dpi=200)
plt.close(fig)
print("[ok] figure/fig_Nstar_vs_eps_trimero_anello.pdf")
