import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codice"))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""
Genera fig_readout_asimmetrico_trimero_anello.pdf: N* in funzione del
rapporto p10/p01 (media fissa) -- Stadio 6bis.
"""
import numpy as np
from stile import plt, C_VIOLA

data = np.load("dati/readout_asimmetrico_validato.npz")
rapporti, Nstars = data["rapporti"], data["Nstars"]

fig, ax = plt.subplots(figsize=(5.8, 4.4))
ax.plot(rapporti, Nstars, "o-", color=C_VIOLA, ms=7, lw=2.0)
ax.set_xscale("log")
ax.set_xlabel(r"rapporto $p_{10}/p_{01}$")
ax.set_ylabel(r"$N^*$")
ax.set_ylim(0, max(Nstars) + 2)
ax.set_title(r"$N^*$ vs asimmetria del readout, media fissa")

fig.savefig("figure/fig_readout_asimmetrico_trimero_anello.pdf", bbox_inches="tight")
fig.savefig("figure/fig_readout_asimmetrico_trimero_anello.png", bbox_inches="tight", dpi=200)
plt.close(fig)
print("[ok] figure/fig_readout_asimmetrico_trimero_anello.pdf")
