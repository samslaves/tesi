import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = np.load('/home/claude/thesis_work/shot_noise_results.npz')
shots_list = d['shots_list']
means = d['means']
stds = d['stds']
c_ref_re = float(d['c_ref_re'])

fig, ax = plt.subplots(figsize=(5.2, 3.8))
ax.errorbar(shots_list, means, yerr=stds, fmt='o-', color='#1f4e8c', capsize=3,
            label=r'stima da conteggi (media $\pm$ dev.std, 40 ripetizioni)')
ax.axhline(c_ref_re, color='gray', ls='--', label='esatto classico')
ref_curve = stds[0] * np.sqrt(shots_list[0]) / np.sqrt(shots_list)
ax.fill_between(shots_list, means - 1/np.sqrt(shots_list), means + 1/np.sqrt(shots_list),
                 color='#1f4e8c', alpha=0.08, label=r'banda $\pm 1/\sqrt{N_{\rm shots}}$')
ax.set_xscale('log')
ax.set_xlabel(r'$N_{\rm shots}$')
ax.set_ylabel(r'$\mathrm{Re}\,C_{11}^{yy}(t{=}1.3)$, stima')
ax.set_title('Convergenza al crescere del numero di shot')
ax.legend(fontsize=7.5, loc='upper right')
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('/home/claude/thesis_work/fig_shot_trimero.png', dpi=170)
print("fig_shot_trimero.png salvata")