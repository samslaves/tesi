import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codice"))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""Genera fig_scan81_anello.pdf: le 81 combinazioni C_ij^{alpha,beta}(t),
ampiezza massima su una griglia di istanti -- mostra a colpo d'occhio i
quattro zeri strutturali (tutti sul sito 3) rispetto al resto."""
import numpy as np
from stile import plt, C_BLU, C_ROSSO

data = np.load("dati/scan81_correlatori.npz", allow_pickle=True)
righe = data["righe"]
ampiezze = np.array([r[4] for r in righe])
zeri_str = data["zeri_strutturali"]

fig, ax = plt.subplots(figsize=(10.0, 4.2))
idx = np.arange(len(righe))
colori = [C_ROSSO if any(r[0] == z[0] and r[1] == z[1] and r[2] == z[2] and r[3] == z[3]
                          for z in zeri_str) else C_BLU for r in righe]
ax.bar(idx, ampiezze, color=colori, width=0.8)
ax.set_xlabel("combinazione (indice, 81 totali)")
ax.set_ylabel(r"$\max_t|C_{ij}^{\alpha\beta}(t)|$")
ax.set_title("Le 81 combinazioni, Scenario A -- in rosso i 4 zeri strutturali (sito 3)")
fig.savefig("figure/fig_scan81_anello.pdf", bbox_inches="tight")
fig.savefig("figure/fig_scan81_anello.png", bbox_inches="tight", dpi=200)
plt.close(fig)
print("[ok] figure/fig_scan81_anello.pdf")
