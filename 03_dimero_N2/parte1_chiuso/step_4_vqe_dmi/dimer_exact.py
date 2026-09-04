"""
Benchmark esatto per il dimero di spin-1/2 (N=2), modello di Heisenberg isotropo.

    H = J (X1X2 + Y1Y2 + Z1Z2) + b (Z1 + Z2) + D (X1Z2 - Z1X2)

- caso base (D=0): autovalori analitici E(S,M) = 2J S(S+1) - 3J + 2 b M
- variante con termine di Dzyaloshinskii-Moriya (D != 0): apre l'anticrossing
  in B/J = 2, rendendo il ground state unico e a gap finito su tutto il range.

Convenzione qubit (Qiskit, little-endian): la label "ZI" agisce con Z sul qubit 1.
Il modello e' simmetrico per scambio dei due spin, quindi Z1+Z2 = "ZI"+"IZ".

Sorgente unica: lo stesso SparsePauliOp alimenta sia questo benchmark sia il VQE.
"""

import numpy as np
from qiskit.quantum_info import SparsePauliOp


def dimer_hamiltonian(b, J=1.0, D=0.0):
    """H(b) come SparsePauliOp per dati J, D."""
    labels = ["XX", "YY", "ZZ", "ZI", "IZ", "XZ", "ZX"]
    coeffs = [J, J, J, b, b, D, -D]
    return SparsePauliOp(labels, coeffs)


def magnetization_operator():
    """Mz = (Z1 + Z2) / 2."""
    return SparsePauliOp(["ZI", "IZ"], [0.5, 0.5])


def analytic_eigenvalues(b, J=1.0):
    """Spettro esatto del caso isotropo (D=0): singoletto + tripletto M=+1,0,-1."""
    return np.sort([-3.0 * J, J + 2.0 * b, J, J - 2.0 * b])


def exact_sweep(b_values, J=1.0, D=0.0):
    """Diagonalizza H su una griglia di campo b.

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
    """QC: confronto numerico vs analitico (D=0) su tutto il range."""
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
