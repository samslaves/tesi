"""
Estensione (facoltativa) del VQE con termine DM sotto rumore -- VQE
noise-aware.

La versione originale del VQE con termine DM sotto rumore
(vqe_dm_rumoroso_dimero.py) misura la DEGRADAZIONE di un risultato
ideale: i parametri theta* sono ottimizzati SENZA rumore (Parte 1), poi
il circuito con quella ricetta viene eseguito su un simulatore CON
rumore. Qui si fa la domanda diversa: se il rumore e' gia' acceso
durante l'ottimizzazione stessa (come su un hardware reale, dove non
esiste una versione ideale a cui accedere), l'ottimizzatore converge a
parametri diversi? Il risultato finale (energia, fedelta') migliora?

SCOPE DICHIARATO ESPLICITAMENTE (vedi risultati_vqe_noise_aware_dimero.tex,
sezione Metodologia, per il ragionamento completo):
  - si rioptimizza SOLO il VQE con termine DM sotto rumore;
  - un SOLO controllo a valle: si riverifica se questo sposta N*=8 della
    quantum simulation (Trotter) sotto rumore (trotter_rumoroso_dimero.py),
    riusando i suoi stessi ingredienti (build_full_circuit,
    fedelta_trotter_rumoroso) con i nuovi parametri al posto di quelli
    ideali;
  - i correlatori dinamici sotto rumore e lo scan sui parametri di rumore
    NON vengono ritoccati in questa sessione: l'estensione a quei due
    stadi si basa su un argomento di struttura (la costante di
    preparazione non entra ne' nel termine 1/N ne' in quello lineare in N,
    quindi lo stesso risultato del controllo su N* per il Trotter
    rumoroso si applica identico), non su una riverifica numerica diretta
    -- criterio di proporzionalita' dato il tempo disponibile prima della
    sessione di laurea di settembre.

ATTENZIONE -- variante della "trappola di transpilazione" gia' nota
(log_decisioni.md), stavolta nella direzione OPPOSTA: si potrebbe pensare
di transpilare l'ansatz UNA VOLTA in forma parametrica (parametri
simbolici) e poi solo assegnare i valori numerici ad ogni valutazione,
come si fa per il blocco di Trotter ripetuto N volte. Verificato che QUI
questo e' SBAGLIATO: con parametri simbolici il transpilatore non puo'
fondere le sequenze di rotazioni a 1 qubit che dipendono dal valore
numerico di theta, e il circuito risultante e' molto piu' rumoroso (19 rz
+ 14 sx contro 11 rz + 8 sx a parita' di CNOT=2, verificato in
validate_vqe_noise_aware_dimero.py). La scelta corretta -- e quella
adottata qui, coerente con vqe_dm_rumoroso_dimero.py -- e' TRANSPILARE
DOPO aver assegnato i parametri numerici, ad ogni valutazione
dell'obiettivo: piu' costoso per valutazione, ma l'unico che riproduce il
conteggio di gate minimo gia' verificato nella pipeline. Il conteggio CNOT
resta comunque invariato (=2) al variare di theta (verificato su 5
assegnazioni casuali).
"""
import numpy as np
from scipy.optimize import minimize
from qiskit import transpile
from qiskit.quantum_info import DensityMatrix, Statevector, state_fidelity
from qiskit_aer import AerSimulator

from dimer_exact import dimer_hamiltonian
from vqe_test2 import pma_2q
from noise_model_dimero import build_noise_model, BASIS_GATES
from vqe_dm_rumoroso_dimero import vqe_energia_fedelta_rumorosa

J, b, D = 1.0, 0.35, 0.80


def transpila_dopo_assegnazione(x, nparam=3, optimization_level=3, seed_transpiler=7):
    """Assegna i parametri numerici e SOLO DOPO transpila (ordine corretto,
    vedi nota in testa al modulo)."""
    bound = pma_2q(nparam).assign_parameters(x)
    return transpile(bound, basis_gates=BASIS_GATES,
                      optimization_level=optimization_level,
                      seed_transpiler=seed_transpiler)


def energia_rumorosa(x, H, noise_model):
    """Energia E=Tr[rho H], transpilando DOPO aver assegnato x."""
    tqc = transpila_dopo_assegnazione(x)
    tqc.save_density_matrix()
    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    result = sim.run(tqc).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])
    return float(np.real(rho.expectation_value(H)))


def energia_fedelta_rumorosa(x, H, noise_model, psi_exact):
    tqc = transpila_dopo_assegnazione(x)
    ncx = tqc.count_ops().get("cx", 0)
    tqc.save_density_matrix()
    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    result = sim.run(tqc).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])
    E = float(np.real(rho.expectation_value(H)))
    F = float(state_fidelity(rho, Statevector(psi_exact)))
    return E, F, ncx


def vqe_noise_aware(noise_model, R=6, maxiter=300, seed=0, x_seme=None):
    """Multistart COBYLA + polish L-BFGS-B, con l'energia SEMPRE valutata
    sotto rumore (anche durante l'ottimizzazione, transpilando dopo ogni
    assegnazione -- vedi nota in testa al modulo). Il canale e'
    deterministico (simulazione a operatore densita' esatta, nessun shot):
    l'obiettivo e' liscio in theta, L-BFGS-B e' applicabile esattamente
    come nel caso ideale (vqe_test2.py).

    x_seme: se fornito (es. i parametri ideali di Parte 1), viene incluso
    come UNO dei punti di partenza del multistart, oltre agli R casuali --
    garantisce che il risultato finale non sia mai peggiore del semplice
    riuso dei parametri ideali sotto rumore."""
    H = dimer_hamiltonian(b=b, J=J, D=D)
    n = 3

    def obj(x):
        return energia_rumorosa(x, H, noise_model)

    rng = np.random.default_rng(seed)
    x0_list = [rng.uniform(0.0, 2 * np.pi, n) for _ in range(R)]
    if x_seme is not None:
        x0_list.append(np.asarray(x_seme))

    finals = []
    best = (np.inf, None)
    for x0 in x0_list:
        res = minimize(obj, x0, method="COBYLA", options={"maxiter": maxiter})
        finals.append(res.fun)
        if res.fun < best[0]:
            best = (res.fun, res.x)
    Ebest, xbest = best

    res_polish = minimize(obj, xbest, method="L-BFGS-B")
    if res_polish.fun < Ebest:
        Ebest, xbest = res_polish.fun, res_polish.x

    return {"E": Ebest, "x": xbest,
            "finals": np.array(finals), "spread": np.ptp(finals)}


def controllo_invarianza_cnot(n_prove=5, seed=0):
    """Verifica la premessa fisica dichiarata: il conteggio CNOT del
    circuito transpilato (DOPO l'assegnazione dei parametri, ordine
    corretto) non dipende dai valori numerici di theta."""
    rng = np.random.default_rng(seed)
    conteggi = []
    dettagli = []
    for _ in range(n_prove):
        x = rng.uniform(0.0, 2 * np.pi, 3)
        tqc = transpila_dopo_assegnazione(x)
        ops = tqc.count_ops()
        conteggi.append(ops.get("cx", 0))
        dettagli.append(dict(ops))
    return conteggi, dettagli


if __name__ == "__main__":
    data = np.load("ground_state_test2.npz")
    vqe_params_ideali = data["vqe_params"]
    psi_exact = data["psi0_exact"]
    E0_exact = float(data["E0_exact"])

    nm_ref, noise_params = build_noise_model()

    print("=" * 70)
    print("0. Invarianza del conteggio CNOT rispetto a theta (premessa fisica)")
    print("=" * 70)
    conteggi, dettagli = controllo_invarianza_cnot()
    print(f"  CNOT su {len(conteggi)} assegnazioni casuali di theta: {conteggi}")
    print(f"  dettaglio gate (prima assegnazione): {dettagli[0]}")

    print()
    print("=" * 70)
    print("1. VQE con termine DM sotto rumore, versione originale: parametri ideali riusati")
    print("=" * 70)
    E_ideale_su_rumore, F_ideale_su_rumore, ncx = vqe_energia_fedelta_rumorosa(
        vqe_params_ideali, psi_exact, noise_model=nm_ref)
    print(f"  E = {E_ideale_su_rumore:.8f}   F = {F_ideale_su_rumore:.8f}   CNOT = {ncx}")

    print()
    print("=" * 70)
    print("2. Autoconsistenza: VQE noise-aware con rumore SPENTO")
    print("   (deve ritrovare l'ottimo ideale gia' noto)")
    print("=" * 70)
    ris_zero = vqe_noise_aware(noise_model=None, R=6, maxiter=300, seed=0)
    print(f"  E (noise-aware, rumore nullo) = {ris_zero['E']:.8f}")
    print(f"  E0 (esatto, registrato)       = {E0_exact:.8f}")
    print(f"  |differenza|                  = {abs(ris_zero['E'] - E0_exact):.2e}")

    print()
    print("=" * 70)
    print("3. VQE noise-aware con rumore ACCESO (ibm_torino, riferimento)")
    print("   multistart R=6 casuali + 1 seme = parametri ideali di Parte 1")
    print("=" * 70)
    ris_rumore = vqe_noise_aware(noise_model=nm_ref, R=6, maxiter=300, seed=0,
                                  x_seme=vqe_params_ideali)
    E_noise_aware, F_noise_aware, ncx_na = energia_fedelta_rumorosa(
        ris_rumore["x"], dimer_hamiltonian(b=b, J=J, D=D), nm_ref, psi_exact)
    print(f"  E (noise-aware) = {E_noise_aware:.8f}   F = {F_noise_aware:.8f}   CNOT = {ncx_na}")
    print(f"  dispersione multistart (max-min E finale) = {ris_rumore['spread']:.2e}")

    print()
    print("=" * 70)
    print("4. Confronto: riuso ideale vs rioptimizzazione sotto rumore")
    print("=" * 70)
    dE = E_noise_aware - E_ideale_su_rumore
    dF = F_noise_aware - F_ideale_su_rumore
    print(f"  Delta E (noise-aware - riuso ideale) = {dE:+.8f}")
    print(f"  Delta F (noise-aware - riuso ideale) = {dF:+.8f}")

    print()
    print("=" * 70)
    print("5. Controllo a valle: N* della quantum simulation (Trotter) sotto")
    print("   rumore, con i parametri noise-aware")
    print("=" * 70)
    from trotter_rumoroso_dimero import fedelta_trotter_rumoroso
    t = 2.0
    Ns = list(range(1, 21)) + [30, 40, 60, 80, 120, 160]
    Fs = []
    for N in Ns:
        F, _ = fedelta_trotter_rumoroso(ris_rumore["x"], psi_exact, t, N,
                                         noise_model=nm_ref)
        Fs.append(F)
    imax = int(np.argmax(Fs))
    print(f"  N* (parametri noise-aware) = {Ns[imax]}   F(N*) = {Fs[imax]:.6f}")
    print(f"  N* (parametri ideali, Trotter rumoroso, gia' noto) = 8   F(N*) = 0.817725")

    np.savez("vqe_noise_aware_result.npz",
             x_noise_aware=ris_rumore["x"],
             E_noise_aware=E_noise_aware, F_noise_aware=F_noise_aware,
             E_ideale_su_rumore=E_ideale_su_rumore,
             F_ideale_su_rumore=F_ideale_su_rumore,
             N_star_noise_aware=Ns[imax], F_N_star_noise_aware=Fs[imax],
             cnot_invarianza=conteggi)
    print("\n[salvato] vqe_noise_aware_result.npz")
