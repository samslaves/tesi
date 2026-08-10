"""
VQE per il ground state del dimero al punto di lavoro del test 2
(relazione_test_parametri.md): b/J = 0.35, D/J = 0.80, J = 1.

Riusa la convenzione dell'Hamiltoniana di dimer_exact.py e l'ansatz
PMA-2q.3 + metodologia multistart validati in confronto_ansatz_entangler.ipynb.
Nessuna scelta nuova qui: solo applicazione a un singolo punto (b, J, D).

Obiettivo: |psi_0^VQE> da usare come stato iniziale nel prossimo stadio
(correlazioni dinamiche con ancilla) al posto di |00>.
"""

import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import SparsePauliOp, Statevector, Operator

# --------------------------------------------------------------------------
# 1. Hamiltoniana — stessa convenzione di dimer_exact.py / confronto_ansatz
# --------------------------------------------------------------------------

def dimer_hamiltonian(b, J=1.0, D=0.0):
    """H = J(XX+YY+ZZ) + b(ZI+IZ) + D(XZ-ZX)."""
    return SparsePauliOp.from_list([
        ("XX", J), ("YY", J), ("ZZ", J),
        ("ZI", b), ("IZ", b),
        ("XZ", D), ("ZX", -D),
    ])


def magnetization_operator():
    return SparsePauliOp.from_list([("ZI", 0.5), ("IZ", 0.5)])


def exact_ground(b, J=1.0, D=0.0):
    H = dimer_hamiltonian(b, J, D).to_matrix()
    w, v = np.linalg.eigh(H)
    return w[0], v[:, 0], w, v


def ground_fidelity(psi, w, v, tol=1e-6):
    """Fidelity verso il sottospazio fondamentale (robusta a degenerazioni)."""
    E0 = w[0]
    idx = np.where(np.abs(w - E0) < tol)[0]
    return float(np.sum([np.abs(np.vdot(v[:, i], psi)) ** 2 for i in idx]))


# --------------------------------------------------------------------------
# 2. Ansatz PMA-2q.3 (blocco RBS + rotazioni Ry indipendenti sui due qubit)
#    Identico a quello di confronto_ansatz_entangler.ipynb — PMA_RECOMMENDED.
# --------------------------------------------------------------------------

def rbs_block(qc, phi, q0=0, q1=1):
    """Blocco M-conservante: H-CZ-Ry(phi)/Ry(-phi)-CZ-H."""
    sub = QuantumCircuit(2, name="RBS")
    sub.h(0); sub.h(1); sub.cz(0, 1)
    sub.ry(phi, 0); sub.ry(-phi, 1)
    sub.cz(0, 1); sub.h(0); sub.h(1)
    qc.append(sub.to_gate(label="RBS"), [q0, q1])


def pma_2q(nparam=3):
    """PMA-2q: X(q1) . RBS(p0) . Ry(p1)_0 . Ry(p2)_1  (3 parametri, F=1 dal minimo teorico)."""
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(2)
    qc.x(1)
    rbs_block(qc, p[0])
    i = 1
    while i < nparam:
        qc.ry(p[i], 0); qc.ry(p[i + 1], 1)
        i += 2
    return qc


def _self_test_rbs():
    """RBS deve riprodurre G(phi) a precisione macchina (stesso test del notebook sorgente)."""
    def givens(phi):
        c, s = np.cos(phi), np.sin(phi)
        G = np.eye(4, dtype=complex)
        G[1, 1] = c; G[1, 2] = -s; G[2, 1] = s; G[2, 2] = c
        return G
    for phi in [0.3, 0.7, -0.5]:
        qc = QuantumCircuit(2)
        rbs_block(qc, phi)
        err = np.max(np.abs(Operator(qc).data - givens(phi)))
        assert err < 1e-12, f"RBS self-test fallito a phi={phi}: err={err:.2e}"
    print("[self-test] blocco RBS conforme a G(phi), precisione macchina.")


# --------------------------------------------------------------------------
# 3. VQE multistart — stessa metodologia: R=6, reinizializzazione nel ciclo
#    esterno, COBYLA (confronto_ansatz_entangler.ipynb, mandato del relatore)
# --------------------------------------------------------------------------

def vqe_multistart(ansatz, H_op, w, v, R=6, maxiter=300, seed=0):
    rng = np.random.default_rng(seed)
    n = ansatz.num_parameters
    finals = []
    best = (np.inf, None, None)
    for _ in range(R):
        x0 = rng.uniform(0.0, 2 * np.pi, n)

        def obj(x):
            sv = Statevector(ansatz.assign_parameters(x))
            return float(np.real(sv.expectation_value(H_op)))

        res = minimize(obj, x0, method="COBYLA", options={"maxiter": maxiter})
        finals.append(res.fun)
        if res.fun < best[0]:
            best = (res.fun, res.x, res.nfev)
    Ebest, xbest, nfev = best

    # polish finale: L-BFGS-B dal miglior punto COBYLA, per scendere a
    # precisione macchina (COBYLA da solo lascia un residuo ~1e-5/1e-6)
    def obj(x):
        sv = Statevector(ansatz.assign_parameters(x))
        return float(np.real(sv.expectation_value(H_op)))

    res_polish = minimize(obj, xbest, method="L-BFGS-B")
    if res_polish.fun < Ebest:
        Ebest, xbest = res_polish.fun, res_polish.x

    sv = Statevector(ansatz.assign_parameters(xbest))
    fid = ground_fidelity(sv.data, w, v)
    return {"E": Ebest, "x": xbest, "fid": fid, "nfev": nfev,
            "finals": np.array(finals), "spread": np.ptp(finals),
            "statevector": sv}


# --------------------------------------------------------------------------
# 4. Applicazione al punto di lavoro del test 2
# --------------------------------------------------------------------------

if __name__ == "__main__":
    _self_test_rbs()

    J = 1.0
    b = 0.35 * J     # test 2: b/J = 0.35
    D = 0.80 * J     # test 2: D/J = 0.80

    print(f"\nPunto di lavoro (test 2): b/J={b/J:.3f}  D/J={D/J:.3f}  J={J}")

    # --- benchmark esatto ---
    E0_exact, psi0_exact, w, v = exact_ground(b, J, D)
    Mz_op = magnetization_operator()
    Mz_exact = float(np.real(psi0_exact.conj() @ Mz_op.to_matrix() @ psi0_exact))

    print(f"\nSpettro esatto: {np.round(w, 6)}")
    print(f"E0 (esatto)   = {E0_exact:.8f}")
    print(f"<Mz> (esatto) = {Mz_exact:.6f}")
    print("Ampiezze del ground state esatto (base |00>,|01>,|10>,|11>):")
    for lbl, amp in zip(["00", "01", "10", "11"], psi0_exact):
        print(f"  |{lbl}>: {amp: .6f}")

    # --- VQE con PMA-2q.3 ---
    H_op = dimer_hamiltonian(b, J, D)
    ansatz = pma_2q(3)
    print(f"\nAnsatz: PMA-2q.3, {ansatz.num_parameters} parametri, multistart R=6")

    result = vqe_multistart(ansatz, H_op, w, v, R=6, seed=0)

    print(f"\nE (VQE)       = {result['E']:.8f}")
    print(f"|E_VQE - E0|  = {abs(result['E'] - E0_exact):.2e}")
    print(f"Fidelity      = {result['fid']:.8f}")
    print(f"Dispersione 6 restart (max-min energia finale) = {result['spread']:.2e}")

    sv_vqe = result["statevector"].data
    Mz_vqe = float(np.real(sv_vqe.conj() @ Mz_op.to_matrix() @ sv_vqe))
    print(f"<Mz> (VQE)    = {Mz_vqe:.6f}")

    print("\nParametri ottimali (rad):", np.round(result["x"], 6))
    print("\nStato VQE (base |00>,|01>,|10>,|11>):")
    for lbl, amp in zip(["00", "01", "10", "11"], sv_vqe):
        print(f"  |{lbl}>: {amp: .6f}")

    # overlap di fase con l'esatto (utile per verificare che non ci sia
    # solo una fase globale relativa arbitraria da fissare a valle)
    overlap = np.vdot(psi0_exact, sv_vqe)
    print(f"\n<psi_exact|psi_VQE> = {overlap:.6f}  (|.|={abs(overlap):.8f})")

    np.savez("ground_state_test2.npz",
             b=b, J=J, D=D,
             E0_exact=E0_exact, E_vqe=result["E"], fidelity=result["fid"],
             psi0_exact=psi0_exact, psi0_vqe=sv_vqe,
             vqe_params=result["x"])
    print("\n[salvato] ground_state_test2.npz (stato per lo stadio successivo: correlazioni)")
