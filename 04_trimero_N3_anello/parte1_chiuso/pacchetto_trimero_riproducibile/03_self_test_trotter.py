"""
Onda 1 (nessuna dipendenza) -- self-test del modulo Trotter: equivalenza
circuito/matrice, convergenza N->infinito, fattorizzazione H0.

Ingresso: nessuno. Uscita: nessun file, solo resoconto a schermo.
Chi lo consuma: nessuno.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))
import runpy
runpy.run_path(os.path.join("..", "codice", "trotter_trimero_anello.py"), run_name="__main__")
