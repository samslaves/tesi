import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))


"""
Scan sistematico delle 81 combinazioni C_ij^{alpha,beta}(t) al punto di
lavoro Scenario A (Documento 4) -- esplicitamente escluso dallo scope
dichiarato della prima versione di questo pacchetto ("scan81_*,
catalogazione, non riproduzione dati/figure").

  1. Zeri all'istante iniziale: verificati 32/81 (stato fondamentale
     reale, prodotti hermitiani-ma-immaginari hanno media nulla su t=0).
  2. Zeri strutturali (per ogni t, non solo t=0): verificati 4/81, tutti
     sullo stesso sito (sito 3) -- non ancora spiegati in forma chiusa,
     solo verificati numericamente.
  3. Ricchezza spettrale indipendente dall'ampiezza: due correlatori con
     ampiezza comparabile possono avere contenuto in frequenza molto
     diverso -- quantificato col numero di frequenze distinte con peso
     apprezzabile nella trasformata, non solo dichiarato.
"""
import itertools
import numpy as np

from circuito_correlazioni_trimero_anello import ground_state, correlator_from_circuit

J, Jp, b, D = 1.0, 0.4, 2.4, 0.15
N = 200
SITI = (1, 2, 3)
COMP = ("x", "y", "z")

psi0, _ = ground_state(J, Jp, b, D)

print("=" * 78)
print("1. ZERI ALL'ISTANTE INIZIALE (t=0)")
print("=" * 78)
zeri_t0 = 0
for (i, al), (j, be) in itertools.product(itertools.product(SITI, COMP),
                                            itertools.product(SITI, COMP)):
    c0 = correlator_from_circuit(i, al, j, be, 0.0, 1, J, Jp, b, D, psi0)
    if abs(c0) < 1e-8:
        zeri_t0 += 1
print(f"  zeri a t=0: {zeri_t0}/81  (atteso: 32)")
assert zeri_t0 == 32, f"atteso 32 zeri a t=0, trovati {zeri_t0}"
print("  -> OK")

print()
print("=" * 78)
print("2. ZERI STRUTTURALI (per ogni t, non solo t=0)")
print("=" * 78)
print("Verifica a precisione macchina: esponenziale di matrice diretto")
print("(non il circuito Trotter -- quello ha residuo finito a N=200, vedi sotto)")


def classical_exact(i, alpha, j, beta, t, H, psi0):
    """<psi0| e^{iHt} A e^{-iHt} B |psi0>, stessa definizione di
    04_valida_correlatori_esatti.py (non importata da li' per evitare il
    suo side-effect di chdir -- copiata qui, come gia' fatto in
    genera_figure_correlatori.py)."""
    I2 = np.eye(2, dtype=complex)
    PAULI = {"x": np.array([[0, 1], [1, 0]], dtype=complex),
             "y": np.array([[0, -1j], [1j, 0]], dtype=complex),
             "z": np.array([[1, 0], [0, -1]], dtype=complex)}

    def site_op(site, comp):
        ops = [I2, I2, I2]
        ops[site - 1] = PAULI[comp]
        return np.kron(np.kron(ops[0], ops[1]), ops[2])

    import scipy.linalg as sla
    A = site_op(i, alpha); B = site_op(j, beta)
    Ut = sla.expm(-1j * H * t)
    return np.vdot(psi0, Ut.conj().T @ A @ Ut @ B @ psi0)


from trimer_ring_exact import trimer_hamiltonian_dm
H = trimer_hamiltonian_dm(J, Jp, b, "B", D).to_matrix()

t_test = [0.3, 1.1, 2.0, 3.5]
zeri_strutturali = []
righe_scan = []
for (i, al), (j, be) in itertools.product(itertools.product(SITI, COMP),
                                            itertools.product(SITI, COMP)):
    vals_esatti = [abs(classical_exact(i, al, j, be, t, H, psi0)) for t in t_test]
    ampiezza_max = max(vals_esatti)
    righe_scan.append((i, al, j, be, ampiezza_max))
    if ampiezza_max < 1e-9:
        zeri_strutturali.append((i, al, j, be))

print(f"  zeri strutturali esatti (max|C(t)| su {len(t_test)} istanti < 1e-9): "
      f"{len(zeri_strutturali)}/81  (atteso: 4)")
for i, al, j, be in zeri_strutturali:
    print(f"    C_{i}{j}^{al}{be}")
assert len(zeri_strutturali) == 4, f"atteso 4 zeri strutturali, trovati {len(zeri_strutturali)}"
assert all(i == 3 and j == 3 for i, al, j, be in zeri_strutturali), \
    "attesi tutti sul sito 3"
print("  -> OK: tutti e quattro sullo stesso sito (sito 3), a precisione macchina")

print("\nConfronto: stesse combinazioni via CIRCUITO (Trotter, N=200) --")
print("atteso piccolo ma NON a precisione macchina (residuo di Trotter finito):")
for i, al, j, be in zeri_strutturali:
    vals_circ = [abs(correlator_from_circuit(i, al, j, be, t, N, J, Jp, b, D, psi0))
                  for t in t_test]
    print(f"    C_{i}{j}^{al}{be}: max|C_circuito| = {max(vals_circ):.2e}")

print()
print("=" * 78)
print("3. RICCHEZZA SPETTRALE INDIPENDENTE DALL'AMPIEZZA")
print("=" * 78)
t_denso = np.linspace(0.05, 8.0, 64)


def n_frequenze_rilevanti(i, al, j, be, soglia=0.1):
    """Numero di componenti in frequenza con peso (modulo della FFT)
    superiore a soglia*picco -- una misura grezza ma quantitativa di
    'ricchezza spettrale', non solo un aggettivo."""
    vals = np.array([correlator_from_circuit(i, al, j, be, t, N, J, Jp, b, D, psi0)
                      for t in t_denso])
    spettro = np.abs(np.fft.fft(vals - vals.mean()))
    if spettro.max() < 1e-10:
        return 0
    return int(np.sum(spettro > soglia * spettro.max()))


casi = [(1, "y", 1, "y"), (3, "y", 3, "y"), (1, "y", 3, "y")]
for i, al, j, be in casi:
    ampiezza = max(abs(correlator_from_circuit(i, al, j, be, t, N, J, Jp, b, D, psi0))
                    for t in t_test)
    nfreq = n_frequenze_rilevanti(i, al, j, be)
    print(f"  C_{i}{j}^{al}{be}: ampiezza max = {ampiezza:.4f}   "
          f"frequenze rilevanti = {nfreq}")

np.savez("scan81_correlatori.npz",
         righe=np.array(righe_scan, dtype=object),
         zeri_strutturali=np.array(zeri_strutturali, dtype=object))
print("\nSalvato: scan81_correlatori.npz")
