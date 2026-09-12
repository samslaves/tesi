"""
Onda 1 (nessuna dipendenza) -- ottimizza il VQE con termine DM (ansatz
W-2q.6) al punto di lavoro confermato e salva i parametri ottimali.

Ingresso: nessuno. Uscita: dati/w2q6_params_optimal.npz.
Chi lo consuma: 05 (validazione correlatori con VQE reale), e tutta la
    pipeline di Parte 2 (pacchetto separato).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))
import runpy
runpy.run_path(os.path.join("..", "codice", "vqe_w2q6_trimero_anello.py"), run_name="__main__")
