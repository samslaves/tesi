"""
Parte 2, Stadio 5 (ultimo) -- scan sui parametri di rumore (trimero ad anello).

RUOLO NELL'INSIEME DEL PACCHETTO: mirror di
`scan_parametri_rumore_dimero.py`, esteso a DUE osservabili di fedelta'
(Scenario A e B, Stadio 3) invece di una sola, perche' l'anello ha due
punti di lavoro distinti (a differenza del dimero). Il correlatore
(Stadio 4) NON viene scansionato qui per costo computazionale -- stessa
scelta del dimero ("osservabile piu' economico"), giustificata dalla
stessa invarianza analitica da p_readout (Stadio 4: fattore moltiplicativo
costante in N, non sposta mai un argmax) -- verificata anche qui
(validate_scan_parametri_rumore_trimero_anello.py), non assunta identica
solo perche' la dimostrazione del dimero non usa dettagli specifici di N.

Tre parametri possibili: eps_1q, eps_2q, p_readout. Lo scan vero riguarda
solo eps_1q ed eps_2q (p_readout provatamente non sposta N*).
"""
import numpy as np

from trotter_rumoroso_trimero_anello import (
    fedelta_trotter_rumoroso, PUNTO_VQE, PUNTO_R0,
)
from trimer_ring_exact import trimer_hamiltonian_dm
from noise_model_trimero_anello import build_noise_model

T_FIXED = 2.0

N_GRID = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50, 60, 80, 100]


def _psi0_vqe_exact(vqe_params=None):
    """Stato fondamentale ESATTO al punto VQE (fase fissata reale),
    indipendente dai parametri VQE passati come argomento (non usato,
    mantenuto per firma simmetrica) -- calcolato per diagonalizzazione
    diretta, non dal circuito.

    RUOLO NEL MODULO: stato bersaglio per lo scenario A in trova_N_star.
    RUOLO NELL'INSIEME: stesso calcolo gia' fatto in
    trotter_rumoroso_trimero_anello.py (Stadio 3) e in
    validate_vqe_dm_rumoroso_trimero_anello.py (Stadio 2) -- qui
    riprodotto localmente per non introdurre un'altra dipendenza
    incrociata solo per una diagonalizzazione a 8x8."""
    H = trimer_hamiltonian_dm(PUNTO_VQE["J"], PUNTO_VQE["Jp"],
                               PUNTO_VQE["b"], "B", PUNTO_VQE["D"]).to_matrix()
    E, V = np.linalg.eigh(H)
    psi0 = V[:, 0]
    imax = np.argmax(np.abs(psi0))
    return psi0 * np.exp(-1j * np.angle(psi0[imax]))


def trova_N_star(scenario, vqe_params, eps_1q, eps_2q, t=T_FIXED, N_grid=N_GRID):
    """Cerca il massimo di F(N) su una griglia discreta di N, per lo
    scenario 'A' (punto VQE, preparazione) o 'B' (punto R0, da |000>).
    Ritorna (N_star, F_star)."""
    nm, _ = build_noise_model(eps_1q=eps_1q, eps_2q=eps_2q, p_readout=0.0)
    if scenario == "A":
        punto, prep, psi0 = PUNTO_VQE, vqe_params, _psi0_vqe_exact()
    elif scenario == "B":
        psi0_000 = np.zeros(8, dtype=complex); psi0_000[0] = 1.0
        punto, prep, psi0 = PUNTO_R0, None, psi0_000
    else:
        raise ValueError("scenario deve essere 'A' o 'B'")

    Fs = []
    for N in N_grid:
        F, _ = fedelta_trotter_rumoroso(**punto, t=t, N=N, psi0=psi0,
                                         noise_model=nm, vqe_params=prep)
        Fs.append(F)
    imax = int(np.argmax(Fs))
    return N_grid[imax], Fs[imax]


def scan_eps2q(scenario, vqe_params, eps2q_values, eps_1q=2.9e-4):
    """Ripete trova_N_star su una lista di valori di eps_2q, eps_1q
    fissato al riferimento.

    RUOLO NEL MODULO: genera la serie usata per la colonna sinistra
    della figura N* vs eps. RUOLO NELL'INSIEME: dati di
    dati/scan_parametri_rumore_trimero_anello.npz, chiave
    '{scenario}_eps2q'/'{scenario}_Nstar2q'."""
    risultati = []
    for eps2q in eps2q_values:
        N_star, F_star = trova_N_star(scenario, vqe_params, eps_1q=eps_1q, eps_2q=eps2q)
        risultati.append((eps2q, N_star, F_star))
    return risultati


def scan_eps1q(scenario, vqe_params, eps1q_values, eps_2q=3.8e-3):
    """Ripete trova_N_star su una lista di valori di eps_1q, eps_2q
    fissato al riferimento.

    RUOLO NEL MODULO: genera la serie usata per la colonna destra della
    figura N* vs eps. RUOLO NELL'INSIEME: dati di
    dati/scan_parametri_rumore_trimero_anello.npz, chiave
    '{scenario}_eps1q'/'{scenario}_Nstar1q'."""
    risultati = []
    for eps1q in eps1q_values:
        N_star, F_star = trova_N_star(scenario, vqe_params, eps_1q=eps1q, eps_2q=eps_2q)
        risultati.append((eps1q, N_star, F_star))
    return risultati


if __name__ == "__main__":
    data = np.load("w2q6_params_optimal.npz")
    vqe_params = data["params"]

    eps2q_vals = [1e-3, 2e-3, 3.8e-3, 6e-3, 1e-2, 1.5e-2, 2.5e-2]
    eps1q_vals = [1e-4, 2.9e-4, 1e-3, 3e-3, 1e-2, 3e-2]

    risultati_npz = {}
    for scenario in ["A", "B"]:
        print(f"=== Scenario {scenario} ===")
        print(f"Scan su eps_2q (eps_1q fissato al riferimento 2.9e-4):")
        r2q = scan_eps2q(scenario, vqe_params, eps2q_vals)
        for eps2q, N_star, F_star in r2q:
            print(f"  eps_2q={eps2q:.2e}   N*={N_star:4d}   F(N*)={F_star:.6f}")

        print(f"\nScan su eps_1q (eps_2q fissato al riferimento 3.8e-3):")
        r1q = scan_eps1q(scenario, vqe_params, eps1q_vals)
        for eps1q, N_star, F_star in r1q:
            print(f"  eps_1q={eps1q:.2e}   N*={N_star:4d}   F(N*)={F_star:.6f}")
        print()

        risultati_npz[f"{scenario}_eps2q"] = np.array([x[0] for x in r2q])
        risultati_npz[f"{scenario}_Nstar2q"] = np.array([x[1] for x in r2q])
        risultati_npz[f"{scenario}_eps1q"] = np.array([x[0] for x in r1q])
        risultati_npz[f"{scenario}_Nstar1q"] = np.array([x[1] for x in r1q])

    np.savez("scan_parametri_rumore_trimero_anello.npz", **risultati_npz)
    print("Salvato: scan_parametri_rumore_trimero_anello.npz")
