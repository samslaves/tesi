"""Genera le figure per circuito_correlazioni_trimero_anello_spiegato.tex."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from trimer_ring_exact import trimer_hamiltonian_dm
from circuito_correlazioni_trimero_anello import (
    ground_state, build_correlator_circuit, correlator_from_circuit,
)
from validate_circuito_correlazioni import classical_exact

J, Jp, b, D = 1.0, 0.4, 2.4, 0.15
H = trimer_hamiltonian_dm(J, Jp, b, "B", D).to_matrix()
psi0, E = ground_state(J, Jp, b, D)

plt.rcParams.update({"font.size": 11})

# ------------------------------------------------------------------
# Fig 1: convergenza di Trotter, C_11^yy(t=1.3)
# ------------------------------------------------------------------
Ns = [10, 20, 40, 80, 160, 320]
c_ref = classical_exact(1, 'y', 1, 'y', 1.3, J, Jp, b, D, psi0, H)
errs = []
for N in Ns:
    c_circ = correlator_from_circuit(1, 'y', 1, 'y', 1.3, N, J, Jp, b, D, psi0)
    errs.append(abs(c_ref - c_circ))

fig, ax = plt.subplots(figsize=(4.6, 3.6))
ax.loglog(Ns, errs, 'o-', color='#1f4e8c', label=r'$|C_{11}^{yy,\rm circ}(N)-C_{11}^{yy,\rm esatto}|$')
ref = errs[0] * Ns[0] / np.array(Ns)
ax.loglog(Ns, ref, '--', color='gray', label=r'$\propto 1/N$')
ax.set_xlabel(r'$N$ (passi di Trotter)')
ax.set_ylabel('errore assoluto')
ax.set_title(r'Convergenza Trotter, $C_{11}^{yy}(t{=}1.3)$')
ax.legend(fontsize=9)
ax.grid(True, which='both', alpha=0.3)
fig.tight_layout()
fig.savefig('fig_trotter_trimero.png', dpi=170)
plt.close(fig)

# ------------------------------------------------------------------
# Fig 2: validazione continua, C_11^yy(t) su un intervallo
# ------------------------------------------------------------------
t_dense = np.linspace(0.05, 3.0, 200)
re_exact, im_exact = [], []
for t in t_dense:
    c = classical_exact(1, 'y', 1, 'y', t, J, Jp, b, D, psi0, H)
    re_exact.append(c.real); im_exact.append(c.imag)

t_circ = np.linspace(0.2, 2.9, 12)
re_circ, im_circ = [], []
for t in t_circ:
    c = correlator_from_circuit(1, 'y', 1, 'y', t, 200, J, Jp, b, D, psi0)
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
fig.suptitle(r'Validazione: $C_{11}^{yy}(t)$, circuito vs esatto')
fig.tight_layout()
fig.savefig('fig_validazione_trimero.png', dpi=170)
plt.close(fig)

# ------------------------------------------------------------------
# Fig 3: lo zero strutturale del sito 3, C_33^xz(t)
# ------------------------------------------------------------------
re3_exact, im3_exact = [], []
for t in t_dense:
    c = classical_exact(3, 'x', 3, 'z', t, J, Jp, b, D, psi0, H)
    re3_exact.append(c.real); im3_exact.append(c.imag)

re3_circ, im3_circ = [], []
for t in t_circ:
    c = correlator_from_circuit(3, 'x', 3, 'z', t, 200, J, Jp, b, D, psi0)
    re3_circ.append(c.real); im3_circ.append(c.imag)

fig, ax = plt.subplots(figsize=(5.2, 3.6))
ax.plot(t_dense, re3_exact, '-', color='#1f4e8c', label=r'$\mathrm{Re}\,C_{33}^{xz}$, esatto ($\equiv0$)')
ax.plot(t_dense, im3_exact, '-', color='#8c1f6e', label=r'$\mathrm{Im}\,C_{33}^{xz}$, esatto ($\equiv0$)')
ax.plot(t_circ, re3_circ, 'o', color='#c0392b', ms=5, label='Re, circuito')
ax.plot(t_circ, im3_circ, 's', color='#e67e22', ms=5, label='Im, circuito')
ax.axhline(0, color='gray', lw=0.7)
ax.set_xlabel('$t$'); ax.set_ylabel(r'$C_{33}^{xz}(t)$')
ax.set_title('Zero strutturale del sito 3 (Corollario, per ogni $t$)')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('fig_sito3_zero_trimero.png', dpi=170)
plt.close(fig)

print("Figure generate:")
print(" fig_trotter_trimero.png")
print(" fig_validazione_trimero.png")
print(" fig_sito3_zero_trimero.png")
print()
print("Ultimo residuo Trotter (N=320):", errs[-1])
print("Max |C_33^xz| circuito su t_circ:", max(abs(np.array(re3_circ)+1j*np.array(im3_circ))))