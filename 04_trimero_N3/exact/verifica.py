import numpy as np
import itertools

I2 = np.eye(2)
X = np.array([[0,1],[1,0]], dtype=complex)
Y = np.array([[0,-1j],[1j,0]], dtype=complex)
Z = np.array([[1,0],[0,-1]], dtype=complex)

def kron3(a,b,c):
    return np.kron(np.kron(a,b),c)

def op_on(site, P):
    """Operatore di Pauli P sul sito 'site' (1,2,3) dei 3 qubit."""
    ops = [I2, I2, I2]
    ops[site-1] = P
    return kron3(*ops)

def sigdot(i,j):
    """sigma_i . sigma_j = XiXj + YiYj + ZiZj"""
    return op_on(i,X)@op_on(j,X) + op_on(i,Y)@op_on(j,Y) + op_on(i,Z)@op_on(j,Z)

def H_trimero(J, Jp, b):
    """H = J s1.s2 (base) + J'(s2.s3 + s3.s1) (lati) + b sum Zi   [convenzione Pauli]"""
    H = J*sigdot(1,2) + Jp*(sigdot(2,3) + sigdot(3,1))
    H = H + b*(op_on(1,Z) + op_on(2,Z) + op_on(3,Z))
    return H

def analitico(J, Jp, b):
    """Le 8 energie previste dal PDF: E = base + 2*b*M."""
    out = []
    for M in [1.5, 0.5, -0.5, -1.5]:
        out.append(('A', M, J + 2*Jp + 2*b*M))
    for M in [0.5, -0.5]:
        out.append(('B', M, J - 4*Jp + 2*b*M))
    for M in [0.5, -0.5]:
        out.append(('C', M, -3*J + 2*b*M))
    return out

print("="*72)
print("TEST 1 - Spettro completo: diagonalizzazione esatta vs formule del PDF")
print("="*72)

rng = np.random.default_rng(0)
maxerr = 0.0
ncheck = 0
for _ in range(400):
    J  = rng.uniform(-3, 3)
    Jp = rng.uniform(-3, 3)
    b  = rng.uniform(-3, 3)
    ev_num = np.sort(np.linalg.eigvalsh(H_trimero(J, Jp, b)))
    ev_ana = np.sort([e for (_,_,e) in analitico(J, Jp, b)])
    err = np.max(np.abs(ev_num - ev_ana))
    maxerr = max(maxerr, err)
    ncheck += 1
print(f"  configurazioni testate : {ncheck}")
print(f"  errore massimo         : {maxerr:.3e}")
print(f"  ESITO                  : {'OK' if maxerr < 1e-10 else 'FALLITO'}")

print()
print("="*72)
print("TEST 2 - Energie dei tre multipletti a b=0")
print("="*72)
for (J, Jp) in [(1,0.4), (1,1.6), (1,-2.5), (1,1), (1,0), (-1,1), (-1,-1), (2,-4)]:
    ev = np.sort(np.linalg.eigvalsh(H_trimero(J, Jp, 0)))
    EA, EB, EC = J+2*Jp, J-4*Jp, -3*J
    # atteso: EA x4, EB x2, EC x2
    atteso = np.sort([EA]*4 + [EB]*2 + [EC]*2)
    ok = np.allclose(ev, atteso, atol=1e-10)
    print(f"  J={J:5.1f} J'={Jp:5.1f} | E_A={EA:7.2f} E_B={EB:7.2f} E_C={EC:7.2f} | {'OK' if ok else 'FALLITO'}")

print()
print("="*72)
print("TEST 3 - Campo critico b_c: formula vs scansione numerica")
print("="*72)

def bc_formula(J, Jp):
    E0 = {'A': J+2*Jp, 'B': J-4*Jp, 'C': -3*J}
    gs0 = min(E0, key=E0.get)
    if gs0 == 'A':
        return None
    bc = 3*Jp if gs0 == 'B' else 2*J + Jp
    return bc if bc > 1e-12 else None

def bc_numerico(J, Jp, bmax=30.0, n=600000):
    """Trova il primo b>0 dove cambia la degenerazione/identita del fondamentale,
    tramite il salto di <Sz> del ground state."""
    bs = np.linspace(1e-6, bmax, 2000)
    prev = None
    for b in bs:
        H = H_trimero(J, Jp, b)
        w, v = np.linalg.eigh(H)
        psi = v[:, 0]
        Sz = 0.5*(op_on(1,Z)+op_on(2,Z)+op_on(3,Z))
        m = np.real(psi.conj() @ Sz @ psi)
        if prev is not None and abs(m - prev) > 0.4:
            # raffina per bisezione
            lo, hi = b_prev, b
            for _ in range(60):
                mid = 0.5*(lo+hi)
                w2, v2 = np.linalg.eigh(H_trimero(J, Jp, mid))
                mm = np.real(v2[:,0].conj() @ Sz @ v2[:,0])
                if abs(mm - prev) > 0.4:
                    hi = mid
                else:
                    lo = mid
            return 0.5*(lo+hi)
        prev = m
        b_prev = b
    return None

casi = [(1,0.4), (1,1.6), (1,-2.5), (1,1), (1,0), (-1,1), (-1,-1), (1,-1), (1,-2), (0.5,2)]
for (J, Jp) in casi:
    f = bc_formula(J, Jp)
    n = bc_numerico(J, Jp)
    if f is None and n is None:
        print(f"  J={J:5.1f} J'={Jp:5.1f} | formula: nessun crossing | numerico: nessuno | OK")
    elif f is None or n is None:
        print(f"  J={J:5.1f} J'={Jp:5.1f} | formula: {f} | numerico: {n} | DISCREPANZA")
    else:
        ok = abs(f - n) < 1e-3
        print(f"  J={J:5.1f} J'={Jp:5.1f} | formula b_c={f:8.4f} | numerico={n:8.4f} | {'OK' if ok else 'FALLITO'}")

print()
print("="*72)
print("TEST 4 - Mappa dei segni: fondamentale a b=0 sulla griglia (J,J')")
print("="*72)

def gs_formula(J, Jp):
    E0 = {'A': J+2*Jp, 'B': J-4*Jp, 'C': -3*J}
    mn = min(E0.values())
    return {k for k,v in E0.items() if abs(v-mn) < 1e-12}

def gs_regione_pdf(J, Jp):
    """Regole enunciate nel PDF (sez. 7)."""
    r = set()
    if -2*J <= Jp <= J:      r.add('C')
    if Jp >= max(J, 0):      r.add('B')
    if Jp <= min(-2*J, 0):   r.add('A')
    return r

bad = 0
tot = 0
for J in np.linspace(-3, 3, 61):
    for Jp in np.linspace(-3, 3, 61):
        if abs(J) < 1e-9 and abs(Jp) < 1e-9:
            continue
        a = gs_formula(J, Jp)
        b_ = gs_regione_pdf(J, Jp)
        tot += 1
        if a != b_:
            bad += 1
            if bad <= 6:
                print(f"  MISMATCH J={J:.2f} J'={Jp:.2f}: energie->{sorted(a)}  regole PDF->{sorted(b_)}")
print(f"  punti testati: {tot}, disaccordi: {bad}")
print(f"  ESITO: {'OK' if bad == 0 else 'DA CONTROLLARE'}")

print()
print("="*72)
print("TEST 5 - Coordinate dei marker nei grafici del PDF (figura 3)")
print("="*72)
pannelli = [('a', 1, 0.4, -8.95, 12.55), ('b', 1, 1.6, -16.63, 25.03),
            ('c', 1, -2.5, -14.62, 15.62), ('d', 1, 1, -10.44, 16.44)]
for (nome, J, Jp, ymin, ymax) in pannelli:
    bc = bc_formula(J, Jp)
    if bc is None:
        print(f"  pannello ({nome}) J={J} J'={Jp}: nessun crossing (nessun marker atteso)")
        continue
    Ec = J + 2*Jp - 3*bc
    dentro = ymin <= Ec <= ymax
    print(f"  pannello ({nome}) J={J} J'={Jp}: b_c={bc:.2f}, E_c={Ec:.2f}, "
          f"ylim=[{ymin},{ymax}] -> marker {'VISIBILE' if dentro else 'FUORI SCALA (CLIPPATO)'}")

# controllo che tutte le rette stiano dentro gli ylim usati
print()
print("  Copertura verticale delle rette per ciascun pannello:")
domini = {'a': 3.2, 'b': 6.2, 'c': 3, 'd': 4}
for (nome, J, Jp, ymin, ymax) in pannelli:
    bmax = domini[nome]
    vals = []
    for base, Ms in [(J+2*Jp, [1.5,0.5,-0.5,-1.5]), (J-4*Jp,[0.5,-0.5]), (-3*J,[0.5,-0.5])]:
        for M in Ms:
            vals += [base, base + 2*M*bmax]
    lo, hi = min(vals), max(vals)
    print(f"    ({nome}) rette spaziano [{lo:.2f},{hi:.2f}] vs ylim [{ymin},{ymax}] -> "
          f"{'tutto dentro' if lo>=ymin and hi<=ymax else 'ALCUNE RETTE TAGLIATE'}")
