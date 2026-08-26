"""
Benchmark esatto per il trimero di spin-1/2 (N=3), catena aperta uniforme.

    H = J (sigma1.sigma2 + sigma2.sigma3) + b (Z1+Z2+Z3)

Solo i legami (1,2) e (2,3): nessun termine sigma3.sigma1 (topologia a
catena, non anello -- vincolo esplicito del relatore). La simmetria di
riflessione P13 (scambio dei siti 1,3 attorno al sito centrale 2) rende
conservato S13^2 = (s1+s3)^2 oltre a S^2, Sz (decomposizione di Kambe,
stessa tecnica dell'anello ma applicata alla coppia NON legata 1,3) -> tre
multipletti:

    A': S13=1, S=3/2   E_A = 2J    (4 stati, M=+-3/2,+-1/2)
    B': S13=1, S=1/2   E_B = -4J   (2 stati, M=+-1/2)
    C': S13=0, S=1/2   E_C = 0     (2 stati, M=+-1/2)

con E(S13,S,M) = E_blocco + 2 b M. Niente frustrazione (nessun ciclo):
per J>0 il fondamentale a b=0 e' B', campo critico b_c=3J (incrocio vero,
non anticrossing); per J<=0 il fondamentale e' gia' A' a b=0, nessun
incrocio. Vedi teoria_trimero_catena_aperta.pdf per la derivazione
completa e derivazione_stati_kambe_trimero_catena.pdf per gli otto stati
espliciti.

Convenzione sito<->qubit (Qiskit, little-endian): site1->qubit2, site2->
qubit1, site3->qubit0 -- Famiglia 1, stessa di dimer_exact.py e
trimer_ring_exact.py (vedi convenzioni_qubit_progetto.pdf, Parte 2). Con
questa scelta la label Pauli letta da sinistra a destra e' "site1 site2
site3", nello stesso ordine della notazione fisica |q1 q2 q3> usata nella
derivazione (derivazione_stati_kambe_trimero_catena.pdf) e dello stesso
ordine kron(site1,site2,site3) usato li' per costruire gli otto stati di
Kambe a mano. Nessuna reindicizzazione e' quindi necessaria tra le due
rappresentazioni; il self-test sotto lo verifica esplicitamente
applicando l'operatore Qiskit ai vettori di Kambe costruiti "a mano".

Sorgente unica: lo stesso SparsePauliOp alimentera' sia questo benchmark
sia il futuro VQE (Fase 4), come gia' fatto per dimero e anello.

Termine DM (Dzyaloshinskii-Moriya): a differenza dell'anello, qui c'e' un
solo grado di liberta' DM compatibile con la simmetria P13 (D12=-D23,
nessuna ambiguita' di scelta come le opzioni A/B dell'anello, perche' il
legame (3,1) non esiste proprio). Sezione inclusa per completezza
strutturale ma NON richiesta dal relatore per la catena allo stato
attuale (vedi domande_relatore.md): non usata da exact_sweep ne' dal
futuro VQE finche' non viene esplicitamente richiesta.
"""

import numpy as np
from qiskit.quantum_info import SparsePauliOp


# ----------------------------------------------------------------------
# Hamiltoniana e operatori
# ----------------------------------------------------------------------

def trimer_hamiltonian(J, b):
    """H(J, b) come SparsePauliOp, topologia catena aperta uniforme.

    Label a 3 caratteri, ordine "site1 site2 site3" (vedi convenzione
    sopra). Solo i bond (1,2) e (2,3): nessuna label per sigma3.sigma1.
    """
    labels = [
        # sigma1.sigma2 (bond esistente)
        "XXI", "YYI", "ZZI",
        # sigma2.sigma3 (bond esistente)
        "IXX", "IYY", "IZZ",
        # Zeeman
        "ZII", "IZI", "IIZ",
    ]
    coeffs = [J, J, J, J, J, J, b, b, b]
    return SparsePauliOp(labels, coeffs)


def magnetization_operator():
    """Mz = (Z1+Z2+Z3)/2, convenzione di spin (s=sigma/2)."""
    return SparsePauliOp(["ZII", "IZI", "IIZ"], [0.5, 0.5, 0.5])


def S13_squared_operator():
    """Casimir della coppia di classificazione (non legata): S13^2 =
    (3/2) I + (1/2) sigma1.sigma3.

    Autovalori attesi: 0 (blocco C', S13=0), 2 (blocchi A'/B', S13=1).
    Nota: sigma1.sigma3 non compare in H (nessun bond fisico 1-3), ma e'
    comunque un operatore ben definito, usato qui solo come etichetta di
    classificazione -- si veda teoria_trimero_catena_aperta.pdf, sez. 5.
    """
    labels = ["III", "XIX", "YIY", "ZIZ"]
    coeffs = [1.5, 0.5, 0.5, 0.5]
    return SparsePauliOp(labels, coeffs)


def S_total_squared_operator():
    """Casimir totale: S^2 = (9/4) I + (1/2)(s1.s2 + s2.s3 + s3.s1 pauli).

    Autovalori attesi: 15/4 (blocco A', S=3/2), 3/4 (blocchi B'/C', S=1/2).
    Include anche sigma3.sigma1 (che non e' in H): S^2 e' lo spin totale
    del sistema fisico, indipendente da quali bond siano effettivamente
    accesi nell'Hamiltoniana.
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

def analytic_eigenvalues(J, b):
    """Le 8 energie esatte E(S13,S,M) = E_blocco + 2bM, ordinate."""
    E_A, E_B, E_C = 2 * J, -4 * J, 0.0
    M_A = [1.5, 0.5, -0.5, -1.5]
    M_BC = [0.5, -0.5]
    energies = (
        [E_A + 2 * b * M for M in M_A]
        + [E_B + 2 * b * M for M in M_BC]
        + [E_C + 2 * b * M for M in M_BC]
    )
    return np.sort(energies)


def critical_field(J):
    """b_c dell'incrocio fondamentale.

    J>0: fondamentale a b=0 e' B' (E_B=-4J < E_A=2J < E_C=0), incrocio
         con A' a b_c=3J (derivazione in teoria_trimero_catena_aperta.pdf,
         sez. 6.1).
    J<=0: fondamentale e' gia' A' a b=0 (nessuna frustrazione possibile,
         niente cicli nella catena), nessun incrocio -> ritorna None.
    """
    if J > 0:
        return 3.0 * J
    return None


# ----------------------------------------------------------------------
# Stati di Kambe espliciti (base computazionale |q1 q2 q3>)
# derivati in derivazione_stati_kambe_trimero_catena.pdf
# ----------------------------------------------------------------------

def _basis_ket(*bits):
    v = np.zeros(8, dtype=complex)
    idx = int("".join(str(bit) for bit in bits), 2)
    v[idx] = 1.0
    return v


def kambe_states():
    """Dizionario {(blocco, M): vettore a 8 componenti}.

    Convenzione qubit |0>=up (Z=+1), |1>=down (Z=-1), stessa del resto
    del progetto. Formule derivate per composizione dei momenti angolari
    con la coppia di classificazione (1,3), poi riordinate nel registro
    fisico |q1 q2 q3> (vedi PDF di derivazione, sez. 2-4), verificate a
    precisione macchina.
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
        ("B", 0.5):  (k100 + k001) / r6 - np.sqrt(2 / 3) * k010,
        ("B", -0.5): (k011 + k110) / r6 - np.sqrt(2 / 3) * k101,
        ("C", 0.5):  (k001 - k100) / r2,
        ("C", -0.5): (k011 - k110) / r2,
    }


def kambe_energy(J, b, block, M):
    """Energia analitica del singolo stato (blocco, M)."""
    E_blocco = {"A": 2 * J, "B": -4 * J, "C": 0.0}[block]
    return E_blocco + 2 * b * M


# ----------------------------------------------------------------------
# Diagonalizzazione esatta su griglia
# ----------------------------------------------------------------------

def exact_sweep(b_values, J=1.0):
    """Diagonalizza H su una griglia di campo b.

    Ritorna un dict con:
      energies       (n_b, 8)  tutti gli autovalori ordinati
      gs_energy      (n_b,)    energia del ground state
      gs_state       (n_b, 8)  autovettore del ground state (arbitrario se degenere)
      gs_mz          (n_b,)    magnetizzazione <Mz> sul ground state -- MEDIATA
                                sul sottospazio degenere quando presente (vedi nota)
      gs_S13sq       (n_b,)    <S13^2> sul ground state (tag di blocco)
      gs_Stotsq      (n_b,)    <S^2> sul ground state (tag di blocco)

    Nota sulla degenerazione. Nei punti in cui il fondamentale e' degenere
    (es. b=0 nel regime J>0, blocco B' con M=+-1/2 alla stessa energia),
    un singolo autovettore restituito da np.linalg.eigh e' una scelta di
    base ARBITRARIA all'interno del sottospazio degenere: il valore di
    <Mz> su un singolo autovettore puo' dipendere da quella scelta e non
    riflette il limite fisico. Qui <Mz> viene invece calcolato come media
    sul sottospazio degenere (traccia di Mz sul proiettore, diviso per la
    degenerazione): a b=0 questo da' correttamente 0 (nessuna direzione
    di M privilegiata), continuo con il limite b->0 da entrambi i lati
    (M=+1/2 e M=-1/2 pesano ugualmente all'esatta degenerazione).
    """
    Mz = magnetization_operator().to_matrix()
    S13sq = S13_squared_operator().to_matrix()
    Stotsq = S_total_squared_operator().to_matrix()

    energies, gs_energy, gs_state = [], [], []
    gs_mz, gs_S13sq, gs_Stotsq = [], [], []

    for b in b_values:
        H = trimer_hamiltonian(J, b).to_matrix()
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
        gs_S13sq.append(np.real(np.trace(P0 @ S13sq)) / deg)
        gs_Stotsq.append(np.real(np.trace(P0 @ Stotsq)) / deg)

    return {
        "b": np.asarray(b_values),
        "energies": np.asarray(energies),
        "gs_energy": np.asarray(gs_energy),
        "gs_state": np.asarray(gs_state),
        "gs_mz": np.asarray(gs_mz),
        "gs_S13sq": np.asarray(gs_S13sq),
        "gs_Stotsq": np.asarray(gs_Stotsq),
    }


def ground_state_projector(J, b, tol=1e-9):
    """Proiettore sul multipletto fondamentale (eventualmente degenere).

    Serve per definire la fidelity F = <psi|P0|psi> nel futuro VQE (Fase
    4), dato che il fondamentale e' quasi ovunque doppiamente degenere
    (blocchi B' o A' a M fissato non lo sono, ma B' stesso ha M=+-1/2
    degenere a b=0).
    """
    H = trimer_hamiltonian(J, b).to_matrix()
    w, v = np.linalg.eigh(H)
    degenerate = np.abs(w - w[0]) < tol
    V0 = v[:, degenerate]
    return V0 @ V0.conj().T, w[0], int(degenerate.sum())


# ----------------------------------------------------------------------
# Termine DM (Dzyaloshinskii-Moriya) -- Fase 5, quantificato
# ----------------------------------------------------------------------
#
# Unica combinazione compatibile con P13 (STRUTTURALMENTE analoga
# all'Opzione A dell'anello -- conserva S13^2 esattamente -- ma qui e'
# l'UNICA scelta possibile, non una fra due): D12 = -D23 = D'. Nessun
# bond (3,1) esiste, quindi nessuna combinazione "tipo Opzione B" e'
# nemmeno definibile per questa topologia.
#
# ATTENZIONE: l'analogia con l'Opzione A dell'anello e' SOLO strutturale,
# non di esito. Sull'anello, l'Opzione A non apre MAI il gap (l'incrocio
# e' C -> A, settori S12 DIVERSI, protetti da von Neumann-Wigner). Qui il
# gap SI APRE (g_min = 2*sqrt(6)*D, verificato), perche' l'incrocio della
# catena e' B -> A: ENTRAMBI con S13=1, stesso settore. Il Casimir
# conservato non li distingue, quindi non li protegge. Vedi
# analisi_dm_trimero_catena.tex per la derivazione completa.
#
# Assunto in autonomia (non richiesto esplicitamente dal relatore per la
# catena finora -- vedi domande_relatore.md), per coerenza con il lavoro
# gia' fatto sull'anello. Da segnalare nel prossimo report.

def dm_term(i, j, D):
    """D*(X_i Z_j - Z_i X_j), stessa forma gia' validata per dimero e anello."""
    pos = {1: 0, 2: 1, 3: 2}  # site1=carattere 0 (sinistra), ..., site3=carattere 2
    lab1, lab2 = ["I", "I", "I"], ["I", "I", "I"]
    lab1[pos[i]], lab1[pos[j]] = "X", "Z"
    lab2[pos[i]], lab2[pos[j]] = "Z", "X"
    return SparsePauliOp(["".join(lab1), "".join(lab2)], [D, -D])


def trimer_hamiltonian_dm(J, b, D):
    """H(J,b) + termine DM simmetrico sotto P13 (D12=-D23=D).

    D=0 -> identico a trimer_hamiltonian.
    """
    H = trimer_hamiltonian(J, b)
    if D == 0:
        return H
    return H + dm_term(1, 2, D) + dm_term(2, 3, -D)


def exact_sweep_dm(b_values, J, D):
    """Come exact_sweep, ma con H_dm al posto di H (D12=-D23=D).

    Serve come benchmark per il VQE quando il DM e' acceso (exact_sweep
    resta la forma chiusa pura, D=0, e non va toccata).

    A differenza del mirror diretto in trimer_ring_exact.py, <Mz> (e gli
    altri valori di aspettazione) sono mediati sul sottospazio degenere
    quando presente -- stessa correzione gia' applicata in exact_sweep
    (D=0) di questo file: a b=0 il fondamentale e' un doppietto di
    Kramers per QUALUNQUE D (scambio e DM sono entrambi T-pari), quindi
    un singolo autovettore di np.linalg.eigh sarebbe una scelta di base
    arbitraria all'interno del doppietto.

    NOTA: con D!=0, S13^2 non e' piu' un numero quantico buono in senso
    stretto (S13^2 resta conservato dal DM, ma l'incrocio B->A mescola
    stati con lo STESSO S13^2 -- vedi commento sopra dm_term) -- gs_S13sq
    resta comunque un valore di aspettativa utile per vedere quanto il
    fondamentale vero si allontana dal carattere di blocco puro.
    """
    Mz = magnetization_operator().to_matrix()
    S13sq = S13_squared_operator().to_matrix()
    Stotsq = S_total_squared_operator().to_matrix()

    energies, gs_energy, gs_state = [], [], []
    gs_mz, gs_S13sq, gs_Stotsq = [], [], []

    for b in b_values:
        H = trimer_hamiltonian_dm(J, b, D).to_matrix()
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
        gs_S13sq.append(np.real(np.trace(P0 @ S13sq)) / deg)
        gs_Stotsq.append(np.real(np.trace(P0 @ Stotsq)) / deg)

    return {
        "b": np.asarray(b_values),
        "energies": np.asarray(energies),
        "gs_energy": np.asarray(gs_energy),
        "gs_state": np.asarray(gs_state),
        "gs_mz": np.asarray(gs_mz),
        "gs_S13sq": np.asarray(gs_S13sq),
        "gs_Stotsq": np.asarray(gs_Stotsq),
    }


def ground_state_projector_dm(J, b, D, tol=1e-9):
    """Come ground_state_projector, ma con H_dm al posto di H."""
    H = trimer_hamiltonian_dm(J, b, D).to_matrix()
    w, v = np.linalg.eigh(H)
    degenerate = np.abs(w - w[0]) < tol
    V0 = v[:, degenerate]
    return V0 @ V0.conj().T, w[0], int(degenerate.sum())


def dm_min_gap(J, D, search_half_width=None):
    """Gap VERO fra i due autovalori piu' bassi: minimo su un INTORNO di b_c.

    Due errori metodologici da evitare, entrambi documentati per l'anello
    in analisi_dm_trimero_anello.tex (sez. "Il controllo corretto" e sez.
    "Una seconda trappola") e verificati esplicitamente anche per la
    catena in analisi_dm_trimero_catena.tex:

    1. NON calcolare il gap a b_c fisso: il punto di incrocio si sposta
       quando il DM e' acceso (qui pero' di pochissimo, vedi nota sotto),
       e un gap positivo misurato nel punto sbagliato non dice nulla
       sull'apertura reale.

    2. NON estendere la ricerca a tutto l'asse b, in particolare fino a
       b=0: a campo nullo H e' invariante per inversione temporale
       (scambio e DM sono entrambi T-pari; solo lo Zeeman e' T-dispari) e
       con un numero DISPARI di spin-1/2 il teorema di Kramers impone che
       ogni livello sia almeno doppiamente degenere. Il minimo cadrebbe
       sempre a b=0 con valore zero, per QUALUNQUE D, mascherando
       completamente l'apertura del gap all'incrocio.

    Nota specifica alla catena: qui il punto critico si sposta molto meno
    che nell'anello (b_min va da 3.0000007 a 3.0196 per D fino a 0.5,
    contro 2.40->2.43 dell'anello Opzione B), perche' il DM accoppia
    direttamente i due stati quasi-degeneri senza spostare al primo
    ordine i rami stessi -- verificato numericamente in
    analisi_dm_trimero_catena.tex.
    """
    from scipy.optimize import minimize_scalar

    bc = critical_field(J)
    if bc is None:
        raise ValueError("critical_field(J) e' None per J<=0: nessun incrocio")
    if search_half_width is None:
        search_half_width = max(1.0, abs(bc) * 0.6)

    def gap_func(b):
        H = trimer_hamiltonian_dm(J, b, D).to_matrix()
        w = np.linalg.eigvalsh(H)
        return w[1] - w[0]

    res = minimize_scalar(
        gap_func, bounds=(max(0.0, bc - search_half_width), bc + search_half_width),
        method="bounded", options={"xatol": 1e-12},
    )
    return res.fun, res.x



# ----------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------

def _P13_matrix():
    """Matrice 8x8 dello scambio dei qubit 1,3 (registro fisico, Famiglia
    1: site1=qubit2, site2=qubit1, site3=qubit0 -> nell'indice a 3 bit
    b1 b2 b3 (MSB=site1), lo scambio e' b1<->b3."""
    P = np.zeros((8, 8))
    for b1 in (0, 1):
        for b2 in (0, 1):
            for b3 in (0, 1):
                idx_in = 4 * b1 + 2 * b2 + b3
                idx_out = 4 * b3 + 2 * b2 + b1
                P[idx_out, idx_in] = 1
    return P


def _self_test():
    rng = np.random.default_rng(0)
    print("=" * 70)
    print("[self-test 1] spettro numerico vs formule analitiche (random)")
    max_err_spec = 0.0
    for _ in range(30):
        J, b = rng.uniform(-2, 2, 2)
        H = trimer_hamiltonian(J, b).to_matrix()
        w_num = np.sort(np.linalg.eigvalsh(H))
        w_ana = analytic_eigenvalues(J, b)
        max_err_spec = max(max_err_spec, np.max(np.abs(w_num - w_ana)))
    print(f"    max|E_num - E_analitico| su 30 punti casuali = {max_err_spec:.3e}")
    assert max_err_spec < 1e-10, "spettro numerico non coincide con l'analitico"

    print("[self-test 2] gli 8 stati di Kambe sono autostati esatti di H")
    print("               (verificati contro l'operatore Qiskit, non a mano)")
    states = kambe_states()
    J, b = 1.3, -0.7   # punto casuale, nessuna simmetria accidentale
    H = trimer_hamiltonian(J, b).to_matrix()
    max_err_norm = max_err_E = max_resid = 0.0
    for (block, M), psi in states.items():
        norm = np.real(psi.conj() @ psi)
        Hpsi = H @ psi
        E_num = np.real(psi.conj() @ Hpsi)
        E_teo = kambe_energy(J, b, block, M)
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

    print("[self-test 4] numeri quantici S13^2, S^2, Mz sugli stati di Kambe")
    S13sq_op = S13_squared_operator().to_matrix()
    Stotsq_op = S_total_squared_operator().to_matrix()
    Mz_op = magnetization_operator().to_matrix()
    S13sq_atteso = {"A": 2.0, "B": 2.0, "C": 0.0}
    Stotsq_atteso = {"A": 3.75, "B": 0.75, "C": 0.75}
    max_err_qn = 0.0
    for (block, M), psi in states.items():
        s13 = np.real(psi.conj() @ S13sq_op @ psi)
        stot = np.real(psi.conj() @ Stotsq_op @ psi)
        mz = np.real(psi.conj() @ Mz_op @ psi)
        max_err_qn = max(max_err_qn,
                          abs(s13 - S13sq_atteso[block]),
                          abs(stot - Stotsq_atteso[block]),
                          abs(mz - M))
    print(f"    max errore numeri quantici (S13^2, S^2, Mz) = {max_err_qn:.3e}")
    assert max_err_qn < 1e-10

    print("[self-test 5] simmetria P13: [P13,H]=0 (chain uniforme)")
    P13 = _P13_matrix()
    max_comm = 0.0
    for _ in range(20):
        J, b = rng.uniform(-2, 2, 2)
        H = trimer_hamiltonian(J, b).to_matrix()
        max_comm = max(max_comm, np.max(np.abs(P13 @ H - H @ P13)))
    print(f"    max||[P13,H]|| su 20 punti casuali = {max_comm:.3e}")
    assert max_comm < 1e-10, "P13 dovrebbe essere simmetria esatta per J12=J23"

    print("[self-test 6] proiettore sul fondamentale: traccia = degenerazione")
    for (J, b) in [(1.0, 0.5), (1.0, 3.0), (1.0, 0.0), (-1.0, 1.5)]:
        P, E0, deg = ground_state_projector(J, b)
        tr_err = abs(np.trace(P).real - deg)
        idem_err = np.max(np.abs(P @ P - P))
        print(f"    (J,b)=({J},{b}): deg={deg}, "
              f"|tr(P)-deg|={tr_err:.2e}, |P^2-P|={idem_err:.2e}")
        assert tr_err < 1e-10 and idem_err < 1e-10

    print("[self-test 7] campo critico: b_c=3J per J>0, nessun incrocio per J<=0")
    for J in [0.5, 1.0, 2.5]:
        bc = critical_field(J)
        b_scan = np.linspace(0, bc * 1.5, 3001)
        gs = np.array([np.linalg.eigvalsh(trimer_hamiltonian(J, b).to_matrix())[0]
                        for b in b_scan])
        d2 = np.diff(gs, 2)
        b_kink = b_scan[np.argmax(np.abs(d2)) + 1]
        print(f"    J={J}: b_c teorico={bc:.4f}, b_c numerico (curvatura max)={b_kink:.4f}")
        assert abs(b_kink - bc) < (b_scan[1] - b_scan[0]) * 2

    J = -1.0
    b_scan = np.linspace(0, 5, 2001)
    gs = np.array([np.linalg.eigvalsh(trimer_hamiltonian(J, b).to_matrix())[0]
                    for b in b_scan])
    curv = np.max(np.abs(np.diff(gs, 2)))
    print(f"    J={J}: curvatura massima ground state = {curv:.3e} (atteso ~0, nessun incrocio)")
    assert curv < 1e-8

    print("[self-test 8] <Mz> a b=0 (fondamentale degenere): media sul sottospazio, non un singolo autovettore")
    res0 = exact_sweep(np.array([0.0, 1e-6, 1e-3]), J=1.0)
    print(f"    <Mz>(b=0)     = {res0['gs_mz'][0]:+.6f}  (atteso 0: media fra M=+1/2 e M=-1/2 degeneri)")
    print(f"    <Mz>(b=1e-6)  = {res0['gs_mz'][1]:+.6f}  (atteso -0.5: degenerazione gia' rotta)")
    print(f"    <Mz>(b=1e-3)  = {res0['gs_mz'][2]:+.6f}  (atteso -0.5)")
    assert abs(res0['gs_mz'][0]) < 1e-10
    assert abs(res0['gs_mz'][1] + 0.5) < 1e-6
    assert abs(res0['gs_mz'][2] + 0.5) < 1e-6

    print("=" * 70)
    print("[self-test] TUTTI I TEST SUPERATI A PRECISIONE MACCHINA")
    print("=" * 70)


def _self_test_dm():
    """Verifica la simmetria P13 del termine DM simmetrico e la rottura
    quando D12 != -D23 (analogo diretto del self-test DM dell'anello)."""
    print("=" * 70)
    print("[self-test DM 1] simmetria P13 del termine DM")
    P13 = _P13_matrix()
    J_test, D = 1.0, 0.15

    H_sym = dm_term(1, 2, D).to_matrix() + dm_term(2, 3, -D).to_matrix()
    H_asym = dm_term(1, 2, D).to_matrix() + dm_term(2, 3, D).to_matrix()  # D12=D23, rompe P13
    comm_sym = np.max(np.abs(P13 @ H_sym @ P13.T - H_sym))
    comm_asym = np.max(np.abs(P13 @ H_asym @ P13.T - H_asym))
    print(f"    D12=-D23 (simmetrico): ||[P13,H_DM]|| = {comm_sym:.3e}  (atteso ~0)")
    print(f"    D12=+D23 (asimmetrico): ||[P13,H_DM]|| = {comm_asym:.3e}  (atteso > 0)")
    assert comm_sym < 1e-10, "D12=-D23 dovrebbe rispettare la simmetria P13"
    assert comm_asym > 0.1, "D12=D23 dovrebbe rompere la simmetria P13"

    print("[self-test DM 2] conservazione di S13^2 con DM simmetrico")
    S13sq = S13_squared_operator().to_matrix()
    bp = 2.4
    H0 = trimer_hamiltonian(J_test, bp).to_matrix()
    comm_S13 = np.linalg.norm((H0 + H_sym) @ S13sq - S13sq @ (H0 + H_sym))
    print(f"    ||[H+H_DM,S13^2]|| = {comm_S13:.3e}  (atteso ~0)")
    assert comm_S13 < 1e-10

    print("[self-test DM 3] D=0 ripristina l'Hamiltoniana base")
    diff = (trimer_hamiltonian_dm(J_test, 1.5, 0.0).to_matrix()
            - trimer_hamiltonian(J_test, 1.5).to_matrix())
    print(f"    max|H_dm(D=0) - H_base| = {np.max(np.abs(diff)):.3e}")
    assert np.max(np.abs(diff)) < 1e-14

    print("[self-test DM 4] exact_sweep_dm e ground_state_projector_dm coerenti")
    max_err_coerenza = 0.0
    for b_test, D_test in [(1.0, 0.1), (3.0, 0.15), (3.0, 0.5)]:
        res = exact_sweep_dm(np.array([b_test]), J_test, D_test)
        _, E0_proj, deg = ground_state_projector_dm(J_test, b_test, D_test)
        max_err_coeranza_b = abs(res["gs_energy"][0] - E0_proj)
        max_err_coerenza = max(max_err_coeranza_b, max_err_coeranza_b)
        print(f"    (b,D)=({b_test},{D_test}): E0 sweep={res['gs_energy'][0]:.10f}  "
              f"E0 projector={E0_proj:.10f}  deg={deg}  "
              f"|diff|={max_err_coeranza_b:.3e}")
    assert max_err_coeranza_b < 1e-10, "sweep e projector devono dare la stessa energia"

    print("[self-test DM 5] dm_min_gap: gap lineare in D, pendenza 2*sqrt(6)")
    attesa = 2 * np.sqrt(6)
    for D_test in [0.009, 0.05, 0.148]:
        gm, bm = dm_min_gap(J_test, D_test)
        ratio = gm / D_test
        print(f"    D={D_test:.3f}: g_min={gm:.6f}  b_min={bm:.6f}  "
              f"g_min/D={ratio:.4f}  (atteso ~{attesa:.4f})")
        assert abs(ratio - attesa) / attesa < 0.01, \
            "pendenza g_min/D deve avvicinarsi a 2*sqrt(6) per D piccolo"

    print("=" * 70)
    print("[self-test DM] TUTTI I TEST SUPERATI")
    print("=" * 70)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    _self_test()
    _self_test_dm()

    J = 1.0
    bc = critical_field(J)
    print(f"\nPunto J={J}: b_c = {bc}")

    b = np.linspace(0.0, 4.0, 400)
    res = exact_sweep(b, J=J)

    # colora il ground state per blocco, via S13^2 (0=C', 2=A'/B') e S^2 (3.75=A')
    block_color = np.where(res["gs_S13sq"] < 1.0, "tab:green",           # C'
                    np.where(res["gs_Stotsq"] > 2.0, "tab:orange",       # A'
                             "tab:blue"))                                 # B'

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    for k in range(8):
        ax1.plot(b / J, res["energies"][:, k], color="0.75", lw=1)
    for i in range(len(b) - 1):
        ax1.plot(b[i:i + 2] / J, res["gs_energy"][i:i + 2],
                  color=block_color[i], lw=2.5)
    ax1.axvline(bc / J, color="0.4", ls=":", lw=1)
    ax1.set_xlabel("b / J"); ax1.set_ylabel("Energia / J")
    ax1.set_title("Spettro del trimero a catena aperta (colore = blocco del GS)")

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
    fig.savefig("trimer_chain_exact.png", dpi=150)
    print("[ok] figura salvata: trimer_chain_exact.png")
