import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codice"))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""
Genera fig_vqe_noise_aware_trimero_anello.pdf: energia e fedelta',
riuso dei parametri ideali contro VQE noise-aware (Stadio 2bis), a
struttura di circuito fissa.
"""
import numpy as np
from stile import plt, C_BLU, C_ARANC

data = np.load("dati/vqe_noise_aware_validato.npz")
E_riuso, F_riuso = float(data["E_riuso"]), float(data["F_riuso"])
E_na, F_na = float(data["E_na"]), float(data["F_na"])

fig, axs = plt.subplots(1, 2, figsize=(8.4, 4.2))

axs[0].bar(["riuso\nideale", "noise-\naware"], [E_riuso, E_na],
           color=[C_BLU, C_ARANC])
axs[0].set_ylabel("$E$ (rumoroso)")
axs[0].set_title("Energia")

axs[1].bar(["riuso\nideale", "noise-\naware"], [F_riuso, F_na],
           color=[C_BLU, C_ARANC])
axs[1].set_ylabel("$F$ (rumorosa)")
axs[1].set_title("Fedeltà")

fig.suptitle("VQE noise-aware vs riuso parametri ideali (struttura fissa)")
fig.tight_layout()
fig.savefig("figure/fig_vqe_noise_aware_trimero_anello.pdf", bbox_inches="tight")
fig.savefig("figure/fig_vqe_noise_aware_trimero_anello.png", bbox_inches="tight", dpi=200)
plt.close(fig)
print("[ok] figure/fig_vqe_noise_aware_trimero_anello.pdf")
print(f"  Delta_E = {E_na - E_riuso:+.6e}   Delta_F = {F_na - F_riuso:+.6e}")
