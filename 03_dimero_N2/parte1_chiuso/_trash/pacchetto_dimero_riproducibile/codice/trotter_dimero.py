"""Quantum simulation del dimero: exp(-iHt) via Suzuki-Trotter (1o ordine).

Convenzione: spin 1 -> qubit 0, spin 2 -> qubit 1.
Stringhe di Pauli in notazione little-endian di Qiskit ('AB': B su q0, A su q1).
H = b(sz1+sz2) + J s1.s2 + D(sx1 sz2 - sz1 sx2) = H1 + H2

RUOLO NELL'INSIEME DEL PACCHETTO: e' il modulo di riferimento per
l'evoluzione temporale reale senza rumore -- costruisce il circuito di
Trotter per DECOMPOSIZIONE ESPLICITA in gate nativi (rxx, ryy, rzz, rz,
h), non tramite UnitaryGate + transpilazione come fa invece
circuito_correlazioni_dimero.py (e, nel pacchetto rumoroso,
trotter_rumoroso_dimero.py). Due percorsi di costruzione indipendenti
per lo stesso passo di Trotter: la funzione U_trotter_mat() qui sotto
permette di verificare che le due costruzioni diano la stessa evoluzione
(fatto verificato: coincidono a precisione macchina). Nota di
convenzione: questo modulo usa lo spin fisico s=sigma/2 (coefficienti
1/2, 1/4 nell'Hamiltoniana), diverso dalla convenzione Pauli diretta di
dimer_exact.py -- stessa fisica, normalizzazione diversa, va tenuto a
mente confrontando i due moduli.
"""
import numpy as np, scipy.linalg as sla
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, Operator, Statevector

P = lambda s: Pauli(s).to_matrix()
Z1, Z2 = P('IZ'), P('ZI')
SZ_TOT = (Z1 + Z2) / 2
PSI0 = np.array([1, 0, 0, 0], dtype=complex)          # |00> = |up up>

def H_parts(b, J, D):
    """Scompone H = H1 + H2 (scambio isotropo + Zeeman, poi solo DM),
    nella convenzione spin s=sigma/2 di questo modulo.

    Ruolo nel modulo: fornisce i due pezzi di Hamiltoniana usati sia da
    step_H1()/step_H2() (costruzione a circuito) sia da U_exact() e
    U_trotter_mat() (costruzione a matrice) -- un'unica sorgente per
    entrambi i percorsi di calcolo.
    Ruolo nell'insieme: e' l'analogo, in questa convenzione di
    normalizzazione, di _H1_H2() in circuito_correlazioni_dimero.py --
    stesso split concettuale, coefficienti diversi per la diversa
    convenzione di spin.
    """
    H1 = b/2*(Z1+Z2) + J/4*(P('XX')+P('YY')+P('ZZ'))
    H2 = D/4*(P('ZX') - P('XZ'))                       # X1Z2 - Z1X2
    return H1, H2

# ---------- circuiti ----------
def step_H1(qc, b, J, tau):
    """Applica, in-place su qc, l'evoluzione esatta sotto H1 per un
    tempo tau (scambio isotropo + Zeeman, che commuta con se stesso a
    tempi diversi, quindi non serve ulteriore approssimazione).

    Ruolo nel modulo: e' la prima meta' del singolo passo di Trotter
    costruito da trotter_circuit() -- decomposizione diretta in gate
    nativi (rz per lo Zeeman, rxx/ryy/rzz per lo scambio), senza passare
    da UnitaryGate.
    Ruolo nell'insieme: stessa fisica (H1 = scambio + Zeeman) del blocco
    corrispondente in circuito_correlazioni_dimero.py, ma costruita qui
    gate-per-gate invece che tramite matrice esponenziata e
    UnitaryGate -- un secondo modo indipendente di ottenere lo stesso
    risultato fisico.
    """
    qc.rz(b*tau, 0); qc.rz(b*tau, 1)
    qc.rxx(J*tau/2, 0, 1); qc.ryy(J*tau/2, 0, 1); qc.rzz(J*tau/2, 0, 1)

def step_H2(qc, D, tau):
    """Applica, in-place su qc, l'evoluzione esatta sotto H2 (solo
    termine DM) per un tempo tau, tramite coniugazione con Hadamard
    (X1Z2 diventa Z1Z2 nella base ruotata sul qubit 0, e viceversa per
    Z1X2 sul qubit 1).

    Ruolo nel modulo: e' la seconda meta' del singolo passo di Trotter
    -- H1 e H2 non commutano quando D!=0, quindi l'ordine (prima H1, poi
    H2) introduce l'errore di Trotter al prim'ordine, O(tau^2) per passo.
    Ruolo nell'insieme: stessa fisica del contributo DM in
    circuito_correlazioni_dimero.py, costruzione a gate espliciti invece
    che a matrice esponenziata -- utile come cross-check indipendente.
    """
    qc.h(0); qc.rzz(D*tau/2, 0, 1); qc.h(0)            # exp(-i theta X1Z2)
    qc.h(1); qc.rzz(-D*tau/2, 0, 1); qc.h(1)           # exp(+i theta Z1X2)

def trotter_circuit(b, J, D, t, N, measure=False):
    """Costruisce il circuito completo: N passi di Trotter (H1 poi H2
    ripetuti N volte), con barriere fra un passo e il successivo.

    Ruolo nel modulo: e' la funzione pubblica principale del file --
    combina step_H1() e step_H2() in un ciclo di N ripetizioni,
    producendo il circuito eseguibile.
    Ruolo nell'insieme: e' l'evoluzione di Trotter costruita per
    decomposizione esplicita, verificata (vedi GUIDA_USO) coincidere a
    precisione macchina con l'evoluzione costruita da
    circuito_correlazioni_dimero.py tramite UnitaryGate + transpilazione
    -- due strade indipendenti allo stesso risultato fisico.
    """
    qc = QuantumCircuit(2, 2) if measure else QuantumCircuit(2)
    tau = t/N
    for _ in range(N):
        step_H1(qc, b, J, tau); step_H2(qc, D, tau); qc.barrier()
    if measure: qc.measure([0, 1], [0, 1])
    return qc

# ---------- riferimenti a matrice ----------
def U_exact(b, J, D, t):
    """Evoluzione esatta e continua (nessun Trotter), via esponenziale
    di matrice diretto.

    Ruolo nel modulo: e' il termine di paragone "senza approssimazione"
    per valutare l'errore di Trotter introdotto da trotter_circuit().
    Ruolo nell'insieme: e' l'analogo, in questa convenzione, di
    target_state() in trotter_rumoroso_dimero.py (pacchetto rumoroso) --
    stesso ruolo concettuale (riferimento fisico esatto), qui senza
    alcun rumore ne' approssimazione di Trotter.
    """
    H1, H2 = H_parts(b, J, D); return sla.expm(-1j*(H1+H2)*t)

def U_trotter_mat(b, J, D, t, N):
    """Evoluzione di Trotter costruita a matrice (non a circuito) --
    stesso passo esponenziale di trotter_circuit(), ma applicato N volte
    come potenza di matrice invece che come sequenza di gate.

    Ruolo nel modulo: e' il secondo percorso di calcolo indipendente
    (accanto a trotter_circuit()) per lo stesso passo di Trotter --
    permette di verificare che circuito e matrice diano lo stesso
    risultato, isolando eventuali bug di implementazione del circuito
    da eventuali errori concettuali nella fisica.
    Ruolo nell'insieme: verificato in GUIDA_USO che coincide a precisione
    macchina sia con trotter_circuit() (stesso modulo) sia, nel limite
    N grande, con l'evoluzione costruita indipendentemente in
    circuito_correlazioni_dimero.py.
    """
    H1, H2 = H_parts(b, J, D); tau = t/N
    # il circuito applica H1 e poi H2 -> in forma matriciale U_step = e^{-iH2 tau} e^{-iH1 tau}
    return np.linalg.matrix_power(sla.expm(-1j*H2*tau) @ sla.expm(-1j*H1*tau), N)

def sz(psi):
    """Aspettazione di Sz_tot=(Z1+Z2)/2 su uno stato psi.

    Ruolo nel modulo: osservabile diagnostico usato per caratterizzare
    lo stato evoluto (es. per un grafico di magnetizzazione contro
    tempo), non usato internamente da nessun'altra funzione di questo
    file.
    Ruolo nell'insieme: stesso osservabile (a meno della normalizzazione
    di spin) di magnetization_operator() in dimer_exact.py.
    """
    return float(np.real(psi.conj() @ SZ_TOT @ psi))
