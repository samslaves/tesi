import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = np.load('/home/claude/thesis_work/scan81_results.npz')
labels = [lab.decode() if isinstance(lab, bytes) else str(lab) for lab in d['labels']]
M_sv = d['M_sv_re'] + 1j * d['M_sv_im']
is_zero = d['is_zero']
mag = np.abs(M_sv)

fig, ax = plt.subplots(figsize=(6.3, 5.6))
im = ax.imshow(mag, cmap='viridis', vmin=0, vmax=mag.max())
ax.set_xticks(range(9))
ax.set_yticks(range(9))
pretty = [f"${lab[0]}{lab[1]}$" for lab in labels]
ax.set_xticklabels(pretty, fontsize=9)
ax.set_yticklabels(pretty, fontsize=9)
ax.set_xlabel(r'$(j,\beta)$ — operatore a $t=0$')
ax.set_ylabel(r'$(i,\alpha)$ — operatore a $t$')
ax.set_title(r'$|C_{ij}^{\alpha\beta}(t{=}1.3)|$ dal circuito (statevector, $N{=}200$)')

for r in range(9):
    for c in range(9):
        if is_zero[r, c]:
            ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False,
                                        edgecolor='red', linewidth=1.8))

# separatori fra i blocchi di sito (ogni 3 righe/colonne)
for k in (2.5, 5.5):
    ax.axhline(k, color='white', linewidth=0.8)
    ax.axvline(k, color='white', linewidth=0.8)

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label(r'$|C_{ij}^{\alpha\beta}(t)|$')

ax.text(0.02, -0.14, 'riquadro rosso = zero strutturale predetto (Corollario sito 3)',
        transform=ax.transAxes, fontsize=8, color='red')

fig.tight_layout()
fig.savefig('/home/claude/thesis_work/fig_scan81_trimero.png', dpi=170)
print("fig_scan81_trimero.png salvata")