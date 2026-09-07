"""
Benchmark esatto per il dimero di spin-1/2 (N=2), modello di Heisenberg isotropo.

    H = J (X1X2 + Y1Y2 + Z1Z2) + b (Z1 + Z2) + D (X1Z2 - Z1X2)

- caso base (D=0): autovalori analitici E(S,M) = 2J S(S+1) - 3J + 2 b M
- variante con termine di Dzyaloshinskii-Moriya (D != 0): apre l'anticrossing
  in B/J = 2, rendendo il ground state unico e a gap finito su tutto il range.

Convenzione qubit (Qiskit, little-endian): la label "ZI" agisce con Z sul qubit 1.
Il modello e' simmetrico per scambio dei due spin, quindi Z1+Z2 = "ZI"+"IZ".

Sorgente unica: lo stesso SparsePauliOp alimenta sia questo benchmark sia il VQE.

RUOLO NELL'INSIEME DEL PACCHETTO: e' il "mattone zero", il modulo piu'
a monte di tutti gli altri -- non importa nulla da nessun altro file di
questo pacchetto, e viene importato praticamente da ovunque (VQE ideale,
VQE sotto rumore, Trotter, correlatori, tutte le estensioni) per costruire
l'Hamiltoniana e per fornire il riferimento esatto (autovalori analitici,
diagonalizzazione numerica) contro cui ogni altro risultato viene
confrontato. Se questo modulo cambiasse silenziosamente, l'errore si
propagherebbe a tutta la pipeline senza dare nessun segnale esplicito --
per questo il self-test qui sotto confronta i due metodi (numerico contro
analitico) ad ogni esecuzione diretta del file.
"""

import numpy as np
from qiskit.quantum_info import SparsePauliOp


def dimer_hamiltonian(b, J=1.0, D=0.0):
    """Costruisce H(b,J,D) come SparsePauliOp a 2 qubit.

    Ruolo nel modulo: e' la funzione che tutte le altre in questo file
    (e in pratica tutti gli altri moduli del pacchetto) chiamano per
    ottenere l'operatore Hamiltoniano -- l'unico punto in cui i sette
    coefficienti di Pauli vengono effettivamente assemblati.
    Ruolo nell'insieme: e' la "sorgente unica" richiamata nel docstring
    di modulo -- VQE, Trotter e correlatori costruiscono tutti la STESSA
    Hamiltoniana chiamando questa funzione con parametri diversi, non
    ridefinendola mai in modo indipendente altrove.
    """
    labels = ["XX", "YY", "ZZ", "ZI", "IZ", "XZ", "ZX"]
    coeffs = [J, J, J, b, b, D, -D]
    return SparsePauliOp(labels, coeffs)


def magnetization_operator():
    """Costruisce Mz = (Z1 + Z2) / 2.

    Ruolo nel modulo: osservabile ausiliario usato da exact_sweep() per
    caratterizzare il ground state lungo lo sweep in campo (utile a
    localizzare l'anticrossing in B/J=2 citato nel docstring di modulo).
    Ruolo nell'insieme: osservabile diagnostico di Parte 1, non usato
    direttamente dalla pipeline di rumore (Parte 2) -- presente qui
    per completezza del benchmark esatto, non e' un prerequisito per
    gli altri moduli del pacchetto.
    """
    return SparsePauliOp(["ZI", "IZ"], [0.5, 0.5])


def analytic_eigenvalues(b, J=1.0):
    """Spettro esatto in forma chiusa del caso isotropo (D=0): singoletto
    + tripletto M=+1,0,-1.

    Ruolo nel modulo: termine di paragone nel self-test qui sotto --
    permette di verificare exact_sweep() (che diagonalizza numericamente)
    senza fidarsi ciecamente di numpy.linalg.eigh.
    Ruolo nell'insieme: e' il valore di riferimento "di carta e penna"
    per l'intero pacchetto quando D=0 -- ogni volta che un altro modulo
    riporta un'energia esatta per D=0, il numero deve poter essere
    fatto risalire, in linea di principio, a questa formula.
    """
    return np.sort([-3.0 * J, J + 2.0 * b, J, J - 2.0 * b])


def exact_sweep(b_values, J=1.0, D=0.0):
    """Diagonalizza H su una griglia di campo b, con o senza termine DM.

    Ruolo nel modulo: generalizza analytic_eigenvalues() al caso D!=0
    (dove non esiste piu' una formula chiusa) tramite diagonalizzazione
    numerica diretta; usato anche per D=0 nel self-test, per avere
    un unico percorso di calcolo confrontato con la formula analitica.
    Ruolo nell'insieme: e' la funzione che produce le figure diagnostiche
    di Parte 1 (spettro, anticrossing, magnetizzazione) quando il modulo
    viene eseguito direttamente; i moduli di Parte 2 (rumore) non la
    chiamano, usano piuttosto singoli punti di lavoro fissi.

    Ritorna un dict con:
      energies      (n_b, 4)  tutti gli autovalori ordinati
      gs_energy     (n_b,)    energia del ground state
      gs_state      (n_b, 4)  autovettore del ground state
      gs_mz         (n_b,)    magnetizzazione <Mz> sul ground state
    """
    Mz = magnetization_operator().to_matrix()
    energies, gs_energy, gs_state, gs_mz = [], [], [], []
    for b in b_values:
        H = dimer_hamiltonian(b, J, D).to_matrix()
        w, v = np.linalg.eigh(H)            # H hermitiana: autovalori reali e ordinati
        g = v[:, 0]
        energies.append(w)
        gs_energy.append(w[0])
        gs_state.append(g)
        gs_mz.append(np.real(g.conj() @ Mz @ g))
    return {
        "b": np.asarray(b_values),
        "energies": np.asarray(energies),
        "gs_energy": np.asarray(gs_energy),
        "gs_state": np.asarray(gs_state),
        "gs_mz": np.asarray(gs_mz),
    }


def _self_test(J=1.0):
    """Controllo di coerenza interna: confronta exact_sweep() (numerico)
    contro analytic_eigenvalues() (formula chiusa) su tutto il range di b.

    Ruolo nel modulo: eseguito automaticamente ogni volta che il file
    viene lanciato come script -- prima riga di difesa contro un errore
    di segno o di convenzione nell'Hamiltoniana che altrimenti si
    propagherebbe silenziosamente a valle.
    Ruolo nell'insieme: essendo dimer_hamiltonian() la sorgente unica
    usata da tutto il pacchetto, questo self-test e' indirettamente
    una garanzia di correttezza per l'intera pipeline, non solo per
    questo file.
    """
    b = np.linspace(0.0, 5.0, 200)
    res = exact_sweep(b, J=J, D=0.0)
    err = max(np.max(np.abs(np.sort(res["energies"][i]) - analytic_eigenvalues(bv, J)))
              for i, bv in enumerate(b))
    print(f"[self-test] max|E_num - E_analitico| (D=0) = {err:.2e}")
    assert err < 1e-10, "spettro numerico non coincide con l'analitico"


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    J = 1.0
    _self_test(J)

    b = np.linspace(0.0, 5.0, 300)
    res0 = exact_sweep(b, J=J, D=0.0)
    resD = exact_sweep(b, J=J, D=0.2)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    for k in range(4):
        ax1.plot(b / J, res0["energies"][:, k], color="0.7", lw=1)
    ax1.plot(b / J, res0["gs_energy"], "k", lw=2, label="GS (D=0)")
    ax1.plot(b / J, resD["gs_energy"], "r--", lw=2, label="GS (D=0.2)")
    ax1.axvline(2.0, color="0.5", ls=":", lw=1)
    ax1.set_xlabel("B / J"); ax1.set_ylabel("Energy / J")
    ax1.set_title("Spettro del dimero"); ax1.legend()

    ax2.plot(b / J, res0["gs_mz"], "k", lw=2, label="D=0 (salto)")
    ax2.plot(b / J, resD["gs_mz"], "r--", lw=2, label="D=0.2 (crossover)")
    ax2.axvline(2.0, color="0.5", ls=":", lw=1)
    ax2.set_xlabel("B / J"); ax2.set_ylabel(r"$\langle M_z \rangle$")
    ax2.set_title("Magnetizzazione del ground state"); ax2.legend()

    fig.tight_layout()
    fig.savefig("dimer_exact.png", dpi=150)
    print("[ok] figura salvata: dimer_exact.png")
