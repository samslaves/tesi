"""Ansatz per il dimero: libreria di varianti (RBS, HA, PMA a diverse
parametrizzazioni), usata per disegnare i circuiti nei documenti
narrativi del progetto.

RUOLO NELL'INSIEME DEL PACCHETTO: nota di trasparenza importante --
nonostante il nome suggerisca un ruolo centrale, questo modulo NON e'
importato da nessun altro file di QUESTO pacchetto: vqe_dimer.py e
vqe_test2.py definiscono ciascuno le proprie funzioni di ansatz
localmente (equivalenti nella sostanza, ma non le stesse istanze di
codice). Nel progetto originale, ansatz_dimero.py e' usato solo da
script di illustrazione dei circuiti per i documenti narrativi
(fig_circuiti.py, fig_doc2.py), non compresi in questo pacchetto
riproducibile perche' producono disegni di circuiti, non risultati
numerici. E' incluso qui per completezza (la libreria di ansatz piu'
ampia definita nel progetto, con anche varianti come ansatz_PMA_W e
ansatz_PMA_1q non esplorate altrove) e perche' rbs_block() e'
concettualmente lo stesso blocco usato, ridefinito localmente, in
vqe_test2.py e vqe_dimer.py -- vederli fianco a fianco chiarisce che
sono davvero la stessa idea implementata piu' volte.
"""
import numpy as np
from qiskit.circuit import QuantumCircuit, ParameterVector
from qiskit.circuit.library import n_local

J = 1.0


def rbs_block(qc, phi, q0=0, q1=1):
    """Blocco M-conservante (rotazione di Givens reale nel settore {|01>,|10>}).

    Ruolo nel modulo: e' il blocco condiviso da ansatz_PMA_Mcons(),
    ansatz_PMA_2q() e ansatz_PMA_1q() -- l'unica primitiva a due qubit
    di questo file, riusata con parametri diversi dalle altre funzioni.
    Ruolo nell'insieme: e' la stessa identica costruzione (a meno del
    nome della funzione) di rbs_block() in vqe_test2.py -- confrontarli
    conferma che le due implementazioni indipendenti concordano.
    """
    sub = QuantumCircuit(2, name="RBS")
    sub.h(0); sub.h(1); sub.cz(0, 1)
    sub.ry(phi, 0); sub.ry(-phi, 1)
    sub.cz(0, 1); sub.h(0); sub.h(1)
    qc.append(sub.to_gate(label="RBS"), [q0, q1])

def ansatz_HA(reps=2):
    """Ansatz hardware-efficient (Ry + CZ, n_local di Qiskit).

    Ruolo nel modulo: e' l'alternativa "generica" (non motivata dalla
    fisica del problema) messa a confronto con le varianti PMA nel
    resto del file.
    Ruolo nell'insieme: stessa idea di make_ha_ansatz() in vqe_dimer.py
    (dove viene effettivamente usata per il confronto HA-vs-PMA) --
    qui e' solo la definizione, non collegata a nessuna ottimizzazione.
    """
    return n_local(2, rotation_blocks="ry", entanglement_blocks="cz",
                   entanglement="full", reps=reps)

def ansatz_PMA_Mcons(K=1):
    """PMA nel settore M conservato: X + K blocchi RBS.

    Ruolo nel modulo: e' la variante piu' vincolata delle famiglie PMA
    qui definite -- K blocchi RBS in sequenza, senza le rotazioni Ry
    aggiuntive che rompono la conservazione di M (a differenza di
    ansatz_PMA_2q()).
    Ruolo nell'insieme: non ha un impiego diretto altrove in questo
    pacchetto -- resta come variante esplorativa, utile per un confronto
    di espressivita' fra ansatz che conservano M e ansatz che non lo
    conservano, mai eseguito in questo pacchetto specifico.
    """
    p = ParameterVector("p", K)
    qc = QuantumCircuit(2); qc.x(1)
    for k in range(K):
        rbs_block(qc, p[k])
    return qc

def ansatz_PMA_2q(nparam=3):
    """PMA esteso: RBS + coppie di Ry indipendenti (rompono la conservazione di M).

    Ruolo nel modulo: e' la variante piu' vicina, concettualmente, alla
    scelta finale del progetto (pma_2q() in vqe_test2.py) -- stessa idea
    (RBS piu' rotazioni indipendenti), stesso numero di parametri di
    default.
    Ruolo nell'insieme: e' l'ansatz che, nella sua forma equivalente
    definita in vqe_test2.py, viene effettivamente usato per produrre i
    parametri VQE di questo pacchetto -- qui e' la versione "di
    libreria", li' la versione realmente eseguita.
    """
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(2); qc.x(1)
    rbs_block(qc, p[0]); i = 1
    while i < nparam:
        qc.ry(p[i], 0); qc.ry(p[i + 1], 1); i += 2
    return qc

def ansatz_PMA_W(b):
    """PMA alla Crippa: stato iniziale scelto nel settore giusto + gate W (1 par.).

    Ruolo nel modulo: e' la variante che segue piu' da vicino la
    costruzione originale di Crippa et al. (2021) -- stato iniziale
    dipendente da b/J (singoletto o |11>) invece di partire sempre da
    |10> come le altre varianti PMA qui definite.
    Ruolo nell'insieme: stessa idea di make_pma_ansatz() in
    vqe_dimer.py, dove questa costruzione (ridefinita localmente) e'
    quella davvero usata per il confronto HA-vs-PMA del pacchetto.
    """
    th = ParameterVector("th", 1)
    qc = QuantumCircuit(2)
    if b / J < 2.0:
        qc.x(0); qc.h(0); qc.cx(0, 1); qc.x(0)      # singoletto
    else:
        qc.x(0); qc.x(1)                             # |11>
    qc.cx(0, 1); qc.ry(th[0], 0); qc.cx(0, 1)        # W_01(theta)
    return qc

def ansatz_PMA_1q(nparam=1):
    """PMA con parametrizzazione alternata (RBS, poi Ry a 1 qubit, poi RBS...).

    Ruolo nel modulo: e' la variante meno usata delle famiglie qui
    definite -- un pattern di parametrizzazione esplorativo, alternando
    blocchi RBS a 2 qubit e rotazioni Ry a singolo qubit sul secondo
    registro.
    Ruolo nell'insieme: non ha un impiego diretto altrove in questo
    pacchetto -- inclusa per completezza della libreria di varianti
    esplorate durante lo sviluppo del progetto, non parte della catena
    computazionale effettivamente eseguita qui.
    """
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(2); qc.x(1); i = 0
    rbs_block(qc, p[i]); i += 1
    while i < nparam:
        qc.ry(p[i], 1); i += 1
        if i < nparam:
            rbs_block(qc, p[i]); i += 1
    return qc

