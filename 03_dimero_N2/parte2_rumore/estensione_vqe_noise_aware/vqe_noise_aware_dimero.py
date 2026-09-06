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


def controllo_N_star_correlatore(vqe_params_ideali, x_noise_aware, noise_model,
                                  t=2.0, N_grid=None,
                                  i=2, alpha="x", j=1, beta="x",
                                  J=1.0, b=0.35, D=0.80, p_readout=0.023):
    """Controllo DIRETTO (non per analogia) su una seconda metrica a valle,
    strutturalmente diversa dalla fedelta' di Trotter: N* = argmax_N |C(N)|
    del correlatore dinamico (Passo 4), con la preparazione VQE ideale
    contro quella noise-aware.

    Perche' questo controllo non era automatico dall'analogia con la
    fedelta' di Trotter (Passo 3): quella e' una fedelta' (combinazione
    lineare additiva di tre contributi, gia' scomposta numericamente in un
    lavoro precedente sul correlatore stesso -- vedi log_decisioni.md,
    'Scomposizione verificata numericamente'), mentre qui N* e' definito
    come il massimo del MODULO di un numero complesso costruito da una
    misura di Hadamard test. Comporre una trasformazione con un modulo non
    preserva in generale le stesse proprieta' di invarianza di una somma
    lineare (visto esplicitamente nel caso del readout asimmetrico, dove
    la stessa preoccupazione ha effettivamente cambiato la conclusione
    teorica, anche se non quella numerica). Il confronto va quindi fatto
    qui, direttamente su questa metrica, non assunto per analogia."""
    from correlatori_rumorosi_dimero import correlator_rumoroso, J_DEFAULT, b_DEFAULT, D_DEFAULT
    if N_grid is None:
        N_grid = list(range(1, 21))

    vals_ideale, vals_na = [], []
    for N in N_grid:
        c_i = correlator_rumoroso(i, alpha, j, beta, t, N, J, b, D,
                                   vqe_params_ideali, noise_model=noise_model,
                                   p_readout=p_readout)
        c_n = correlator_rumoroso(i, alpha, j, beta, t, N, J, b, D,
                                   x_noise_aware, noise_model=noise_model,
                                   p_readout=p_readout)
        vals_ideale.append(abs(c_i))
        vals_na.append(abs(c_n))

    imax_i = int(np.argmax(vals_ideale))
    imax_n = int(np.argmax(vals_na))
    return {
        "N_grid": N_grid,
        "vals_ideale": vals_ideale, "vals_na": vals_na,
        "N_star_ideale": N_grid[imax_i], "N_star_na": N_grid[imax_n],
        "val_star_ideale": vals_ideale[imax_i], "val_star_na": vals_na[imax_n],
    }


def verifica_secondo_punto_lavoro(noise_model, R=6, maxiter=300, seed=0,
                                   t=2.0, N_grid=None):
    """Ripete l'intera catena di controlli (VQE ideale multistart, VQE
    noise-aware, N* Trotter, N* correlatore) a un SECONDO punto di lavoro
    -- b/J=-0.18, D/J=1 (J=1), gia' usato nella documentazione narrativa
    per le slide (dimero_03_dinamica.tex) per la dinamica non
    monocromatica, con un termine DM 5 volte piu' forte del punto
    ``test 2''. Serve a verificare che le conclusioni di questo documento
    non siano un artefatto del singolo punto di lavoro gia' testato.

    Non sovrascrive lo stato globale del modulo: b, D vengono passati
    esplicitamente, mai letti dalle costanti di modulo J,b,D definite in
    testa a questo file (quelle restano legate al punto ``test 2'')."""
    from dimer_exact import dimer_hamiltonian
    from vqe_test2 import exact_ground, vqe_multistart
    import trotter_rumoroso_dimero as _trd
    import correlatori_rumorosi_dimero as _crd

    J2, b2, D2 = 1.0, -0.18, 1.0
    E0_exact, psi0_exact, w, v = exact_ground(b2, J2, D2)

    # VQE ideale: multistart su piu' seed (necessario qui: un solo seed
    # non sempre trova la fedelta' a precisione macchina a questo punto)
    best = None
    for s in range(10):
        ris = vqe_multistart(pma_2q(3), dimer_hamiltonian(b2, J2, D2), w, v,
                              R=6, seed=s)
        if best is None or ris["E"] < best["E"]:
            best = ris
    vqe_params_ideali = best["x"]

    # riuso ideale sotto rumore (Passo 2 originale, a questo punto)
    H2 = dimer_hamiltonian(b=b2, J=J2, D=D2)
    E_ideale_su_rumore, F_ideale_su_rumore, _ = energia_fedelta_rumorosa(
        vqe_params_ideali, H2, noise_model, psi0_exact)

    # VQE noise-aware a questo punto (serve un obj locale: b,D diversi da
    # quelli di modulo usati da energia_rumorosa/vqe_noise_aware)
    def obj_locale(x):
        return energia_rumorosa(x, H2, noise_model)
    rng = np.random.default_rng(seed)
    x0_list = [rng.uniform(0.0, 2 * np.pi, 3) for _ in range(R)]
    x0_list.append(np.asarray(vqe_params_ideali))
    best_E, best_x = np.inf, None
    from scipy.optimize import minimize
    for x0 in x0_list:
        res = minimize(obj_locale, x0, method="COBYLA",
                        options={"maxiter": maxiter})
        if res.fun < best_E:
            best_E, best_x = res.fun, res.x
    res_polish = minimize(obj_locale, best_x, method="L-BFGS-B")
    if res_polish.fun < best_E:
        best_E, best_x = res_polish.fun, res_polish.x
    x_noise_aware = best_x

    E_na, F_na, _ = energia_fedelta_rumorosa(x_noise_aware, H2, noise_model,
                                              psi0_exact)

    # N* Trotter
    if N_grid is None:
        N_grid = list(range(1, 21)) + [30, 40, 60, 80, 120, 160]
    b_bak, D_bak, J_bak = _trd.b, _trd.D, _trd.J
    _trd.b, _trd.D, _trd.J = b2, D2, J2
    try:
        F_i, F_n = [], []
        for N in N_grid:
            Fi, _ = _trd.fedelta_trotter_rumoroso(vqe_params_ideali, psi0_exact,
                                                   t, N, noise_model=noise_model)
            Fn, _ = _trd.fedelta_trotter_rumoroso(x_noise_aware, psi0_exact,
                                                   t, N, noise_model=noise_model)
            F_i.append(Fi); F_n.append(Fn)
    finally:
        _trd.b, _trd.D, _trd.J = b_bak, D_bak, J_bak
    N_star_trotter_i = N_grid[int(np.argmax(F_i))]
    N_star_trotter_n = N_grid[int(np.argmax(F_n))]

    # N* correlatore
    N_grid_corr = list(range(1, 21))
    b_bak2 = (_crd.b_DEFAULT, _crd.D_DEFAULT, _crd.J_DEFAULT)
    _crd.b_DEFAULT, _crd.D_DEFAULT, _crd.J_DEFAULT = b2, D2, J2
    try:
        vals_i, vals_n = [], []
        for N in N_grid_corr:
            c_i = _crd.correlator_rumoroso(2, "x", 1, "x", t, N, J2, b2, D2,
                                            vqe_params_ideali, noise_model=noise_model,
                                            p_readout=0.023)
            c_n = _crd.correlator_rumoroso(2, "x", 1, "x", t, N, J2, b2, D2,
                                            x_noise_aware, noise_model=noise_model,
                                            p_readout=0.023)
            vals_i.append(abs(c_i)); vals_n.append(abs(c_n))
    finally:
        _crd.b_DEFAULT, _crd.D_DEFAULT, _crd.J_DEFAULT = b_bak2
    N_star_corr_i = N_grid_corr[int(np.argmax(vals_i))]
    N_star_corr_n = N_grid_corr[int(np.argmax(vals_n))]

    return {
        "b": b2, "D": D2, "J": J2, "E0_exact": E0_exact,
        "vqe_params_ideali": vqe_params_ideali, "x_noise_aware": x_noise_aware,
        "E_ideale_su_rumore": E_ideale_su_rumore, "F_ideale_su_rumore": F_ideale_su_rumore,
        "E_noise_aware": E_na, "F_noise_aware": F_na,
        "N_grid_trotter": N_grid, "F_trotter_ideale": F_i, "F_trotter_na": F_n,
        "N_star_trotter_ideale": N_star_trotter_i, "N_star_trotter_na": N_star_trotter_n,
        "N_grid_corr": N_grid_corr, "vals_corr_ideale": vals_i, "vals_corr_na": vals_n,
        "N_star_corr_ideale": N_star_corr_i, "N_star_corr_na": N_star_corr_n,
    }


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

    print()
    print("=" * 70)
    print("6. Controllo DIRETTO (non per analogia) su una metrica diversa:")
    print("   N* del correlatore dinamico (Passo 4), argmax|C(N)|")
    print("=" * 70)
    ris_corr = controllo_N_star_correlatore(vqe_params_ideali, ris_rumore["x"], nm_ref)
    print(f"  N* (preparazione ideale)      = {ris_corr['N_star_ideale']}"
          f"   |C(N*)| = {ris_corr['val_star_ideale']:.6f}")
    print(f"  N* (preparazione noise-aware) = {ris_corr['N_star_na']}"
          f"   |C(N*)| = {ris_corr['val_star_na']:.6f}")
    diff_max = max(abs(a - b) for a, b in zip(ris_corr["vals_ideale"], ris_corr["vals_na"]))
    print(f"  scostamento massimo su tutto lo scan di N: {diff_max:.2e}")

    np.savez("vqe_noise_aware_result.npz",
             x_noise_aware=ris_rumore["x"],
             E_noise_aware=E_noise_aware, F_noise_aware=F_noise_aware,
             E_ideale_su_rumore=E_ideale_su_rumore,
             F_ideale_su_rumore=F_ideale_su_rumore,
             N_star_noise_aware=Ns[imax], F_N_star_noise_aware=Fs[imax],
             cnot_invarianza=conteggi,
             N_grid_corr=ris_corr["N_grid"],
             vals_corr_ideale=ris_corr["vals_ideale"],
             vals_corr_na=ris_corr["vals_na"],
             N_star_corr_ideale=ris_corr["N_star_ideale"],
             N_star_corr_na=ris_corr["N_star_na"])
    print("\n[salvato] vqe_noise_aware_result.npz")
