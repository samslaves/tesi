"""
Genera fig_scan_eps2q_trimero_anello.pdf: energia e fedelta' rumorose in
funzione di eps_2q (Stadio 2). Mirror concettuale della figura analoga sul
dimero (fig_passo2_scan_eps2q.pdf), dati propri del trimero ad anello.
"""
import numpy as np
from stile import plt, C_BLU, C_ARANC

EPS_2Q_REF = 3.8e-3

data = np.load("scan_eps2q_vqe_dm_trimero_anello.npz")
eps2q, E, F = data["eps2q"], data["E"], data["F"]

fig, ax1 = plt.subplots(figsize=(7.0, 4.4))
ax2 = ax1.twinx()

ax1.plot(eps2q * 100, E, "o-", color=C_BLU, label="$E$")
ax2.plot(eps2q * 100, F, "s--", color=C_ARANC, label="$F$")

ax1.axvline(EPS_2Q_REF * 100, color="0.5", ls=":", lw=1.3)

ax1.set_xlabel(r"$\varepsilon_{2q}$ $\times10^{-2}$")
ax1.set_ylabel("$E$ (energia rumorosa)", color=C_BLU)
ax2.set_ylabel("$F$ (fedeltà rumorosa)", color=C_ARANC)
ax1.tick_params(axis="y", labelcolor=C_BLU)
ax2.tick_params(axis="y", labelcolor=C_ARANC)
ax1.set_title("VQE+DM sotto rumore (anello): scan su " r"$\varepsilon_{2q}$")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower left")

fig.savefig("figure/fig_scan_eps2q_trimero_anello.pdf", bbox_inches="tight")
fig.savefig("figure/fig_scan_eps2q_trimero_anello.png", bbox_inches="tight", dpi=200)
plt.close(fig)
print("[ok] figure/fig_scan_eps2q_trimero_anello.pdf")
