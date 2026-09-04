"""Stile grafico condiviso per tutte le figure dei documenti sul dimero.

Criteri: font grandi (le figure finiranno in slide), nessuna sovrapposizione
fra testo e curve (legende fuori dai dati o in angoli liberi verificati),
palette sicura per daltonismo, output vettoriale (PDF).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# palette CVD-safe (Okabe-Ito)
C_NERO   = "#000000"
C_BLU    = "#0072B2"
C_ARANC  = "#E69F00"
C_VERDE  = "#009E73"
C_ROSSO  = "#D55E00"
C_VIOLA  = "#CC79A7"
C_AZZURRO= "#56B4E9"
C_GIALLO = "#F0E442"
C_GRIGIO = "#9a9a9a"

plt.rcParams.update({
    "pdf.fonttype": 42,   # font vettoriali veri (TrueType-in-PDF), non Type 3 bitmap
    "ps.fonttype": 42,
    "figure.dpi": 120,
    "savefig.dpi": 400,
    "font.size": 13,
    "axes.titlesize": 14,
    "axes.labelsize": 14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 11.5,
    "legend.framealpha": 0.92,
    "legend.edgecolor": "0.8",
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "lines.linewidth": 2.0,
    "figure.constrained_layout.use": True,
    "mathtext.fontset": "cm",
    "font.family": "serif",
})


def salva(fig, nome):
    fig.savefig(f"figure/{nome}.pdf", bbox_inches="tight")
    fig.savefig(f"figure/{nome}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"[ok] figure/{nome}.pdf")
