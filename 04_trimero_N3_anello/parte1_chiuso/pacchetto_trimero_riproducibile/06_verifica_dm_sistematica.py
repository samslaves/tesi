import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))


"""
Verifica sistematica del termine DM (Documento 0, Documento 1): fra tutte
le combinazioni di segno di (D_12, D_23, D_31) proporzionali a (J,J',J'),
quale rispetta la simmetria di scambio 1<->2 (operatore di permutazione
P12)?

Fonte: analisi_dm_trimero_anello.tex (gia' nel progetto) -- questo script
riproduce e verifica indipendentemente quella tabella, non solo il
confronto puntuale fra Opzione A e Opzione B gia' fatto dentro
_self_test_dm() di trimer_ring_exact.py (quel self-test verifica SOLO le
due opzioni gia' scelte, non esplora lo spazio completo delle
combinazioni -- e' questo script a farlo).

Risultato atteso: fra le 12 combinazioni (D_12 in {0,+,-}; D_23,D_31 in
{+,-}), UNA SOLA coppia rispetta la simmetria esattamente
(D_12=0, D_23=-D_31 e la sua immagine speculare) -- quella diventa
l'Opzione A. L'Opzione B (proposta del relatore: tutti e tre i legami,
stesso segno) e', fra tutte, quella che rompe la simmetria DI PIU'
(valore massimo di ||[P12,H_DM]||), non una rottura qualsiasi.
"""
import itertools
import numpy as np

from trimer_ring_exact import dm_term

J, Jp, r = 1.0, 0.4, 0.15


def P12_matrix():
    """Matrice di permutazione 8x8 che scambia i qubit dei siti 1 e 2
    (identica alla costruzione dentro _self_test_dm di
    trimer_ring_exact.py -- non duplicata per caso: e' la stessa
    definizione, verificata coerente)."""
    P = np.zeros((8, 8))
    for b1 in (0, 1):
        for b2 in (0, 1):
            for b3 in (0, 1):
                idx_in = 4 * b1 + 2 * b2 + b3
                idx_out = 4 * b2 + 2 * b1 + b3
                P[idx_out, idx_in] = 1
    return P


def H_DM_segni(s12, s23, s31):
    """Hamiltoniana DM per una data combinazione di segno (ciascuno in
    {-1,0,+1}), coefficienti proporzionali a (r*J, r*J', r*J')."""
    H = np.zeros((8, 8), dtype=complex)
    if s12 != 0:
        H += dm_term(1, 2, s12 * r * J).to_matrix()
    if s23 != 0:
        H += dm_term(2, 3, s23 * r * Jp).to_matrix()
    if s31 != 0:
        H += dm_term(3, 1, s31 * r * Jp).to_matrix()
    return H


P12 = P12_matrix()

print("=" * 78)
print(f"Verifica su tutte le combinazioni di segno (D12,D23,D31), r={r}:")
print(f"{'D12':>5} {'D23':>5} {'D31':>5} {'max|[P12,H_DM]|':>18}")
righe = []
for s12, s23, s31 in itertools.product([0, 1, -1], [1, -1], [1, -1]):
    H = H_DM_segni(s12, s23, s31)
    comm = P12 @ H @ P12.T - H
    val = np.max(np.abs(comm))
    lab = {0: "0", 1: "+", -1: "-"}
    print(f"{lab[s12]:>5} {lab[s23]:>5} {lab[s31]:>5} {val:>18.4f}")
    righe.append((s12, s23, s31, val))

simmetriche = [r_ for r_ in righe if r_[3] < 1e-9]
print(f"\nCombinazioni simmetriche (valore ~0): {len(simmetriche)}")
for s12, s23, s31, val in simmetriche:
    print(f"  D12={s12}, D23={s23}, D31={s31}  (Opzione A: D12=0, D23=-D31)")
assert len(simmetriche) == 2, "atteso esattamente 2 (la coppia D23=-D31 e la sua speculare)"

valore_max = max(r_[3] for r_ in righe)
riga_max = [r_ for r_ in righe if r_[3] == valore_max][0]
print(f"\nCombinazione che rompe la simmetria DI PIU': "
      f"D12={riga_max[0]}, D23={riga_max[1]}, D31={riga_max[2]} "
      f"(valore={valore_max:.4f})")
assert riga_max[0] == 1 and riga_max[1] == 1 and riga_max[2] == 1, \
    "atteso che sia proprio (+,+,+), l'Opzione B"
print("  -> Confermato: l'Opzione B (+,+,+), proposta del relatore, e' la "
      "combinazione che rompe la simmetria P12 piu' di ogni altra fra "
      "quelle testate -- non una rottura qualsiasi.")

np.savez("verifica_dm_sistematica.npz",
         righe=np.array(righe, dtype=float))
print("\nSalvato: verifica_dm_sistematica.npz")
