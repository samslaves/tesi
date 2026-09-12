"""Stile grafico condiviso per tutte le figure dei documenti sul dimero.

Criteri: font grandi (le figure finiranno in slide), nessuna sovrapposizione
fra testo e curve (legende fuori dai dati o in angoli liberi verificati),
palette sicura per daltonismo, output vettoriale (PDF).

RUOLO NELL'INSIEME DEL PACCHETTO: e' l'unico modulo di questo pacchetto
che non calcola nulla di fisico -- fissa solo l'aspetto grafico condiviso
da tutti e 12 gli script in genera_figure/. Ogni script di figura importa
`plt` da qui (mai `import matplotlib.pyplot` direttamente) insieme alla
palette di colori e alla funzione salva(), cosi' che tutte le 15 figure
del pacchetto abbiano lo stesso stile, senza doverlo ripetere in ognuno.
La scelta pdf.fonttype=42 (vedi commento sotto) e' cio' che garantisce
che le figure si aprano correttamente in QUALUNQUE visualizzatore PDF,
inclusi i browser -- un problema reale gia' incontrato in una sessione
precedente con i documenti LaTeX (font Type 3 bitmap invece che
vettoriali), qui prevenuto alla radice per le figure.
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
    """Salva la figura in figure/nome.pdf e figure/nome.png, creando la
    cartella se non esiste, poi chiude la figura per liberare memoria.

    Ruolo nel modulo: e' la funzione pubblica del file -- ogni script in
    genera_figure/ la chiama esattamente una volta (o due, per gli
    script che producono due figure) come ultimo passo.
    Ruolo nell'insieme: e' il punto unico di tutto il pacchetto in cui
    una figura passa da oggetto matplotlib in memoria a file su disco --
    concentrare qui il percorso di salvataggio (sempre "figure/", sempre
    sia PDF sia PNG) garantisce che i nomi file coincidano esattamente
    con quelli richiamati dai documenti .tex che le usano.
    """
    import os
    os.makedirs("figure", exist_ok=True)
    fig.savefig(f"figure/{nome}.pdf", bbox_inches="tight")
    fig.savefig(f"figure/{nome}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"[ok] figure/{nome}.pdf")
