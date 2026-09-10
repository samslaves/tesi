"""
Onda 1 (nessuna dipendenza) -- ottimizza il VQE con termine DM (ansatz
W-2q.6, 3 qubit) al punto di lavoro confermato (b=b_c=2.4, D=0.15, mode
"B") e salva i parametri ottimali.

Ingresso: nessuno (calcola tutto da zero: Hamiltoniana + ottimizzazione).
Uscita: dati/w2q6_params_optimal.npz -- campi: params (6 parametri VQE),
    E_vqe, E_exact, fidelity.
Chi lo consuma: 02, 03, 04, 05, 06 (tutti gli stadi successivi dipendono
    da questi parametri).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "codice"))
os.makedirs("dati", exist_ok=True)

import runpy
# vqe_w2q6_trimero_anello.py (Parte 1) esegue l'ottimizzazione nel suo
# blocco __main__ e salva "w2q6_params_optimal.npz" nella cwd -- lo
# eseguiamo con la cwd puntata su dati/ per rispettare la struttura del
# pacchetto senza modificare il file di Parte 1 (bit-per-bit identico al
# Project).
os.chdir("dati")
sys.path.insert(0, os.path.join("..", "codice"))
runpy.run_path(os.path.join("..", "codice", "vqe_w2q6_trimero_anello.py"), run_name="__main__")
