"""
Rigenera fig_depolarizzazione_bloch.pdf come vero PDF vettoriale.

RUOLO: il file originale del Project, letto in questa sessione, risulta un
archivio zip con anteprima JPEG (limite della piattaforma per i PDF montati
in /mnt/project in questo ambiente, non un difetto del file sorgente).
Impossibile recuperare l'originale vettoriale da questa sessione: la figura
viene ricostruita da zero, usando la formula nota (contrazione = 1-lambda,
canale depolarizzante) e i valori/etichette esatti recuperati dal testo
estratto nel manifest del pacchetto stesso (assi, range, legenda), non
inventati.
"""
import numpy as np
from stile import plt, C_BLU, C_ARANC, salva
from noise_model_dimero import eps_to_lambda, EPS_1Q_REF, EPS_2Q_REF

lam_1q, lam_2q = eps_to_lambda(EPS_1Q_REF, EPS_2Q_REF)

lam = np.linspace(0, 0.02, 400)
contrazione = 1 - lam

fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.plot(lam * 100, contrazione, color=C_BLU, label=r"$1-\lambda$")
ax.axvline(lam_1q * 100, color=C_ARANC, ls="--", lw=1.6,
           label=rf"$\lambda_{{1q}}$ (ibm-torino)")
ax.axvline(lam_2q * 100, color=C_ARANC, ls=":", lw=1.6,
           label=rf"$\lambda_{{2q}}$ (ibm-torino)")
ax.set_xlim(0, 2.0)
ax.set_ylim(0.98, 1.0)
ax.set_xlabel(r"$\lambda$ (parametro del canale depolarizzante) $\times10^{-2}$")
ax.set_ylabel("contrazione del vettore di Bloch")
ax.set_title("Canale depolarizzante: contrazione della sfera di Bloch")
ax.legend(loc="lower left")

salva(fig, "fig_depolarizzazione_bloch")
