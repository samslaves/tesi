"""
Estensione (facoltativa) del VQE con termine DM sotto rumore -- VQE
noise-aware, trimero ad anello. Mirror di vqe_noise_aware_dimero.py, con
UNA DIFFERENZA SOSTANZIALE rispetto al dimero, scoperta in questa sessione
e trattata esplicitamente in tutto il modulo (vedi risultati_vqe_noise_
aware_trimero_anello_definitivo.tex per la trattazione completa):

  sul dimero, il conteggio CNOT del circuito transpilato (nell'ordine
  corretto: dopo l'assegnazione di theta) e' stato VERIFICATO indipendente
  da theta su assegnazioni casuali -- premessa che rendeva valido
  l'argomento del canale isotropo anche in pratica (nessuna via indiretta,
  via costo in gate, per cui convenisse spostarsi da theta_ideale).

  Sul trimero ad anello questa premessa NON regge in generale: l'ansatz
  W-2q.6 (6 parametri, contro i 3 del dimero) puo' avere, a valori
  speciali di theta (vicini a 0 o pi), una struttura CNOT-Ry-CNOT che il
  transpilatore semplifica, riducendo il conteggio CNOT (6->4). Un
  ottimizzatore che minimizza l'energia rumorosa puo' raggiungere questi
  punti "a costo zero" (meno canali di rumore attraversati), a scapito
  della fedelta' al vero stato fondamentale -- un compromesso energia/
  fedelta' che il dimero non mostra mai.

SCOPE (deciso dopo la verifica del Passo 0): SOLO Scenario A (J=1, J'=0.4,
b=b_c=2.4, D=0.15, ansatz W-2q.6). R0 non ha una preparazione VQE nella
pipeline attuale (Trotter parte da |000>, i correlatori non lo usano mai)
-- non e' quindi un candidato per questa estensione, a differenza di R1
sul dimero.

Due metodologie, entrambe implementate in questo modulo:
  - "produzione" (optimization_level=3): quella usata in tutta la
    pipeline principale, gate-minima ma NON invariante in theta per
    questo ansatz -- puo' mostrare il comportamento anomalo sopra.
  - "struttura fissa" (optimization_level=0): SEMPRE lo stesso conteggio
    di gate (18 rz + 12 sx + 6 cx) qualunque theta, verificato
    esplicitamente -- isola l'effetto fisico della riottimizzazione
    dall'artefatto discontinuo del transpilatore. E' la metodologia usata
    per il risultato fisico principale di questo documento.
"""
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import XGate, YGate, ZGate
from qiskit.quantum_info import DensityMatrix, Statevector, state_fidelity, SparsePauliOp
from qiskit_aer import AerSimulator
import scipy.linalg as sla

from trimer_ring_exact import trimer_hamiltonian_dm
from vqe_w2q6_trimero_anello import w2q6_circuit
from trotter_trimero_anello import step_Hex, step_field, step_HDM, H_parts, Q
from noise_model_trimero_anello import build_noise_model, BASIS_GATES

J, Jp, b, D, MODE = 1.0, 0.4, 2.4, 0.15, "B"
NPARAM = 6
ANCILLA = 3
PAULI_GATE = {'x': XGate(), 'y': YGate(), 'z': ZGate()}


# ----------------------------------------------------------------------
# Preparazione: due livelli di transpilazione, stessa interfaccia
# ----------------------------------------------------------------------

def transpila_dopo_assegnazione(x, optimization_level=3, seed_transpiler=7):
    """Assegna i parametri numerici e SOLO DOPO transpila -- ordine
    corretto (stessa disciplina del dimero) per il conteggio di gate
    minimo. optimization_level=3: produzione (non invariante in theta per
    questo ansatz). optimization_level=0: struttura fissa (SEMPRE 18 rz +
    12 sx + 6 cx, verificato su prove multiple incluse ai valori speciali
    0/pi -- vedi validate_vqe_noise_aware_trimero_anello.py, controllo 1)."""
    bound = w2q6_circuit().assign_parameters(x)
    return transpile(bound, basis_gates=BASIS_GATES,
                      optimization_level=optimization_level,
                      seed_transpiler=seed_transpiler)


def energia_rumorosa(x, H, noise_model, optimization_level=3):
    tqc = transpila_dopo_assegnazione(x, optimization_level=optimization_level)
    tqc.save_density_matrix()
    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    result = sim.run(tqc).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])
    return float(np.real(rho.expectation_value(H)))


def energia_fedelta_rumorosa(x, H, noise_model, psi_exact, optimization_level=3):
    tqc = transpila_dopo_assegnazione(x, optimization_level=optimization_level)
    ncx = tqc.count_ops().get("cx", 0)
    tqc.save_density_matrix()
    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    result = sim.run(tqc).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])
    E = float(np.real(rho.expectation_value(H)))
    F = float(state_fidelity(rho, Statevector(psi_exact)))
    return E, F, ncx


# ----------------------------------------------------------------------
# Ottimizzazione
# ----------------------------------------------------------------------

def vqe_noise_aware(noise_model, R=12, maxiter=300, seed=0, x_seme=None,
                     optimization_level=3):
    """Multistart COBYLA + polish L-BFGS-B, energia sempre valutata sotto
    rumore, alla metodologia scelta (3=produzione, 0=struttura fissa).
    x_seme (i parametri ideali) incluso come punto di partenza aggiuntivo,
    come sul dimero."""
    H = trimer_hamiltonian_dm(J, Jp, b, MODE, D)

    def obj(x):
        return energia_rumorosa(x, H, noise_model, optimization_level=optimization_level)

    rng = np.random.default_rng(seed)
    x0_list = [rng.uniform(0.0, 2 * np.pi, NPARAM) for _ in range(R)]
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


def controllo_invarianza_cnot(n_prove=5, seed=0, optimization_level=3):
    """Verifica se il conteggio CNOT del circuito transpilato dipende dai
    valori numerici di theta. A optimization_level=3 (produzione): puo'
    variare (differenza col dimero). A optimization_level=0 (struttura
    fissa): sempre costante, per costruzione."""
    rng = np.random.default_rng(seed)
    conteggi, dettagli = [], []
    for _ in range(n_prove):
        x = rng.uniform(0.0, 2 * np.pi, NPARAM)
        tqc = transpila_dopo_assegnazione(x, optimization_level=optimization_level)
        ops = tqc.count_ops()
        conteggi.append(ops.get("cx", 0))
        dettagli.append(dict(ops))
    return conteggi, dettagli


def controllo_invarianza_cnot_valori_speciali(optimization_level=0):
    """Controllo mirato (non casuale): il conteggio CNOT resta invariato
    anche ai valori di theta che, a livello 3, hanno mostrato riduzione
    CNOT (vicini a 0 o pi)? Verificato a livello 0 (struttura fissa)."""
    casi = {
        "tutti zero": np.zeros(NPARAM),
        "p1=pi, p2~0 (punto anomalo trovato)": np.array(
            [0.76 * np.pi, np.pi, 0.0, 1.0 * np.pi, 1.33 * np.pi, 1.65 * np.pi]),
    }
    risultati = {}
    for nome, x in casi.items():
        tqc = transpila_dopo_assegnazione(x, optimization_level=optimization_level)
        risultati[nome] = dict(tqc.count_ops())
    return risultati


# ----------------------------------------------------------------------
# Trotter e correlatore, entrambi parametrici nel livello di
# transpilazione della SOLA preparazione (il blocco di Trotter resta
# sempre a livello 3, gia' verificato gate-minimo e indipendente da
# theta -- non e' l'ansatz VQE, non e' affetto dal problema qui discusso)
# ----------------------------------------------------------------------

def _build_step_block(t, N, optimization_level=3, seed_transpiler=7):
    tau = t / N
    qc = QuantumCircuit(3)
    step_Hex(qc, J, Jp, tau)
    step_field(qc, b, tau)
    step_HDM(qc, J, Jp, D, tau)
    return transpile(qc, basis_gates=BASIS_GATES,
                      optimization_level=optimization_level,
                      seed_transpiler=seed_transpiler)


def build_full_circuit(params, t, N, prep_level=3):
    qc = QuantumCircuit(3)
    prep = transpila_dopo_assegnazione(params, optimization_level=prep_level)
    qc.compose(prep, [0, 1, 2], inplace=True)
    step_block = _build_step_block(t, N)
    for _ in range(N):
        qc.compose(step_block, [0, 1, 2], inplace=True)
    return qc


def target_state(t, psi0):
    H0, H_DM = H_parts(J, Jp, b, D)
    U = sla.expm(-1j * (H0 + H_DM) * t)
    return U @ psi0


def fedelta_trotter(params, t, N, psi0, noise_model, prep_level=3):
    """Fedelta' rispetto allo stato bersaglio fisico (evoluzione esatta,
    no Trotter, no rumore, a partire da psi0), dopo N passi di Trotter
    rumorosi con preparazione a livello prep_level."""
    qc = build_full_circuit(params, t, N, prep_level=prep_level)
    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    qc2 = qc.copy()
    qc2.save_density_matrix()
    result = sim.run(qc2).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])
    psi_t = target_state(t, psi0)
    return float(state_fidelity(rho, Statevector(psi_t)))


def _transpile_once(qc, level=3):
    return transpile(qc, basis_gates=BASIS_GATES, optimization_level=level, seed_transpiler=7)


def _ctrl_W_block(beta):
    qc = QuantumCircuit(2)
    qc.h(0)
    {"x": qc.cx, "y": qc.cy, "z": qc.cz}[beta](0, 1)
    return _transpile_once(qc)


def _final_block(alpha, part):
    qc = QuantumCircuit(2)
    anti_gate = PAULI_GATE[alpha].control(1, ctrl_state=0)
    qc.append(anti_gate, [0, 1])
    if part == "re":
        qc.h(0)
    elif part == "im":
        qc.rx(np.pi / 2, 0)
    return _transpile_once(qc)


def build_noisy_correlator_circuit(i, alpha, j, beta, t, N, part, params, prep_level=3):
    qc = QuantumCircuit(4)
    prep = transpila_dopo_assegnazione(params, optimization_level=prep_level)
    qc.compose(prep, [0, 1, 2], inplace=True)
    ctrlW = _ctrl_W_block(beta)
    qc.compose(ctrlW, [ANCILLA, Q[j]], inplace=True)
    step_block = _build_step_block(t, N)
    for _ in range(N):
        qc.compose(step_block, [0, 1, 2], inplace=True)
    final = _final_block(alpha, part)
    qc.compose(final, [ANCILLA, Q[i]], inplace=True)
    return qc


def ancilla_z(qc, noise_model):
    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    qc2 = qc.copy()
    qc2.save_density_matrix()
    result = sim.run(qc2).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])
    op = SparsePauliOp.from_sparse_list([("Z", [ANCILLA], 1.0)], num_qubits=4)
    return float(np.real(rho.expectation_value(op)))


def correlator_rumoroso(i, alpha, j, beta, t, N, params, noise_model, p_readout, prep_level=3):
    qc_re = build_noisy_correlator_circuit(i, alpha, j, beta, t, N, "re", params, prep_level)
    qc_im = build_noisy_correlator_circuit(i, alpha, j, beta, t, N, "im", params, prep_level)
    z_re = ancilla_z(qc_re, noise_model) * (1 - 2 * p_readout)
    z_im = ancilla_z(qc_im, noise_model) * (1 - 2 * p_readout)
    return z_re + 1j * z_im


def scan_N_star_trotter(params, t, N_grid, psi0, noise_model, prep_level=3):
    F = [fedelta_trotter(params, t, N, psi0, noise_model, prep_level=prep_level) for N in N_grid]
    imax = int(np.argmax(F))
    return N_grid[imax], F[imax], F


def scan_N_star_correlatore(i, alpha, j, beta, params, t, N_grid, noise_model,
                             p_readout, prep_level=3):
    vals = [abs(correlator_rumoroso(i, alpha, j, beta, t, N, params, noise_model,
                                     p_readout, prep_level=prep_level))
            for N in N_grid]
    imax = int(np.argmax(vals))
    return N_grid[imax], vals[imax], vals


if __name__ == "__main__":
    data = np.load("w2q6_params_optimal.npz")
    vqe_params_ideali = data["params"]
    E0_exact = float(data["E_exact"])

    H_mat = trimer_hamiltonian_dm(J, Jp, b, MODE, D).to_matrix()
    Evals, V = np.linalg.eigh(H_mat)
    psi_exact = V[:, 0]
    imax = np.argmax(np.abs(psi_exact))
    psi_exact = psi_exact * np.exp(-1j * np.angle(psi_exact[imax]))

    nm_ref, noise_params = build_noise_model()

    print("=" * 70)
    print("0. Invarianza CNOT: produzione (livello 3) vs struttura fissa (livello 0)")
    print("=" * 70)
    c3, _ = controllo_invarianza_cnot(optimization_level=3)
    c0, _ = controllo_invarianza_cnot(optimization_level=0)
    print(f"  livello 3, 5 prove casuali: {c3}")
    print(f"  livello 0, 5 prove casuali: {c0}")
    speciali0 = controllo_invarianza_cnot_valori_speciali(optimization_level=0)
    for nome, ops in speciali0.items():
        print(f"  livello 0, {nome}: {ops}")

    print()
    print("=" * 70)
    print("1. Riuso ideale sotto rumore (entrambi i livelli)")
    print("=" * 70)
    for lvl in [3, 0]:
        E, F, ncx = energia_fedelta_rumorosa(vqe_params_ideali, H_mat, nm_ref, psi_exact,
                                              optimization_level=lvl)
        print(f"  livello {lvl}: E={E:.8f}  F={F:.8f}  CNOT={ncx}")

    print()
    print("=" * 70)
    print("2. VQE noise-aware, struttura fissa (livello 0), R=12+seme")
    print("=" * 70)
    ris = vqe_noise_aware(nm_ref, R=12, maxiter=300, seed=0,
                           x_seme=vqe_params_ideali, optimization_level=0)
    E_na, F_na, ncx_na = energia_fedelta_rumorosa(ris["x"], H_mat, nm_ref, psi_exact,
                                                    optimization_level=0)
    print(f"  E={E_na:.8f}  F={F_na:.8f}  CNOT={ncx_na}")
    np.savez("vqe_noise_aware_trimero_anello_result.npz",
             x_noise_aware_fixed=ris["x"], E_noise_aware_fixed=E_na, F_noise_aware_fixed=F_na)
    print("\n[salvato] vqe_noise_aware_trimero_anello_result.npz")
