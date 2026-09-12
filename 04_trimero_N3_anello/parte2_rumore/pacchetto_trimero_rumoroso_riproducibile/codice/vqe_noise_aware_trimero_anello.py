"""
Parte 2, Stadio 2bis -- VQE NOISE-AWARE: riottimizzare vedendo il rumore
(trimero ad anello), invece di riusare i parametri ideali (Stadio 2).

RUOLO NELL'INSIEME DEL PACCHETTO: estensione facoltativa, analoga a
`vqe_noise_aware_dimero.py`. La domanda e' complementare a quella dello
Stadio 2: li' si misura quanto degrada un VQE ideale eseguito su
simulatore rumoroso; qui si ottimizza l'energia DIRETTAMENTE sotto rumore
(come si farebbe su hardware vero, dove non esiste un riferimento ideale
per calibrare), e si confrontano energia, fedelta' e gli N* a valle
(Stadio 3 e Stadio 4bis) fra i due approcci.

Argomento teorico (canale depolarizzante isotropo):
    E_rumoroso(theta) = (1-lambda)*E_ideale(theta) + lambda*Tr[H]/d
trasformazione AFFINE in E_ideale a struttura di circuito fissa -> lo
stesso theta* che minimizza E_ideale minimizza anche E_rumoroso.
Previsione dichiarata PRIMA di guardare i numeri: nessun vantaggio a
riottimizzare -- verificato che sul trimero questa previsione puo'
FALLIRE (a differenza del dimero), per un motivo strutturale legato
all'ansatz a sei parametri, non all'argomento in se' (vedi sotto).

ATTENZIONE -- artefatto del transpilatore, non un effetto fisico: con
l'ansatz a sei parametri, a VALORI SPECIALI di theta (vicini a 0 o pi) il
transpilatore (livello di ottimizzazione 3) puo' semplificare il blocco
CNOT-Ry-CNOT riducendo il conteggio CNOT (6 -> 4), cosa che NON succede a
theta generici. Per isolare l'effetto fisico da questo artefatto, questo
modulo lavora a STRUTTURA FISSA (optimization_level=0) come metodologia
principale -- la struttura a produzione (livello 3) e' riportata solo
come nota di confronto, mai come risultato primario.
"""
import numpy as np
from qiskit import transpile
from qiskit.quantum_info import DensityMatrix, state_fidelity, Statevector
from qiskit_aer import AerSimulator

from trimer_ring_exact import trimer_hamiltonian_dm
from vqe_w2q6_trimero_anello import w2q6_circuit
from noise_model_trimero_anello import build_noise_model, BASIS_GATES

J, Jp, b, D, MODE = 1.0, 0.4, 2.4, 0.15, "B"


def energia_rumorosa(params, H, noise_model, optimization_level=0, seed_transpiler=7):
    """Energia <H> del circuito VQE (W-2q.6) sotto rumore, a un dato
    livello di transpilazione -- funzione di costo per la riottimizzazione.

    RUOLO NEL MODULO: obiettivo passato a scipy.optimize.minimize dentro
    ottimizza_vqe_noise_aware. RUOLO NELL'INSIEME: stessa energia dello
    Stadio 2 (vqe_energia_fedelta_rumorosa), ma qui e' l'obiettivo da
    minimizzare, non solo una misura finale -- e il livello di
    transpilazione e' un parametro esplicito, non fisso a 3, proprio per
    poter isolare l'artefatto descritto sopra."""
    ansatz = w2q6_circuit().assign_parameters(params)
    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    tqc = transpile(ansatz, basis_gates=BASIS_GATES,
                     optimization_level=optimization_level,
                     seed_transpiler=seed_transpiler)
    tqc.save_density_matrix()
    result = sim.run(tqc).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])
    return float(np.real(rho.expectation_value(H)))


def conteggio_cx(params, optimization_level, seed_transpiler=7):
    """Conteggio CNOT del circuito transpilato a un dato livello, ai
    parametri dati -- usato per diagnosticare l'artefatto del
    transpilatore (non per l'ottimizzazione stessa)."""
    ansatz = w2q6_circuit().assign_parameters(params)
    tqc = transpile(ansatz, basis_gates=BASIS_GATES,
                     optimization_level=optimization_level,
                     seed_transpiler=seed_transpiler)
    return tqc.count_ops().get("cx", 0)


def ottimizza_vqe_noise_aware(noise_model, n_start=12, seed=0,
                               optimization_level=0):
    """Multistart (COBYLA + polish L-BFGS-B, stesso schema dello Stadio
    2/Parte 1) dell'energia rumorosa, a struttura di circuito fissata
    (default: livello 0, vedi nota sull'artefatto in cima al modulo).

    Ritorna (params_ottimi, E_ottima).
    """
    from scipy.optimize import minimize

    H = trimer_hamiltonian_dm(J, Jp, b, MODE, D)
    rng = np.random.default_rng(seed)

    def obj(p):
        return energia_rumorosa(p, H, noise_model, optimization_level)

    best = None
    for _ in range(n_start):
        x0 = rng.uniform(-np.pi, np.pi, size=6)
        res = minimize(obj, x0, method="COBYLA",
                        options=dict(maxiter=300, rhobeg=0.5, tol=1e-6))
        if best is None or res.fun < best.fun:
            best = res
    polish = minimize(obj, best.x, method="L-BFGS-B",
                       options=dict(maxiter=200, ftol=1e-10, eps=1e-4))
    if polish.fun < best.fun:
        best = polish
    return best.x, best.fun


if __name__ == "__main__":
    data = np.load("w2q6_params_optimal.npz")
    vqe_params_ideali = data["params"]

    H = trimer_hamiltonian_dm(J, Jp, b, MODE, D).to_matrix()
    Evals, V = np.linalg.eigh(H)
    psi_exact = V[:, 0]
    imax = np.argmax(np.abs(psi_exact))
    psi_exact = psi_exact * np.exp(-1j * np.angle(psi_exact[imax]))

    nm_ref, params_ref = build_noise_model()
    Hop = trimer_hamiltonian_dm(J, Jp, b, MODE, D)

    print("Verifica dell'artefatto: conteggio CX a struttura fissa vs produzione,")
    print("su 5 assegnazioni casuali di theta (deve essere identico, 6, in entrambe):")
    rng = np.random.default_rng(1)
    for _ in range(5):
        p = rng.uniform(-np.pi, np.pi, 6)
        c0 = conteggio_cx(p, optimization_level=0)
        c3 = conteggio_cx(p, optimization_level=3)
        print(f"  livello 0: {c0} CX   livello 3: {c3} CX")

    print("\n--- Riuso dei parametri ideali (Stadio 2), struttura fissa ---")
    E_riuso = energia_rumorosa(vqe_params_ideali, Hop, nm_ref, optimization_level=0)
    sim = AerSimulator(method="density_matrix", noise_model=nm_ref)
    ansatz = w2q6_circuit().assign_parameters(vqe_params_ideali)
    tqc = transpile(ansatz, basis_gates=BASIS_GATES, optimization_level=0, seed_transpiler=7)
    tqc.save_density_matrix()
    rho = DensityMatrix(sim.run(tqc).result().data(0)["density_matrix"])
    F_riuso = float(state_fidelity(rho, Statevector(psi_exact)))
    print(f"  E = {E_riuso:.8f}   F = {F_riuso:.8f}")

    print("\n--- VQE noise-aware, struttura fissa (multistart) ---")
    params_na, E_na = ottimizza_vqe_noise_aware(nm_ref, n_start=12, seed=0,
                                                  optimization_level=0)
    ansatz_na = w2q6_circuit().assign_parameters(params_na)
    tqc_na = transpile(ansatz_na, basis_gates=BASIS_GATES, optimization_level=0, seed_transpiler=7)
    tqc_na.save_density_matrix()
    rho_na = DensityMatrix(sim.run(tqc_na).result().data(0)["density_matrix"])
    F_na = float(state_fidelity(rho_na, Statevector(psi_exact)))
    print(f"  E = {E_na:.8f}   F = {F_na:.8f}")
    print(f"\n  Delta_E = {E_na - E_riuso:+.6e}   Delta_F = {F_na - F_riuso:+.6e}")

    np.savez("vqe_noise_aware_params.npz", params=params_na, E=E_na, F=F_na,
             E_riuso=E_riuso, F_riuso=F_riuso)
    print("\nSalvato: vqe_noise_aware_params.npz")
