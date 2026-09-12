"""
Passo 5 -- scan sui parametri di rumore, VERIFICA DIRETTA con la
preparazione noise-aware su tutta la griglia (non solo al punto di
riferimento).

Perche' questo completa (e non solo ripete) i controlli precedenti: le
sessioni precedenti hanno verificato N* invariato fra theta_ideale e
theta_noise-aware SOLO al punto di riferimento (eps_1q=2.9e-4,
eps_2q=3.8e-3, p_readout=2.3e-2). L'argomento di continuita' (vedi
nota_continuita_preparazione.tex) rende plausibile che la stessa
invarianza regga su tutta la griglia del Passo 5, ma "plausibile" non e'
"verificato": questo script chiude il conto punto per punto, su
entrambe le metriche (fedelta' di Trotter, modulo del correlatore).

RUOLO NELL'INSIEME DEL PACCHETTO: e' il modulo che estende il controllo
di vqe_noise_aware_dimero.py dal singolo punto di riferimento all'intera
griglia gia' esplorata da scan_parametri_rumore_dimero.py -- non
introduce nuova fisica, combina le funzioni gia' esistenti (trova_N_star
per il Trotter, una propria N_star_correlatore per i correlatori) in un
controllo sistematico a 25 punti. E' il file che trasforma "l'argomento
di continuita' rende plausibile che..." in "verificato che...".
"""
import numpy as np

from scan_parametri_rumore_dimero import trova_N_star
from correlatori_rumorosi_dimero import correlator_rumoroso, J_DEFAULT, b_DEFAULT, D_DEFAULT
from noise_model_dimero import build_noise_model

T_CORR = 2.0
N_GRID_CORR = list(range(1, 21))


def N_star_correlatore(theta, eps_1q, eps_2q, p_readout=0.023,
                        i=2, alpha="x", j=1, beta="x", N_grid=None):
    """arg max_N |C(N)| a parametri di rumore fissati, per una data
    preparazione theta.

    Ruolo nel modulo: e' l'analogo, per il correlatore, di trova_N_star()
    (scan_parametri_rumore_dimero.py) per il Trotter -- non esisteva
    prima una funzione di questo tipo per i correlatori a parametri di
    rumore variabili, serviva scriverla per completare la griglia.
    Ruolo nell'insieme: e' usata da verifica_griglia_completa() per la
    meta' dei 25 punti della griglia (quelli sul correlatore) -- la
    controparte diretta di trova_N_star() per l'altra metrica.
    """
    if N_grid is None:
        N_grid = N_GRID_CORR
    nm, _ = build_noise_model(eps_1q=eps_1q, eps_2q=eps_2q, p_readout=p_readout)
    vals = [abs(correlator_rumoroso(i, alpha, j, beta, T_CORR, N, J_DEFAULT,
                                     b_DEFAULT, D_DEFAULT, theta,
                                     noise_model=nm, p_readout=p_readout))
            for N in N_grid]
    imax = int(np.argmax(vals))
    return N_grid[imax], vals[imax]


def verifica_griglia_completa(theta_ideale, theta_na, psi_exact):
    """Ripete lo scan del Passo 5 con ENTRAMBE le preparazioni, su
    entrambe le metriche, su tutta la griglia. Ritorna una lista di righe
    (metrica, parametro_variato, valore, N_star_ideale, N_star_na, ok).

    Ruolo nel modulo: e' la funzione pubblica del file -- orchestra le
    25 chiamate (7+6 per il Trotter su eps_2q/eps_1q, 5+4+3 per il
    correlatore su eps_2q/eps_1q/p_readout) e restituisce una tabella
    pronta da stampare o salvare.
    Ruolo nell'insieme: il suo output (25/25 con N* invariato) e' il
    numero citato nella documentazione dei risultati dell'estensione
    come prova che l'invarianza rispetto alla scelta di preparazione non
    e' un fatto isolato del punto di riferimento -- e' importata anche
    dal blocco __main__ di vqe_noise_aware_dimero.py.
    """
    righe = []

    for eps2q in [1e-3, 2e-3, 3.8e-3, 6e-3, 1e-2, 1.5e-2, 2.5e-2]:
        Ni, Fi, _ = trova_N_star(theta_ideale, psi_exact, eps_1q=2.9e-4, eps_2q=eps2q)
        Nn, Fn, _ = trova_N_star(theta_na, psi_exact, eps_1q=2.9e-4, eps_2q=eps2q)
        righe.append(("Trotter", "eps_2q", eps2q, Ni, Nn, Ni == Nn))

    for eps1q in [1e-4, 2.9e-4, 1e-3, 3e-3, 1e-2, 3e-2]:
        Ni, Fi, _ = trova_N_star(theta_ideale, psi_exact, eps_1q=eps1q, eps_2q=3.8e-3)
        Nn, Fn, _ = trova_N_star(theta_na, psi_exact, eps_1q=eps1q, eps_2q=3.8e-3)
        righe.append(("Trotter", "eps_1q", eps1q, Ni, Nn, Ni == Nn))

    for eps2q in [1e-3, 2e-3, 3.8e-3, 6e-3, 1e-2]:
        Ni, _ = N_star_correlatore(theta_ideale, 2.9e-4, eps2q)
        Nn, _ = N_star_correlatore(theta_na, 2.9e-4, eps2q)
        righe.append(("Correlatore", "eps_2q", eps2q, Ni, Nn, Ni == Nn))

    for eps1q in [1e-4, 2.9e-4, 1e-3, 3e-3]:
        Ni, _ = N_star_correlatore(theta_ideale, eps1q, 3.8e-3)
        Nn, _ = N_star_correlatore(theta_na, eps1q, 3.8e-3)
        righe.append(("Correlatore", "eps_1q", eps1q, Ni, Nn, Ni == Nn))

    for pr in [0.0, 0.05, 0.20]:
        Ni, _ = N_star_correlatore(theta_ideale, 2.9e-4, 3.8e-3, p_readout=pr)
        Nn, _ = N_star_correlatore(theta_na, 2.9e-4, 3.8e-3, p_readout=pr)
        righe.append(("Correlatore", "p_readout", pr, Ni, Nn, Ni == Nn))

    return righe


if __name__ == "__main__":
    data = np.load("ground_state_test2.npz")
    theta_ideale = data["vqe_params"]
    psi_exact = data["psi0_exact"]
    na = np.load("vqe_noise_aware_result.npz")
    theta_na = na["x_noise_aware"]

    righe = verifica_griglia_completa(theta_ideale, theta_na, psi_exact)

    print(f"{'metrica':<12} {'parametro':<10} {'valore':>10} {'N*_ideale':>10} {'N*_na':>7} {'esito':>6}")
    for metrica, par, val, Ni, Nn, ok in righe:
        print(f"{metrica:<12} {par:<10} {val:>10.2e} {Ni:>10d} {Nn:>7d} {'OK' if ok else 'DIFF':>6}")

    n_tot = len(righe)
    n_ok = sum(1 for r in righe if r[5])
    print(f"\n{n_ok}/{n_tot} punti della griglia con N* invariato fra le due preparazioni.")

    np.savez("verifica_passo5_risultato.npz",
             righe=np.array(righe, dtype=object), n_ok=n_ok, n_tot=n_tot)
    print("[salvato] verifica_passo5_risultato.npz")
