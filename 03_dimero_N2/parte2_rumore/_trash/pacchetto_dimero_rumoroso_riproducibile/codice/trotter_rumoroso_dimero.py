"""
Parte 2, Passo 3 -- quantum simulation (Trotter) sotto rumore.

Prima applicazione reale della strategia decisa nella sessione precedente:
il singolo passo di Trotter viene transpilato UNA VOLTA al suo costo minimo
(3 CNOT), poi il blocco gia' compilato viene composto N volte -- MAI
ritranspilato per intero (altrimenti il transpiler fonde gli N passi in un
unico blocco a costo costante, cancellando la dipendenza da N: vedi
log_decisioni.md, sessione precedente).

Osservabile: fedelta' rispetto allo stato bersaglio FISICO, cioe' evoluto
in modo continuo ed esatto (nessun Trotter, nessun rumore) a partire dal
ground state esatto:

    |psi_target(t)> = exp(-iHt) |psi0_exact>
    F(N, rumore) = <psi_target(t)| rho_N |psi_target(t)>

dove rho_N e' lo stato ottenuto da: preparazione (ansatz VQE, come nel
Passo 2) -> N passi di Trotter rumorosi. Questa singola quantita' impacchetta
tutti e tre i contributi caratterizzati nella sessione precedente:
preparazione (costante in N), Trotter (decresce con N), rumore accumulato
(cresce con N).

RUOLO NELL'INSIEME DEL PACCHETTO: e' il modulo che introduce per la
prima volta la dipendenza da N (numero di passi di Trotter) nella
pipeline di rumore -- ne' il modulo VQE (Passo 2) ne' il modello di
rumore hanno un analogo. Il pattern "transpila il blocco una volta,
componi N volte" stabilito qui in build_step_block()/build_full_circuit()
e' riusato IDENTICO in correlatori_rumorosi_dimero.py (che aggiunge
sopra l'ancilla) ed e' il singolo accorgimento tecnico piu' citato in
tutta la documentazione del progetto: la sua violazione e' l'unico
modo trovato per rompere silenziosamente lo scan sui parametri di
rumore (Passo 5), che dipende in modo essenziale dal fatto che il
costo in gate cresca davvero con N.
"""
import numpy as np
import scipy.linalg as sla
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import UnitaryGate
from qiskit.quantum_info import DensityMatrix, Statevector, state_fidelity
from qiskit_aer import AerSimulator

from dimer_exact import dimer_hamiltonian
from vqe_test2 import pma_2q
from noise_model_dimero import build_noise_model, BASIS_GATES

J, b, D = 1.0, 0.35, 0.80


def build_step_block(t, N, optimization_level=3, seed_transpiler=7):
    """Transpila UNA VOLTA il singolo passo di Trotter (H1 poi H2, come
    trotter_dimero.py) al suo costo minimo. Ritorna un QuantumCircuit gia'
    in base {rz,sx,x,cx} -- da riusare via compose(), mai da ritranspilare
    per intero insieme alle sue ripetizioni.

    Ruolo nel modulo: e' il "mattone" che build_full_circuit() ripete N
    volte -- separarlo in una funzione propria e' cio' che rende
    possibile transpilarlo una sola volta indipendentemente da N.
    Ruolo nell'insieme: e' l'implementazione concreta dell'accorgimento
    "transpilazione a blocchi" richiamato nel docstring di modulo --
    ogni altro punto della pipeline che ripete un'evoluzione di Trotter
    (correlatori_rumorosi_dimero.py, gli script di figura
    dell'estensione VQE noise-aware) segue lo stesso schema.
    """
    tau = t / N
    H1 = dimer_hamiltonian(b=b, J=J, D=0.0).to_matrix()
    H2 = dimer_hamiltonian(b=0.0, J=0.0, D=D).to_matrix()
    step = sla.expm(-1j * H2 * tau) @ sla.expm(-1j * H1 * tau)
    qc = QuantumCircuit(2)
    qc.append(UnitaryGate(step), [0, 1])
    return transpile(qc, basis_gates=BASIS_GATES,
                      optimization_level=optimization_level,
                      seed_transpiler=seed_transpiler)


def build_full_circuit(vqe_params, t, N):
    """Ansatz VQE (preparazione, Passo 2) + N passi di Trotter, blocco
    compilato una volta e composto (mai ritranspilato per intero).
    L'ansatz stesso contiene il gate custom RBS (non nativo per Aer):
    va transpilato in base {rz,sx,x,cx} una sola volta, come il passo di
    Trotter -- stessa logica, stesso motivo.

    Ruolo nel modulo: e' la funzione che assembla il circuito completo
    valutato da fedelta_trotter_rumoroso() -- preparazione piu'
    evoluzione, entrambe transpilate a blocchi separati e mai
    ricomposte in un'unica transpilazione finale.
    Ruolo nell'insieme: e' l'unico punto del modulo dove preparazione
    (Passo 2) ed evoluzione (Passo 3) si incontrano in un solo circuito
    -- il circuito che poi viene effettivamente eseguito su
    AerSimulator in fedelta_trotter_rumoroso().
    """
    ansatz = pma_2q(3).assign_parameters(vqe_params)
    ansatz_block = transpile(ansatz, basis_gates=BASIS_GATES,
                              optimization_level=3, seed_transpiler=7)
    step_block = build_step_block(t, N)

    qc = QuantumCircuit(2)
    qc.compose(ansatz_block, [0, 1], inplace=True)
    for _ in range(N):
        qc.compose(step_block, [0, 1], inplace=True)
    return qc


def target_state(psi0_exact, t):
    """Stato bersaglio fisico: evoluzione esatta e continua (no Trotter,
    no rumore) del ground state esatto.

    Ruolo nel modulo: fornisce il termine di paragone per
    fedelta_trotter_rumoroso() -- senza questo, non ci sarebbe nulla
    rispetto a cui misurare "quanto e' fedele" lo stato rumoroso
    approssimato via Trotter.
    Ruolo nell'insieme: e' il riferimento fisico "ideale" (nessuna
    approssimazione, nessun rumore) rispetto a cui l'intero compromesso
    Trotter/rumore studiato in questo stadio della pipeline viene
    quantificato -- il ruolo analogo, per i correlatori, e' svolto dal
    confronto diretto con la Parte 1 nei validate_*.py.
    """
    H = dimer_hamiltonian(b=b, J=J, D=D).to_matrix()
    U = sla.expm(-1j * H * t)
    return U @ psi0_exact


def fedelta_trotter_rumoroso(vqe_params, psi0_exact, t, N, noise_model=None):
    """Fedelta' rispetto allo stato bersaglio fisico, dopo N passi di
    Trotter rumorosi. Ritorna (fedelta', n_cx_totali).

    Ruolo nel modulo: e' la funzione pubblica del file -- combina
    build_full_circuit() (il circuito), target_state() (il riferimento)
    e la simulazione a operatore densita' in un unico numero.
    Ruolo nell'insieme: e' la funzione richiamata da ogni script che
    deve trovare N* (il numero di passi ottimale) per la fedelta' di
    Trotter -- scan_parametri_rumore_dimero.py la chiama a molti valori
    di N per ciascun punto della griglia di rumore, ed e' importata
    identica dall'estensione VQE noise-aware per il confronto fra
    preparazione ideale e preparazione ottimizzata di nuovo. Stessa
    avvertenza di vqe_dm_rumoroso_dimero.py: b, J, D sono costanti di
    modulo, non parametri della funzione.
    """
    qc = build_full_circuit(vqe_params, t, N)
    ncx = qc.count_ops().get("cx", 0)

    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    qc = qc.copy()
    qc.save_density_matrix()
    result = sim.run(qc).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])

    psi_t = target_state(psi0_exact, t)
    F = float(state_fidelity(rho, Statevector(psi_t)))
    return F, ncx


if __name__ == "__main__":
    data = np.load("ground_state_test2.npz")
    vqe_params = data["vqe_params"]
    psi0_exact = data["psi0_exact"]
    t = 2.0

    nm_ref, _ = build_noise_model()

    print(f"{'N':>4} {'CNOT':>6} {'F (rumore nullo)':>18} {'F (rumore ibm_torino)':>22}")
    for N in [1, 2, 5, 10, 20, 40, 80, 160]:
        F0, ncx = fedelta_trotter_rumoroso(vqe_params, psi0_exact, t, N, noise_model=None)
        Fn, _ = fedelta_trotter_rumoroso(vqe_params, psi0_exact, t, N, noise_model=nm_ref)
        print(f"{N:>4} {ncx:>6} {F0:>18.10f} {Fn:>22.10f}")
