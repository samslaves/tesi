"""Genera fig_depolarizzazione_bloch.pdf (documento: modello di rumore).
Eseguire dalla RADICE del pacchetto: python3 genera_figure/genera_fig_modello_rumore.py

RUOLO NELL'INSIEME DEL PACCHETTO: produce l'unica figura del documento
sul modello di rumore -- illustrazione puramente concettuale (la
contrazione del vettore di Bloch al crescere di lambda), non dipende
da nessun file in dati/ ne' da nessun altro script del pacchetto:
puo' essere eseguito per primo, prima ancora di 01_.
"""
import numpy as np
import sys
sys.path.insert(0, "codice")
from stile import plt, C_BLU, C_ARANC, C_ROSSO, salva

lam = np.linspace(0, 0.02, 200)
r = 1 - lam

fig, ax = plt.subplots(figsize=(6.0, 4.2))
ax.plot(lam, r, color=C_BLU, lw=2.2)
ax.axvline(5.8e-4, color=C_ARANC, ls="--", lw=1.5, label=r"$\lambda_{1q}$ (ibm-torino)")
ax.axvline(5.0667e-3, color=C_ROSSO, ls="--", lw=1.5, label=r"$\lambda_{2q}$ (ibm-torino)")
ax.set_xlabel(r"$\lambda$ (parametro del canale depolarizzante)")
ax.set_ylabel(r"$1-\lambda$ (contrazione del vettore di Bloch)")
ax.set_title("Canale depolarizzante: contrazione della sfera di Bloch")
ax.legend(fontsize=9)
ax.xaxis.set_major_formatter(plt.matplotlib.ticker.ScalarFormatter(useMathText=True))
ax.ticklabel_format(axis="x", style="sci", scilimits=(0, 0))

salva(fig, "fig_depolarizzazione_bloch")
print("[ok] fig_depolarizzazione_bloch.pdf")
