"""
Genera fig_correlatore_rumoroso_trimero_anello.pdf: |C_21^xx(N)| a rumore
nullo e di riferimento, con N* evidenziato.
"""
import numpy as np
from stile import plt, C_BLU, C_ARANC, C_VERDE

data = np.load("scan_N_correlatore_trimero_anello.npz")
Ns, absC0, absCn = data["Ns"], data["absC0"], data["absCn"]

fig, ax = plt.subplots(figsize=(7.2, 4.6))
ax.plot(Ns, absC0, "o-", color=C_BLU, label="rumore nullo")
ax.plot(Ns, absCn, "s--", color=C_ARANC, label="rumore (ibm-torino)")

imax = int(np.argmax(absCn))
ax.axvline(Ns[imax], color=C_VERDE, ls=":", lw=1.5)
ax.text(0.97, 0.93, f"$N^*={Ns[imax]}$", transform=ax.transAxes,
        fontsize=12, color=C_VERDE, ha="right", va="top")

ax.set_xscale("log")
ax.set_xlabel("$N$ (passi di Trotter)")
ax.set_ylabel(r"$|C_{21}^{xx}(t{=}2, N)|$")
ax.set_title("Correlatore dinamico sotto rumore: compromesso Trotter/rumore")
ax.legend(loc="center right")

fig.savefig("figure/fig_correlatore_rumoroso_trimero_anello.pdf", bbox_inches="tight")
fig.savefig("figure/fig_correlatore_rumoroso_trimero_anello.png", bbox_inches="tight", dpi=200)
plt.close(fig)
print("[ok] figure/fig_correlatore_rumoroso_trimero_anello.pdf")
