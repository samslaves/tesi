import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codice"))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""
Genera fig_correlatore_shots_trimero_anello.pdf: |C_21^xx(N)| a rumore di
riferimento, readout genuinamente campionato (Stadio 4bis) -- mirror
diretto di genera_correlatore_rumoroso_trimero_anello.py (Stadio 4), con
la sola differenza del metodo di lettura.
"""
import numpy as np
from stile import plt, C_BLU, C_VERDE

data = np.load("dati/scan_N_correlatore_shots_trimero_anello.npz")
N_grid, vals, Nstar = data["N_grid"], data["vals"], int(data["Nstar"])

fig, ax = plt.subplots(figsize=(7.2, 4.6))
ax.plot(N_grid, vals, "o-", color=C_BLU)
ax.axvline(Nstar, color=C_VERDE, ls=":", lw=1.5)
ax.annotate(f"$N^*={Nstar}$", xy=(Nstar, vals[list(N_grid).index(Nstar)]),
            xytext=(Nstar + 3, vals.max() - 0.05),
            fontsize=12, color=C_VERDE,
            arrowprops=dict(arrowstyle="->", color=C_VERDE))
ax.set_xlabel("$N$ (passi di Trotter)")
ax.set_ylabel(r"$|C_{21}^{xx}(t{=}2, N)|$")
ax.set_title("Correlatore rumoroso, readout a shot finiti (Stadio 4bis)")

fig.savefig("figure/fig_correlatore_shots_trimero_anello.pdf", bbox_inches="tight")
fig.savefig("figure/fig_correlatore_shots_trimero_anello.png", bbox_inches="tight", dpi=200)
plt.close(fig)
print("[ok] figure/fig_correlatore_shots_trimero_anello.pdf")
