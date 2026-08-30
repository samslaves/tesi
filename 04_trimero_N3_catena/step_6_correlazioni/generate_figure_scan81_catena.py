import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def make_figure(npz_path, title_suffix, out_path):
    d = np.load(npz_path)
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
    ax.set_title(r'$|C_{ij}^{\alpha\beta}(t{=}1.3)|$ dal circuito, catena' + '\n' + title_suffix)

    for r in range(9):
        for c in range(9):
            if is_zero[r, c]:
                ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False,
                                            edgecolor='red', linewidth=1.8))

    for k in (2.5, 5.5):
        ax.axhline(k, color='white', linewidth=0.8)
        ax.axvline(k, color='white', linewidth=0.8)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(r'$|C_{ij}^{\alpha\beta}(t)|$')

    ax.text(0.02, -0.14,
             'nessuno zero strutturale predetto (Cor. P13-relazioni, catena): nessun riquadro rosso',
             transform=ax.transAxes, fontsize=7.5, color='red')

    fig.tight_layout()
    fig.savefig(out_path, dpi=170)
    print(f"{out_path} salvata")


make_figure('scan81_catena_vqedm_results.npz',
            r'VQE-DM ($b_c{=}3.0,\,D{=}0.15$)',
            'fig_scan81_trimero_catena_vqedm.png')
make_figure('scan81_catena_S0_results.npz',
            r'S0 Trotter ($b{=}3.0073414,\,D{=}0.3$)',
            'fig_scan81_trimero_catena_S0.png')
