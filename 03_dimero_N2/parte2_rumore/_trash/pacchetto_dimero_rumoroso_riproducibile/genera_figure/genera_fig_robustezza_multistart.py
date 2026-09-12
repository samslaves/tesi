"""Genera fig_robustezza_multistart.pdf.
Eseguire dalla RADICE del pacchetto, dopo 01_ e 02_.
Nota: piu' lento (20+6+6 ottimizzazioni COBYLA sotto rumore).

RUOLO NELL'INSIEME DEL PACCHETTO: produce la figura diagnostica sulla
dispersione del multistart -- non un risultato fisico sull'invarianza
di N*, ma la giustificazione del perche' vqe_noise_aware() includa
sempre i parametri ideali come seme (senza, un multistart con pochi
riavvii puo' restare lontano dall'ottimo vero).
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_ARANC, C_AZZURRO, C_GIALLO, C_GRIGIO, salva
from noise_model_dimero import build_noise_model
from vqe_noise_aware_dimero import energia_rumorosa
from dimer_exact import dimer_hamiltonian
from scipy.optimize import minimize

data = np.load("dati/ground_state_test2.npz")
vqe_params_ideali = data["vqe_params"]
na = np.load("dati/vqe_noise_aware_result.npz")
E_ottimo_noto = float(na["E_noise_aware"])

nm_ref, _ = build_noise_model()
H = dimer_hamiltonian(b=0.35, J=1.0, D=0.80)


def obj(x):
    return energia_rumorosa(x, H, nm_ref)


def multistart_dettaglio(R, seed, con_seme):
    rng = np.random.default_rng(seed)
    x0_list = [rng.uniform(0.0, 2 * np.pi, 3) for _ in range(R)]
    if con_seme:
        x0_list.append(np.asarray(vqe_params_ideali))
    finals = []
    for x0 in x0_list:
        res = minimize(obj, x0, method="COBYLA", options={"maxiter": 300})
        finals.append(res.fun)
    return np.array(finals)


print("Eseguo R=6 (no seme, seed=1)...")
f6 = multistart_dettaglio(6, seed=1, con_seme=False)
print("Eseguo R=6+seme (seed=0, quello usato nel risultato principale)...")
f6s = multistart_dettaglio(6, seed=0, con_seme=True)
print("Eseguo R=20 (no seme, seed=2)...")
f20 = multistart_dettaglio(20, seed=2, con_seme=False)

for nome, arr in [("R=6", f6), ("R=6+seme", f6s), ("R=20", f20)]:
    print(f"{nome}: best={arr.min():.8f}  scostamento dal noto={arr.min()-E_ottimo_noto:.2e}")

fig, ax = plt.subplots(figsize=(6.6, 4.6))
gruppi = [f6, f6s, f20]
colori = [C_ARANC, C_AZZURRO, C_GIALLO]
etichette = ["R=6\n(no seme)", "R=6+seme", "R=20\n(no seme)"]
for i, (g, c) in enumerate(zip(gruppi, colori)):
    jitter = np.random.default_rng(0).uniform(-0.12, 0.12, len(g))
    ax.scatter(np.full(len(g), i) + jitter, g, color=c, alpha=0.85, s=40, zorder=3)
ax.axhline(E_ottimo_noto, color=C_GRIGIO, ls="--", lw=1.2, label="ottimo noto")
ax.set_xticks(range(3)); ax.set_xticklabels(etichette)
ax.set_ylabel("E finale (per singolo restart COBYLA)")
ax.set_title("Dispersione degli esiti del multistart (rumore acceso)")
ax.legend(fontsize=9.5)
salva(fig, "fig_robustezza_multistart")
