"""Genera le figure per circuito_correlazioni_trimero_catena_spiegato.tex.
Mirror di generate_figures_circuito_trimero_anello.py, con la Fig.3
sostituita: la catena non ha uno zero strutturale sul sito fisso (a
differenza dell'anello), quindi la figura mostra il CONTRASTO -- il sito
fisso (2) ha un'autocorrelazione mista genericamente non nulla.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from trimer_chain_exact import trimer_hamiltonian_dm
from circuito_correlazioni_trimero_catena import (
    ground_state, build_correlator_circuit, correlator_from_circuit,
)
from validate_circuito_correlazioni_catena import classical_exact

J, b, D = 1.0, 3.0, 0.15
H = trimer_hamiltonian_dm(J, b, D).to_matrix()
psi0, E = ground_state(J, b, D)

plt.rcParams.update({"font.size": 11})

# ------------------------------------------------------------------
# Fig 1: convergenza di Trotter, C_11^yy(t=1.3)
# ------------------------------------------------------------------
Ns = [10, 20, 40, 80, 160, 320]
c_ref = classical_exact(1, 'y', 1, 'y', 1.3, J, b, D, psi0, H)
errs = []
for N in Ns:
    c_circ = correlator_from_circuit(1, 'y', 1, 'y', 1.3, N, J, b, D, psi0)
    errs.append(abs(c_ref - c_circ))

fig, ax = plt.subplots(figsize=(4.6, 3.6))
ax.loglog(Ns, errs, 'o-', color='#1f4e8c', label=r'$|C_{11}^{yy,\rm circ}(N)-C_{11}^{yy,\rm esatto}|$')
ref = errs[0] * Ns[0] / np.array(Ns)
ax.loglog(Ns, ref, '--', color='gray', label=r'$\propto 1/N$')
ax.set_xlabel(r'$N$ (passi di Trotter)')
ax.set_ylabel('errore assoluto')
ax.set_title(r'Convergenza Trotter, $C_{11}^{yy}(t{=}1.3)$, catena')
ax.legend(fontsize=9)
ax.grid(True, which='both', alpha=0.3)
fig.tight_layout()
fig.savefig('fig_trotter_trimero_catena.png', dpi=170)
plt.close(fig)

# ------------------------------------------------------------------
# Fig 2: validazione continua, C_11^yy(t) su un intervallo
# ------------------------------------------------------------------
t_dense = np.linspace(0.05, 3.0, 200)
re_exact, im_exact = [], []
for t in t_dense:
    c = classical_exact(1, 'y', 1, 'y', t, J, b, D, psi0, H)
    re_exact.append(c.real); im_exact.append(c.imag)

t_circ = np.linspace(0.2, 2.9, 12)
re_circ, im_circ = [], []
for t in t_circ:
    c = correlator_from_circuit(1, 'y', 1, 'y', t, 200, J, b, D, psi0)
    re_circ.append(c.real); im_circ.append(c.imag)

fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.4))
axs[0].plot(t_dense, re_exact, '-', color='#1f4e8c', label='esatto classico')
axs[0].plot(t_circ, re_circ, 'o', color='#c0392b', ms=5, label='circuito ($N{=}200$)')
axs[0].set_xlabel('$t$'); axs[0].set_ylabel(r'$\mathrm{Re}\,C_{11}^{yy}(t)$')
axs[0].legend(fontsize=8); axs[0].grid(alpha=0.3)

axs[1].plot(t_dense, im_exact, '-', color='#1f4e8c', label='esatto classico')
axs[1].plot(t_circ, im_circ, 'o', color='#c0392b', ms=5, label='circuito ($N{=}200$)')
axs[1].set_xlabel('$t$'); axs[1].set_ylabel(r'$\mathrm{Im}\,C_{11}^{yy}(t)$')
axs[1].legend(fontsize=8); axs[1].grid(alpha=0.3)
fig.suptitle(r'Validazione: $C_{11}^{yy}(t)$, circuito vs esatto, catena')
fig.tight_layout()
fig.savefig('fig_validazione_trimero_catena.png', dpi=170)
plt.close(fig)

# ------------------------------------------------------------------
# Fig 3 (CONTRASTO con l'anello): il sito fisso (2) NON ha zero
# strutturale -- C_22^xz(t) e' genericamente non nullo per t>0, a
# differenza di C_33^xz dell'anello che e' identicamente zero per ogni t.
# ------------------------------------------------------------------
re2_exact, im2_exact = [], []
for t in t_dense:
    c = classical_exact(2, 'x', 2, 'z', t, J, b, D, psi0, H)
    re2_exact.append(c.real); im2_exact.append(c.imag)

re2_circ, im2_circ = [], []
for t in t_circ:
    c = correlator_from_circuit(2, 'x', 2, 'z', t, 200, J, b, D, psi0)
    re2_circ.append(c.real); im2_circ.append(c.imag)

fig, ax = plt.subplots(figsize=(5.2, 3.6))
ax.plot(t_dense, re2_exact, '-', color='#1f4e8c', label=r'$\mathrm{Re}\,C_{22}^{xz}$, esatto')
ax.plot(t_dense, im2_exact, '-', color='#8c1f6e', label=r'$\mathrm{Im}\,C_{22}^{xz}$, esatto')
ax.plot(t_circ, re2_circ, 'o', color='#c0392b', ms=5, label='Re, circuito')
ax.plot(t_circ, im2_circ, 's', color='#e67e22', ms=5, label='Im, circuito')
ax.axhline(0, color='gray', lw=0.7)
ax.axvline(0, color='gray', lw=0.7, ls=':')
ax.annotate('zero solo a $t=0$\n(Cor. zero-t0-same)', xy=(0, 0), xytext=(1.55, -0.32),
            fontsize=8, color='gray', ha='center',
            arrowprops=dict(arrowstyle='->', color='gray', lw=0.8))
ax.set_xlabel('$t$'); ax.set_ylabel(r'$C_{22}^{xz}(t)$')
ax.set_title('Sito fisso (2): NESSUNO zero strutturale per $t>0$')
ax.legend(fontsize=8, loc='upper right')
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('fig_sito2_non_zero_trimero_catena.png', dpi=170)
plt.close(fig)

print("Figure generate:")
print(" fig_trotter_trimero_catena.png")
print(" fig_validazione_trimero_catena.png")
print(" fig_sito2_non_zero_trimero_catena.png")
print()
print("Ultimo residuo Trotter (N=320):", errs[-1])
print("C_22^xz(0) esatto:", classical_exact(2, 'x', 2, 'z', 0.0, J, b, D, psi0, H))
print("Max |C_22^xz| per t in [0.2,2.9] circuito:",
      max(abs(np.array(re2_circ) + 1j * np.array(im2_circ))))
