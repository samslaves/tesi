"""
Onda 1 (nessuna dipendenza) -- self-test del benchmark esatto (trimer_ring_exact.py):
diagonalizzazione, simmetrie, gap, verifica Opzione A vs B del termine DM.

Ingresso: nessuno. Uscita: nessun file, solo resoconto a schermo.
Chi lo consuma: nessuno (punto di arrivo).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))
import runpy
runpy.run_path(os.path.join("..", "codice", "trimer_ring_exact.py"), run_name="__main__")
