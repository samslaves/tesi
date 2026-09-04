"""
Parte 2, Passo 5 (ultimo) -- scan sui parametri di rumore.

Tre parametri da esplorare: eps_1q, eps_2q, p_readout. Un risultato
analitico emerso PRIMA di scrivere il codice dello scan (derivato e
verificato in validate_scan_parametri_rumore_dimero.py) semplifica il
lavoro: la correzione di readout e' un fattore costante (1-2p) applicato
a TUTTI gli N allo stesso modo (Passo 4), quindi non sposta MAI N* --
scala solo l'ampiezza del segnale. Lo scan vero riguarda quindi solo
eps_1q ed eps_2q, sull'osservabile piu' economico (la fedelta' del Passo
3, che non richiede il blocco correlatori completo).

Per ciascun valore di eps, N* e' cercato su una griglia di N via ricerca
del massimo (stessa logica manuale usata nei Passi 3-4, qui automatizzata).
"""
import numpy as np

from trotter_rumoroso_dimero import fedelta_trotter_rumoroso
from noise_model_dimero import build_noise_model

J, b, D = 1.0, 0.35, 0.80
T_FIXED = 2.0

N_GRID = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40,
          50, 60, 80, 100, 120, 160, 200]


def trova_N_star(vqe_params, psi0_exact, eps_1q, eps_2q, t=T_FIXED,
                  N_grid=N_GRID):
    """Cerca il massimo di F(N) su una griglia discreta di N. Ritorna
    (N_star, F_star, tabella_completa)."""
    nm, _ = build_noise_model(eps_1q=eps_1q, eps_2q=eps_2q, p_readout=0.0)
    Fs = []
    for N in N_grid:
        F, _ = fedelta_trotter_rumoroso(vqe_params, psi0_exact, t, N,
                                         noise_model=nm)
        Fs.append(F)
    imax = int(np.argmax(Fs))
    return N_grid[imax], Fs[imax], list(zip(N_grid, Fs))


def scan_eps2q(vqe_params, psi0_exact, eps2q_values, eps_1q=2.9e-4):
    risultati = []
    for eps2q in eps2q_values:
        N_star, F_star, _ = trova_N_star(vqe_params, psi0_exact,
                                          eps_1q=eps_1q, eps_2q=eps2q)
        risultati.append((eps2q, N_star, F_star))
    return risultati


def scan_eps1q(vqe_params, psi0_exact, eps1q_values, eps_2q=3.8e-3):
    risultati = []
    for eps1q in eps1q_values:
        N_star, F_star, _ = trova_N_star(vqe_params, psi0_exact,
                                          eps_1q=eps1q, eps_2q=eps_2q)
        risultati.append((eps1q, N_star, F_star))
    return risultati


if __name__ == "__main__":
    data = np.load("ground_state_test2.npz")
    vqe_params = data["vqe_params"]
    psi0_exact = data["psi0_exact"]

    print("Scan su eps_2q (eps_1q fissato al riferimento 2.9e-4):")
    for eps2q, N_star, F_star in scan_eps2q(
            vqe_params, psi0_exact,
            [1e-3, 2e-3, 3.8e-3, 6e-3, 1e-2, 1.5e-2, 2.5e-2]):
        print(f"  eps_2q={eps2q:.2e}   N*={N_star:4d}   F(N*)={F_star:.6f}")

    print("\nScan su eps_1q (eps_2q fissato al riferimento 3.8e-3):")
    for eps1q, N_star, F_star in scan_eps1q(
            vqe_params, psi0_exact,
            [1e-4, 2.9e-4, 1e-3, 3e-3, 1e-2, 3e-2]):
        print(f"  eps_1q={eps1q:.2e}   N*={N_star:4d}   F(N*)={F_star:.6f}")
