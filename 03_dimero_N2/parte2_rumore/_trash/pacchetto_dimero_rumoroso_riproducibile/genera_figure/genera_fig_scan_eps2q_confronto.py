"""Genera fig_scan_eps2q_confronto.pdf.
Eseguire dalla RADICE del pacchetto, dopo 01_ e 02_.
Nota: ripete il VQE noise-aware a 5 valori di rumore -- più lento
degli altri script (qualche minuto).

RUOLO NELL'INSIEME DEL PACCHETTO: produce la figura che confronta
riuso ideale e ottimizzazione noise-aware SULLO STESSO SCAN gia' fatto
per il documento base (genera_fig_vqe_dm_rumoroso.py) -- a differenza
di quello script, qui vqe_noise_aware() viene richiamato ad ogni valore
di eps_2q, non solo al riferimento, per mostrare che le due curve
restano sovrapposte su tutto l'intervallo.
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_BLU, C_ARANC, salva
from noise_model_dimero import build_noise_model
from vqe_dm_rumoroso_dimero import vqe_energia_fedelta_rumorosa
from vqe_noise_aware_dimero import vqe_noise_aware, energia_fedelta_rumorosa
from dimer_exact import dimer_hamiltonian

data = np.load("dati/ground_state_test2.npz")
vqe_params_ideali = data["vqe_params"]
psi0_exact = data["psi0_exact"]
H = dimer_hamiltonian(b=0.35, J=1.0, D=0.80)

eps2q_grid = [0.0, 1e-3, 3.8e-3, 8e-3, 1.5e-2]
E_ideale, F_ideale, E_na, F_na = [], [], [], []
for e in eps2q_grid:
    nm, _ = build_noise_model(eps_2q=e) if e > 0 else (None, None)
    Ei, Fi, _ = vqe_energia_fedelta_rumorosa(vqe_params_ideali, psi0_exact, noise_model=nm)
    E_ideale.append(Ei); F_ideale.append(Fi)

    ris = vqe_noise_aware(noise_model=nm, R=6, maxiter=300, seed=0,
                           x_seme=vqe_params_ideali)
    En, Fn, _ = energia_fedelta_rumorosa(ris["x"], H, nm, psi0_exact)
    E_na.append(En); F_na.append(Fn)
    print(f"eps2q={e:.1e}: E_ideale={Ei:.6f} E_na={En:.6f}  F_ideale={Fi:.6f} F_na={Fn:.6f}")

labels = [f"{e:.1e}" if e > 0 else "0" for e in eps2q_grid]
xs = np.arange(len(eps2q_grid))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
ax1.plot(xs, E_ideale, "o-", color=C_BLU, label="riuso ideale")
ax1.plot(xs, E_na, "s--", color=C_ARANC, label="noise-aware")
ax1.set_xticks(xs); ax1.set_xticklabels(labels, rotation=20)
ax1.set_xlabel(r"$\varepsilon_{2q}$"); ax1.set_ylabel("E (rumoroso)")
ax1.set_title("Energia"); ax1.legend(fontsize=9)

ax2.plot(xs, F_ideale, "o-", color=C_BLU, label="riuso ideale")
ax2.plot(xs, F_na, "s--", color=C_ARANC, label="noise-aware")
ax2.set_xticks(xs); ax2.set_xticklabels(labels, rotation=20)
ax2.set_xlabel(r"$\varepsilon_{2q}$"); ax2.set_ylabel("F (rumorosa)")
ax2.set_title("Fedeltà"); ax2.legend(fontsize=9)

salva(fig, "fig_scan_eps2q_confronto")
