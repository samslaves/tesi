"""Genera fig_confronto_ansatz_HA_PMA.pdf.
Eseguire dalla RADICE del pacchetto (nessun dato precalcolato richiesto).
Tempo stimato: ~30 secondi (80 ottimizzazioni VQE in tutto).

RUOLO NELL'INSIEME DEL PACCHETTO: produce la figura che giustifica la
scelta dell'ansatz PMA (rispetto a quello hardware-efficient HA) usata
poi ovunque nel resto del progetto -- griglia 4x4 (HA/PMA x D=0/D=0.2),
energia/errore/fedeltà/magnetizzazione contro B/J. Riusa esattamente
vqe_sweep() e plot_grid() di codice/vqe_dimer.py, adattando solo il
percorso di salvataggio per essere coerente con lo stile del pacchetto
(cartella figure/, tramite stile.salva invece del salvataggio interno
di plot_grid).
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from vqe_dimer import vqe_sweep, _plot_row
from stile import salva

J = 1.0
reps_HA = 2
K_PMA = 1
n_b = 33
n_rest = 3

b_values = np.linspace(0.0, 4.0, n_b)
configs = [
    ("HA", 0.0, reps_HA, K_PMA),
    ("HA", 0.2, reps_HA, K_PMA),
    ("PMA", 0.0, reps_HA, K_PMA),
    ("PMA", 0.2, reps_HA, K_PMA),
]
rows_meta = [
    ("HA  D=0", "tab:blue"),
    ("HA  D=0.2", "tab:orange"),
    ("PMA D=0", "tab:green"),
    ("PMA D=0.2", "tab:red"),
]

all_results = []
for ansatz_type, D, reps, K in configs:
    print(f"VQE sweep: {ansatz_type}  D={D} ...")
    res = vqe_sweep(b_values, J=J, D=D, ansatz_type=ansatz_type,
                     reps=reps, K=K, n_restarts=n_rest, verbose=False)
    all_results.append(res)
    max_delta_e = max(r["delta_e"] for r in res)
    min_fid = min(r["fidelity"] for r in res)
    print(f"  max|Delta E| = {max_delta_e:.2e}   min fedeltà = {min_fid:.6f}")

fig, axes = plt.subplots(4, 4, figsize=(18, 14))
fig.suptitle("VQE dimero N=2 — confronto HA vs PMA, D=0 vs D=0.2", fontsize=12)
for row_idx, (label, color) in enumerate(rows_meta):
    _plot_row(axes[row_idx], all_results[row_idx], J, label, color)
fig.tight_layout(rect=[0, 0, 1, 0.97])

salva(fig, "fig_confronto_ansatz_HA_PMA")
