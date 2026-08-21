"""
Benchmark esatto per il trimero di spin-1/2 (N=3), anello/triangolo isoscele.

    H = J (sigma1.sigma2) + J' (sigma2.sigma3 + sigma3.sigma1) + b (Z1+Z2+Z3)

Base J sui siti (1,2) (simmetrici per scambio), lati J' su (2,3) e (3,1).
La simmetria di scambio 1<->2 rende conservato S12^2 = (s1+s2)^2 oltre a
S^2, Sz (decomposizione di Kambe) -> tre multipletti:

    A: S12=1, S=3/2   E_A = J + 2J'   (4 stati, M=+-3/2,+-1/2)
    B: S12=1, S=1/2   E_B = J - 4J'   (2 stati, M=+-1/2)
    C: S12=0, S=1/2   E_C = -3J       (2 stati, M=+-1/2)

con E(S12,S,M) = E_blocco + 2 b M. Campo critico b_c = 2J+J' se il
fondamentale a b=0 e' C, b_c = 3J' se e' B (vedi teoria_trimero_isoscele.pdf
per la mappa dei segni completa).

Convenzione sito<->qubit (Qiskit, little-endian): site1->qubit2, site2->
qubit1, site3->qubit0. Con questa scelta la label Pauli letta da sinistra a
destra e' "site1 site2 site3", nello stesso ordine della notazione fisica
|q1 q2 q3> usata nella derivazione (derivazione_stati_kambe_trimero.pdf) e
dello stesso ordine kron(site1,site2,site3) usato li' per costruire gli
otto stati di Kambe a mano. Nessuna reindicizzazione e' quindi necessaria
tra le due rappresentazioni; il self-test sotto lo verifica esplicitamente
applicando l'operatore Qiskit ai vettori di Kambe costruiti "a mano".

Sorgente unica: lo stesso SparsePauliOp alimenta sia questo benchmark sia
il VQE (vqe_trimer_ring.py), come gia' fatto per il dimero.

Termine DM (Dzyaloshinskii-Moriya): due forme candidate disponibili
(trimer_hamiltonian_dm, dm_term, dm_min_gap) -- vedi la sezione dedicata
piu' sotto e analisi_dm_trimero.pdf per la derivazione completa. Non ancora
usate nel resto del progetto: in attesa di conferma dal relatore su quale
opzione adottare per una trattazione quantitativa.
"""

import numpy as np
from qiskit.quantum_info import SparsePauliOp


# ----------------------------------------------------------------------
# Hamiltoniana e operatori
# ----------------------------------------------------------------------

def trimer_hamiltonian(J, Jp, b):
    """H(J, J', b) come SparsePauliOp, topologia anello isoscele.

    Label a 3 caratteri, ordine "site1 site2 site3" (vedi convenzione sopra).
    """
    labels = [
        # sigma1.sigma2  (bond base, coeff J)
        "XXI", "YYI", "ZZI",
        # sigma2.sigma3  (bond laterale, coeff J')
        "IXX", "IYY", "IZZ",
        # sigma3.sigma1  (bond laterale, coeff J')
        "XIX", "YIY", "ZIZ",
        # Zeeman, coeff b
        "ZII", "IZI", "IIZ",
    ]
    coeffs = [J, J, J, Jp, Jp, Jp, Jp, Jp, Jp, b, b, b]
    return SparsePauliOp(labels, coeffs)


def magnetization_operator():
    """Mz = (Z1+Z2+Z3)/2, convenzione di spin (s=sigma/2)."""
    return SparsePauliOp(["ZII", "IZI", "IIZ"], [0.5, 0.5, 0.5])


def S12_squared_operator():
    """Casimir della coppia base: S12^2 = (3/2) I + (1/2) sigma1.sigma2.

    Autovalori attesi: 0 (blocco C, S12=0), 2 (blocchi A/B, S12=1).
    """
    labels = ["III", "XXI", "YYI", "ZZI"]
    coeffs = [1.5, 0.5, 0.5, 0.5]
    return SparsePauliOp(labels, coeffs)


def S_total_squared_operator():
    """Casimir totale: S^2 = (9/4) I + (1/2)(s1.s2 + s2.s3 + s3.s1 pauli).

    Autovalori attesi: 15/4 (blocco A, S=3/2), 3/4 (blocchi B/C, S=1/2).
    """
    labels = ["III",
              "XXI", "YYI", "ZZI",
              "IXX", "IYY", "IZZ",
              "XIX", "YIY", "ZIZ"]
    coeffs = [2.25] + [0.5] * 9
    return SparsePauliOp(labels, coeffs)


# ----------------------------------------------------------------------
# Spettro analitico (Kambe)
# ----------------------------------------------------------------------

def analytic_eigenvalues(J, Jp, b):
    """Le 8 energie esatte E(S12,S,M) = E_blocco + 2bM, ordinate."""
    E_A, E_B, E_C = J + 2 * Jp, J - 4 * Jp, -3 * J
    M_A = [1.5, 0.5, -0.5, -1.5]
    M_BC = [0.5, -0.5]
    energies = (
        [E_A + 2 * b * M for M in M_A]
        + [E_B + 2 * b * M for M in M_BC]
        + [E_C + 2 * b * M for M in M_BC]
    )
    return np.sort(energies)


def critical_field(J, Jp):
    """b_c dell'incrocio fondamentale, a seconda di chi e' il GS a b=0.

    GS(b=0) = C se E_C < E_B  (-3J < J-4J', cioe' J' < J), altrimenti B.
    """
    E_B, E_C = J - 4 * Jp, -3 * J
    if E_C <= E_B:
        return 2 * J + Jp     # incrocio C -> A
    return 3 * Jp             # incrocio B -> A


# ----------------------------------------------------------------------
# Stati di Kambe espliciti (base computazionale |q1 q2 q3>)
# derivati in derivazione_stati_kambe_trimero.pdf, sezioni 2-4
# ----------------------------------------------------------------------

def _basis_ket(*bits):
    v = np.zeros(8, dtype=complex)
    idx = int("".join(str(bit) for bit in bits), 2)
    v[idx] = 1.0
    return v


def kambe_states():
    """Dizionario {(blocco, M): vettore a 8 componenti}.

    Convenzione qubit |0>=up (Z=+1), |1>=down (Z=-1), stessa del resto del
    progetto. Formule derivate per composizione dei momenti angolari
    (vedi PDF di derivazione), verificate a precisione macchina.
    """
    k000, k001, k010, k100 = (_basis_ket(0, 0, 0), _basis_ket(0, 0, 1),
                               _basis_ket(0, 1, 0), _basis_ket(1, 0, 0))
    k011, k101, k110, k111 = (_basis_ket(0, 1, 1), _basis_ket(1, 0, 1),
                               _basis_ket(1, 1, 0), _basis_ket(1, 1, 1))

    r2, r3, r6 = np.sqrt(2.0), np.sqrt(3.0), np.sqrt(6.0)

    return {
        ("A", 1.5):  k000,
        ("A", 0.5):  (k001 + k010 + k100) / r3,
        ("A", -0.5): (k011 + k101 + k110) / r3,
        ("A", -1.5): k111,
        ("B", 0.5):  np.sqrt(2 / 3) * k001 - (k010 + k100) / r6,
        ("B", -0.5): (k011 + k101) / r6 - np.sqrt(2 / 3) * k110,
        ("C", 0.5):  (k010 - k100) / r2,
        ("C", -0.5): (k011 - k101) / r2,
    }


def kambe_energy(J, Jp, b, block, M):
    """Energia analitica del singolo stato (blocco, M)."""
    E_blocco = {"A": J + 2 * Jp, "B": J - 4 * Jp, "C": -3 * J}[block]
    return E_blocco + 2 * b * M


# ----------------------------------------------------------------------
# Diagonalizzazione esatta su griglia
# ----------------------------------------------------------------------

def exact_sweep(b_values, J=1.0, Jp=0.4):
    """Diagonalizza H su una griglia di campo b.

    Ritorna un dict con:
      energies       (n_b, 8)  tutti gli autovalori ordinati
      gs_energy      (n_b,)    energia del ground state
      gs_state       (n_b, 8)  autovettore del ground state (arbitrario se degenere)
      gs_mz          (n_b,)    magnetizzazione <Mz> sul ground state -- MEDIATA
                                sul sottospazio degenere quando presente (vedi nota)
      gs_S12sq       (n_b,)    <S12^2> sul ground state (tag di blocco)
      gs_Stotsq      (n_b,)    <S^2> sul ground state (tag di blocco)

    Nota sulla degenerazione. Nei punti in cui il fondamentale e' degenere
    (es. b=0 quando il GS e' il blocco B, M=+-1/2 alla stessa energia),
    un singolo autovettore restituito da np.linalg.eigh e' una scelta di
    base ARBITRARIA all'interno del sottospazio degenere: il valore di
    <Mz> su un singolo autovettore puo' dipendere da quella scelta e non
    riflette il limite fisico. Qui <Mz> viene invece calcolato come media
    sul sottospazio degenere (traccia di Mz sul proiettore, diviso per la
    degenerazione): a b=0 questo da' correttamente 0 (nessuna direzione
    di M privilegiata), mentre per b>0 (degenerazione rotta) coincide con
    il valore ordinario su singolo autovettore. Stesso trattamento gia'
    applicato in trimer_chain_exact.py.
    """
    Mz = magnetization_operator().to_matrix()
    S12sq = S12_squared_operator().to_matrix()
    Stotsq = S_total_squared_operator().to_matrix()

    energies, gs_energy, gs_state = [], [], []
    gs_mz, gs_S12sq, gs_Stotsq = [], [], []

    for b in b_values:
        H = trimer_hamiltonian(J, Jp, b).to_matrix()
        w, v = np.linalg.eigh(H)
        degenerate = np.abs(w - w[0]) < 1e-9
        V0 = v[:, degenerate]
        deg = V0.shape[1]
        P0 = V0 @ V0.conj().T
        g = v[:, 0]  # un rappresentante, riportato per compatibilita'/ispezione
        energies.append(w)
        gs_energy.append(w[0])
        gs_state.append(g)
        gs_mz.append(np.real(np.trace(P0 @ Mz)) / deg)
        gs_S12sq.append(np.real(np.trace(P0 @ S12sq)) / deg)
        gs_Stotsq.append(np.real(np.trace(P0 @ Stotsq)) / deg)

    return {
        "b": np.asarray(b_values),
        "energies": np.asarray(energies),
        "gs_energy": np.asarray(gs_energy),
        "gs_state": np.asarray(gs_state),
        "gs_mz": np.asarray(gs_mz),
        "gs_S12sq": np.asarray(gs_S12sq),
        "gs_Stotsq": np.asarray(gs_Stotsq),
    }


def ground_state_projector(J, Jp, b, tol=1e-9):
    """Proiettore sul multipletto fondamentale (eventualmente degenere).

    Serve per definire la fidelity F = <psi|P0|psi> nel VQE, dato che il
    fondamentale del trimero e' quasi ovunque un multipletto degenere
    (vedi nota 1 in teoria_trimero_isoscele.pdf), non un singolo autostato.
    """
    H = trimer_hamiltonian(J, Jp, b).to_matrix()
    w, v = np.linalg.eigh(H)
    degenerate = np.abs(w - w[0]) < tol
    V0 = v[:, degenerate]
    return V0 @ V0.conj().T, w[0], int(degenerate.sum())


# ----------------------------------------------------------------------
# Termine DM (Dzyaloshinskii-Moriya) -- IN ATTESA DI CONFERMA DAL RELATORE
# ----------------------------------------------------------------------
#
# Due forme candidate per D_ij(X_i Z_j - Z_i X_j), verificate rispetto alla
# simmetria di scambio 1<->2 (vedi analisi_dm_trimero.pdf per la derivazione
# completa, inclusa la ricerca errata iniziale e la sua correzione):
#
#   Opzione A: nessun DM sul legame di base (D_12=0), segno OPPOSTO sui due
#              legami laterali (D_23=-D_31=D'). Rispetta esattamente la
#              simmetria P_12 e [H,S12^2]=0. Conseguenza (von Neumann-Wigner
#              applicata a S12^2): l'incrocio C<->A NON si apre mai, qualunque
#              sia D' -- resta un incrocio vero, solo spostato in b.
#
#   Opzione B: DM su tutti e tre i legami, STESSO segno, proporzionale a J
#              (D_12=rJ, D_23=D_31=rJ'). Proposta dal relatore come scelta
#              semplice. Rompe la simmetria P_12 e [H,S12^2]!=0. L'incrocio
#              C<->A si apre davvero, gap cresce linearmente con r.
#
# NON e' ancora stato confermato dal relatore quale opzione (o quale forma
# alternativa) usare per un'eventuale trattazione quantitativa in tesi.
# Queste funzioni sono quindi disponibili ma non usate da exact_sweep, ne'
# da vqe_trimer_ring.py, finche' non arriva una conferma esplicita.

def dm_term(i, j, D):
    """D*(X_i Z_j - Z_i X_j), stessa forma gia' validata per il dimero."""
    pos = {1: 0, 2: 1, 3: 2}  # site1=carattere 0 (sinistra), ..., site3=carattere 2
    lab1, lab2 = ["I", "I", "I"], ["I", "I", "I"]
    lab1[pos[i]], lab1[pos[j]] = "X", "Z"
    lab2[pos[i]], lab2[pos[j]] = "Z", "X"
    return SparsePauliOp(["".join(lab1), "".join(lab2)], [D, -D])


def trimer_hamiltonian_dm(J, Jp, b, mode, D):
    """H(J,J',b) + termine DM, secondo l'opzione scelta.

    mode: None -> nessun DM (identico a trimer_hamiltonian)
          "A"  -> DM solo sui legami laterali, segno opposto (preserva S12^2)
          "B"  -> DM su tutti e tre i legami, stesso segno prop. a J (rompe S12^2)
    """
    H = trimer_hamiltonian(J, Jp, b)
    if mode is None or D == 0:
        return H
    if mode == "A":
        return H + dm_term(2, 3, D) + dm_term(3, 1, -D)
    if mode == "B":
        return H + dm_term(1, 2, D * J) + dm_term(2, 3, D * Jp) + dm_term(3, 1, D * Jp)
    raise ValueError(f"mode sconosciuto: {mode!r} (atteso None, 'A' o 'B')")


def dm_min_gap(J, Jp, mode, D, search_half_width=None):
    """Gap VERO fra i due autovalori piu' bassi: minimo su tutto b, non a
    b_c fisso (il punto di incrocio si sposta quando il DM e' acceso --
    vedi l'errore metodologico documentato in analisi_dm_trimero.pdf, sez. 4).
    """
    from scipy.optimize import minimize_scalar

    bc = critical_field(J, Jp)
    if search_half_width is None:
        search_half_width = max(1.0, abs(bc) * 0.6)

    def gap_func(b):
        H = trimer_hamiltonian_dm(J, Jp, b, mode, D).to_matrix()
        w = np.linalg.eigvalsh(H)
        return w[1] - w[0]

    res = minimize_scalar(
        gap_func, bounds=(max(0.0, bc - search_half_width), bc + search_half_width),
        method="bounded", options={"xatol": 1e-10},
    )
    return res.fun, res.x


def exact_sweep_dm(b_values, J, Jp, mode, D):
    """Come exact_sweep, ma con H_dm al posto di H. Serve come benchmark per
    il VQE quando il DM e' acceso (exact_sweep resta la forma chiusa pura,
    D=0, e non va toccata).

    NOTA: con mode="B" (o comunque quando S12^2 non e' piu' conservato),
    gs_S12sq NON e' un numero quantico buono -- e' comunque riportato come
    valore di aspettazione, utile per vedere quanto il fondamentale vero si
    allontana dal carattere di blocco puro (A/B/C) al crescere di D.
    """
    Mz = magnetization_operator().to_matrix()
    S12sq = S12_squared_operator().to_matrix()
    Stotsq = S_total_squared_operator().to_matrix()

    energies, gs_energy, gs_state = [], [], []
    gs_mz, gs_S12sq, gs_Stotsq = [], [], []

    for b in b_values:
        H = trimer_hamiltonian_dm(J, Jp, b, mode, D).to_matrix()
        w, v = np.linalg.eigh(H)
        g = v[:, 0]
        energies.append(w)
        gs_energy.append(w[0])
        gs_state.append(g)
        gs_mz.append(np.real(g.conj() @ Mz @ g))
        gs_S12sq.append(np.real(g.conj() @ S12sq @ g))
        gs_Stotsq.append(np.real(g.conj() @ Stotsq @ g))

    return {
        "b": np.asarray(b_values),
        "energies": np.asarray(energies),
        "gs_energy": np.asarray(gs_energy),
        "gs_state": np.asarray(gs_state),
        "gs_mz": np.asarray(gs_mz),
        "gs_S12sq": np.asarray(gs_S12sq),
        "gs_Stotsq": np.asarray(gs_Stotsq),
    }


def ground_state_projector_dm(J, Jp, b, mode, D, tol=1e-9):
    """Come ground_state_projector, ma con H_dm al posto di H."""
    H = trimer_hamiltonian_dm(J, Jp, b, mode, D).to_matrix()
    w, v = np.linalg.eigh(H)
    degenerate = np.abs(w - w[0]) < tol
    V0 = v[:, degenerate]
    return V0 @ V0.conj().T, w[0], int(degenerate.sum())


def _self_test_dm():
    """Verifica le proprieta' di simmetria e il comportamento del gap per
    entrambe le opzioni di DM, agli stessi valori gia' controllati a mano
    in analisi_dm_trimero.pdf (cross-check indipendente qui nel modulo)."""
    print("=" * 70)
    print("[self-test DM 1] simmetria di scambio P12")

    def P12_matrix():
        P = np.zeros((8, 8))
        for b1 in (0, 1):
            for b2 in (0, 1):
                for b3 in (0, 1):
                    idx_in = 4 * b1 + 2 * b2 + b3
                    idx_out = 4 * b2 + 2 * b1 + b3
                    P[idx_out, idx_in] = 1
        return P

    P12 = P12_matrix()
    J, Jp, D = 1.0, 0.4, 0.15
    H_A = dm_term(2, 3, D).to_matrix() + dm_term(3, 1, -D).to_matrix()
    H_B = (dm_term(1, 2, D * J) + dm_term(2, 3, D * Jp) + dm_term(3, 1, D * Jp)).to_matrix()
    comm_A = np.max(np.abs(P12 @ H_A @ P12.T - H_A))
    comm_B = np.max(np.abs(P12 @ H_B @ P12.T - H_B))
    print(f"    Opzione A: ||[P12,H_DM]|| = {comm_A:.3e}  (atteso ~0)")
    print(f"    Opzione B: ||[P12,H_DM]|| = {comm_B:.3e}  (atteso > 0)")
    assert comm_A < 1e-10, "Opzione A dovrebbe rispettare la simmetria P12"
    assert comm_B > 0.1, "Opzione B dovrebbe rompere la simmetria P12"

    print("[self-test DM 2] conservazione di S12^2")
    S12sq = S12_squared_operator().to_matrix()
    H0 = trimer_hamiltonian(J, Jp, 2.4).to_matrix()
    comm_A2 = np.linalg.norm((H0 + H_A) @ S12sq - S12sq @ (H0 + H_A))
    comm_B2 = np.linalg.norm((H0 + H_B) @ S12sq - S12sq @ (H0 + H_B))
    print(f"    Opzione A: ||[H,S12^2]|| = {comm_A2:.3e}  (atteso ~0)")
    print(f"    Opzione B: ||[H,S12^2]|| = {comm_B2:.3e}  (atteso > 0)")
    assert comm_A2 < 1e-10
    assert comm_B2 > 0.1

    print("[self-test DM 3] gap vero (minimo su b, non a b_c fisso)")
    gap_A, bmin_A = dm_min_gap(J, Jp, "A", D)
    gap_B, bmin_B = dm_min_gap(J, Jp, "B", D)
    print(f"    Opzione A: gap={gap_A:.2e} a b={bmin_A:.4f}  (atteso ~0: incrocio vero)")
    print(f"    Opzione B: gap={gap_B:.4f} a b={bmin_B:.4f}  (atteso ~0.25)")
    assert gap_A < 1e-5, "Opzione A non dovrebbe aprire il gap"
    assert 0.20 < gap_B < 0.30, "gap Opzione B fuori dal range atteso"

    print("[self-test DM 4] mode=None ripristina l'Hamiltoniana base")
    diff = (trimer_hamiltonian_dm(J, Jp, 1.5, None, 0.3).to_matrix()
            - trimer_hamiltonian(J, Jp, 1.5).to_matrix())
    print(f"    max|H_dm(mode=None) - H_base| = {np.max(np.abs(diff)):.3e}")
    assert np.max(np.abs(diff)) < 1e-14

    print("[self-test DM 5] exact_sweep_dm e ground_state_projector_dm coerenti")
    b_test = np.array([1.0, 2.4, 3.5])
    res = exact_sweep_dm(b_test, J, Jp, "B", D)
    for i, b in enumerate(b_test):
        P, E0, deg = ground_state_projector_dm(J, Jp, b, "B", D)
        err_E = abs(E0 - res["gs_energy"][i])
        assert err_E < 1e-10, f"energia proiettore/sweep incoerente a b={b}"
    print(f"    coerenza energia proiettore <-> sweep: OK su {len(b_test)} punti")

    print("=" * 70)
    print("[self-test DM] TUTTI I TEST SUPERATI")
    print("=" * 70)


# ----------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------

def _self_test():
    rng = np.random.default_rng(0)
    print("=" * 70)
    print("[self-test 1] spettro numerico vs formule analitiche (random)")
    max_err_spec = 0.0
    for _ in range(30):
        J, Jp, b = rng.uniform(-2, 2, 3)
        H = trimer_hamiltonian(J, Jp, b).to_matrix()
        w_num = np.sort(np.linalg.eigvalsh(H))
        w_ana = analytic_eigenvalues(J, Jp, b)
        max_err_spec = max(max_err_spec, np.max(np.abs(w_num - w_ana)))
    print(f"    max|E_num - E_analitico| su 30 punti casuali = {max_err_spec:.3e}")
    assert max_err_spec < 1e-10, "spettro numerico non coincide con l'analitico"

    print("[self-test 2] gli 8 stati di Kambe sono autostati esatti di H")
    print("               (verificati contro l'operatore Qiskit, non a mano)")
    states = kambe_states()
    J, Jp, b = 1.3, -0.7, 0.9   # punto casuale, nessuna simmetria accidentale
    H = trimer_hamiltonian(J, Jp, b).to_matrix()
    max_err_norm = max_err_E = max_resid = 0.0
    for (block, M), psi in states.items():
        norm = np.real(psi.conj() @ psi)
        Hpsi = H @ psi
        E_num = np.real(psi.conj() @ Hpsi)
        E_teo = kambe_energy(J, Jp, b, block, M)
        resid = np.linalg.norm(Hpsi - E_teo * psi)
        max_err_norm = max(max_err_norm, abs(norm - 1))
        max_err_E = max(max_err_E, abs(E_num - E_teo))
        max_resid = max(max_resid, resid)
    print(f"    max|norma-1|             = {max_err_norm:.3e}")
    print(f"    max|E_num - E_teorico|   = {max_err_E:.3e}")
    print(f"    max||H|psi> - E|psi>||   = {max_resid:.3e}  (autostato esatto)")
    assert max_err_norm < 1e-12 and max_err_E < 1e-10 and max_resid < 1e-10

    print("[self-test 3] ortonormalita' reciproca degli 8 stati di Kambe")
    V = np.array(list(states.values())).T
    Gram = V.conj().T @ V
    off_diag = np.max(np.abs(Gram - np.eye(8)))
    print(f"    max|Gram - I| = {off_diag:.3e}")
    assert off_diag < 1e-12

    print("[self-test 4] numeri quantici S12^2, S^2, Mz sugli stati di Kambe")
    S12sq_op = S12_squared_operator().to_matrix()
    Stotsq_op = S_total_squared_operator().to_matrix()
    Mz_op = magnetization_operator().to_matrix()
    S12sq_atteso = {"A": 2.0, "B": 2.0, "C": 0.0}
    Stotsq_atteso = {"A": 3.75, "B": 0.75, "C": 0.75}
    max_err_qn = 0.0
    for (block, M), psi in states.items():
        s12 = np.real(psi.conj() @ S12sq_op @ psi)
        stot = np.real(psi.conj() @ Stotsq_op @ psi)
        mz = np.real(psi.conj() @ Mz_op @ psi)
        max_err_qn = max(max_err_qn,
                          abs(s12 - S12sq_atteso[block]),
                          abs(stot - Stotsq_atteso[block]),
                          abs(mz - M))
    print(f"    max errore numeri quantici (S12^2, S^2, Mz) = {max_err_qn:.3e}")
    assert max_err_qn < 1e-10

    print("[self-test 5] proiettore sul fondamentale: traccia = degenerazione")
    for (J, Jp, b) in [(1.0, 0.4, 0.5), (1.0, 0.4, 3.0), (1.0, 1.0, 0.3)]:
        P, E0, deg = ground_state_projector(J, Jp, b)
        tr_err = abs(np.trace(P).real - deg)
        idem_err = np.max(np.abs(P @ P - P))
        print(f"    (J,J',b)=({J},{Jp},{b}): deg={deg}, "
              f"|tr(P)-deg|={tr_err:.2e}, |P^2-P|={idem_err:.2e}")
        assert tr_err < 1e-10 and idem_err < 1e-10

    print("[self-test 6] <Mz> a b=0 (fondamentale degenere): media sul sottospazio, non un singolo autovettore")
    for (J, Jp, label) in [(1.0, 0.4, "regione C"), (1.0, 1.6, "regione B")]:
        res0 = exact_sweep(np.array([0.0, 1e-6, 1e-3]), J=J, Jp=Jp)
        print(f"    {label} (J={J}, J'={Jp}):")
        print(f"      <Mz>(b=0)     = {res0['gs_mz'][0]:+.6f}  (atteso 0: media fra M=+1/2 e M=-1/2 degeneri)")
        print(f"      <Mz>(b=1e-6)  = {res0['gs_mz'][1]:+.6f}  (atteso -0.5: degenerazione gia' rotta)")
        assert abs(res0['gs_mz'][0]) < 1e-10
        assert abs(res0['gs_mz'][1] + 0.5) < 1e-6

    print("=" * 70)
    print("[self-test] TUTTI I TEST SUPERATI A PRECISIONE MACCHINA")
    print("=" * 70)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    _self_test()
    _self_test_dm()

    # punto di lavoro proposto (in attesa di conferma dal relatore): regione C
    J, Jp = 1.0, 0.4
    bc = critical_field(J, Jp)
    print(f"\nPunto di lavoro J={J}, J'={Jp}: b_c = {bc}")

    b = np.linspace(0.0, 4.0, 400)
    res = exact_sweep(b, J=J, Jp=Jp)

    # colora il ground state per blocco, via S12^2 (0=C, 2=A/B) e S^2 (3.75=A)
    block_color = np.where(res["gs_S12sq"] < 1.0, "tab:green",           # C
                    np.where(res["gs_Stotsq"] > 2.0, "tab:orange",       # A
                             "tab:blue"))                                 # B

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    for k in range(8):
        ax1.plot(b / J, res["energies"][:, k], color="0.75", lw=1)
    for i in range(len(b) - 1):
        ax1.plot(b[i:i + 2] / J, res["gs_energy"][i:i + 2],
                  color=block_color[i], lw=2.5)
    ax1.axvline(bc / J, color="0.4", ls=":", lw=1)
    ax1.set_xlabel("b / J"); ax1.set_ylabel("Energia / J")
    ax1.set_title("Spettro del trimero isoscele (colore = blocco del GS)")

    ax2.plot(b[1:] / J, res["gs_mz"][1:], "k", lw=2)
    ax2.plot([0], [res["gs_mz"][0]], "o", mfc="white", mec="0.3", ms=7, zorder=5)
    ax2.annotate(
        "b=0: fondamentale degenere\n(convenzione: media sul\nsottospazio, non un limite)",
        xy=(0, res["gs_mz"][0]), xytext=(0.55, -0.12),
        fontsize=8.5, color="0.35",
        arrowprops=dict(arrowstyle="->", color="0.5", lw=0.8),
    )
    ax2.axvline(bc / J, color="0.4", ls=":", lw=1)
    ax2.annotate(
        "incrocio vero (fisico)\nsalto discontinuo di <Mz>",
        xy=(bc / J, (res["gs_mz"][np.searchsorted(b, bc) - 1]
                     + res["gs_mz"][np.searchsorted(b, bc)]) / 2),
        xytext=(bc / J + 0.25, -1.05),
        fontsize=8.5, color="0.35",
        arrowprops=dict(arrowstyle="->", color="0.5", lw=0.8),
    )
    ax2.set_ylim(top=0.25)
    ax2.set_xlabel("b / J"); ax2.set_ylabel(r"$\langle M_z \rangle$")
    ax2.set_title("Magnetizzazione del ground state")

    fig.tight_layout()
    fig.savefig("trimer_ring_exact.png", dpi=150)
    print("[ok] figura salvata: trimer_ring_exact.png")
