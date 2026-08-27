"""Quantum simulation del trimero a catena aperta: exp(-iHt) via Suzuki-Trotter.

Sorgente unica per l'Hamiltoniana: trimer_chain_exact.py. Convenzione Pauli
DIRETTA (non spin s=sigma/2), Famiglia 1 per il mapping sito<->qubit:
site1 -> qubit2, site2 -> qubit1, site3 -> qubit0.

    H = b*Sz_tot + H_ex + H_DM
    H_ex = J (sigma1.sigma2 + sigma2.sigma3)          [due bond, nessun (3,1)]
    H_DM = D (X1Z2 - Z1X2) - D (X2Z3 - Z2X3)          [D12 = -D23 = D, fissato da P13]

DIFFERENZE DI CONVENZIONE DA trotter_trimero_anello.py (da non confondere):
  1. L'anello ha tre bond con due accoppiamenti (J, J'); qui due bond con un
     solo J.
  2. L'anello scala il DM con l'accoppiamento del bond (D_ij = D * J_ij); qui
     D e' ASSOLUTO (D_12 = +D, D_23 = -D), perche' e' cosi' che lo definisce
     trimer_chain_exact.py::dm_term / trimer_hamiltonian_dm. Usare la
     convenzione dell'anello qui farebbe divergere circuito e benchmark
     esatto di un fattore J.
  3. L'anello ha due opzioni DM (A/B); qui la simmetria P13 ne lascia una sola.

NORMA DI MATRICE. Ovunque in questo file e nella documentazione associata,
||M|| e' la norma di FROBENIUS, cioe' numpy.linalg.norm(M) senza argomento
`ord`. Stessa convenzione gia' in uso nei self-test di
trotter_trimero_anello.py e dei moduli esatti. Dichiarata qui esplicitamente
perche' i valori numerici riportati nei commenti e nel log non sono
confrontabili con una norma spettrale.

-----------------------------------------------------------------------
STRUTTURA A TRE LIVELLI E ORIGINE DELL'ERRORE
-----------------------------------------------------------------------
Livello 0 -- ESATTO. Il campo e lo scambio si fattorizzano senza errore:

    exp(-i tau (b Sz_tot + H_ex)) = exp(-i tau b Sz_tot) exp(-i tau H_ex)

e questo VALE PERCHE' [Sz_tot, H_ex] = 0 (verificato bond per bond:
||[Sz_tot,h12]|| = ||[Sz_tot,h23]|| = 0 esattamente). Nient'altro.

  ATTENZIONE, errore da non rifare: [Sz_tot, H_ex] = 0 NON implica in alcun
  modo [H_ex, H_DM] = 0 -- sono condizioni logicamente indipendenti. Per la
  catena a J=1, b=0.7, D=0.3 si misura ||[H_ex,H_DM]|| = 10.182337 contro
  ||[Sz_tot,H_DM]|| = 3.394112: H_ex e' il contributo DOMINANTE al mancato
  annullamento, circa il triplo del campo. L'esattezza del livello 0
  riguarda la coppia (campo, scambio) e si ferma li'.

L'errore Trotter di questo circuito NON viene quindi da un ipotetico
splitting esterno a due blocchi "H0 esatto contro H_DM": viene dagli
splitting interni annidati, livello 1 e livello 2, piu' i termini incrociati
fra i tre blocchi applicati in sequenza.

Livello 1 -- H_ex spezzato sui due bond, che condividono il sito 2:

    [sigma1.sigma2, sigma2.sigma3] = -2i chi,   chi = sigma1.(sigma2 x sigma3)

(identita' esatta, residuo 0.0 in norma di Frobenius). Per BCH, con i bond
applicati nell'ordine (1,2) poi (2,3):

    exp(-i tau J h23) exp(-i tau J h12) = exp(-i tau [H_ex + tau J^2 chi] + O(tau^3))

Il SEGNO dipende dall'ordine: invertendo i bond il termine chirale cambia
segno (verificato, s = +1.000 / -1.000). Da qui l'opzione `alternate` sotto.

Livello 2 -- H_DM spezzato sui due bond, stesso motivo:

    [d12, -d23] = -2i Theta,   Theta = X1 Y2 Z3 - Z1 Y2 X3

Theta e' hermitiano e dispari sotto P13. NON e' proporzionale a chi: i due
livelli generano strutture d'errore indipendenti, il livello 2 non e'
assorbibile in una ridefinizione del livello 1.

-----------------------------------------------------------------------
SCELTA DELLO STATO INIZIALE NEI TEST DI CONVERGENZA
-----------------------------------------------------------------------
|000> e' un pessimo stato di prova per l'errore di livello 1: e' autostato
di OGNI bond separatamente (h_ij |00> = +|00> su ciascun bond, verificato:
||h12|000> - |000>|| = ||h23|000> - |000>|| = 0), quindi tutti i fattori
Trotter di H_ex agiscono su di esso come semplici fasi e commutano. Un test
di convergenza su |000> a D=0 restituisce infedelta' ~1e-14 (precisione
macchina) per QUALUNQUE N e non misura nulla del livello 1. I self-test di
convergenza qui sotto usano quindi |010> e uno stato random.

-----------------------------------------------------------------------
ALTERNANZA DELL'ORDINE DEI BOND (`alternate=True`)
-----------------------------------------------------------------------
Poiche' il termine chirale di livello 1 cambia segno con l'ordine dei bond,
alternare (1,2)->(2,3) e (2,3)->(1,2) su passi consecutivi lo cancella al
leading order, A PARITA' ESATTA DI GATE.

Guadagno misurato (stato random, t=2, N=80):
  - D = 0   : errore da O(1/N^2) a O(1/N^4). Rapporti misurati x4.0 (fisso)
              contro x16.0 (alternato) per raddoppio di N. Guadagno 34x a
              N=80 e crescente come N^2.
  - D = 0.3 : guadagno REALE ma PARZIALE (5.7x a N=80) e destinato a
              saturare. L'alternanza cancella solo il termine chirale di
              livello 1; il livello 2 e i termini incrociati H_ex/H_DM,
              Sz_tot/H_DM restano O(1/N^2) e tornano a dominare per N
              grande. Non spacciare il risultato a D=0 come valido in
              generale.
Rilevante per la Parte 2: stesso numero di canali di rumore, meno passi per
una data accuratezza -- soprattutto nel regime a DM debole.
"""
import numpy as np
import scipy.linalg as sla
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Operator, Pauli

from trimer_chain_exact import trimer_hamiltonian, trimer_hamiltonian_dm

# --- convenzione sito <-> qubit, identica a trimer_chain_exact.py ---
Q = {1: 2, 2: 1, 3: 0}
BONDS = [(1, 2), (2, 3)]          # ordine "diretto" di applicazione
POS = {1: 0, 2: 1, 3: 2}          # sito -> carattere nella label Pauli

PSI0 = Statevector.from_label("000")


def _sign_dm(bond):
    """D12 = +D, D23 = -D (simmetria P13). Convenzione di trimer_chain_exact."""
    return +1.0 if bond == (1, 2) else -1.0


# ----------------------------------------------------------------------
# blocchi di circuito
# ----------------------------------------------------------------------
def step_field(qc, b, tau):
    """exp(-i tau b Sz_tot). ESATTO rispetto a H_ex ([Sz_tot,H_ex]=0)."""
    for site in (1, 2, 3):
        qc.rz(2 * b * tau, Q[site])


def step_Hex(qc, J, tau, bonds=None):
    """Livello 1: Trotter di 1o ordine per H_ex sui due bond."""
    for (i, j) in (bonds or BONDS):
        qi, qj = Q[i], Q[j]
        qc.rxx(2 * J * tau, qi, qj)
        qc.ryy(2 * J * tau, qi, qj)
        qc.rzz(2 * J * tau, qi, qj)


def step_HDM(qc, D, tau, bonds=None):
    """Livello 2: Trotter di 1o ordine per H_DM sui due bond.

    D e' assoluto (non scalato per J): D_ij = _sign_dm(bond) * D.
    """
    for (i, j) in (bonds or BONDS):
        Dij = _sign_dm((i, j)) * D
        qi, qj = Q[i], Q[j]
        qc.h(qi); qc.rzz(2 * Dij * tau, qi, qj); qc.h(qi)     # exp(-i tau Dij Xi Zj)
        qc.h(qj); qc.rzz(-2 * Dij * tau, qi, qj); qc.h(qj)    # exp(+i tau Dij Zi Xj)


def trotter_circuit(J, b, D, t, N, measure=False, alternate=False):
    """N passi, ordine per passo: H_ex -> campo -> H_DM.

    alternate=True inverte l'ordine dei bond nei passi dispari, cancellando
    al leading order il termine chirale di livello 1 senza gate aggiuntivi.
    """
    qc = QuantumCircuit(3, 3) if measure else QuantumCircuit(3)
    tau = t / N
    for k in range(N):
        bonds = BONDS if (not alternate or k % 2 == 0) else BONDS[::-1]
        step_Hex(qc, J, tau, bonds)
        step_field(qc, b, tau)
        step_HDM(qc, D, tau, bonds)
        qc.barrier()
    if measure:
        qc.measure([0, 1, 2], [0, 1, 2])
    return qc


# ----------------------------------------------------------------------
# riferimenti a matrice
# ----------------------------------------------------------------------
def _P(label):
    return Pauli(label).to_matrix()


def bond_exchange_matrix(i, j):
    M = np.zeros((8, 8), dtype=complex)
    for A in "XYZ":
        c = ["I", "I", "I"]
        c[POS[i]] = c[POS[j]] = A
        M += _P("".join(c))
    return M


def bond_dm_matrix(i, j):
    c1, c2 = ["I", "I", "I"], ["I", "I", "I"]
    c1[POS[i]], c1[POS[j]] = "X", "Z"
    c2[POS[i]], c2[POS[j]] = "Z", "X"
    return _P("".join(c1)) - _P("".join(c2))


def chi_operator():
    """Chiralita' scalare di spin sigma1.(sigma2 x sigma3), hermitiana."""
    eps = {("X", "Y", "Z"): 1, ("Y", "Z", "X"): 1, ("Z", "X", "Y"): 1,
           ("X", "Z", "Y"): -1, ("Z", "Y", "X"): -1, ("Y", "X", "Z"): -1}
    return sum(s * _P(a + b + c) for (a, b, c), s in eps.items())


def theta_operator():
    """Theta = X1 Y2 Z3 - Z1 Y2 X3, generatore dell'errore di livello 2."""
    return _P("XYZ") - _P("ZYX")


def sz_tot_matrix():
    return sum(_P("".join("Z" if k == s - 1 else "I" for k in range(3)))
               for s in (1, 2, 3))


def H_parts(J, b, D):
    """(H0, H_DM) come matrici 8x8, H0 = b*Sz_tot + H_ex."""
    H0 = trimer_hamiltonian(J, b).to_matrix()
    H_full = trimer_hamiltonian_dm(J, b, D).to_matrix()
    return H0, H_full - H0


def U_exact(J, b, D, t):
    H0, H_DM = H_parts(J, b, D)
    return sla.expm(-1j * (H0 + H_DM) * t)


# ----------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------
def _self_test():
    rng = np.random.default_rng(0)
    SZ = sz_tot_matrix()
    h12, h23 = bond_exchange_matrix(1, 2), bond_exchange_matrix(2, 3)
    d12, d23 = bond_dm_matrix(1, 2), bond_dm_matrix(2, 3)
    CHI, TH = chi_operator(), theta_operator()

    print("=" * 70)
    print("Norma usata ovunque: FROBENIUS (np.linalg.norm senza ord)")
    print("=" * 70)

    print("[self-test 1] livello 0 esatto: [Sz_tot, H_ex] = 0 bond per bond")
    for lab, h in (("h12", h12), ("h23", h23)):
        e = np.linalg.norm(SZ @ h - h @ SZ)
        print(f"    ||[Sz_tot,{lab}]|| = {e:.3e}   (atteso 0 esatto)")
        assert e == 0.0
    for _ in range(3):
        J, b = rng.uniform(-2, 2, 2)
        tau = rng.uniform(0.05, 0.5)
        H0, _ = H_parts(J, b, 0.0)
        Hex = H0 - b * SZ
        e = np.linalg.norm(sla.expm(-1j * H0 * tau)
                           - sla.expm(-1j * b * tau * SZ) @ sla.expm(-1j * Hex * tau))
        print(f"    J={J:+.3f} b={b:+.3f}: ||U_H0 - U_campo U_Hex|| = {e:.3e}")
        assert e < 1e-12

    print("[self-test 2] il livello 0 NON si estende a H_DM (non-sequitur da evitare)")
    J, b, D = 1.0, 0.7, 0.3
    Hex = J * (h12 + h23)
    HDM = D * d12 - D * d23
    n_ex = np.linalg.norm(Hex @ HDM - HDM @ Hex)
    n_sz = np.linalg.norm(SZ @ HDM - HDM @ SZ)
    print(f"    ||[H_ex ,H_DM]|| = {n_ex:.6f}")
    print(f"    ||[Sz_tot,H_DM]|| = {n_sz:.6f}   -> H_ex domina, rapporto {n_ex/n_sz:.2f}")
    assert n_ex > 2 * n_sz

    print("[self-test 3] identita' dei commutatori di bond")
    e1 = np.linalg.norm((h12 @ h23 - h23 @ h12) + 2j * CHI)
    e2 = np.linalg.norm((d12 @ (-d23) - (-d23) @ d12) + 2j * TH)
    print(f"    ||[h12,h23] + 2i chi||   = {e1:.3e}   (atteso 0 esatto)")
    print(f"    ||[d12,-d23] + 2i Theta|| = {e2:.3e}   (atteso 0 esatto)")
    assert e1 == 0.0 and e2 == 0.0
    print(f"    chi hermitiano: {np.linalg.norm(CHI - CHI.conj().T):.3e} ; "
          f"Theta hermitiano: {np.linalg.norm(TH - TH.conj().T):.3e}")

    print("[self-test 4] segno del termine chirale in funzione dell'ordine dei bond")
    Jt, tau = 0.83, 0.01
    for name, (f, s), atteso in (("(1,2) poi (2,3)", (h12, h23), +1.0),
                                 ("(2,3) poi (1,2)", (h23, h12), -1.0)):
        U = sla.expm(-1j * tau * Jt * s) @ sla.expm(-1j * tau * Jt * f)
        Heff = 1j * sla.logm(U) / tau
        R = (Heff - Jt * (h12 + h23)) / tau
        coef = (np.vdot(CHI.ravel(), R.ravel()) / np.vdot(CHI.ravel(), CHI.ravel())).real
        print(f"    {name}: s = {coef/Jt**2:+.3f}   (atteso {atteso:+.1f})")
        assert abs(coef / Jt**2 - atteso) < 1e-2

    print("[self-test 5] circuito vs prodotto a matrice, N=1 (livelli 1+2 espliciti)")
    for _ in range(5):
        J, b, D = rng.uniform(-2, 2, 3)
        t = rng.uniform(0.1, 1.0)
        U_circ = Operator(trotter_circuit(J, b, D, t, 1)).data
        U_mat = np.eye(8, dtype=complex)
        for (i, j) in BONDS:
            U_mat = sla.expm(-1j * J * t * bond_exchange_matrix(i, j)) @ U_mat
        U_mat = sla.expm(-1j * b * t * SZ) @ U_mat
        for (i, j) in BONDS:
            Dij = _sign_dm((i, j)) * D
            U_mat = sla.expm(-1j * Dij * t * bond_dm_matrix(i, j)) @ U_mat
        e = np.linalg.norm(U_circ - U_mat)
        print(f"    J={J:+.3f} b={b:+.3f} D={D:+.3f} t={t:.3f}: "
              f"||U_circ - U_mat|| = {e:.3e}")
        assert e < 1e-10

    print("[self-test 6] |000> e' cieco all'errore di livello 1 (autostato dei bond)")
    for lab, h in (("h12", h12), ("h23", h23)):
        e = np.linalg.norm(h @ PSI0.data - PSI0.data)
        print(f"    ||{lab}|000> - |000>|| = {e:.3e}   (atteso 0: autostato)")
        assert e == 0.0
    ref0 = U_exact(1.0, 0.7, 0.0, 2.0) @ PSI0.data
    psi0 = Statevector(trotter_circuit(1.0, 0.7, 0.0, 2.0, 20)).data
    print(f"    -> infedelta' su |000> a D=0, N=20: {1-abs(np.vdot(ref0,psi0))**2:.3e} "
          f"(precisione macchina per qualunque N: test vuoto)")

    print("[self-test 7] convergenza su stato non banale e guadagno dell'alternanza")
    rs = np.random.default_rng(7)
    v = rs.normal(size=8) + 1j * rs.normal(size=8)
    v /= np.linalg.norm(v)
    for D, atteso in ((0.0, "alternato ~O(1/N^4), rapporto x16"),
                      (0.3, "guadagno reale ma parziale, satura")):
        J, b, t = 1.0, 0.7, 2.0
        ref = U_exact(J, b, D, t) @ v
        print(f"    D={D}:  ({atteso})")
        print(f"    {'N':>6} {'fisso':>12} {'':>6} {'alternato':>12} {'':>6} {'guadagno':>9}")
        pf = pa = None
        for N in [10, 20, 40, 80]:
            o = []
            for alt in (False, True):
                psi = Operator(trotter_circuit(J, b, D, t, N, alternate=alt)).data @ v
                o.append(1 - abs(np.vdot(ref, psi)) ** 2)
            rf = f"x{pf/o[0]:.1f}" if pf else "   -"
            ra = f"x{pa/o[1]:.1f}" if pa else "   -"
            print(f"    {N:6d} {o[0]:12.3e} {rf:>6} {o[1]:12.3e} {ra:>6} {o[0]/o[1]:9.1f}")
            pf, pa = o
        assert pf > pa

    print("=" * 70)
    print("[self-test] TUTTI I TEST SUPERATI")
    print("=" * 70)


if __name__ == "__main__":
    _self_test()
