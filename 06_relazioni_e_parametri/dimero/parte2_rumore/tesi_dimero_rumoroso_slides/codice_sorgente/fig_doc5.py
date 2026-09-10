"""Figura del documento 5 -- contrazione della sfera di Bloch sotto il
canale depolarizzante, in funzione di lambda, con i valori di calibrazione
ibm_torino segnati come riferimento."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *
from noise_model_dimero import eps_to_lambda, EPS_1Q_REF, EPS_2Q_REF

os.makedirs("figure", exist_ok=True)

lam1q, lam2q = eps_to_lambda(EPS_1Q_REF, EPS_2Q_REF)
lam = np.linspace(0.0, 0.02, 400)
contrazione = 1.0 - lam

fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.plot(lam, contrazione, color=C_BLU, lw=2.4)
ax.axvline(lam1q, color=C_ARANC, ls="--", lw=1.6,
           label=r"$\lambda_{1q}$ (ibm\_torino)")
ax.axvline(lam2q, color=C_ROSSO, ls="--", lw=1.6,
           label=r"$\lambda_{2q}$ (ibm\_torino)")
ax.set_xlabel(r"$\lambda$ (parametro del canale depolarizzante)")
ax.set_ylabel(r"$1-\lambda$ (contrazione del vettore di Bloch)")
ax.set_title("Canale depolarizzante: contrazione della sfera di Bloch")
ax.set_xlim(0, 0.02)
ax.ticklabel_format(axis="x", style="sci", scilimits=(0, 0), useMathText=True)
ax.legend(loc="lower left")
salva(fig, "fig_depolarizzazione_bloch")

print(f"lambda_1q={lam1q:.6f}  lambda_2q={lam2q:.6f}")
