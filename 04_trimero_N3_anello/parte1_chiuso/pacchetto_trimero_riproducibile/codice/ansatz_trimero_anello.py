"""Famiglia di ansatz PMA-2q per il trimero ad anello: due blocchi a due
qubit intercambiabili (RBS, W), stessa struttura esterna (X sul qubit 0,
un blocco per ciascuno dei tre legami, eventuali strati di R_y locali).

RUOLO NELL'INSIEME DEL PACCHETTO: modulo mancante nella prima versione di
questo pacchetto -- vqe_w2q6_trimero_anello.py isola solo la
specializzazione a W (l'ansatz canonico usato per il VQE finale), ma il
confronto RBS-vs-W (Documento 2) richiede anche il blocco RBS, mai
isolato in un modulo separato. Qui i due blocchi e la factory condivisa
vivono insieme, cosi' il confronto si fa allo stesso livello di codice
(stessa pma_2q_trimer_exact, cambia solo l'argomento block).

Fonte: confronto_ansatz_entangler_trimero_anello.ipynb (stessa nota di
provenienza di vqe_w2q6_trimero_anello.py -- il codice vive nei notebook,
qui isolato in un modulo minimo).
"""
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector

BOND12, BOND23, BOND31 = (2, 1), (1, 0), (0, 2)
BONDS = [BOND12, BOND23, BOND31]


def rbs_block(qc, phi, q0, q1):
    """Blocco RBS (Reconfigurable Beam Splitter, rotazione di Givens
    reale): H su entrambi i qubit, CZ, R_y(phi)/R_y(-phi), CZ, H.

    Un SOLO parametro libero phi nonostante i due gate R_y -- il secondo
    usa -phi, lo stesso angolo con segno cambiato, non un angolo
    indipendente (verificato: il blocco costruito ha esattamente 1
    parametro, non 2).

    RUOLO NEL MODULO: alternativa a w_block nella factory
    pma_2q_trimer_exact. RUOLO NELL'INSIEME: da' RBS-2q quando passato
    come block -- genuinamente M-conservante su tutto lo spazio a due
    qubit (mai mescola |00>,|11> con |01>,|10>), a differenza di
    w_block sotto."""
    sub = QuantumCircuit(2, name="RBS")
    sub.h(0); sub.h(1)
    sub.cz(0, 1)
    sub.ry(phi, 0); sub.ry(-phi, 1)
    sub.cz(0, 1)
    sub.h(0); sub.h(1)
    qc.append(sub.to_gate(label="RBS"), [q0, q1])


def w_block(qc, theta, q0, q1):
    """Blocco W a 2 qubit (CX-RY-CX): building block dell'ansatz W-2q,
    identico a quello in vqe_w2q6_trimero_anello.py (duplicato qui per
    poter importare rbs_block e w_block dallo stesso modulo senza
    dipendenza circolare -- vqe_w2q6_trimero_anello.py resta la fonte
    canonica per l'ansatz usato nel VQE finale).

    ATTENZIONE al nome: questo NON e' il gate W_ij(theta)=e^{-i theta
    s_i.s_j} di Crippa et al. 2021 (quello e' R_xx(theta/2)R_yy(theta/2)
    R_zz(theta/2), genuinamente M-conservante su tutto lo spazio). Questo
    blocco, verificato esplicitamente, NON conserva M su tutto lo spazio
    a due qubit: applicato a |00> o |11> li mischia fra loro
    (|00> -> cos(theta/2)|00> + sin(theta/2)|11>); conserva M solo
    quando il suo ingresso e' gia' nel settore {|01>,|10>}. E' proprio
    questa capacita' di mescolare -- combinata con l'applicazione su
    legami sovrapposti nell'anello -- a spiegare perche' l'ansatz W-2q
    non ha bisogno di rami di preparazione diversi a seconda di b/J
    (verificato: W puro su tre legami diversi, senza R_y finali, da'
    gia' F=0.47; RBS nello stesso caso resta a F=0.001).

    RUOLO NEL MODULO: alternativa a rbs_block. RUOLO NELL'INSIEME: 2
    CNOT per legame, 6 CNOT totali per l'ansatz W-2q.6 -- meno gate di
    RBS-2q (che ne usa il doppio, per via delle Hadamard e delle due
    R_y indipendenti per blocco) e con fedelta' migliore sotto DM."""
    sub = QuantumCircuit(2, name="W")
    sub.cx(0, 1); sub.ry(theta, 0); sub.cx(0, 1)
    qc.append(sub.to_gate(label="W"), [q0, q1])


def pma_2q_trimer_exact(nparam, block):
    """Costruisce l'ansatz PMA-2q generico per il trimero (3 qubit): X
    sul qubit 0, poi un blocco per ciascuno dei tre legami, poi eventuali
    strati aggiuntivi di rotazioni locali R_y indipendenti se
    nparam > 3.

    RUOLO NEL MODULO: factory condivisa da rbs_block e w_block. RUOLO
    NELL'INSIEME: identica a quella in vqe_w2q6_trimero_anello.py
    (duplicata qui per le stesse ragioni di w_block sopra) -- con
    block=rbs_block da' RBS-2q.N, con block=w_block da' W-2q.N."""
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(3)
    qc.x(0)
    block(qc, p[0], *BOND12); block(qc, p[1], *BOND23); block(qc, p[2], *BOND31)
    i = 3
    while i < nparam:
        qc.ry(p[i], 0); qc.ry(p[i + 1], 1); qc.ry(p[i + 2], 2)
        i += 3
    return qc


def rbs2q_circuit(nparam=6):
    """Specializzazione a RBS: RBS-2q.6 (6 parametri, 3 blocchi RBS + 3
    R_y locali) -- l'alternativa a w2q6_circuit() confrontata nel
    Documento 2. Con nparam=3: RBS-2q "puro" (nessun R_y finale), usato
    per il tetto strutturale."""
    return pma_2q_trimer_exact(nparam, rbs_block)


def w2q_circuit_locale(nparam=6):
    """Specializzazione a W, EQUIVALENTE a w2q6_circuit() di
    vqe_w2q6_trimero_anello.py (stessa costruzione, stesso block) --
    fornita qui solo per simmetria di interfaccia col confronto RBS-vs-W
    a diversi nparam (es. il tetto strutturale con nparam=3). Per il VQE
    finale usare sempre w2q6_circuit() dal suo modulo originale, non
    questa."""
    return pma_2q_trimer_exact(nparam, w_block)
