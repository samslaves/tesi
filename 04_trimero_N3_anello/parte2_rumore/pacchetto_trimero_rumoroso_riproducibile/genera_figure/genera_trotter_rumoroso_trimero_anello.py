import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codice"))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""
Genera fig_trotter_rumoroso_trimero_anello.pdf: fedelta' rumorosa F(N) per
entrambi gli scenari (A: punto VQE; B: punto R0), con N* evidenziato.
"""
import numpy as np
from stile import plt, C_BLU, C_ARANC, C_VERDE

data = np.load("dati/scan_N_trotter_rumoroso_trimero_anello.npz")
Ns = data["Ns"]
Fs_A = data["Fs_A"]
Fs_B = data["Fs_B"]

fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), sharey=True)

for ax, Fs, titolo, colore in [
    (axes[0], Fs_A, "Scenario A --- punto VQE ($b=2.4,\\,D=0.15$)", C_BLU),
    (axes[1], Fs_B, "Scenario B --- punto $R_0$ ($b=0.05,\\,D=1.93$)", C_ARANC),
]:
    ax.plot(Ns, Fs, "o-", color=colore)
    imax = int(np.argmax(Fs))
    ax.axvline(Ns[imax], color=C_VERDE, ls=":", lw=1.5)
    ax.text(0.97, 0.93, f"$N^*={Ns[imax]}$", transform=ax.transAxes,
            fontsize=12, color=C_VERDE, ha="right", va="top")
    ax.set_xlabel("$N$ (passi di Trotter)")
    ax.set_title(titolo, fontsize=12.5)
    ax.set_xscale("log")

axes[0].set_ylabel("$F$ (fedeltà rumorosa)")
fig.suptitle("Compromesso Trotter/rumore: $F(N)$ al rumore di riferimento (ibm-torino)",
             fontsize=13.5)

fig.savefig("figure/fig_trotter_rumoroso_trimero_anello.pdf", bbox_inches="tight")
fig.savefig("figure/fig_trotter_rumoroso_trimero_anello.png", bbox_inches="tight", dpi=200)
plt.close(fig)
print("[ok] figure/fig_trotter_rumoroso_trimero_anello.pdf")
